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

    def analyze_job_requirements(self, job_description: str) -> dict:
        """
        Analyze job description and extract requirements without comparing to user data.

        Args:
            job_description: The job description text

        Returns:
            Dictionary with:
            - parsed_requirements: List of FieldMetadata objects
            - extracted_keywords: List of important keywords
        """
        try:
            logger.info("Analyzing job requirements...")

            # Build prompt focused only on extracting requirements
            prompt = f"""
You are a job requirements analysis expert. Analyze the job description and extract all requirements, qualifications, and key information.

**Job Description:**
{job_description}

**Task:**
1. Extract all requirements from the job description (skills, experience, education, certifications, etc.)
2. Categorize each requirement by type (skill, education, certification, experience, project)
3. Assign priority (1-5) where 5 is critical/required and 1 is nice-to-have
4. Assign confidence (0.0-1.0) based on how explicitly the requirement is stated
5. Extract important keywords and technologies mentioned

**Return a valid JSON object with this exact structure:**
{{
  "parsed_requirements": [
    {{
      "name": "requirement name (e.g., 'Python', 'Bachelor's Degree', 'Docker')",
      "type": "skill|education|certification|experience|project",
      "description": "brief description of the requirement",
      "priority": 1-5,
      "confidence": 0.0-1.0
    }}
  ],
  "extracted_keywords": ["keyword1", "keyword2", "keyword3"]
}}

**Guidelines:**
- Priority 5: Explicitly required/must-have
- Priority 4: Strongly preferred
- Priority 3: Preferred/nice-to-have
- Priority 2: Mentioned but optional
- Priority 1: Tangentially related

IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
"""

            system_prompt = "You are a professional job requirements analyzer. Always return valid JSON responses."

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

            logger.info(f"Analysis complete. Found {len(result.get('parsed_requirements', []))} requirements")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response}")
            # Return fallback structure
            return {
                "parsed_requirements": [],
                "extracted_keywords": [],
                "error": "Failed to parse AI response"
            }
        except Exception as e:
            logger.error(f"Error analyzing job requirements: {str(e)}")
            raise

    def compare_and_find_missing_fields(
        self,
        parsed_requirements: list,
        user_knowledge_graph: dict
    ) -> dict:
        """
        Compare job requirements against user's knowledge graph and identify missing fields.

        Args:
            parsed_requirements: List of requirements from job analysis
            user_knowledge_graph: User's knowledge graph with education, experience, skills, etc.

        Returns:
            Dictionary with:
            - missing_fields: List of FieldMetadata objects for missing requirements
            - matched_fields: List of FieldMetadata objects for matched requirements
            - fill_suggestions: Suggestions for how to fill missing fields
        """
        try:
            logger.info("Comparing job requirements with user knowledge graph...")

            # Build prompt for comparison
            prompt = f"""
You are an expert at comparing job requirements against a candidate's profile.

**Job Requirements:**
{parsed_requirements}

**User's Knowledge Graph:**
{user_knowledge_graph}

**Task:**
1. Compare each job requirement against the user's knowledge graph
2. Identify which requirements are MISSING from the user's profile
3. Identify which requirements are MATCHED (user has this skill/experience)
4. For missing fields, suggest how the user could fill them (e.g., "Add project experience with Docker", "Add Python certification")
5. Assign confidence (0.0-1.0) for each match/mismatch

**Return a valid JSON object with this exact structure:**
{{
  "missing_fields": [
    {{
      "name": "requirement name",
      "type": "skill|education|certification|experience|project",
      "description": "why this is missing",
      "priority": 1-5,
      "confidence": 0.0-1.0,
      "source": "ai_inferred"
    }}
  ],
  "matched_fields": [
    {{
      "name": "requirement name",
      "type": "skill|education|certification|experience|project",
      "description": "how user satisfies this",
      "priority": 1-5,
      "confidence": 0.0-1.0,
      "source": "user_knowledge_graph",
      "value": "matching value from user's profile"
    }}
  ],
  "fill_suggestions": [
    {{
      "field_name": "missing requirement name",
      "suggestion": "specific suggestion on how to fill this field",
      "category": "education|experience|skill|project|certification"
    }}
  ]
}}

**Guidelines:**
- Consider partial matches (e.g., user has "JavaScript" when job requires "React")
- Be strict: only mark as matched if user clearly has the requirement
- Confidence should reflect how well the user meets the requirement
- Missing fields should have lower confidence if it's unclear whether user truly lacks it
- Fill suggestions should be actionable and specific

IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
"""

            system_prompt = "You are a professional resume analyst. Always return valid JSON responses."

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

            logger.info(
                f"Comparison complete. Found {len(result.get('missing_fields', []))} missing fields, "
                f"{len(result.get('matched_fields', []))} matched fields"
            )
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response}")
            # Return fallback structure
            return {
                "missing_fields": [],
                "matched_fields": [],
                "fill_suggestions": [],
                "error": "Failed to parse AI response"
            }
        except Exception as e:
            logger.error(f"Error comparing requirements with knowledge graph: {str(e)}")
            raise

    def generate_questionnaire(self, missing_fields: list) -> dict:
        """
        Generate contextual questions for missing fields in user's profile.

        Args:
            missing_fields: List of FieldMetadata objects representing missing requirements

        Returns:
            Dictionary with:
            - questions: List of question objects with question text and related_field
        """
        try:
            logger.info(f"Generating questionnaire for {len(missing_fields)} missing fields...")

            # Build prompt for questionnaire generation
            prompt = f"""
You are an expert at creating targeted questions to fill in missing information for a resume.

**Missing Fields from User's Profile:**
{missing_fields}

**Task:**
For each missing field, generate a clear, specific question that will help the user provide the necessary information.

**Guidelines:**
1. Questions should be conversational and easy to understand
2. Questions should be specific to the field type (skill, education, certification, experience, project)
3. For skills: Ask about proficiency level and specific projects where used
4. For education: Ask about institution, degree, field of study, dates
5. For certifications: Ask about certification name, issuer, date obtained
6. For experience: Ask about company, role, duration, key responsibilities
7. For projects: Ask about project name, description, technologies used
8. Prioritize high-priority fields (priority 4-5) first
9. Keep questions concise but comprehensive enough to gather needed details

**Return a valid JSON object with this exact structure:**
{{
  "questions": [
    {{
      "question": "Clear, specific question text",
      "related_field": "exact name of the missing field",
      "field_type": "skill|education|certification|experience|project",
      "priority": 1-5,
      "suggested_format": "Brief hint on what format/detail level expected"
    }}
  ]
}}

**Example:**
If missing field is "Docker" (skill, priority 5):
{{
  "questions": [
    {{
      "question": "Do you have experience with Docker? If yes, please describe your proficiency level and any projects where you've used Docker for containerization.",
      "related_field": "Docker",
      "field_type": "skill",
      "priority": 5,
      "suggested_format": "Describe proficiency (beginner/intermediate/advanced) and 1-2 specific examples"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
"""

            system_prompt = "You are a professional questionnaire designer for resume building. Always return valid JSON responses."

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

            logger.info(f"Questionnaire generation complete. Generated {len(result.get('questions', []))} questions")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response}")
            # Return fallback structure
            return {
                "questions": [],
                "error": "Failed to parse AI response"
            }
        except Exception as e:
            logger.error(f"Error generating questionnaire: {str(e)}")
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
