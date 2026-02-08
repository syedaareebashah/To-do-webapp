"""
Message Service for Todo AI Chatbot System

This module provides business logic for message-related operations.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime
from src.models.message import Message, MessageCreate
from src.database.session import get_session


class MessageService:
    """
    Service class for handling message-related operations.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the message service with a database session.

        Args:
            db_session (Session): Database session for operations
        """
        self.db = db_session

    def create(self, obj_in: MessageCreate) -> Message:
        """
        Create a new message.

        Args:
            obj_in (MessageCreate): Data for creating the message

        Returns:
            Message: The created message object
        """
        # Create a new Message instance from the input data
        db_obj = Message(
            conversation_id=obj_in.conversation_id,
            role=obj_in.role,
            content=obj_in.content
        )

        # Add to database
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    def get_messages_by_conversation(self, conversation_id: UUID, limit: int = 50) -> List[Message]:
        """
        Get all messages for a specific conversation ordered by timestamp.

        Args:
            conversation_id (UUID): ID of the conversation to get messages for
            limit (int): Maximum number of messages to return (default: 50)

        Returns:
            List[Message]: List of messages in the conversation ordered by timestamp (oldest first)
        """
        # Query for messages in the specified conversation ordered by timestamp
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).limit(limit)

        messages = self.db.exec(statement).all()
        return messages

    def get_by_id(self, message_id: UUID) -> Optional[Message]:
        """
        Get a specific message by its ID.

        Args:
            message_id (UUID): ID of the message to retrieve

        Returns:
            Optional[Message]: The message if found, None otherwise
        """
        # Query for message by ID
        statement = select(Message).where(Message.id == message_id)
        message = self.db.exec(statement).first()
        return message

    def update(self, db_obj: Message, obj_in: dict) -> Message:
        """
        Update an existing message.

        Args:
            db_obj (Message): The existing message object to update
            obj_in (dict): Dictionary of fields to update

        Returns:
            Message: The updated message object
        """
        # Update fields from the input data
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        # Commit changes
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    def remove(self, message_id: UUID) -> Optional[Message]:
        """
        Remove a message by its ID.

        Args:
            message_id (UUID): ID of the message to remove

        Returns:
            Optional[Message]: The removed message if successful, None otherwise
        """
        # Get the message
        message = self.get_by_id(message_id)
        if not message:
            return None

        # Remove the message
        self.db.delete(message)
        self.db.commit()

        return message