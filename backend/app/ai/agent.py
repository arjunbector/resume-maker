from smolagents import LiteLLMModel
from loguru import logger
import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class ResumeAgent:
    """
    AI Agent for resume generation and analysis.
    Supports multiple LLM providers (Gemini, Ollama).
    """

    def __init__(self, model: str = "gemini/gemini-2.5-flash"):
        """
        Initialize the ResumeAgent with specified model.

        Args:
            model: Model identifier. Supported formats:
                - "gemini/gemini-2.5-flash" (Gemini)
                - "ollama_chat/gpt-oss" (Ollama)
        """
        self.model_id = model
        self.model = self._initialize_model(model)
        logger.info(f"ResumeAgent initialized with model: {model}")

    def _initialize_model(self, model: str) -> LiteLLMModel:
        """
        Initialize the LLM model based on provider.

        Args:
            model: Model identifier string

        Returns:
            Initialized LiteLLMModel instance
        """
        if "ollama" in model:
            logger.info("Initializing Ollama model")
            return LiteLLMModel(
                model_id=model,
                api_base="http://localhost:11434",
                num_ctx=8192
            )
        elif "gemini" in model:
            logger.info("Initializing Gemini model")
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                logger.warning("GEMINI_API_KEY not found in environment")
            return LiteLLMModel(
                model_id=model,
                api_key=api_key
            )
        else:
            logger.warning(f"Unknown model provider: {model}, defaulting to Gemini")
            return LiteLLMModel(
                model_id="gemini/gemini-2.5-flash",
                api_key=os.getenv("GEMINI_API_KEY")
            )

    def run_prompt(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Run an arbitrary prompt through the LLM and return the response.

        Args:
            prompt: The user prompt to send to the LLM
            system_prompt: Optional system prompt to set context

        Returns:
            The LLM's response as a string
        """
        try:
            logger.debug(f"Running prompt: {prompt[:100]}...")

            # Prepare messages
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": prompt})

            # Call the model
            response = self.model(messages)

            # Extract content from ChatMessage object
            if hasattr(response, 'content'):
                response_text = response.content
            elif isinstance(response, str):
                response_text = response
            else:
                response_text = str(response)

            logger.debug(f"Received response: {response_text[:100]}...")
            return response_text

        except Exception as e:
            logger.error(f"Error running prompt: {str(e)}")
            raise

    def __repr__(self) -> str:
        return f"ResumeAgent(model='{self.model_id}')"
