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

        # Update session with comparison results
        session_updates = {
            "resume_state.missing_fields": [field.model_dump() for field in missing_fields],
            "resume_state.stage": ResumeStage.REQUIREMENTS_IDENTIFIED.value,
            "resume_state.ai_context": {
                "summary": f"Compared job requirements with user profile",
                "total_missing": len(missing_fields),
                "total_matched": len(matched_fields),
                "fill_suggestions": comparison.get('fill_suggestions', [])
            },
            "resume_state.last_action": "requirements_compared"
        }

        SessionOperations.update_session(session_id, session_updates)
        logger.info(f"Session {session_id} updated with comparison results")

        return {
            "message": "Requirements comparison completed",
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
