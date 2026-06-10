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
        prompt = f"""
        You are the VP of Product for VS Code. 
        Based on these technical issues and social sentiments, propose 3 strategic initiatives for the next quarter.
        
        Technical Pain Points (GitHub):
        {github_themes}
        
        User Sentiment (Social):
        {social_themes}
        
        Output Format:
        1. Initiative Name: [Name]
           - Problem Solved: [Specific pain point]
           - Metric for Success: [e.g., Reduce issue count by 20%]
        """
        return self.llm.invoke(prompt)
