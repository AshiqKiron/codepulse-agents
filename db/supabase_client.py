import os
from supabase import create_client, Client
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

class SupabaseClient:
    def __init__(self):
        self.url: str = os.getenv("SUPABASE_URL")
        self.key: str = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("Supabase URL and Key must be set in environment variables.")
        
        # Initialize the Supabase client
        self.supabase: Client = create_client(self.url, self.key)

    def save_insight(self, source: str, content: str, sentiment: str, embedding: list = None):
        """
        Save a single insight (e.g., a GitHub issue summary or HN comment) to the database.
        """
        try:
            data = {
                "source": source,       # e.g., "github", "hackernews", "reddit"
                "content": content,     # The text of the issue/comment
                "sentiment": sentiment, # e.g., "Negative", "Positive"
                "created_at": datetime.now().isoformat(),
                # "embedding": embedding # Optional: If you want to use vector search later
            }
            
            response = self.supabase.table("insights").insert(data).execute()
            return response.data
        except Exception as e:
            print(f"Error saving insight: {e}")
            return None

    def get_recent_insights(self, limit: int = 10, source: str = None):
        """
        Retrieve recent insights, optionally filtered by source.
        """
        try:
            query = self.supabase.table("insights").select("*").order("created_at", desc=True).limit(limit)
            
            if source:
                query = query.eq("source", source)
                
            response = query.execute()
            return response.data
        except Exception as e:
            print(f"Error fetching insights: {e}")
            return []

    def get_sentiment_trends(self, days: int = 7):
        """
        Get a count of sentiments over the last N days for trending analysis.
        """
        try:
            # Calculate date threshold
            from datetime import timedelta
            threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            response = self.supabase.table("insights").select("sentiment").gte("created_at", threshold).execute()
            
            sentiments = [item['sentiment'] for item in response.data]
            trend_data = {
                "Positive": sentiments.count("Positive"),
                "Negative": sentiments.count("Negative"),
                "Neutral": sentiments.count("Neutral")
            }
            return trend_data
        except Exception as e:
            print(f"Error fetching trends: {e}")
            return {}

# Example usage for testing
if __name__ == "__main__":
    try:
        client = SupabaseClient()
        print("✅ Supabase Client initialized successfully.")
        
        # Test saving an insight
        test_insight = client.save_insight(
            source="test", 
            content="This is a test insight from VS Code analysis.", 
            sentiment="Neutral"
        )
        print(f"Saved insight: {test_insight}")
        
        # Test fetching insights
        recent = client.get_recent_insights(limit=5)
        print(f"Recent insights: {len(recent)} found.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
