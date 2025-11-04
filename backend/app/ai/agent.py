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
1. Questions MUST be short and concise - ideally a single sentence
2. Questions should be direct and to the point
3. For skills: Ask if they have experience and at what level
4. For education: Ask about degree and institution
5. For certifications: Ask if they have the certification
6. For experience: Ask about relevant work experience
7. For projects: Ask if they've worked on related projects
8. Prioritize high-priority fields (priority 4-5) first
9. Use simple, conversational language

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
      "question": "What is your experience level with Docker?",
      "related_field": "Docker",
      "field_type": "skill",
      "priority": 5,
      "suggested_format": "Brief answer like 'beginner', 'intermediate', 'advanced' or specific project examples"
    }}
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation. Keep questions SHORT - one sentence maximum.
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

    def process_answer(self, question: str, answer: str, related_field: str, field_type: str) -> dict:
        """
        Process a user's answer to a questionnaire question and determine what to add to knowledge graph.

        Args:
            question: The original question text
            answer: The user's answer
            related_field: The field this question is related to
            field_type: Type of field (skill, education, certification, experience, project)

        Returns:
            Dictionary with:
            - knowledge_graph_updates: What to add to the user's knowledge graph
            - confidence: Confidence score for the answer (0.0-1.0)
            - category: Which knowledge graph category to update
        """
        try:
            logger.info(f"Processing answer for field: {related_field}")

            prompt = f"""
You are an expert at processing resume information and structuring it for a knowledge graph.

**Question Asked:** {question}
**User's Answer:** {answer}
**Related Field:** {related_field}
**Field Type:** {field_type}

**Task:**
1. Analyze the user's answer
2. Determine what should be added to their knowledge graph
3. Structure the data according to the field type
4. Assign a confidence score (0.0-1.0) based on answer quality and completeness

**Knowledge Graph Categories and Schemas:**
- **education**: {{"institution": str (required), "degree": str (required), "field": str (optional), "start_date": str (optional, YYYY-MM or YYYY), "end_date": str (optional, YYYY-MM or YYYY or "present"), "gpa": str (optional)}}
- **work_experience**: {{"company": str (required), "position": str (required), "start_date": str (optional, YYYY-MM or YYYY), "end_date": str (optional, YYYY-MM or YYYY or "present"), "description": str (optional, SHORT BULLETED format)}}
- **projects**: {{"name": str (required), "description": str (required, SHORT BULLETED format), "technologies": [str] (optional), "url": str (optional), "start_date": str (optional, YYYY-MM or YYYY), "end_date": str (optional, YYYY-MM or YYYY or "present")}}
- **certifications**: {{"name": str (required), "issuer": str (optional), "date": str (optional, YYYY-MM or YYYY), "credential_id": str (optional), "url": str (optional)}}
- **research_work**: {{"title": str (required), "venue": str (optional), "date": str (optional, YYYY-MM or YYYY), "description": str (optional, SHORT BULLETED format), "url": str (optional)}}
- **skills**: [str] (array of skill names)
- **misc**: {{}} (flexible dictionary for truly miscellaneous items)

**Return a valid JSON object with this exact structure:**
{{
  "knowledge_graph_updates": {{
    "category": "education|work_experience|projects|certifications|research_work|skills|misc",
    "data": {{}} or [str]
  }},
  "confidence": 0.0-1.0,
  "summary": "brief summary of what was extracted"
}}

**Guidelines:**
- If answer is vague or incomplete, assign lower confidence (0.3-0.5)
- If answer is detailed and complete, assign higher confidence (0.7-1.0)
- For skills: extract skill name and proficiency if mentioned
- Extract specific details like dates, companies, institutions when mentioned
- If user says "no" or "none", return empty data with low confidence
- Match the schema for the appropriate category

**Example 1 - Skill:**
Question: "What is your experience level with Docker?"
Answer: "I've used Docker in 3 projects, intermediate level"
Response:
{{
  "knowledge_graph_updates": {{
    "category": "skills",
    "data": ["Docker"]
  }},
  "confidence": 0.8,
  "summary": "Added Docker skill with intermediate proficiency"
}}

**Example 2 - Education:**
Question: "Do you have a Bachelor's degree in Computer Science?"
Answer: "Yes, from Stanford University, graduated in 2022 with 3.8 GPA"
Response:
{{
  "knowledge_graph_updates": {{
    "category": "education",
    "data": {{
      "institution": "Stanford University",
      "degree": "Bachelor's degree",
      "field": "Computer Science",
      "start_date": "",
      "end_date": "2022",
      "gpa": "3.8"
    }}
  }},
  "confidence": 0.9,
  "summary": "Added Bachelor's degree in Computer Science from Stanford University"
}}

**Example 3 - Project:**
Question: "Do you have experience building web applications with Python?"
Answer: "Yes, I built an AI-powered resume builder using FastAPI and React"
Response:
{{
  "knowledge_graph_updates": {{
    "category": "projects",
    "data": {{
      "name": "AI Resume Builder",
      "description": "• Web application for generating tailored resumes using AI\\n• Built with FastAPI backend and React frontend",
      "technologies": ["Python", "FastAPI", "React", "AI/ML"],
      "url": "",
      "start_date": "",
      "end_date": ""
    }}
  }},
  "confidence": 0.8,
  "summary": "Added AI Resume Builder project with Python and FastAPI"
}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation.
"""

            system_prompt = "You are a professional resume data processor. Always return valid JSON responses."

            # Get response from LLM
            response = self.run_prompt(prompt, system_prompt)

            # Parse JSON response
            import json
            import re

            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                result = json.loads(response)

            logger.info(f"Answer processed. Confidence: {result.get('confidence', 0.0)}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response}")
            return {
                "knowledge_graph_updates": {
                    "category": "misc",
                    "data": {}
                },
                "confidence": 0.0,
                "summary": "Failed to parse answer",
                "error": "Failed to parse AI response"
            }
        except Exception as e:
            logger.error(f"Error processing answer: {str(e)}")
            raise

    def optimize_knowledge_graph(self, knowledge_graph: dict) -> dict:
        """
        Analyze the knowledge graph and restructure misplaced items into proper sections.

        Args:
            knowledge_graph: The user's knowledge graph with potentially misplaced items

        Returns:
            Dictionary with:
            - restructured_graph: Optimized knowledge graph with items in proper sections
            - changes_made: List of changes that were made
            - suggestions: Additional suggestions for the user
        """
        try:
            logger.info("Optimizing knowledge graph structure...")

            # Build prompt for knowledge graph optimization
            prompt = f"""
You are an expert at organizing professional resume data into the correct categories.

**Current Knowledge Graph:**
{knowledge_graph}

**Task:**
Analyze the knowledge graph and identify items that are in the wrong sections. Move them to the appropriate sections for better resume structuring.

**Knowledge Graph Structure and Schemas:**

- **education**: Array of objects with schema:
  - institution (required): University/college name
  - degree (required): Degree type
  - field (optional): Field of study
  - start_date (optional): YYYY-MM or YYYY
  - end_date (optional): YYYY-MM or YYYY or "present"
  - gpa (optional): GPA or grade

- **work_experience**: Array of objects with schema:
  - company (required): Company name
  - position (required): Job title
  - start_date (optional): YYYY-MM or YYYY
  - end_date (optional): YYYY-MM or YYYY or "present"
  - description (optional): SHORT BULLETED responsibilities and achievements

- **projects**: Array of objects with schema:
  - name (required): Project name
  - description (required): SHORT BULLETED project description
  - technologies (optional): Array of technology names
  - url (optional): Project URL or repository
  - start_date (optional): YYYY-MM or YYYY
  - end_date (optional): YYYY-MM or YYYY or "present"

- **certifications**: Array of objects with schema:
  - name (required): Certification name
  - issuer (optional): Issuing organization
  - date (optional): YYYY-MM or YYYY
  - credential_id (optional): Credential ID
  - url (optional): Verification URL

- **research_work**: Array of objects with schema:
  - title (required): Paper or research title
  - venue (optional): Conference or journal
  - date (optional): YYYY-MM or YYYY
  - description (optional): SHORT BULLETED summary
  - url (optional): Publication URL

- **skills**: Array of strings (skill names only, e.g., ["Python", "Leadership"])

- **misc**: Dictionary for truly miscellaneous items that don't fit elsewhere (languages spoken, hobbies, etc.)

**Common Misplacements to Fix:**
1. **misc items** that should be in work_experience (e.g., "FastAPI_experience: 5 years" → work_experience)
2. **misc items** that should be in skills (e.g., "Python_skills: advanced" → skills: ["Python"])
3. **skills** that are too detailed and should be in work_experience (e.g., "5 years Python backend development")
4. **certifications** in misc that should be in certifications section
5. **projects** in misc that should be in projects section

**Guidelines:**
1. Extract work experience details from misc and create proper work_experience entries
2. Extract skill names from verbose descriptions
3. Move certifications to proper section with name, issuer, date
4. Keep misc only for truly miscellaneous information (languages spoken, hobbies, etc.)
5. Preserve all original information - don't lose any data
6. If misc has "X_experience: Y years", create a work_experience entry or note it in description

**Return a valid JSON object with this exact structure:**
{{
  "restructured_graph": {{
    "education": [...],
    "work_experience": [...],
    "projects": [...],
    "skills": [...],
    "certifications": [...],
    "research_work": [...],
    "misc": {{}}
  }},
  "changes_made": [
    "Moved 'FastAPI_experience: 5 years' from misc to work_experience",
    "Extracted 'Python' skill from detailed description"
  ],
  "suggestions": [
    "Consider adding more details about FastAPI work experience (company, dates, responsibilities)"
  ]
}}

**Example:**
Input misc: {{"FastAPI_experience": "5 years", "languages": ["English", "Spanish"]}}
Output:
- work_experience: [{{
    "company": "",
    "position": "Backend Developer (FastAPI)",
    "start_date": "",
    "end_date": "",
    "description": "• 5 years of experience with FastAPI framework"
  }}]
- skills: add "FastAPI" if not already present
- misc: {{"languages": ["English", "Spanish"]}}

IMPORTANT: Return ONLY the JSON object, no additional text or explanation. Preserve ALL data from the original knowledge graph.
"""

            system_prompt = "You are a professional resume data organizer. Always return valid JSON responses and preserve all user data."

            # Get response from LLM
            response = self.run_prompt(prompt, system_prompt)

            # Parse JSON response
            import json
            import re

            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                result = json.loads(response)

            logger.info(f"Knowledge graph optimization complete. Made {len(result.get('changes_made', []))} changes")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response}")
            return {
                "restructured_graph": knowledge_graph,
                "changes_made": [],
                "suggestions": [],
                "error": "Failed to parse AI response"
            }
        except Exception as e:
            logger.error(f"Error optimizing knowledge graph: {str(e)}")
            raise

    def parse_free_text_to_knowledge_graph(self, text: str) -> dict:
        """
        Parse free-form text into structured knowledge graph data.
        Automatically detects the type of information and structures it according to the schema.

        Args:
            text: Free-form text describing a project, education, work experience, or other professional info

        Returns:
            Dictionary with:
            - category: Which knowledge graph category this belongs to (education, work_experience, projects, etc.)
            - data: Structured data following the category's schema
            - confidence: Confidence score (0.0-1.0)
        """
        try:
            logger.info("Parsing free-form text into structured knowledge graph data...")

            # Build prompt for parsing
            prompt = f"""
You are an expert at parsing professional information from free-form text into structured resume data.

**User Input:**
{text}

**Your Task:**
1. Identify what type of information this is (project, education, work experience, certification, research work, skill, or misc)
2. Extract ALL relevant information from the text
3. Structure it according to the appropriate schema
4. Return a JSON object with the category and structured data

**Knowledge Graph Schemas:**

**Education:**
{{
  "institution": "string (required)",
  "degree": "string (required)",
  "field": "string (optional)",
  "start_date": "string (YYYY-MM or YYYY format, optional)",
  "end_date": "string (YYYY-MM or YYYY or 'present', optional)",
  "gpa": "string (optional)"
}}

**Work Experience:**
{{
  "company": "string (required)",
  "position": "string (required)",
  "start_date": "string (YYYY-MM or YYYY format, optional)",
  "end_date": "string (YYYY-MM or YYYY or 'present', optional)",
  "description": "string - SHORT, BULLETED format (optional)"
}}

**Projects:**
{{
  "name": "string (required)",
  "description": "string - SHORT, BULLETED format (required)",
  "technologies": ["array", "of", "strings"] (optional),
  "url": "string (optional)",
  "start_date": "string (YYYY-MM or YYYY format, optional)",
  "end_date": "string (YYYY-MM or YYYY or 'present', optional)"
}}

**Certifications:**
{{
  "name": "string (required)",
  "issuer": "string (optional)",
  "date": "string (YYYY-MM or YYYY format, optional)",
  "credential_id": "string (optional)",
  "url": "string (optional)"
}}

**Research Work:**
{{
  "title": "string (required)",
  "venue": "string (optional)",
  "date": "string (YYYY-MM or YYYY format, optional)",
  "description": "string - SHORT, BULLETED format (optional)",
  "url": "string (optional)"
}}

**Skills:**
If the input describes skills, extract ONLY the skill names as a simple array of strings.
Example: ["Python", "FastAPI", "Docker", "Kubernetes"]

**Important Guidelines:**
1. **Descriptions MUST be SHORT and BULLETED** - Not long paragraphs
2. Break down descriptions into bullet points with "•" or "-"
3. Each bullet should be 1-2 lines maximum
4. Focus on impact and quantifiable results when possible
5. For projects: Include what it does, key features, and impact
6. For work experience: Include responsibilities and achievements
7. Extract ALL technologies/tools mentioned
8. Use proper date formats (YYYY-MM or YYYY)
9. If dates are unclear, leave them empty
10. Set confidence based on how much information was provided

**Return Format:**
Return ONLY a valid JSON object with this structure:
{{
  "category": "projects" | "education" | "work_experience" | "certifications" | "research_work" | "skills" | "misc",
  "data": {{...structured data according to schema above...}},
  "confidence": 0.0-1.0,
  "reasoning": "Brief explanation of categorization and extracted info"
}}

**Examples:**

**Input:** "I have built a website that lets you build resumes using AI using python and fastapi"
**Output:**
{{
  "category": "projects",
  "data": {{
    "name": "AI Resume Builder",
    "description": "• Web application that generates tailored resumes using AI\\n• Allows users to input job descriptions and automatically creates customized resumes\\n• Built with Python backend and AI integration",
    "technologies": ["Python", "FastAPI", "AI/ML"],
    "url": "",
    "start_date": "",
    "end_date": ""
  }},
  "confidence": 0.8,
  "reasoning": "Clearly describes a project with technical details. Extracted programming languages and framework."
}}

**Input:** "I worked at Google as a Software Engineer from 2020 to 2023, where I developed backend services for search infrastructure"
**Output:**
{{
  "category": "work_experience",
  "data": {{
    "company": "Google",
    "position": "Software Engineer",
    "start_date": "2020",
    "end_date": "2023",
    "description": "• Developed backend services for search infrastructure\\n• Worked on scalable distributed systems\\n• Contributed to core search functionality"
  }},
  "confidence": 0.95,
  "reasoning": "Contains clear company name, position, dates, and responsibilities."
}}

**Input:** "Bachelor of Science in Computer Science from Stanford University, graduated 2022 with 3.8 GPA"
**Output:**
{{
  "category": "education",
  "data": {{
    "institution": "Stanford University",
    "degree": "Bachelor of Science",
    "field": "Computer Science",
    "start_date": "",
    "end_date": "2022",
    "gpa": "3.8"
  }},
  "confidence": 0.95,
  "reasoning": "Contains institution, degree, field, graduation year, and GPA."
}}

**Input:** "I know Python, JavaScript, Docker, Kubernetes, and AWS"
**Output:**
{{
  "category": "skills",
  "data": ["Python", "JavaScript", "Docker", "Kubernetes", "AWS"],
  "confidence": 1.0,
  "reasoning": "Explicit list of technical skills."
}}

IMPORTANT:
- Return ONLY the JSON object, no additional text
- Make descriptions SHORT and BULLETED
- Extract ALL technologies mentioned
- Use proper schema for each category
- If unsure about category, use "misc" and structure as simple key-value
"""

            system_prompt = "You are a professional resume data parser. Always return valid JSON with structured data following the provided schemas. Keep descriptions concise and bulleted."

            # Get response from LLM
            response = self.run_prompt(prompt, system_prompt)

            # Parse JSON response
            import json
            import re

            # Try to extract JSON from response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                json_str = json_match.group(0)
                result = json.loads(json_str)
            else:
                result = json.loads(response)

            logger.info(f"Successfully parsed text into category: {result.get('category')}")
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            logger.error(f"Response was: {response}")
            return {
                "category": "misc",
                "data": {"raw_text": text},
                "confidence": 0.0,
                "reasoning": "Failed to parse - storing as misc",
                "error": "Failed to parse AI response"
            }
        except Exception as e:
            logger.error(f"Error parsing free text: {str(e)}")
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
