import streamlit as st
import os
from groq import Groq


class AnalystAgent:
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(source: str, items: list) -> str:
        if not items:
            return "No recent data."

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Error: Missing GROQ_API_KEY"

        client = Groq(api_key=api_key)

        titles = []
        for i in items:
            t = i.get('title', 'Unknown Issue')
            titles.append(f"- {t}")
        
        text_content = "\n".join(titles)
        
        messages = [
            {"role": "system", "content": "You are a product analyst. Be concise."},
            {"role": "user", "content": f"Extract 2 key pain points from these {source} items:\n{text_content}"}
        ]

        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",  # Free tier model
                messages=messages,
                temperature=0.1,
                max_tokens=150,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Analysis failed: {str(e)[:80]}"
