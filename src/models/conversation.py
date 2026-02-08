"""
Conversation database model for the Todo AI Chatbot System.

This module defines the Conversation entity with its fields, relationships, and constraints.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List, TYPE_CHECKING
from datetime import datetime
import uuid


if TYPE_CHECKING:
    from src.models.user import User
    from src.models.message import Message


class ConversationBase(SQLModel):
    """
    Base class for Conversation model containing common fields.
    """
    pass


class Conversation(ConversationBase, table=True):
    """
    Conversation model representing a conversation thread between user and assistant.

    Attributes:
        id (uuid.UUID): Unique identifier for the conversation
        user_id (uuid.UUID): References the User who owns the conversation
        created_at (datetime): Timestamp when the conversation was started
        updated_at (datetime): Timestamp when the conversation was last updated
        user (User): The user who owns this conversation
        messages (List[Message]): List of messages in this conversation
    """
    __tablename__ = "conversations"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    user: "User" = Relationship(back_populates="conversations")
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationRead(ConversationBase):
    """
    Schema for reading Conversation data.

    Attributes:
        id (uuid.UUID): Unique identifier for the conversation
        user_id (uuid.UUID): ID of the user who owns the conversation
        created_at (datetime): Timestamp when the conversation was started
        updated_at (datetime): Timestamp when the conversation was last updated
    """
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConversationCreate(SQLModel):
    """
    Schema for creating a new Conversation.

    Attributes:
        user_id (uuid.UUID): ID of the user who owns the conversation
    """
    user_id: uuid.UUID


class ConversationUpdate(SQLModel):
    """
    Schema for updating Conversation data.

    Attributes:
        updated_at (datetime): New timestamp for when the conversation was last updated
    """
    updated_at: datetime