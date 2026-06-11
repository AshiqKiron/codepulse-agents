import streamlit as st
import os

# Resilient imports for Python 3.12/3.14
try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    from langchain.prompts import PromptTemplate

try:
    from langchain_huggingface import HuggingFaceEndpoint
except ImportError:
    from langchain_community.llms import HuggingFaceHub as HuggingFaceEndpoint


class AnalystAgent:
    def __init__(self):
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("Missing HF_TOKEN secret")
            
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=hf_token,
            temperature=0.1,
            max_new_tokens=300  # Shorter responses = faster
        )

    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(self, data_source, items):
        if not items:
            return "No data available."
            
        text_items = "\n".join([f"- {item['title']}" for item in items])
        
        prompt = PromptTemplate.from_template(
            "Analyze these {source} items for VS Code.\n"
            "Identify top 3 pain points concisely.\n"
            "Items:\n{text}\n\nThemes:"
        )
        chain = prompt | self.llm
        response = chain.invoke({"source": data_source, "text": text_items})
        
        # Handle string or AIMessage response
        return response.content if hasattr(response, 'content') else str(response)
