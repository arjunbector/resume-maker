from fastapi import APIRouter, HTTPException, Request
from loguru import logger
from database.models import PromptRequest
from ai.agent import ResumeAgent
from typing import Optional
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class CustomPromptRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    model: Optional[str] = None  # Allow model override


@router.post("/custom")
def run_custom_prompt(request: CustomPromptRequest, app_request: Request):
    """
    Run a custom prompt through the AI agent and return the response.

    This endpoint allows you to send arbitrary prompts to the LLM.
    Useful for testing, experimentation, or custom AI interactions.
    """
    try:
        logger.info(f"Running custom prompt (length: {len(request.prompt)})")

        # Get the agent from app state
        agent = app_request.app.state.agent

        # Use custom model if provided, otherwise use app state agent
        if request.model:
            logger.info(f"Using custom model: {request.model}")
            custom_agent = ResumeAgent(model=request.model)
            response = custom_agent.run_prompt(
                prompt=request.prompt,
                system_prompt=request.system_prompt
            )
            model_used = request.model
        else:
            response = agent.run_prompt(
                prompt=request.prompt,
                system_prompt=request.system_prompt
            )
            model_used = agent.model_id

        logger.info("Prompt executed successfully")

        return {
            "response": response,
            "model": model_used,
            "prompt_length": len(request.prompt),
            "response_length": len(response)
        }

    except Exception as e:
        logger.error(f"Error running custom prompt: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute prompt: {str(e)}"
        )
