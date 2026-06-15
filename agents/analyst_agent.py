import streamlit as st
import os
import requests
import time


class AnalystAgent:
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

        # Safe title extraction
        titles = []
        for i in items:
            t = i.get('title', 'Unknown Issue')
            titles.append(f"- {t}")
        
        text_content = "\n".join(titles)
        prompt = f"[INST] Extract 2 key pain points from these {source} items. Be concise.\n{text_content}\nPoints: [/INST]"

        # Retry logic for cold starts / rate limits
        max_retries = 3
        for attempt in range(max_retries):
            try:
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 150,
                        "temperature": 0.1,
                        "return_full_text": False,
                        "wait_for_model": True  # CRITICAL: Waits for model to load instead of timing out
                    }
                }

                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=60  # Increased timeout for cold starts
                )
                
                # Handle rate limiting (429) or model loading (503)
                if response.status_code == 503:
                    wait_time = response.json().get("estimated_time", 20)
                    time.sleep(min(wait_time, 30))  # Wait but cap at 30s
                    continue 
                    
                response.raise_for_status()
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                elif isinstance(result, dict):
                    return result.get("generated_text", "").strip()
                
                return "Analysis failed: Unexpected API response"

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return "Analysis timed out. Model may be loading."
            except Exception as e:
                return f"Analysis failed: {str(e)[:80]}"
        
        return "Analysis failed after multiple retries."
