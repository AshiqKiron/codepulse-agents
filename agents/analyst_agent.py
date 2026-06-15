import os
import requests


class PM_AGENT:
    def create_roadmap(self, gh_themes: str, soc_themes: str) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Error: Missing GROQ_API_KEY in secrets"
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama3-8b-8192",
            "messages": [
                {"role": "system", "content": "You are VP of Product for VS Code."},
                {"role": "user", "content": f"GitHub: {gh_themes}\nSocial: {soc_themes}\nFormat: [Name] - [Problem] - [Metric]"}
            ],
            "temperature": 0.2,
            "max_tokens": 200
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
        except Exception as e:
            return f"Roadmap failed: {str(e)[:80]}"
