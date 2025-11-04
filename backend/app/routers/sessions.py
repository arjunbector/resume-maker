from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from database.operations import SessionOperations, UserOperations
from typing import Dict, Any
from utils.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

@router.post("/new")
def create_session(current_user: dict = Depends(get_current_user)):
    """
    Create a new blank session for the authenticated user.

    The session is created with empty job details and can be populated later
    using the update endpoint or the /api/v1/ai/analyze endpoint.
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Creating new blank session for user_id: {user_id}")
        result = SessionOperations.create_session(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.put("")
def update_session(session_id: str, updates: Dict[str, Any]):
    try:
        logger.info(f"Updating session with session_id: {session_id}")
        result = SessionOperations.update_session(session_id, updates)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

@router.get("/{session_id}")
def get_session(session_id: str):
    """
    Get session details by session_id.

    Returns complete session information including job details, resume state,
    questionnaire, and timestamps.
    """
    try:
        logger.info(f"Retrieving session with session_id: {session_id}")
        session = SessionOperations.get_session(session_id)
        return session
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve session: {str(e)}")

@router.get("/user/all")
def get_user_sessions(current_user: dict = Depends(get_current_user)):
    """
    Get all sessions for the authenticated user.

    Uses authentication (cookie or Authorization header) to identify the user.
    Returns all sessions sorted by last_active (most recent first).
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Retrieving all sessions for user_id: {user_id}")
        result = SessionOperations.get_user_sessions(user_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve user sessions: {str(e)}")


@router.get("/{session_id}/resume-data")
def get_resume_data(session_id: str, current_user: dict = Depends(get_current_user)):
    """
    Get complete resume data for a session.

    Combines user profile data and session data into a single structured response
    ready for resume generation. Returns all necessary information including:
    - Personal information (name, contact details)
    - Professional summary (current job title)
    - Knowledge graph (education, experience, skills, projects, certifications)
    - Job details (target role, company, requirements)
    - Resume metadata (name, description)
    - Session status and stage
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Retrieving resume data for session {session_id} and user {user_id}")

        # Get session data
        session = SessionOperations.get_session(session_id)

        # Verify session belongs to current user
        if session['user_id'] != user_id:
            raise HTTPException(status_code=403, detail="Not authorized to access this session")

        # Get user data
        user = UserOperations.get_user_by_id(user_id)

        # Remove sensitive data
        user.pop('hashed_password', None)

        # Structure the resume data
        resume_data = {
            # Personal Information
            "personal_info": {
                "name": user.get('name', ''),
                "email": user.get('resume_email', '') or user.get('email', ''),
                "phone": user.get('phone', ''),
                "address": user.get('address', ''),
                "current_job_title": user.get('current_job_title', ''),
                "socials": user.get('socials', {})
            },

            # Professional Profile
            "professional_profile": {
                "education": user.get('knowledge_graph', {}).get('education', []),
                "work_experience": user.get('knowledge_graph', {}).get('work_experience', []),
                "projects": user.get('knowledge_graph', {}).get('projects', []),
                "skills": user.get('knowledge_graph', {}).get('skills', []),
                "certifications": user.get('knowledge_graph', {}).get('certifications', []),
                "research_work": user.get('knowledge_graph', {}).get('research_work', []),
                "misc": user.get('knowledge_graph', {}).get('misc', {})
            },

            # Target Job Information
            "target_job": {
                "job_role": session.get('job_details', {}).get('job_role', ''),
                "company_name": session.get('job_details', {}).get('company_name', ''),
                "company_url": session.get('job_details', {}).get('company_url', ''),
                "job_description": session.get('job_details', {}).get('job_description', ''),
                "parsed_requirements": session.get('job_details', {}).get('parsed_requirements', []),
                "extracted_keywords": session.get('job_details', {}).get('extracted_keywords', [])
            },

            # Resume Metadata
            "resume_metadata": {
                "resume_name": session.get('resume_name', ''),
                "resume_description": session.get('resume_description', ''),
                "session_id": session.get('session_id', ''),
                "created_at": session.get('created_at'),
                "last_active": session.get('last_active')
            },

            # Analysis & Status
            "analysis": {
                "stage": session.get('resume_state', {}).get('stage', 'init'),
                "missing_fields": session.get('resume_state', {}).get('missing_fields', []),
                "required_fields": session.get('resume_state', {}).get('required_fields', []),
                "ai_context": session.get('resume_state', {}).get('ai_context', {}),
                "last_action": session.get('resume_state', {}).get('last_action', '')
            },

            # Questionnaire (if applicable)
            "questionnaire": {
                "questions": session.get('questionnaire', {}).get('questions', []),
                "completion": session.get('questionnaire', {}).get('completion', 0.0)
            }
        }

        logger.info(f"Resume data retrieved successfully for session {session_id}")
        return resume_data

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving resume data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve resume data: {str(e)}")


@router.get("/user/all/resume-data")
def get_all_resume_data(current_user: dict = Depends(get_current_user)):
    """
    Get complete resume data for ALL sessions of the authenticated user.

    Returns an array of resume data objects, one for each session. Each object contains:
    - Personal information (name, contact details)
    - Professional profile (education, experience, skills, projects, certifications)
    - Target job information (role, company, requirements)
    - Resume metadata (name, description, session_id)
    - Analysis status (stage, missing fields)
    - Questionnaire data

    Sessions are sorted by last_active (most recent first).
    """
    try:
        user_id = current_user['user_id']
        logger.info(f"Retrieving resume data for all sessions of user {user_id}")

        # Get all user sessions
        sessions = SessionOperations.get_user_sessions(user_id)

        # Get user data once (same for all sessions)
        user = UserOperations.get_user_by_id(user_id)
        user.pop('hashed_password', None)

        # Build resume data for each session
        all_resume_data = []

        for session in sessions.get('sessions', []):
            resume_data = {
                # Session ID at top level for easy access
                "session_id": session.get('session_id', ''),

                # Personal Information (same across all sessions)
                "personal_info": {
                    "name": user.get('name', ''),
                    "email": user.get('resume_email', '') or user.get('email', ''),
                    "phone": user.get('phone', ''),
                    "address": user.get('address', ''),
                    "current_job_title": user.get('current_job_title', ''),
                    "socials": user.get('socials', {})
                },

                # Professional Profile (same across all sessions)
                "professional_profile": {
                    "education": user.get('knowledge_graph', {}).get('education', []),
                    "work_experience": user.get('knowledge_graph', {}).get('work_experience', []),
                    "projects": user.get('knowledge_graph', {}).get('projects', []),
                    "skills": user.get('knowledge_graph', {}).get('skills', []),
                    "certifications": user.get('knowledge_graph', {}).get('certifications', []),
                    "research_work": user.get('knowledge_graph', {}).get('research_work', []),
                    "misc": user.get('knowledge_graph', {}).get('misc', {})
                },

                # Target Job Information (unique per session)
                "target_job": {
                    "job_role": session.get('job_details', {}).get('job_role', ''),
                    "company_name": session.get('job_details', {}).get('company_name', ''),
                    "company_url": session.get('job_details', {}).get('company_url', ''),
                    "job_description": session.get('job_details', {}).get('job_description', ''),
                    "parsed_requirements": session.get('job_details', {}).get('parsed_requirements', []),
                    "extracted_keywords": session.get('job_details', {}).get('extracted_keywords', [])
                },

                # Resume Metadata (unique per session)
                "resume_metadata": {
                    "resume_name": session.get('resume_name', ''),
                    "resume_description": session.get('resume_description', ''),
                    "session_id": session.get('session_id', ''),
                    "created_at": session.get('created_at'),
                    "last_active": session.get('last_active')
                },

                # Analysis & Status (unique per session)
                "analysis": {
                    "stage": session.get('resume_state', {}).get('stage', 'init'),
                    "missing_fields": session.get('resume_state', {}).get('missing_fields', []),
                    "required_fields": session.get('resume_state', {}).get('required_fields', []),
                    "ai_context": session.get('resume_state', {}).get('ai_context', {}),
                    "last_action": session.get('resume_state', {}).get('last_action', '')
                },

                # Questionnaire (unique per session)
                "questionnaire": {
                    "questions": session.get('questionnaire', {}).get('questions', []),
                    "completion": session.get('questionnaire', {}).get('completion', 0.0)
                }
            }

            all_resume_data.append(resume_data)

        logger.info(f"Retrieved resume data for {len(all_resume_data)} sessions")

        return {
            "user_id": user_id,
            "total_sessions": len(all_resume_data),
            "resume_data": all_resume_data
        }

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error retrieving all resume data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve all resume data: {str(e)}")
