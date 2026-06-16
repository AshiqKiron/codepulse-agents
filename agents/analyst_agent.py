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
            return "Error: GROQ_API_KEY missing in Streamlit Secrets"

        titles = [f"- {i.get('title', 'Unknown')}" for i in items]
        text_content = "\n".join(titles)
        
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "Extract 2 concise pain points."},
                {"role": "user", "content": f"{source} items:\n{text_content}"}
            ],
            "temperature": 0.1,
            "max_tokens": 150
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=30)
            if resp.status_code == 401:
                return "Error: Invalid Groq API Key"
            if resp.status_code == 400:
                err = resp.json().get("error", {}).get("message", "Bad Request")
                return f"Groq Error: {err}"
                
            resp.raise_for_status()
            return resp.json()["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Request failed: {str(e)[:80]}"
