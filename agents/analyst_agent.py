import streamlit as st
import os
from typing import List, Dict, Any

# Resilient import for Streamlit Cloud / Python 3.14 compatibility
try:
    from langchain_core.prompts import PromptTemplate
except ImportError:
    from langchain.prompts import PromptTemplate

try:
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
except ImportError:
    # Fallback for older langchain versions
    from langchain_community.llms import HuggingFaceHub as HuggingFaceEndpoint
    ChatHuggingFace = None


class AnalystAgent:
    """Analyzes user feedback and extracts pain point themes using Mistral-7B."""

    def __init__(self):
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize LLM with fallbacks for different langchain versions."""
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN secret is required but not found.")

        try:
            # Preferred: ChatHuggingFace wrapper (newer langchain)
            return ChatHuggingFace(
                llm=HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                    huggingfacehub_api_token=hf_token,
                    temperature=0.1,
                    max_new_tokens=512,
                )
            )
        except Exception:
            # Fallback: Direct endpoint (older langchain)
            return HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                huggingfacehub_api_token=hf_token,
                temperature=0.1,
                max_new_tokens=512,
            )

    @st.cache_data(ttl=3600, show_spinner=False)
    def summarize_pain_points(self, data_source: str, items: List[Dict[str, Any]]) -> str:
        """
        Summarize user feedback into actionable themes.
        Results cached for 1 hour to avoid redundant API calls.
        """
        if not items:
            return "No data available for analysis."

        text_items = "\n".join([f"- {item.get('title', '')}" for item in items])

        prompt = PromptTemplate.from_template(
            "You are a Product Analyst specializing in developer tools. "
            "Analyze these {source} items for VS Code.\n"
            "Identify the top 3 recurring pain points or themes.\n"
            "Be specific and actionable.\n\n"
            "Items:\n{text}\n\nThemes:"
        )

        chain = prompt | self.llm
        response = chain.invoke({"source": data_source, "text": text_items})

        # Handle both string and AIMessage responses
        if hasattr(response, 'content'):
            return response.content
        return str(response)
