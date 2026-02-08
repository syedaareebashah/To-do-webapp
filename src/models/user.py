"""
User database model for the Todo AI Chatbot System.

This module defines the User entity with its fields, relationships, and constraints.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import uuid


class UserBase(SQLModel):
    """
    Base class for User model containing common fields.
    """
    username: str = Field(unique=True, nullable=False, max_length=50)
    email: str = Field(unique=True, nullable=False, max_length=100)
    password_hash: str = Field(nullable=False)


class User(UserBase, table=True):
    """
    User model representing a system user.

    Attributes:
        id (uuid.UUID): Unique identifier for the user
        username (str): Unique username for the user
        email (str): User's email address
        created_at (datetime): Timestamp when the user account was created
        tasks (List[Task]): List of tasks associated with the user
        conversations (List[Conversation]): List of conversations associated with the user
    """
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    tasks: List["Task"] = Relationship(back_populates="user")
    conversations: List["Conversation"] = Relationship(back_populates="user")


class UserRead(UserBase):
    """
    Schema for reading User data.

    Attributes:
        id (uuid.UUID): Unique identifier for the user
        created_at (datetime): Timestamp when the user account was created
    """
    id: uuid.UUID
    created_at: datetime


class UserCreate(UserBase):
    """
    Schema for creating a new User.
    """
    pass


class UserUpdate(SQLModel):
    """
    Schema for updating User data.

    Attributes:
        username (Optional[str]): New username for the user
        email (Optional[str]): New email for the user
    """
    username: Optional[str] = None
    email: Optional[str] = None