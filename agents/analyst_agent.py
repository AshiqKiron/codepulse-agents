import streamlit as st
from langchain_core.prompts import PromptTemplate
import os

class AnalystAgent:
    def __init__(self):
        # Lazy import inside method would be better, but cache handles it
        from langchain_huggingface import HuggingFaceEndpoint
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=os.getenv("HF_TOKEN"),
            temperature=0.1
        )

    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(self, data_source, items):
        """Cached: identical inputs return instantly without API call"""
        if not items:
            return "No data available."
            
        text_items = "\n".join([f"- {item['title']}" for item in items])
        
        prompt = PromptTemplate.from_template(
            "You are a Product Analyst. Analyze these {source} items for VS Code.\n"
            "Identify top 3 recurring pain points or themes.\n"
            "Items:\n{text}\n\nThemes:"
        )
        chain = prompt | self.llm
        return chain.invoke({"source": data_source, "text": text_items})
