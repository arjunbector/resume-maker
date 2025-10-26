from fastapi import APIRouter, HTTPException
from loguru import logger
from database.models import User
from database.client import mongodb
from uuid import uuid4
from typing import Dict, Any

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("")
def create_user(user: User):
    try:
        logger.info(f"Creating new user: {user.email}")

        # Check if user already exists
        existing_user = mongodb.db.users.find_one({"email": user.email})
        if existing_user:
            logger.warning(f"User with email {user.email} already exists")
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Generate user_id if not provided
        if not user.user_id:
            user.user_id = str(uuid4())

        # Insert user into database
        user_dict = user.model_dump()
        result = mongodb.db.users.insert_one(user_dict)

        logger.info(f"User created successfully with id: {user.user_id}")

        return {
            "message": "User created successfully",
            "user_id": user.user_id
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

@router.put("")
def update_user(email: str, updates: Dict[str, Any]):
    try:
        logger.info(f"Updating user with email: {email}")

        # Check if user exists
        existing_user = mongodb.db.users.find_one({"email": email})
        if not existing_user:
            logger.warning(f"User with email {email} not found")
            raise HTTPException(status_code=404, detail="User not found")

        # Remove email from updates if present (can't update email)
        if "email" in updates:
            del updates["email"]

        # Remove user_id from updates if present (can't update user_id)
        if "user_id" in updates:
            del updates["user_id"]

        # Update user in database
        result = mongodb.db.users.update_one(
            {"email": email},
            {"$set": updates}
        )

        logger.info(f"User updated successfully: {email}")

        return {
            "message": "User updated successfully",
            "email": email,
            "modified_count": result.modified_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update user: {str(e)}")
