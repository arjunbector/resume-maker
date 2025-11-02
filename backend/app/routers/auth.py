from fastapi import APIRouter, HTTPException, Response, Cookie
from loguru import logger
from database.models import SignupRequest, LoginRequest, UserResponse
from database.operations import UserOperations
from utils.auth import create_access_token, decode_access_token
from typing import Optional

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/signup")
def signup(request: SignupRequest, response: Response):
    """
    Sign up a new user with email and password
    Creates a user with default values for other fields
    """
    try:
        logger.info(f"Signing up new user: {request.email}")
        result = UserOperations.create_user_with_password(request.email, request.password)

        # Create access token
        access_token = create_access_token(
            data={"sub": result["user_id"], "email": request.email}
        )

        # Set cookie with JWT token
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=30 * 24 * 60 * 60,  # 30 days in seconds
            samesite="lax",
            secure=False  # Set to True in production with HTTPS
        )

        logger.info(f"User signed up successfully: {request.email}")

        return {
            "message": "User created successfully",
            "user_id": result["user_id"],
            "email": request.email
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error signing up user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sign up user: {str(e)}")


@router.post("/login")
def login(request: LoginRequest, response: Response):
    """
    Login user with email and password
    Sets JWT access token in cookie
    """
    try:
        logger.info(f"Logging in user: {request.email}")

        # Authenticate user
        user = UserOperations.authenticate_user(request.email, request.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create access token
        access_token = create_access_token(
            data={"sub": user["user_id"], "email": user["email"]}
        )

        # Set cookie with JWT token
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            max_age=30 * 24 * 60 * 60,  # 30 days in seconds
            samesite="lax",
            secure=False  # Set to True in production with HTTPS
        )

        logger.info(f"User logged in successfully: {request.email}")

        return {
            "message": "Login successful",
            "user_id": user["user_id"],
            "email": user["email"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to login: {str(e)}")


@router.get("/me")
def get_current_user(access_token: Optional[str] = Cookie(None)):
    """
    Get current authenticated user details from JWT token
    """
    try:
        if not access_token:
            raise HTTPException(status_code=401, detail="Not authenticated")

        # Decode token
        payload = decode_access_token(access_token)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")

        # Get user from database
        user = UserOperations.get_user_by_id(user_id)

        # Remove hashed_password from response
        user.pop("hashed_password", None)

        logger.info(f"Current user fetched: {user['email']}")

        return user

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get current user: {str(e)}")


@router.post("/logout")
def logout(response: Response):
    """
    Logout user by removing the access token cookie
    """
    try:
        # Remove cookie
        response.delete_cookie(key="access_token")

        logger.info("User logged out successfully")

        return {"message": "Logout successful"}

    except Exception as e:
        logger.error(f"Error logging out user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to logout: {str(e)}")
