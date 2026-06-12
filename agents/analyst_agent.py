import streamlit as st
import os
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint


class AnalystAgent:
    def __init__(self):
        token = os.getenv("HF_TOKEN")
        if not token: 
            raise ValueError("Missing HF_TOKEN secret")
        self.llm = HuggingFaceEndpoint(
            repo_id="mistralai/Mistral-7B-Instruct-v0.2",
            huggingfacehub_api_token=token,
            temperature=0.1, 
            max_new_tokens=150
        )

    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(self, source, items):
        if not items: 
            return "No recent data."
        text = "\n".join([f"- {i['title']}" for i in items])
        prompt = PromptTemplate.from_template(
            "Extract 2 key pain points from these {s} items. Be concise.\n{text}\nPoints:"
        )
        resp = (prompt | self.llm).invoke({"s": source, "text": text})
        return resp.content if hasattr(resp, 'content') else str(resp)
