from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class SignupRequest(BaseModel):
    """Request model for user signup."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., min_length=8, description="User's password (min 8 characters)")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }

class SigninRequest(BaseModel):
    """Request model for user signin."""
    email: EmailStr = Field(..., description="User's email address")
    password: str = Field(..., description="User's password")

    class Config:
        schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123"
            }
        }

class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""
    token: str = Field(..., description="JWT authentication token")
    user: "UserPublic" = Field(..., description="User information")

    class Config:
        schema_extra = {
            "example": {
                "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "user": {
                    "user_id": "550e8400-e29b-41d4-a716-446655440000",
                    "email": "user@example.com",
                    "created_at": "2026-02-04T12:00:00Z"
                }
            }
        }

# Import UserPublic to resolve forward reference
from .user import UserPublic
AuthResponse.update_forward_refs()
