import os
from typing import Optional

# Resilient imports
try:
    from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
except ImportError:
    from langchain_community.llms import HuggingFaceHub as HuggingFaceEndpoint
    ChatHuggingFace = None


class PM_AGENT:
    """Generates strategic product roadmap recommendations based on analyzed pain points."""

    def __init__(self):
        self.llm = self._init_llm()

    def _init_llm(self):
        """Initialize LLM with same fallback pattern as AnalystAgent."""
        hf_token = os.getenv("HF_TOKEN")
        if not hf_token:
            raise ValueError("HF_TOKEN secret is required but not found.")

        try:
            return ChatHuggingFace(
                llm=HuggingFaceEndpoint(
                    repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                    huggingfacehub_api_token=hf_token,
                    temperature=0.2,
                    max_new_tokens=768,
                )
            )
        except Exception:
            return HuggingFaceEndpoint(
                repo_id="mistralai/Mistral-7B-Instruct-v0.2",
                huggingfacehub_api_token=hf_token,
                temperature=0.2,
                max_new_tokens=768,
            )

    def create_roadmap(self, github_themes: str, social_themes: str) -> str:
        """
        Generate 3 strategic initiatives for VS Code's next quarter.

        Args:
            github_themes: Summarized technical pain points from GitHub
            social_themes: Summarized user sentiment from HN/Reddit

        Returns:
            Formatted roadmap recommendation string
        """
        prompt = f"""You are the VP of Product for Visual Studio Code. 
Based on the following real user feedback, propose exactly 3 strategic initiatives for the next quarter.

TECHNICAL PAIN POINTS (GitHub Issues):
{github_themes}

USER SENTIMENT (Social Discussions):
{social_themes}

OUTPUT FORMAT (strictly follow this structure):
1. Initiative Name: [Clear, concise name]
   - Problem Solved: [Specific pain point addressed]
   - Metric for Success: [Measurable outcome, e.g., "Reduce related issues by 30%"]

2. Initiative Name: [Clear, concise name]
   - Problem Solved: [Specific pain point addressed]
   - Metric for Success: [Measurable outcome]

3. Initiative Name: [Clear, concise name]
   - Problem Solved: [Specific pain point addressed]
   - Metric for Success: [Measurable outcome]

Do NOT include any preamble, disclaimers, or additional commentary."""

        response = self.llm.invoke(prompt)

        # Handle both string and AIMessage responses
        if hasattr(response, 'content'):
            return response.content
        return str(response)
