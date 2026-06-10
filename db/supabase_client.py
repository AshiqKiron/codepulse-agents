# db/supabase_client.py
import os
from supabase import create_client, Client
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


class SupabaseClient:
    """
    Manages all interactions with the Supabase 'insights' table.
    Designed for online deployment where credentials come from environment variables/secrets.
    """

    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL")
        self.key: str = os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "Supabase credentials not found. "
                "Please set SUPABASE_URL and SUPABASE_KEY in your deployment secrets."
            )

        self.supabase: Client = create_client(self.url, self.key)

    def save_insight(
        self,
        source: str,
        content: str,
        sentiment: str,
        embedding: Optional[List[float]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Save a single insight to the database.

        Args:
            source: Data source (e.g., 'github', 'hackernews', 'reddit')
            content: The text content of the issue/comment/post
            sentiment: Analyzed sentiment ('Positive', 'Negative', 'Neutral')
            embedding: Optional vector embedding for semantic search

        Returns:
            Inserted row data or None on failure
        """
        try:
            data = {
                "source": source,
                "content": content[:5000],  # Truncate to avoid DB limits
                "sentiment": sentiment,
                "created_at": datetime.now().isoformat(),
            }

            # Only include embedding if provided and non-empty
            if embedding and len(embedding) > 0:
                data["embedding"] = embedding

            response = self.supabase.table("insights").insert(data).execute()
            return response.data[0] if response.data else None

        except Exception as e:
            print(f"❌ Error saving insight: {e}")
            return None

    def get_recent_insights(
        self, limit: int = 10, source: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve recent insights, optionally filtered by source.

        Args:
            limit: Max number of records to return
            source: Filter by specific source (optional)

        Returns:
            List of insight dictionaries ordered by newest first
        """
        try:
            query = (
                self.supabase.table("insights")
                .select("*")
                .order("created_at", desc=True)
                .limit(limit)
            )

            if source:
                query = query.eq("source", source)

            response = query.execute()
            return response.data if response.data else []

        except Exception as e:
            print(f"❌ Error fetching insights: {e}")
            return []

    def get_sentiment_trends(self, days: int = 7) -> Dict[str, int]:
        """
        Get sentiment distribution over the last N days.

        Args:
            days: Number of days to look back

        Returns:
            Dictionary with counts per sentiment category
        """
        try:
            threshold = (datetime.now() - timedelta(days=days)).isoformat()

            response = (
                self.supabase.table("insights")
                .select("sentiment")
                .gte("created_at", threshold)
                .execute()
            )

            sentiments = [item.get("sentiment", "Unknown") for item in response.data]

            return {
                "Positive": sentiments.count("Positive"),
                "Negative": sentiments.count("Negative"),
                "Neutral": sentiments.count("Neutral"),
                "Unknown": sentiments.count("Unknown"),
            }

        except Exception as e:
            print(f"❌ Error fetching sentiment trends: {e}")
            return {"Positive": 0, "Negative": 0, "Neutral": 0, "Unknown": 0}

    def get_insight_count_by_source(self) -> Dict[str, int]:
        """
        Get total insight count grouped by source for dashboard stats.

        Returns:
            Dictionary mapping source names to record counts
        """
        try:
            response = (
                self.supabase.table("insights")
                .select("source", count="exact")
                .execute()
            )

            # Group manually since Supabase doesn't have GROUP BY in Python client
            sources: Dict[str, int] = {}
            for item in response.data:
                src = item.get("source", "unknown")
                sources[src] = sources.get(src, 0) + 1

            return sources

        except Exception as e:
            print(f"❌ Error counting insights by source: {e}")
            return {}
