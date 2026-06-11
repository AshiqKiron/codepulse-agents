import os
from langchain_huggingface import HuggingFaceEndpoint


class PM_AGENT:
    def __init__(self):
        token = os.getenv("HF_TOKEN")
        if not token: raise ValueError("Missing HF_TOKEN")
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=token,
            temperature=0.2, max_new_tokens=300
        )

    def create_roadmap(self, gh_themes, soc_themes):
        prompt = f"""VP Product for VS Code. Propose 3 initiatives:
GitHub: {gh_themes}
Social: {soc_themes}
Format: 1. [Name] - [Problem] - [Metric]"""
        resp = self.llm.invoke(prompt)
        return resp.content if hasattr(resp, 'content') else str(resp)
