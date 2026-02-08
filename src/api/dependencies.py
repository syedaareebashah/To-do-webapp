"""
API Dependencies for Todo AI Chatbot System

This module defines shared dependencies for the API endpoints.
"""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlmodel import Session
from src.database.session import get_session
import os


# Get secret key from environment - prioritize SECRET_KEY, fallback to BETTER_AUTH_SECRET
SECRET_KEY = os.getenv("SECRET_KEY", os.getenv("BETTER_AUTH_SECRET", "fallback_secret_key_for_development"))
ALGORITHM = "HS256"


security = HTTPBearer()


def get_current_user(
    token: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_session)
):
    """
    Dependency to get the current authenticated user from the token.

    Args:
        token (HTTPAuthorizationCredentials): The authentication token
        db (Session): Database session

    Returns:
        User: The authenticated user object

    Raises:
        HTTPException: If authentication fails
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # Decode the token to get user information
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        
        # The token from the main backend contains "user_id", not "sub"
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # In a real implementation, you would fetch the user from the database
    # For now, we'll return a basic user object with just the ID
    # In practice, you would do something like:
    # user = user_service.get(db, user_id)
    # if user is None:
    #     raise credentials_exception
    # return user

    # For this demo, we'll return a simple dict with the user ID
    return {"id": user_id, "username": f"user_{user_id}"}


def get_current_active_user(current_user = Depends(get_current_user)):
    """
    Dependency to get the current active user.

    Args:
        current_user: The current authenticated user

    Returns:
        User: The authenticated user object
    """
    # In a real implementation, you would check if the user is active
    # For now, we assume all authenticated users are active
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Inactive user"
        )

    return current_user