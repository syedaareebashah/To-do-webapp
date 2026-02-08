"""
Response Service for Todo AI Chatbot System

This module provides business logic for handling assistant responses.
"""

from typing import List, Optional
from uuid import UUID
from sqlmodel import Session, select
from datetime import datetime
from src.models.message import Message, MessageCreate, MessageRole
from src.database.session import get_session


class ResponseService:
    """
    Service class for handling assistant response operations.
    """

    def __init__(self, db_session: Session):
        """
        Initialize the response service with a database session.

        Args:
            db_session (Session): Database session for operations
        """
        self.db = db_session

    def create_assistant_response(
        self,
        conversation_id: UUID,
        content: str,
        tool_calls: Optional[List[dict]] = None
    ) -> Message:
        """
        Create an assistant response message.

        Args:
            conversation_id (UUID): ID of the conversation to add the response to
            content (str): The content of the assistant's response
            tool_calls (Optional[List[dict]]): List of tool calls made during the response

        Returns:
            Message: The created assistant response message
        """
        # Create a new Message instance for the assistant response
        response_message = Message(
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=content
        )

        # Add to database
        self.db.add(response_message)
        self.db.commit()
        self.db.refresh(response_message)

        return response_message

    def get_latest_responses(
        self,
        conversation_id: UUID,
        limit: int = 5
    ) -> List[Message]:
        """
        Get the most recent assistant responses in a conversation.

        Args:
            conversation_id (UUID): ID of the conversation
            limit (int): Maximum number of responses to return

        Returns:
            List[Message]: List of recent assistant responses
        """
        # Query for assistant messages in the specified conversation
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.role == MessageRole.ASSISTANT
        ).order_by(Message.timestamp.desc()).limit(limit)

        responses = self.db.exec(statement).all()
        return responses

    def update_response_content(self, response_id: UUID, new_content: str) -> Optional[Message]:
        """
        Update the content of an existing assistant response.

        Args:
            response_id (UUID): ID of the response to update
            new_content (str): New content for the response

        Returns:
            Optional[Message]: The updated response if successful, None otherwise
        """
        # Get the existing response
        response = self.db.get(Message, response_id)
        if not response or response.role != MessageRole.ASSISTANT:
            return None

        # Update the content
        response.content = new_content
        response.timestamp = datetime.utcnow()  # Update timestamp

        # Commit changes
        self.db.add(response)
        self.db.commit()
        self.db.refresh(response)

        return response

    def delete_response(self, response_id: UUID) -> bool:
        """
        Delete an assistant response.

        Args:
            response_id (UUID): ID of the response to delete

        Returns:
            bool: True if deletion was successful, False otherwise
        """
        # Get the response
        response = self.db.get(Message, response_id)
        if not response or response.role != MessageRole.ASSISTANT:
            return False

        # Delete the response
        self.db.delete(response)
        self.db.commit()

        return True

    def get_response_by_id(self, response_id: UUID) -> Optional[Message]:
        """
        Get a specific assistant response by its ID.

        Args:
            response_id (UUID): ID of the response to retrieve

        Returns:
            Optional[Message]: The response if found and is an assistant message, None otherwise
        """
        response = self.db.get(Message, response_id)
        if response and response.role == MessageRole.ASSISTANT:
            return response
        return None

    def get_responses_with_tool_calls(
        self,
        conversation_id: UUID,
        limit: int = 10
    ) -> List[Message]:
        """
        Get assistant responses that include tool calls.

        Args:
            conversation_id (UUID): ID of the conversation
            limit (int): Maximum number of responses to return

        Returns:
            List[Message]: List of assistant responses that include tool calls
        """
        # This would typically involve looking for responses that have tool call metadata
        # For now, we'll return all assistant responses since the Message model doesn't
        # currently have a specific field for tool calls
        statement = select(Message).where(
            Message.conversation_id == conversation_id,
            Message.role == MessageRole.ASSISTANT
        ).order_by(Message.timestamp.desc()).limit(limit)

        responses = self.db.exec(statement).all()

        # In a real implementation, we would filter for messages that have tool call data
        # For now, returning all assistant messages
        return responses