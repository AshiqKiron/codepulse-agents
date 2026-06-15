import streamlit as st
import os
import requests


class AnalystAgent:
    def __init__(self):
        self.token = os.getenv("HF_TOKEN")
        if not self.token:
            raise ValueError("Missing HF_TOKEN secret")
        self.api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        self.headers = {"Authorization": f"Bearer {self.token}"}

    # ✅ FIX: Removed 'self' from arguments. Only hashable types allowed.
    @staticmethod
    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(source: str, items: list) -> str:
        if not items:
            return "No recent data."

        # Re-initialize client inside static method
        token = os.getenv("HF_TOKEN")
        api_url = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
        headers = {"Authorization": f"Bearer {token}"}

        text = "\n".join([f"- {i['title']}" for i in items])
        prompt = (
            f"[INST] Extract 2 key pain points from these {source} items. Be concise.\n"
            f"{text}\nPoints: [/INST]"
        )

        try:
            response = requests.post(
                api_url,
                headers=headers,
                json={
