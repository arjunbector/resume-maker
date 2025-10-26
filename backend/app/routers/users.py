from fastapi import APIRouter, HTTPException
from loguru import logger
from database.models import User
from database.client import mongodb
from uuid import uuid4

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
