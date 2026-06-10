from langchain_huggingface import HuggingFaceEndpoint
import os

class PM_AGENT:
    def __init__(self):
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=os.getenv("HF_TOKEN"),
            temperature=0.2
        )

    def create_roadmap(self, github_themes, social_themes):
        prompt = f"""You are VP of Product for VS Code. Based on these inputs, propose 3 strategic initiatives:

Technical Pain Points (GitHub):
{github_themes}

User Sentiment (Social):
{social_themes}

Format:
1. Initiative Name: [Name]
   - Problem Solved: [Specific pain point]
   - Metric for Success: [Measurable outcome]"""
        return self.llm.invoke(prompt)
