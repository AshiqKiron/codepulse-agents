import os
from groq import Groq


class PM_AGENT:
    def create_roadmap(self, gh_themes: str, soc_themes: str) -> str:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            return "Error: Missing GROQ_API_KEY in secrets"
            
        client = Groq(api_key=api_key)

        messages = [
            {"role": "system", "content": "You are VP of Product for VS Code. Propose exactly 1 strategic initiative."},
            {"role": "user", "content": f"""GitHub Pain Points: {gh_themes}
Social Sentiment: {soc_themes}
Format: [Name] - [Problem] - [Metric]"""}
        ]

        try:
            response = client.chat.completions.create(
                model="llama3-8b-8192",
                messages=messages,
                temperature=0.2,
                max_tokens=200,
                timeout=30
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Roadmap failed: {str(e)[:80]}"
