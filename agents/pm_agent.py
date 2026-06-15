import os
from huggingface_hub import InferenceClient


class PM_AGENT:
    def __init__(self):
        token = os.getenv("HF_TOKEN")
        if not token: 
            raise ValueError("Missing HF_TOKEN secret")
        self.client = InferenceClient(
            model="mistralai/Mistral-7B-Instruct-v0.2",
            token=token
        )

    def create_roadmap(self, gh_themes, soc_themes):
        prompt = (
            f"VP Product VS Code. Propose 1 strategic initiative:\n"
            f"GitHub Pain Points: {gh_themes}\n"
            f"Social Sentiment: {soc_themes}\n"
            f"Format: [Name] - [Problem] - [Metric]"
        )
        
        response = self.client.text_generation(
            prompt,
            max_new_tokens=200,
            temperature=0.2,
            return_full_text=False
        )
        return response.strip()
