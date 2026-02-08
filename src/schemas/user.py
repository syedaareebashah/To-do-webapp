"""
User schema for the Todo AI Chatbot System
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import uuid


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