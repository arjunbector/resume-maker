import os
from google import genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.model_id = "gemini-2.5-flash"
    
    def generate_content(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model=self.model_id,
            contents=prompt
        )
        return response.text

gemini_client = GeminiClient()