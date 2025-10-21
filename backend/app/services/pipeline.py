from smolagents import (
    ToolCallingAgent,
    LiteLLMModel,
)
import os

from .scraper import get_website_content


class JobQuestionsPipeline:
    def __init__(self, model: str = "ollama_chat/gpt-oss"):

        if "ollama" in model:
            self.model = LiteLLMModel(
                model_id = model,
                api_base = "http://localhost:11434",
                num_ctx = 8192
            )
        elif "gemini" in model:
            self.model = LiteLLMModel(
                model_id = model,
                api_key = os.getenv("GEMINI_API_KEY")
            )

    @property
    def agent(self) -> ToolCallingAgent:
        return ToolCallingAgent(tools = [get_website_content], model = self.model)

