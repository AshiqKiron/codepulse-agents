import os
import requests


class PM_AGENT:
    def __init__(self):
        self.token = os.getenv("HF_TOKEN")
        if not self.token:
            raise ValueError("Missing HF_TOKEN secret")
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    def create_roadmap(self, gh_themes: str, soc_themes: str) -> str:
        prompt = (
            f"[INST] VP Product VS Code. Propose 1 strategic initiative:\n"
            f"GitHub Pain Points: {gh_themes}\n"
            f"Social Sentiment: {soc_themes}\n"
            f"Format: [Name] - [Problem] - [Metric] [/INST]"
        )

        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json={
                    "inputs": prompt,
                    "parameters": {
                        "max_new_tokens": 200,
                        "temperature": 0.2,
                        "return_full_text": False
                    }
                },
                timeout=30
            )
            response.raise_for_status()
            result = response.json()

            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "").strip()
            elif isinstance(result, dict):
                return result.get("generated_text", "").strip()
            return "Roadmap generation failed"

        except Exception as e:
            return f"Roadmap failed: {str(e)[:80]}"
