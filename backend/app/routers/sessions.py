from fastapi import APIRouter, HTTPException
from loguru import logger
from database.operations import SessionOperations
from database.models import JobDetails
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/sessions", tags=["sessions"])

@router.post("")
def create_session(user_id: str, job_details: JobDetails):
    try:
        logger.info(f"Creating new session for user_id: {user_id}")
        result = SessionOperations.create_session(user_id, job_details)
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
