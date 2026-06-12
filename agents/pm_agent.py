import os

try:
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    try:
        from langchain_community.llms import HuggingFaceHub as HuggingFaceEndpoint
    except ImportError:
        from langchain.llms import HuggingFaceHub as HuggingFaceEndpoint


class PM_AGENT:
    def __init__(self):
        token = os.getenv("HF_TOKEN")
        if not token: 
            raise ValueError("Missing HF_TOKEN secret")
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=token,
            temperature=0.2, 
            max_new_tokens=200
        )

    def create_roadmap(self, gh_themes, soc_themes):
        prompt = f"""VP Product VS Code. 1 initiative only:
GitHub: {gh_themes}
Social: {soc_themes}
Format: [Name] - [Problem] - [Metric]"""
        resp = self.llm.invoke(prompt)
        return resp.content if hasattr(resp, 'content') else str(resp)
