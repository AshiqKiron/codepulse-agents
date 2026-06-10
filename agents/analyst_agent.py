from langchain_huggingface import HuggingFaceEndpoint
from langchain_core.prompts import PromptTemplate
import os

class AnalystAgent:
    def __init__(self):
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=os.getenv("HF_TOKEN"),
            temperature=0.1
        )

    def summarize_pain_points(self, data_source, items):
        """Summarize top 5 items into key themes"""
        if not items:
            return "No data available for analysis."
            
        text_items = "\n".join([f"- {item['title']}" for item in items])
        
        prompt = PromptTemplate.from_template(
            "You are a Product Analyst. Analyze these {source} items for VS Code.\n"
            "Identify the top 3 recurring pain points or themes.\n"
            "Items:\n{text}\n\nThemes:"
        )
        chain = prompt | self.llm
        return chain.invoke({"source": data_source, "text": text_items})
