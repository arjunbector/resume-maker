from fastapi import APIRouter, HTTPException, Response, Depends
from loguru import logger
from database.models import SignupRequest, LoginRequest, UserResponse
from database.operations import UserOperations
from utils.auth import create_access_token
from utils.dependencies import get_current_user as get_current_user_dependency

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
            "email": request.email,
            "access_token": access_token
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
            "email": user["email"],
            "access_token": access_token
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging in user: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to login: {str(e)}")


@router.get("/me")
def get_current_user(current_user: dict = Depends(get_current_user_dependency)):
    """
    Get current authenticated user details from JWT token.
    Supports both cookie and Authorization header (Bearer token).
    """
    return current_user


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
