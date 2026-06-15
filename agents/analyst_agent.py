import streamlit as st
import os
from huggingface_hub import InferenceClient


class AnalystAgent:
    def __init__(self):
        token = os.getenv("HF_TOKEN")
        if not token: 
            raise ValueError("Missing HF_TOKEN secret")
        self.client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            token=token
        )

    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(self, source, items):
        if not items: 
            return "No recent data."
        text = "\n".join([f"- {i['title']}" for i in items])
        
        # ✅ REPLACED PromptTemplate with f-string
        prompt = (
            f"Extract 2 key pain points from these {source} items. Be concise.\n"
            f"{text}\nPoints:"
        )
        
        response = self.client.text_generation(
            prompt,
            max_new_tokens=150,
            temperature=0.1,
            return_full_text=False
        )
        return response.strip()
