from fastapi import Cookie, Header, HTTPException
from typing import Optional
from utils.auth import decode_access_token
from database.operations import UserOperations
from loguru import logger


def get_current_user(
    access_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
):
    """
    Get current authenticated user from JWT token.
    Checks both cookie and Authorization header (Bearer token).

    Priority:
    1. Cookie (access_token)
    2. Authorization header (Bearer {token})

    Args:
        access_token: JWT token from cookie
        authorization: Authorization header with Bearer token

    Returns:
        User dict without hashed_password

    Raises:
        HTTPException: 401 if not authenticated or token invalid
        HTTPException: 404 if user not found
    """
    token = None

    # First, try to get token from cookie
    if access_token:
        token = access_token
        logger.debug("Token found in cookie")
    # If no cookie, try Authorization header
    elif authorization:
        # Check if it's a Bearer token
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "").strip()
            logger.debug("Token found in Authorization header")
        else:
            raise HTTPException(
                status_code=401,
                detail="Invalid Authorization header format. Expected: Bearer {token}"
            )

    # If no token found in either location
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated. Provide token via cookie or Authorization header"
        )

    # Decode and validate token
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token payload"
        )

    # Get user from database
    try:
        user = UserOperations.get_user_by_id(user_id)
        # Remove hashed_password from response
        user.pop("hashed_password", None)

        logger.info(f"Current user authenticated: {user['email']}")
        return user

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
