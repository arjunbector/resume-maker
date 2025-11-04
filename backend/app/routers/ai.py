from fastapi import APIRouter, HTTPException, Request, Depends
from loguru import logger
from database.models import PromptRequest, JobDetails, KnowledgeGraph, FieldMetadata, ResumeStage
from database.operations import UserOperations, SessionOperations
from ai.agent import ResumeAgent
from typing import Dict, Optional
from pydantic import BaseModel
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/ai", tags=["ai"])


class CustomPromptRequest(BaseModel):
    prompt: str
    system_prompt: Optional[str] = None
    model: Optional[str] = None  # Allow model override


class AnalyzeJobRequest(BaseModel):
    job_description: str
    job_role: Optional[str] = None
    company_name: Optional[str] = None
    session_id: Optional[str] = None  # Optional session to update with results


class MultiAnswerRequest(BaseModel):
    session_id: str
    answers: Dict[str, str]


class ParseTextRequest(BaseModel):
    text: str 


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


@router.post("/analyze")
def analyze_job_requirements(
    request: AnalyzeJobRequest,
    app_request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze job description and extract requirements.

    This endpoint takes a job description and extracts all requirements, qualifications,
    and keywords without comparing to the user's profile.

    Returns:
    - parsed_requirements: Detailed requirements extracted from job description
    - extracted_keywords: Important keywords and skills from the job posting
    """
    try:
        logger.info(f"Analyzing job requirements for user: {current_user['email']}")

        # Get the agent from app state
        agent: ResumeAgent = app_request.app.state.agent

        # Analyze job requirements (without user comparison)
        analysis = agent.analyze_job_requirements(
            job_description=request.job_description
        )

        logger.info("Job analysis completed successfully")

        # Update session if session_id is provided
        session_updated = False
        if request.session_id:
            try:
                logger.info(f"Updating session {request.session_id} with analysis results")

                # Convert parsed_requirements to FieldMetadata format
                parsed_requirements = [
                    FieldMetadata(**req) for req in analysis.get('parsed_requirements', [])
                ]

                # Update session with analysis results and all job details
                session_updates = {
                    "job_details.job_description": request.job_description,
                    "job_details.job_role": request.job_role or "",
                    "job_details.company_name": request.company_name or "",
                    "job_details.parsed_requirements": [req.model_dump() for req in parsed_requirements],
                    "job_details.extracted_keywords": analysis.get('extracted_keywords', []),
                    "resume_state.stage": ResumeStage.JOB_ANALYZED.value,
                    "resume_state.required_fields": [req.model_dump() for req in parsed_requirements],
                    "resume_state.ai_context": {
                        "summary": f"Analyzed job for {request.job_role or 'position'} at {request.company_name or 'company'}",
                        "total_requirements": len(parsed_requirements)
                    },
                    "resume_state.last_action": "job_analyzed"
                }

                SessionOperations.update_session(request.session_id, session_updates)
                session_updated = True
                logger.info(f"Session {request.session_id} updated successfully")

            except ValueError as e:
                logger.warning(f"Session update failed: {str(e)}")
                # Don't fail the request if session update fails
            except Exception as e:
                logger.error(f"Error updating session: {str(e)}")
                # Don't fail the request if session update fails

        return {
            "message": "Job analysis completed",
            "user_id": current_user['user_id'],
            "job_role": request.job_role,
            "company_name": request.company_name,
            "session_id": request.session_id,
            "session_updated": session_updated,
            "analysis": analysis,
            "parsed_requirements": analysis.get('parsed_requirements', []),
            "extracted_keywords": analysis.get('extracted_keywords', [])
        }

    except Exception as e:
        logger.error(f"Error analyzing job requirements: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze job requirements: {str(e)}"
        )


@router.post("/compare")
def compare_with_user_profile(
    session_id: str,
    app_request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Compare job requirements with user's knowledge graph and identify missing fields.

    This endpoint takes a session with analyzed job requirements and compares them
    against the user's profile to identify what's missing.

    Updates the session's resume_state with missing_fields and matched_fields.
    """
    try:
        logger.info(f"Comparing session {session_id} with user profile for {current_user['email']}")

        # Get the session
        session = SessionOperations.get_session(session_id)

        # Verify session belongs to current user
        if session['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")

        # Get parsed requirements from session
        parsed_requirements = session.get('job_details', {}).get('parsed_requirements', [])

        if not parsed_requirements:
            raise HTTPException(
                status_code=400,
                detail="Session has no parsed requirements. Please analyze the job first using /api/v1/ai/analyze"
            )

        # Get user's knowledge graph
        user = UserOperations.get_user_by_id(current_user['user_id'])
        user_knowledge_graph = user.get('knowledge_graph', {})

        # Get the agent from app state
        agent: ResumeAgent = app_request.app.state.agent

        # Compare requirements with user's knowledge graph
        comparison = agent.compare_and_find_missing_fields(
            parsed_requirements=parsed_requirements,
            user_knowledge_graph=user_knowledge_graph
        )

        logger.info("Comparison completed successfully")

        # Convert missing_fields and matched_fields to FieldMetadata format
        missing_fields = [
            FieldMetadata(**field) for field in comparison.get('missing_fields', [])
        ]
        matched_fields = [
            FieldMetadata(**field) for field in comparison.get('matched_fields', [])
        ]

        # Determine stage and message based on missing fields
        if len(missing_fields) == 0:
            # No missing fields - ready for resume generation
            stage = ResumeStage.READY_FOR_RESUME.value
            message = "No missing fields found"
            logger.info(f"No missing fields found for session {session_id}, setting stage to READY_FOR_RESUME")

            # Clean up any unanswered questions from questionnaire
            questionnaire = session.get('questionnaire', {})
            questions = questionnaire.get('questions', [])
            if questions:
                # Keep only answered questions
                answered_questions = [q for q in questions if q.get('status') == 'answered']
                unanswered_count = len(questions) - len(answered_questions)

                if unanswered_count > 0:
                    logger.info(f"Removing {unanswered_count} unanswered questions as resume is ready")

                # Recalculate completion
                completion = 100.0 if len(answered_questions) > 0 else 0.0

                # Update questionnaire in session
                questionnaire_updates = {
                    "questionnaire.questions": answered_questions,
                    "questionnaire.completion": completion
                }
            else:
                questionnaire_updates = {}
        else:
            # Has missing fields - need questionnaire
            stage = ResumeStage.REQUIREMENTS_IDENTIFIED.value
            message = "Requirements comparison completed"
            questionnaire_updates = {}

        # Update session with comparison results
        session_updates = {
            "resume_state.missing_fields": [field.model_dump() for field in missing_fields],
            "resume_state.stage": stage,
            "resume_state.ai_context": {
                "summary": f"Compared job requirements with user profile",
                "total_missing": len(missing_fields),
                "total_matched": len(matched_fields),
                "fill_suggestions": comparison.get('fill_suggestions', [])
            },
            "resume_state.last_action": "requirements_compared"
        }

        # Merge questionnaire updates if any
        session_updates.update(questionnaire_updates)

        SessionOperations.update_session(session_id, session_updates)
        logger.info(f"Session {session_id} updated with comparison results")

        return {
            "message": message,
            "user_id": current_user['user_id'],
            "session_id": session_id,
            "missing_fields": comparison.get('missing_fields', []),
            "matched_fields": comparison.get('matched_fields', []),
            "fill_suggestions": comparison.get('fill_suggestions', []),
            "total_missing": len(missing_fields),
            "total_matched": len(matched_fields)
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error comparing with user profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare with user profile: {str(e)}"
        )


@router.post("/generate-questionnaire")
def generate_questionnaire(
    session_id: str,
    app_request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a questionnaire based on missing fields identified in the session.

    This endpoint takes a session with identified missing fields and generates
    contextual questions to help the user fill in those gaps.

    Updates the session's questionnaire field with generated questions and
    advances the stage to QUESTIONNAIRE_PENDING.
    """
    try:
        logger.info(f"Generating questionnaire for session {session_id}")

        # Get the session
        session = SessionOperations.get_session(session_id)

        # Verify session belongs to current user
        if session['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")

        # Get missing fields from session
        missing_fields = session.get('resume_state', {}).get('missing_fields', [])

        if not missing_fields:
            raise HTTPException(
                status_code=400,
                detail="Session has no missing fields. Please run comparison first using /api/v1/ai/compare"
            )

        # Get the agent from app state
        agent: ResumeAgent = app_request.app.state.agent

        # Generate questionnaire
        questionnaire_data = agent.generate_questionnaire(missing_fields)

        logger.info("Questionnaire generated successfully")

        # Convert to QuestionItem format with unique IDs
        from uuid import uuid4
        from database.models import QuestionItem

        questions = []
        for q_data in questionnaire_data.get('questions', []):
            question_item = QuestionItem(
                id=str(uuid4()),
                question=q_data.get('question', ''),
                related_field=q_data.get('related_field', ''),
                answer=None,
                confidence=None,
                status="unanswered"
            )
            questions.append(question_item)

        # Calculate completion (all unanswered at this point)
        completion = 0.0

        # Update session with questionnaire
        session_updates = {
            "questionnaire.questions": [q.model_dump() for q in questions],
            "questionnaire.completion": completion,
            "resume_state.stage": ResumeStage.QUESTIONNAIRE_PENDING.value,
            "resume_state.ai_context": {
                "summary": f"Generated questionnaire with {len(questions)} questions",
                "total_questions": len(questions),
                "questions_answered": 0
            },
            "resume_state.last_action": "questionnaire_generated"
        }

        SessionOperations.update_session(session_id, session_updates)
        logger.info(f"Session {session_id} updated with questionnaire")

        return {
            "message": "Questionnaire generated successfully",
            "user_id": current_user['user_id'],
            "session_id": session_id,
            "total_questions": len(questions),
            "questions": [q.model_dump() for q in questions],
            "completion": completion
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating questionnaire: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate questionnaire: {str(e)}"
        )


@router.post("/answer-question")
def answer_question(
    request: MultiAnswerRequest,
    app_request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit an answer to a questionnaire question.

    This endpoint processes the user's answer, updates the questionnaire,
    and automatically adds relevant information to the user's knowledge graph.
    """
    try:
        session_id = request.session_id
        logger.info(f"Processing {len(request.answers)} answers for session {session_id}")

        # Retrieve session
        session = SessionOperations.get_session(session_id)

        # Verify session ownership
        if session['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")

        questionnaire = session.get('questionnaire', {})
        questions = questionnaire.get('questions', [])
        if not questions:
            raise HTTPException(status_code=400, detail="No questionnaire found in this session")

        agent: ResumeAgent = app_request.app.state.agent

        total_questions = len(questions)
        answered_count = sum(1 for q in questions if q.get('status') == 'answered')
        knowledge_graph_updated = False
        processed_results = []

        # Process each answer
        for question_id, answer_text in request.answers.items():
            question_item = next((q for q in questions if q.get('id') == question_id), None)
            if not question_item:
                logger.warning(f"Question ID {question_id} not found, skipping.")
                continue

            try:
                # Process with AI
                processing_result = agent.process_answer(
                    question=question_item.get('question', ''),
                    answer=answer_text,
                    related_field=question_item.get('related_field', ''),
                    field_type=question_item.get('field_type', 'misc')
                )

                # Update question entry
                question_item['answer'] = answer_text
                question_item['confidence'] = processing_result.get('confidence', 0.5)
                question_item['status'] = 'answered'

                processed_results.append({
                    "question_id": question_id,
                    "confidence": processing_result.get('confidence', 0.5),
                    "summary": processing_result.get('summary', '')
                })

                # Knowledge Graph update
                kg_updates = processing_result.get('knowledge_graph_updates', {})
                category = kg_updates.get('category')
                data = kg_updates.get('data')

                if category and data:
                    try:
                        user = UserOperations.get_user_by_id(current_user['user_id'])
                        current_kg = user.get('knowledge_graph', {})
                        kg_update_ops = {}

                        if category == 'skills' and isinstance(data, list):
                            current_skills = set(current_kg.get('skills', []))
                            new_skills = [s for s in data if s not in current_skills]
                            if new_skills:
                                kg_update_ops["knowledge_graph.skills"] = list(current_skills) + new_skills

                        elif category in ['education', 'work_experience', 'projects', 'certifications', 'research_work']:
                            if isinstance(data, dict) and data:
                                current_items = current_kg.get(category, [])
                                kg_update_ops[f"knowledge_graph.{category}"] = current_items + [data]

                        elif category == 'misc' and isinstance(data, dict):
                            current_misc = current_kg.get('misc', {})
                            current_misc.update(data)
                            kg_update_ops["knowledge_graph.misc"] = current_misc

                        if kg_update_ops:
                            UserOperations.update_user(current_user['email'], kg_update_ops)
                            knowledge_graph_updated = True
                            logger.info(f"Knowledge graph updated for category: {category}")

                    except Exception as kg_err:
                        logger.error(f"Failed to update knowledge graph for {question_id}: {kg_err}")

            except Exception as err:
                logger.error(f"Error processing answer for {question_id}: {err}")

        # Recalculate completion
        answered_count = sum(1 for q in questions if q.get('status') == 'answered')
        completion = (answered_count / total_questions) * 100 if total_questions > 0 else 0

        # Update session
        session_updates = {
            "questionnaire.questions": questions,
            "questionnaire.completion": completion,
            "resume_state.ai_context": {
                "summary": f"Answered {answered_count}/{total_questions} questions",
                "total_questions": total_questions,
                "questions_answered": answered_count,
                "last_batch_summary": [r["summary"] for r in processed_results]
            },
            "resume_state.last_action": "questions_batch_answered"
        }

        # Advance stage if complete
        if completion >= 100:
            session_updates["resume_state.stage"] = ResumeStage.READY_FOR_RESUME.value

        SessionOperations.update_session(session_id, session_updates)

        logger.info(f"Batch answers processed for session {session_id}: {answered_count}/{total_questions}")

        return {
            "message": "Answers processed successfully",
            "user_id": current_user['user_id'],
            "session_id": session_id,
            "total_questions": total_questions,
            "answered_count": answered_count,
            "completion": completion,
            "knowledge_graph_updated": knowledge_graph_updated,
            "results": processed_results,
            "all_questions_answered": completion >= 100
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing batch answers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process answers: {str(e)}")

@router.post("/optimize")
def optimize_knowledge_graph(
    app_request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze and optimize the user's knowledge graph structure.

    This endpoint uses AI to identify misplaced items in the knowledge graph
    and move them to appropriate sections. For example:
    - "FastAPI_experience: 5 years" in misc → work_experience
    - Verbose skill descriptions → proper skills array
    - Certifications in misc → certifications section

    The user's knowledge graph is automatically updated with the optimized structure.
    """
    try:
        user_id = current_user['user_id']
        email = current_user['email']
        logger.info(f"Optimizing knowledge graph for user: {email}")

        # Get current user data
        user = UserOperations.get_user_by_id(user_id)
        current_kg = user.get('knowledge_graph', {})

        # Check if knowledge graph is empty
        if not current_kg or all(not v for v in current_kg.values()):
            raise HTTPException(
                status_code=400,
                detail="Knowledge graph is empty. Add some data first using /api/v1/users/knowledge-graph/add"
            )

        # Get the agent from app state
        agent: ResumeAgent = app_request.app.state.agent

        # Optimize the knowledge graph
        optimization_result = agent.optimize_knowledge_graph(current_kg)

        if "error" in optimization_result:
            logger.warning(f"AI optimization failed: {optimization_result['error']}")
            raise HTTPException(
                status_code=500,
                detail="Failed to optimize knowledge graph with AI"
            )

        restructured_graph = optimization_result.get('restructured_graph', {})
        changes_made = optimization_result.get('changes_made', [])
        suggestions = optimization_result.get('suggestions', [])

        # Update user's knowledge graph with optimized structure
        if changes_made:
            update_operations = {
                "knowledge_graph": restructured_graph
            }
            UserOperations.update_user(email, update_operations)
            logger.info(f"Knowledge graph updated with {len(changes_made)} changes")
        else:
            logger.info("No changes needed - knowledge graph is already well-structured")

        return {
            "message": "Knowledge graph optimized successfully" if changes_made else "Knowledge graph is already well-structured",
            "user_id": user_id,
            "email": email,
            "changes_made": changes_made,
            "total_changes": len(changes_made),
            "suggestions": suggestions,
            "optimized_graph": restructured_graph
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error optimizing knowledge graph: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to optimize knowledge graph: {str(e)}"
        )


@router.post("/parse-text")
def parse_text_to_knowledge_graph(
    request: ParseTextRequest,
    app_request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Parse free-form text into structured knowledge graph data.
    Automatically detects the type of information (project, education, work experience, etc.)
    and structures it according to the appropriate schema.

    The endpoint will:
    1. Analyze the input text using AI
    2. Determine the category (projects, education, work_experience, certifications, research_work, skills, misc)
    3. Extract and structure the data according to the category's schema
    4. Add the structured data to the user's knowledge graph

    **Schemas:**
    - **Education**: institution, degree, field, start_date, end_date, gpa
    - **Work Experience**: company, position, start_date, end_date, description (SHORT, BULLETED)
    - **Projects**: name, description (SHORT, BULLETED), technologies[], url, start_date, end_date
    - **Certifications**: name, issuer, date, credential_id, url
    - **Research Work**: title, venue, date, description (SHORT, BULLETED), url
    - **Skills**: Array of skill names (e.g., ["Python", "FastAPI", "Docker"])

    **Important Notes:**
    - Descriptions are automatically formatted as SHORT, BULLETED points
    - Technologies/tools are extracted and listed
    - Dates are formatted as YYYY-MM or YYYY
    - The AI determines the best category based on content

    **Example Inputs:**
    - "I have built a website that lets you build resumes using AI using python and fastapi"
    - "I worked at Google as a Software Engineer from 2020 to 2023"
    - "Bachelor of Science in Computer Science from Stanford University, graduated 2022 with 3.8 GPA"
    - "I know Python, JavaScript, Docker, Kubernetes, and AWS"

    Returns:
        - category: Which knowledge graph section the data belongs to
        - data: Structured data following the appropriate schema
        - confidence: AI confidence score (0.0-1.0)
        - reasoning: Explanation of categorization
        - knowledge_graph_updated: Whether the data was added to user's knowledge graph
    """
    try:
        user_id = current_user['user_id']
        email = current_user['email']

        logger.info(f"Parsing free-form text for user {email}")
        logger.info(f"Text length: {len(request.text)} characters")

        # Validate input
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Text input is required and cannot be empty"
            )

        # Get agent from app state
        agent = app_request.app.state.agent

        # Parse the free-form text
        parse_result = agent.parse_free_text_to_knowledge_graph(request.text)

        # Check for parsing errors
        if "error" in parse_result:
            raise HTTPException(
                status_code=500,
                detail="Failed to parse text with AI"
            )

        category = parse_result.get('category')
        data = parse_result.get('data')
        confidence = parse_result.get('confidence', 0.0)
        reasoning = parse_result.get('reasoning', '')

        logger.info(f"Parsed text into category: {category} with confidence: {confidence}")

        # Get current user data
        user = UserOperations.get_user_by_id(user_id)
        knowledge_graph = user.get('knowledge_graph', {})

        # Add parsed data to appropriate knowledge graph category
        knowledge_graph_updated = False

        if category == "skills":
            # Skills is an array of strings
            current_skills = knowledge_graph.get('skills', [])
            if isinstance(data, list):
                # Add new skills, avoiding duplicates
                for skill in data:
                    if skill not in current_skills:
                        current_skills.append(skill)
                        knowledge_graph_updated = True
                knowledge_graph['skills'] = current_skills

        elif category in ["education", "work_experience", "projects", "certifications", "research_work"]:
            # These are arrays of objects
            current_items = knowledge_graph.get(category, [])
            if not isinstance(current_items, list):
                current_items = []

            # Add the new item
            current_items.append(data)
            knowledge_graph[category] = current_items
            knowledge_graph_updated = True

        elif category == "misc":
            # Misc is a dictionary
            current_misc = knowledge_graph.get('misc', {})
            if isinstance(data, dict):
                current_misc.update(data)
            else:
                # If data is not a dict, store it with a generated key
                import time
                key = f"item_{int(time.time())}"
                current_misc[key] = data
            knowledge_graph['misc'] = current_misc
            knowledge_graph_updated = True

        # Update user's knowledge graph
        if knowledge_graph_updated:
            update_operations = {
                "knowledge_graph": knowledge_graph
            }
            UserOperations.update_user(email, update_operations)
            logger.info(f"Knowledge graph updated with new {category} data")

        return {
            "message": f"Successfully parsed text and added to {category}",
            "user_id": user_id,
            "email": email,
            "category": category,
            "data": data,
            "confidence": confidence,
            "reasoning": reasoning,
            "knowledge_graph_updated": knowledge_graph_updated
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error parsing text: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse text: {str(e)}"
        )
