from loguru import logger
from database.client import mongodb
from database.models import User, Session, ResumeState, Questionnaire, KnowledgeGraph, ResumeStage
from uuid import uuid4
from typing import Dict, Any, Optional
from datetime import datetime
from utils.auth import hash_password, verify_password

class UserOperations:
    @staticmethod
    def get_user(email: str) -> Dict[str, Any]:
        """Get user by email"""
        user = mongodb.db.users.find_one({"email": email})
        if not user:
            logger.warning(f"User with email {email} not found")
            raise ValueError("User not found")

        # Remove MongoDB _id field
        user.pop("_id", None)

        logger.info(f"User fetched successfully: {email}")
        return user

    @staticmethod
    def get_user_by_id(user_id: str) -> Dict[str, Any]:
        """Get user by user_id"""
        user = mongodb.db.users.find_one({"user_id": user_id})
        if not user:
            logger.warning(f"User with id {user_id} not found")
            raise ValueError("User not found")

        # Remove MongoDB _id field
        user.pop("_id", None)

        logger.info(f"User fetched successfully: {user_id}")
        return user

    @staticmethod
    def create_user_with_password(email: str, password: str) -> Dict[str, str]:
        """Create a new user with email and password"""
        # Check if user already exists
        existing_user = mongodb.db.users.find_one({"email": email})
        if existing_user:
            logger.warning(f"User with email {email} already exists")
            raise ValueError("User with this email already exists")

        # Generate user_id and hash password
        user_id = str(uuid4())
        hashed_password = hash_password(password)

        # Create user with default values including empty knowledge_graph
        user = User(
            user_id=user_id,
            email=email,
            hashed_password=hashed_password,
            name="",
            phone="",
            socials={},
            address="",
            knowledge_graph=KnowledgeGraph()
        )

        # Insert user into database
        user_dict = user.model_dump()
        mongodb.db.users.insert_one(user_dict)

        logger.info(f"User created successfully with id: {user_id}")

        return {
            "message": "User created successfully",
            "user_id": user_id
        }

    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with email and password"""
        user = mongodb.db.users.find_one({"email": email})
        if not user:
            logger.warning(f"User with email {email} not found")
            return None

        # Verify password
        if not verify_password(password, user["hashed_password"]):
            logger.warning(f"Invalid password for user {email}")
            return None

        # Remove MongoDB _id and hashed_password from response
        user.pop("_id", None)
        user.pop("hashed_password", None)

        logger.info(f"User authenticated successfully: {email}")
        return user

    @staticmethod
    def update_user(email: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update user fields by email"""
        # Check if user exists
        existing_user = mongodb.db.users.find_one({"email": email})
        if not existing_user:
            logger.warning(f"User with email {email} not found")
            raise ValueError("User not found")

        # Remove protected fields from updates if present
        protected_fields = ["email", "user_id", "hashed_password"]
        for field in protected_fields:
            if field in updates:
                del updates[field]

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

class SessionOperations:
    @staticmethod
    def create_session(user_id: str, job_details) -> Dict[str, str]:
        """Create a new session for a user"""
        # Check if user exists
        user = mongodb.db.users.find_one({"user_id": user_id})
        if not user:
            logger.warning(f"User with id {user_id} not found")
            raise ValueError("User not found")

        # Generate session_id
        session_id = str(uuid4())

        # Create session with default values using new models
        now = datetime.utcnow()
        session = Session(
            session_id=session_id,
            user_id=user_id,
            job_details=job_details,
            resume_state=ResumeState(
                stage=ResumeStage.INIT,
                required_fields=[],
                missing_fields=[],
                ai_context={},
                last_action="session_created"
            ),
            questionnaire=Questionnaire(
                questions=[],
                completion=0.0
            ),
            last_active=now,
            created_at=now
        )

        # Insert session into database
        session_dict = session.model_dump()
        mongodb.db.sessions.insert_one(session_dict)

        logger.info(f"Session created successfully with id: {session_id}")

        return {
            "message": "Session created successfully",
            "session_id": session_id,
            "user_id": user_id
        }

    @staticmethod
    def update_session(session_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update session fields by session_id"""
        # Check if session exists
        existing_session = mongodb.db.sessions.find_one({"session_id": session_id})
        if not existing_session:
            logger.warning(f"Session with id {session_id} not found")
            raise ValueError("Session not found")

        # Remove session_id from updates if present (can't update session_id)
        if "session_id" in updates:
            del updates["session_id"]

        # Update last_active timestamp
        updates["last_active"] = datetime.utcnow()

        # Update session in database
        result = mongodb.db.sessions.update_one(
            {"session_id": session_id},
            {"$set": updates}
        )

        logger.info(f"Session updated successfully: {session_id}")

        return {
            "message": "Session updated successfully",
            "session_id": session_id,
            "modified_count": result.modified_count
        }
