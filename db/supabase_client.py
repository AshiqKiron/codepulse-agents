import os
from supabase import create_client, Client
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

class SupabaseClient:
    def __init__(self):
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        if not self.url or not self.key:
            raise ValueError("Missing Supabase credentials in secrets.")
        self.supabase = create_client(self.url, self.key)

    def save_insight(self, source: str, content: str, sentiment: str, 
                     embedding: Optional[List[float]] = None) -> Optional[Dict]:
        try:
            data = {"source": source, "content": content[:5000], 
                    "sentiment": sentiment, "created_at": datetime.now().isoformat()}
            if embedding: data["embedding"] = embedding
            resp = self.supabase.table("insights").insert(data).execute()
            return resp.data[0] if resp.data else None
        except Exception as e:
            print(f"DB Save Error: {e}")
            return None

    def get_recent_insights(self, limit=10, source=None) -> List[Dict]:
        try:
            q = self.supabase.table("insights").select("*").order("created_at", desc=True).limit(limit)
            if source: q = q.eq("source", source)
            return q.execute().data or []
        except Exception: return []

    def get_sentiment_trends(self, days=7) -> Dict[str, int]:
        try:
            threshold = (datetime.now() - timedelta(days=days)).isoformat()
            resp = self.supabase.table("insights").select("sentiment").gte("created_at", threshold).execute()
            sents = [i.get("sentiment","Unknown") for i in resp.data]
            return {k: sents.count(k) for k in ["Positive","Negative","Neutral","Unknown"]}
        except Exception: return {"Positive":0,"Negative":0,"Neutral":0,"Unknown":0}
