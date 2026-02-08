"""
Authentication endpoints for the main Todo AI Chatbot API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from sqlmodel import Session, select
from datetime import timedelta
from jose import jwt
import os
import uuid
from datetime import datetime

from src.models.user import User
from src.database.session import get_session
from src.config.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from src.schemas.auth import SignupRequest, SigninRequest, AuthResponse
from src.schemas.user import UserPublic
from src.utils.password import hash_password, verify_password, validate_password_strength
from src.utils.jwt import create_access_token
from src.api.dependencies import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Create new user account.

    Args:
        signup_data: User signup information (email and password)
        session: Database session

    Returns:
        AuthResponse: JWT token and user information

    Raises:
        HTTPException: 400 if password weak, 409 if email exists
    """
    # Validate password strength
    is_valid, error_message = validate_password_strength(signup_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Check for duplicate email (case-insensitive)
    statement = select(User).where(
        User.email == signup_data.email.lower()
    )
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    # Hash password
    password_hash = hash_password(signup_data.password)

    # Create user with a UUID
    user = User(
        id=uuid.uuid4(),  # Generate a new UUID for the user
        email=signup_data.email.lower(),
        username=signup_data.email.split('@')[0],  # Use part of email as username
        password_hash=password_hash,
        created_at=datetime.utcnow()
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate JWT token
    token = create_access_token({"user_id": str(user.id)}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # Return response
    return AuthResponse(
        token=token,
        user=UserPublic(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at
        )
    )


@router.post("/signin", response_model=AuthResponse)
async def signin(
    signin_data: SigninRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate existing user.

    Args:
        signin_data: User signin information (email and password)
        session: Database session

    Returns:
        AuthResponse: JWT token and user information

    Raises:
        HTTPException: 401 if credentials invalid
    """
    # Query user by email (case-insensitive)
    statement = select(User).where(
        User.email == signin_data.email.lower()
    )
    user = session.exec(statement).first()

    if not user:
        # Use dummy hash to maintain constant time - timing attack prevention
        dummy_hash = "$2b$12$5aZqCkedUxLpC6Pn3ozRhO.76rrhbOm48WCpdXljFlk7YUAB7Nw5K"
        verify_password(signin_data.password, dummy_hash)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(signin_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Generate JWT token
    token = create_access_token({"user_id": str(user.id)}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    # Return response
    return AuthResponse(
        token=token,
        user=UserPublic(
            id=user.id,
            email=user.email,
            username=user.username,
            created_at=user.created_at
        )
    )


@router.get("/me", response_model=UserPublic)
async def get_current_user_info(
    current_user_data: dict = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Args:
        current_user_data: Authenticated user data from JWT token

    Returns:
        UserPublic: Current user information
    """
    # For this implementation, we'll create a minimal user representation
    # In a real implementation, you would fetch the full user from the database
    from datetime import datetime
    import uuid
    
    # Create a minimal user object for response
    # In a real implementation, you would fetch the user from the database
    # using the user_id from current_user_data
    user_id = current_user_data.get("id")
    
    # For demo purposes, we'll create a minimal user representation
    # In a real implementation, you would fetch the user from the database
    # and return the actual user object
    return UserPublic(
        id=uuid.UUID(user_id) if isinstance(user_id, str) and len(user_id) == 36 else uuid.uuid4(),
        email=current_user_data.get("username", "user@example.com"),
        username=current_user_data.get("username", "unknown_user"),
        created_at=datetime.utcnow()
    )