import streamlit as st
import os
import requests


class AnalystAgent:
    # ✅ FIX: Static method with simple, safe string formatting
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(source: str, items: list) -> str:
        if not items:
            return "No recent data."

        token = os.getenv("HF_TOKEN")
        if not token:
            return "Error: Missing HF_TOKEN"

        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {token}"}

        # Safe title extraction - no complex f-strings
        titles = []
        for i in items:
            t = i.get('title', 'Unknown Issue')
            titles.append(f"- {t}")
        
        text_content = "\n".join(titles)
        
        # Simple prompt without nested brackets
        prompt = f"[INST] Extract 2 key pain points from these {source} items. Be concise.\n{text_content}\nPoints: [/INST]"

        try:
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 150,
                    "temperature": 0.1,
                    "return_full_text": False
                }
            }

            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
            
            return "Analysis failed: Unexpected API response"

        except requests.exceptions.Timeout:
            return "Analysis timed out. Please try again."
        except Exception as e:
            return f"Analysis failed: {str(e)[:80]}"
