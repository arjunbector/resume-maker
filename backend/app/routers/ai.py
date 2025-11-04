from fastapi import APIRouter, HTTPException, Request, Depends
from loguru import logger
from database.models import PromptRequest, JobDetails, KnowledgeGraph, FieldMetadata, ResumeStage
from database.operations import UserOperations, SessionOperations
from ai.agent import ResumeAgent
from typing import Optional
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


class AnswerQuestionRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


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
    request: AnswerQuestionRequest,
    app_request: Request,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit an answer to a questionnaire question.

    This endpoint processes the user's answer, updates the questionnaire,
    and automatically adds relevant information to the user's knowledge graph.
    """
    try:
        logger.info(f"Processing answer for question {request.question_id} in session {request.session_id}")

        # Get the session
        session = SessionOperations.get_session(request.session_id)

        # Verify session belongs to current user
        if session['user_id'] != current_user['user_id']:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")

        # Get questionnaire from session
        questionnaire = session.get('questionnaire', {})
        questions = questionnaire.get('questions', [])

        # Find the specific question
        question_item = None
        question_index = None
        for idx, q in enumerate(questions):
            if q.get('id') == request.question_id:
                question_item = q
                question_index = idx
                break

        if not question_item:
            raise HTTPException(status_code=404, detail="Question not found in session")

        # Check if question is already answered
        if question_item.get('status') == 'answered':
            logger.warning(f"Question {request.question_id} already answered, updating answer")

        # Get the agent from app state
        agent: ResumeAgent = app_request.app.state.agent

        # Process the answer using AI to extract structured data
        processing_result = agent.process_answer(
            question=question_item.get('question', ''),
            answer=request.answer,
            related_field=question_item.get('related_field', ''),
            field_type=question_item.get('field_type', 'misc')
        )

        logger.info(f"Answer processed: {processing_result.get('summary', '')}")

        # Update the question with answer and confidence
        question_item['answer'] = request.answer
        question_item['confidence'] = processing_result.get('confidence', 0.5)
        question_item['status'] = 'answered'
        questions[question_index] = question_item

        # Calculate completion percentage
        answered_count = sum(1 for q in questions if q.get('status') == 'answered')
        completion = (answered_count / len(questions)) * 100 if questions else 0

        # Update session with new answer
        session_updates = {
            f"questionnaire.questions": questions,
            f"questionnaire.completion": completion,
            "resume_state.ai_context": {
                "summary": f"Answered {answered_count}/{len(questions)} questions",
                "total_questions": len(questions),
                "questions_answered": answered_count,
                "last_answer_summary": processing_result.get('summary', '')
            },
            "resume_state.last_action": "question_answered"
        }

        # If all questions are answered, advance stage
        if completion >= 100:
            session_updates["resume_state.stage"] = ResumeStage.READY_FOR_RESUME.value

        SessionOperations.update_session(request.session_id, session_updates)

        # Update user's knowledge graph with extracted information
        kg_updates = processing_result.get('knowledge_graph_updates', {})
        category = kg_updates.get('category')
        data = kg_updates.get('data')

        knowledge_graph_updated = False
        if category and data:
            try:
                # Get current user data
                user = UserOperations.get_user_by_id(current_user['user_id'])
                current_kg = user.get('knowledge_graph', {})

                # Prepare update based on category
                kg_update_operations = {}

                if category == 'skills' and isinstance(data, list) and len(data) > 0:
                    # Add skills (deduplicate)
                    current_skills = set(current_kg.get('skills', []))
                    new_skills = [skill for skill in data if skill not in current_skills]
                    if new_skills:
                        kg_update_operations["knowledge_graph.skills"] = list(current_skills) + new_skills

                elif category in ['education', 'work_experience', 'projects', 'certifications', 'research_work']:
                    # Add to appropriate array
                    if isinstance(data, dict) and data:
                        current_items = current_kg.get(category, [])
                        kg_update_operations[f"knowledge_graph.{category}"] = current_items + [data]

                elif category == 'misc' and isinstance(data, dict) and data:
                    # Merge into misc
                    current_misc = current_kg.get('misc', {})
                    current_misc.update(data)
                    kg_update_operations["knowledge_graph.misc"] = current_misc

                # Perform the update if there's something to update
                if kg_update_operations:
                    UserOperations.update_user(current_user['email'], kg_update_operations)
                    knowledge_graph_updated = True
                    logger.info(f"Knowledge graph updated: {category}")

            except Exception as e:
                logger.error(f"Error updating knowledge graph: {str(e)}")
                # Don't fail the request if KG update fails

        logger.info(f"Answer submitted successfully. Completion: {completion}%")

        return {
            "message": "Answer submitted successfully",
            "user_id": current_user['user_id'],
            "session_id": request.session_id,
            "question_id": request.question_id,
            "confidence": processing_result.get('confidence', 0.5),
            "completion": completion,
            "answered_count": answered_count,
            "total_questions": len(questions),
            "knowledge_graph_updated": knowledge_graph_updated,
            "extracted_data": processing_result.get('summary', ''),
            "all_questions_answered": completion >= 100
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit answer: {str(e)}"
        )


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
