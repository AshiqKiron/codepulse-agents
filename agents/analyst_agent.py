import streamlit as st
import os
import requests


class AnalystAgent:
    def __init__(self):
        self.token = os.getenv("HF_TOKEN")
        if not self.token:
            raise ValueError("Missing HF_TOKEN secret")
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(self, source, items):
        if not items:
            return "No recent data."

        text = "\n".join([f"- {i['title']}" for i in items])
        prompt = (
            f"[INST] Extract 2 key pain points from these {source} items. Be concise.\n"
            f"{text}\nPoints: [/INST]"
        )

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 150,
                        "temperature": 0.1,
                        "return_full_text": False
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            # Handle both list and dict responses
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
            return "Analysis failed: Unexpected API response format"

        except requests.exceptions.Timeout:
            return "Analysis timed out. Please try again."
        except Exception as e:
            return f"Analysis failed: {str(e)[:80]}"
