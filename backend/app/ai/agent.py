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

    def analyze_job_requirements(self, job_description: str, user_knowledge_graph: dict) -> dict:
        """
        Analyze job requirements and identify missing fields in user's knowledge graph.

        Args:
            job_description: The job description text
            user_knowledge_graph: User's knowledge graph with their professional info

        Returns:
            Dictionary with:
            - missing_fields: List of missing field names
            - parsed_requirements: List of FieldMetadata objects
            - extracted_keywords: List of important keywords
        """
        try:
            logger.info("Analyzing job requirements...")

            # Build prompt with job description and current knowledge graph
            prompt = f"""
You are a resume analysis expert. Analyze the job description and identify what information is missing from the candidate's profile.

**Job Description:**
{job_description}

**Candidate's Current Knowledge Graph:**
- Education: {len(user_knowledge_graph.get('education', []))} entries
- Work Experience: {len(user_knowledge_graph.get('work_experience', []))} entries
- Research Work: {len(user_knowledge_graph.get('research_work', []))} entries
- Projects: {len(user_knowledge_graph.get('projects', []))} entries
- Certifications: {len(user_knowledge_graph.get('certifications', []))} entries
- Skills: {', '.join(user_knowledge_graph.get('skills', [])) if user_knowledge_graph.get('skills') else 'None listed'}

**Task:**
1. Identify which fields from the knowledge graph (education, work_experience, research_work, projects, certifications, skills) are most relevant for this job
2. Determine which relevant fields are missing or insufficient in the candidate's profile
3. Extract key requirements and keywords from the job description

**Return a valid JSON object with this exact structure:**
{{
  "missing_fields": ["field_name1", "field_name2"],
  "parsed_requirements": [
    {{
      "name": "requirement name",
      "type": "skill|education|certification|experience",
      "description": "brief description",
      "priority": 1-5,
      "confidence": 0.0-1.0
    }}
  ],
  "extracted_keywords": ["keyword1", "keyword2", "keyword3"]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
"""

            system_prompt = "You are a professional resume analyzer. Always return valid JSON responses."

            # Get response from LLM
            response = self.run_prompt(prompt, system_prompt)

            # Parse JSON response
            import json
            import re

            # Try to extract JSON from response (in case LLM adds extra text)
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                result = json.loads(response)

            logger.info(f"Analysis complete. Found {len(result.get('missing_fields', []))} missing fields")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response}")
            # Return fallback structure
            return {
                "missing_fields": [],
                "parsed_requirements": [],
                "extracted_keywords": [],
                "error": "Failed to parse AI response"
            }
        except Exception as e:
            logger.error(f"Error analyzing job requirements: {str(e)}")
            raise

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
