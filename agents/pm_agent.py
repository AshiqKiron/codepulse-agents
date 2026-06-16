import os
import requests


class PM_AGENT:
    def create_roadmap(self, gh_themes: str, soc_themes: str) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Error: GROQ_API_KEY missing in Streamlit Secrets"
            
        url = "https://api.groq.com/openai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "llama-3.1-8b-instant",  # ✅ CURRENT VALID MODEL
            "messages": [
                {"role": "system", "content": "VP of Product. Propose 1 initiative."},
                {"role": "user", "content": f"GitHub: {gh_themes}\nSocial: {soc_themes}\nFormat: [Name] - [Problem] - [Metric]"}
            ],
            "temperature": 0.2,
            "max_tokens": 200
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
