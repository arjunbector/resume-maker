from smolagents.models import LiteLLMModel
from smolagents import CodeAgent
import os
from dotenv import load_dotenv

load_dotenv()

class SmolagentsPipeline:
    def __init__(self):
        # Use LiteLLM to access Gemini through smolagents
        self.model = LiteLLMModel(
            model_id="gemini/gemini-2.5-flash",
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.agent = CodeAgent(
            tools=[],
            model=self.model
        )
    
    def process_prompt(self, user_prompt: str) -> str:
        """Single step pipeline: pass prompt to Gemini model via smolagents"""
        response = self.agent.run(user_prompt)
        return response

pipeline = SmolagentsPipeline()