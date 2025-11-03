from fastapi import APIRouter, HTTPException, Depends
from loguru import logger
from database.operations import SessionOperations
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
