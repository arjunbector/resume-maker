from loguru import logger
from database.client import mongodb
from database.models import User
from uuid import uuid4
from typing import Dict, Any, Optional

class UserOperations:
    @staticmethod
    def create_user(user: User) -> Dict[str, str]:
        """Create a new user in the database"""
        # Check if user already exists
        existing_user = mongodb.db.users.find_one({"email": user.email})
        if existing_user:
            logger.warning(f"User with email {user.email} already exists")
            raise ValueError("User with this email already exists")

        # Generate user_id if not provided
        if not user.user_id:
            user.user_id = str(uuid4())

        # Insert user into database
        user_dict = user.model_dump()
        mongodb.db.users.insert_one(user_dict)

        logger.info(f"User created successfully with id: {user.user_id}")

        return {
            "message": "User created successfully",
            "user_id": user.user_id
        }

    @staticmethod
    def update_user(email: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user fields by email"""
        # Check if user exists
        existing_user = mongodb.db.users.find_one({"email": email})
        if not existing_user:
            logger.warning(f"User with email {email} not found")
            raise ValueError("User not found")

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
