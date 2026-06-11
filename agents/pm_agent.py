import os

try:
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    from langchain_community.llms import HuggingFaceHub as HuggingFaceEndpoint


class PM_AGENT:
    def __init__(self):
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("Missing HF_TOKEN secret")
            
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=hf_token,
            temperature=0.2,
            max_new_tokens=400
        )

    def create_roadmap(self, github_themes, social_themes):
        prompt = f"""You are VP of Product for VS Code. Propose 3 strategic initiatives:

Technical Pain Points:
{github_themes}

User Sentiment:
{social_themes}

Format:
1. Initiative: [Name]
   - Problem: [Specific issue]
   - Metric: [Measurable outcome]"""
        
        response = self.llm.invoke(prompt)
        return response.content if hasattr(response, 'content') else str(response)
