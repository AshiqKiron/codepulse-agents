import streamlit as st
import os
import requests


class AnalystAgent:
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(source: str, items: list) -> str:
        if not items:
            return "No recent data."

        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Error: Missing GROQ_API_KEY in secrets"

        titles = []
        for i in items:
            t = i.get('title', 'Unknown Issue')
            titles.append(f"- {t}")
        
        text_content = "\n".join(titles)
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are a product analyst. Be concise."},
                {"role": "user", "content": f"Extract 2 key pain points from these {source} items:\n{text_content}"}
            ],
            "temperature": 0.1,
            "max_tokens": 150
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Analysis failed: {str(e)[:80]}"
