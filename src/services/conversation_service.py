"""
Conversation Service for Todo AI Chatbot System

This module handles conversation-related business logic and operations.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime
from src.models.conversation import Conversation, ConversationCreate
from src.models.message import Message
from src.database.session import get_session


class ConversationService:
    """
    Service class for handling conversation-related operations.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the conversation service with a database session.

        Args:
            db_session (Session): Database session for operations
        """
        self.db = db_session

    def create(self, obj_in: ConversationCreate) -> Conversation:
        """
        Create a new conversation.

        Args:
            obj_in (ConversationCreate): Data for creating the conversation

        Returns:
            Conversation: The created conversation object
        """
        # Create a new Conversation instance from the input data
        db_obj = Conversation(
            user_id=obj_in.user_id
        )

        # Add to database
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    def get_by_id_and_user(self, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
        """
        Get a specific conversation by its ID and user ID.

        Args:
            conversation_id (UUID): ID of the conversation to retrieve
            user_id (str): ID of the user who owns the conversation

        Returns:
            Optional[Conversation]: The conversation if found and owned by user, None otherwise
        """
        # Query for conversation that belongs to the specified user
        statement = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        conversation = self.db.exec(statement).first()
        return conversation

    def get_conversation_history(self, conversation_id: UUID, limit: int = 50) -> List[Message]:
        """
        Get the message history for a conversation.

        Args:
            conversation_id (UUID): ID of the conversation
            limit (int): Maximum number of messages to return (default: 50)

        Returns:
            List[Message]: List of messages in the conversation ordered by timestamp
        """
        # Query for messages in the specified conversation ordered by timestamp
        statement = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp.asc()).limit(limit)

        messages = self.db.exec(statement).all()
        return messages

    def update(self, db_obj: Conversation, obj_in: dict) -> Conversation:
        """
        Update an existing conversation.

        Args:
            db_obj (Conversation): The existing conversation object to update
            obj_in (dict): Dictionary of fields to update

        Returns:
            Conversation: The updated conversation object
        """
        # Update fields from the input data
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        # Update the updated_at timestamp
        db_obj.updated_at = datetime.utcnow()

        # Commit changes
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)

        return db_obj

    def remove(self, conversation_id: UUID, user_id: str) -> Optional[Conversation]:
        """
        Remove a conversation by its ID and user ID.

        Args:
            conversation_id (UUID): ID of the conversation to remove
            user_id (str): ID of the user who owns the conversation

        Returns:
            Optional[Conversation]: The removed conversation if successful, None otherwise
        """
        # Get the conversation
        conversation = self.get_by_id_and_user(conversation_id, user_id)
        if not conversation:
            return None

        # Remove the conversation
        self.db.delete(conversation)
        self.db.commit()

        return conversation

    def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """
        Get all conversations for a specific user.

        Args:
            user_id (str): ID of the user
            limit (int): Maximum number of conversations to return (default: 20)

        Returns:
            List[Conversation]: List of conversations belonging to the user
        """
        # Query for conversations belonging to the specified user
        statement = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.created_at.desc()).limit(limit)

        conversations = self.db.exec(statement).all()
        return conversations

    def get_conversation_statistics(self, user_id: str) -> dict:
        """
        Get statistics about a user's conversations.

        Args:
            user_id (str): ID of the user

        Returns:
            dict: Statistics about the user's conversations
        """
        # Get all conversations for the user
        all_conversations = self.get_user_conversations(user_id, limit=1000)  # High limit to get all

        # Get all messages for these conversations
        conversation_ids = [conv.id for conv in all_conversations]

        if conversation_ids:
            message_statement = select(Message).where(
                Message.conversation_id.in_(conversation_ids)
            )
            all_messages = self.db.exec(message_statement).all()
        else:
            all_messages = []

        # Calculate statistics
        total_conversations = len(all_conversations)
        total_messages = len(all_messages)

        # Calculate average messages per conversation
        avg_messages_per_conv = total_messages / total_conversations if total_conversations > 0 else 0

        return {
            "total_conversations": total_conversations,
            "total_messages": total_messages,
            "average_messages_per_conversation": round(avg_messages_per_conv, 2),
            "last_conversation_at": max((conv.updated_at for conv in all_conversations), default=None) if all_conversations else None
        }

    def validate_conversation_access(self, conversation_id: UUID, user_id: str) -> bool:
        """
        Validate that a user has access to a specific conversation.

        Args:
            conversation_id (UUID): ID of the conversation to check
            user_id (str): ID of the user requesting access

        Returns:
            bool: True if the user has access, False otherwise
        """
        conversation = self.get_by_id_and_user(conversation_id, user_id)
        return conversation is not None

    def get_or_create_user_conversation(self, user_id: str) -> Conversation:
        """
        Get an existing conversation for the user or create a new one if none exists.

        Args:
            user_id (str): ID of the user

        Returns:
            Conversation: Existing or newly created conversation for the user
        """
        # Try to get the most recent conversation for the user
        user_conversations = self.get_user_conversations(user_id, limit=1)

        if user_conversations:
            # Return the most recent conversation
            return user_conversations[0]
        else:
            # Create a new conversation for the user
            conversation_create = ConversationCreate(user_id=user_id)
            return self.create(conversation_create)