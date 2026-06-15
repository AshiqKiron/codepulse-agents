import os
import requests
import time


class PM_AGENT:
    def create_roadmap(self, gh_themes: str, soc_themes: str) -> str:
        token = os.getenv("HF_TOKEN")
        if not token:
            return "Error: Missing HF_TOKEN"
            
        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {token}"}

        prompt = (
            f"[INST] VP Product VS Code. Propose 1 strategic initiative:\n"
            f"GitHub Pain Points: {gh_themes}\n"
            f"Social Sentiment: {soc_themes}\n"
            f"Format: [Name] - [Problem] - [Metric] [/INST]"
        )

        max_retries = 3
        for attempt in range(max_retries):
            try:
                payload = {
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 200,
                        "temperature": 0.2,
                        "return_full_text": False,
                        "wait_for_model": True  # CRITICAL FIX
                    }
                }

                response = requests.post(
                    api_url,
                    headers=headers,
                    json=payload,
                    timeout=60
                )

                if response.status_code == 503:
                    wait_time = response.json().get("estimated_time", 20)
                    time.sleep(min(wait_time, 30))
                    continue
                    
                response.raise_for_status()
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "").strip()
                elif isinstance(result, dict):
                    return result.get("generated_text", "").strip()
                    
                return "Roadmap generation failed"

            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue
                return f"Roadmap failed: {str(e)[:80]}"
                
        return "Roadmap failed after retries."
