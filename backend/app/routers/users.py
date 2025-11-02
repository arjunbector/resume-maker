from fastapi import APIRouter, HTTPException
from loguru import logger
from database.models import User
from database.operations import UserOperations
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("")
def get_user(email: str):
    try:
        logger.info(f"Fetching user with email: {email}")
        result = UserOperations.get_user(email)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")

@router.put("")
def update_user(email: str, updates: Dict[str, Any]):
    try:
        logger.info(f"Updating user with email: {email}")
        result = UserOperations.update_user(email, updates)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
