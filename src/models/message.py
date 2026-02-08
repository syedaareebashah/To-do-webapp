"""
Message database model for the Todo AI Chatbot System.

This module defines the Message entity with its fields, relationships, and constraints.
"""

from enum import Enum
from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid


if TYPE_CHECKING:
    from src.models.conversation import Conversation


class MessageRole(str, Enum):
    """
    Enum for message role values.
    """
    USER = "user"
    ASSISTANT = "assistant"


class MessageBase(SQLModel):
    """
    Base class for Message model containing common fields.
    """
    role: MessageRole = Field(nullable=False)
    content: str = Field(nullable=False, max_length=10000)


class Message(MessageBase, table=True):
    """
    Message model representing a single message in a conversation.

    Attributes:
        id (uuid.UUID): Unique identifier for the message
        conversation_id (uuid.UUID): References the Conversation this message belongs to
        role (MessageRole): Role of the message sender (user, assistant)
        content (str): The content of the message
        timestamp (datetime): Timestamp when the message was sent
        conversation (Conversation): The conversation this message belongs to
    """
    __tablename__ = "messages"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id", nullable=False)
    timestamp: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationship
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageRead(MessageBase):
    """
    Schema for reading Message data.

    Attributes:
        id (uuid.UUID): Unique identifier for the message
        conversation_id (uuid.UUID): ID of the conversation this message belongs to
        timestamp (datetime): Timestamp when the message was sent
    """
    id: uuid.UUID
    conversation_id: uuid.UUID
    timestamp: datetime


class MessageCreate(MessageBase):
    """
    Schema for creating a new Message.

    Attributes:
        conversation_id (uuid.UUID): ID of the conversation this message belongs to
    """
    conversation_id: uuid.UUID


class MessageUpdate(SQLModel):
    """
    Schema for updating Message data.

    Attributes:
        content (Optional[str]): New content for the message
        role (Optional[MessageRole]): New role for the message
    """
    content: Optional[str] = None
    role: Optional[MessageRole] = None