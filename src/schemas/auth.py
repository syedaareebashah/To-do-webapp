"""
Authentication schemas for the Todo AI Chatbot System
"""

from pydantic import BaseModel, EmailStr, validator
from typing import Optional
from datetime import datetime
import uuid


class SignupRequest(BaseModel):
    """
    Schema for user signup requests.
    
    Attributes:
        email (EmailStr): User's email address
        password (str): User's password
    """
    email: EmailStr
    password: str


class SigninRequest(BaseModel):
    """
    Schema for user signin requests.
    
    Attributes:
        email (EmailStr): User's email address
        password (str): User's password
    """
    email: EmailStr
    password: str


class UserPublic(BaseModel):
    """
    Schema for public user information.
    
    Attributes:
        id (uuid.UUID): User's unique identifier
        email (str): User's email address
        username (str): User's username
        created_at (datetime): When the user account was created
    """
    id: uuid.UUID
    email: str
    username: str
    created_at: datetime


class AuthResponse(BaseModel):
    """
    Schema for authentication responses.
    
    Attributes:
        token (str): JWT access token
        user (UserPublic): User information
    """
    token: str
    user: UserPublic