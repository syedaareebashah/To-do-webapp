"""
Conversation Manager for Todo AI Chatbot Agent

This module manages conversation contexts, including creation, retrieval, and cleanup.
"""

from typing import Dict, Optional
from uuid import uuid4
from datetime import datetime
from ..models.conversation_context import ConversationContext


class ConversationManager:
    """
    Manages conversation contexts, including creation, retrieval, and cleanup.
    """

    def __init__(self):
        """
        Initialize the conversation manager.
        """
        self.conversations: Dict[str, ConversationContext] = {}

    def create_conversation(self, conversation_id: Optional[str] = None, max_turns: int = 20) -> ConversationContext:
        """
        Create a new conversation context.

        Args:
            conversation_id (Optional[str]): Specific ID for the conversation (if None, generates one)
            max_turns (int): Maximum number of turns to keep in context

        Returns:
            ConversationContext: The newly created conversation context
        """
        if conversation_id is None:
            conversation_id = str(uuid4())

        context = ConversationContext(conversation_id=conversation_id, max_turns=max_turns)
        self.conversations[conversation_id] = context

        return context

    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """
        Retrieve an existing conversation context.

        Args:
            conversation_id (str): The ID of the conversation to retrieve

        Returns:
            Optional[ConversationContext]: The conversation context if found, None otherwise
        """
        # Check if conversation exists and hasn't expired
        if conversation_id in self.conversations:
            context = self.conversations[conversation_id]
            if context.is_expired():
                self.cleanup_expired_conversations()
                return self.conversations.get(conversation_id)
            return context

        return None

    def update_conversation(self, context: ConversationContext) -> None:
        """
        Update an existing conversation context.

        Args:
            context (ConversationContext): The updated conversation context
        """
        self.conversations[context.conversation_id] = context

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Delete a conversation context.

        Args:
            conversation_id (str): The ID of the conversation to delete

        Returns:
            bool: True if the conversation was deleted, False if it didn't exist
        """
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
            return True
        return False

    def cleanup_expired_conversations(self) -> int:
        """
        Remove all expired conversations.

        Returns:
            int: Number of conversations removed
        """
        expired_ids = []
        current_time = datetime.now()

        for conversation_id, context in self.conversations.items():
            if context.is_expired():
                expired_ids.append(conversation_id)

        for conversation_id in expired_ids:
            del self.conversations[conversation_id]

        return len(expired_ids)

    def get_active_conversations_count(self) -> int:
        """
        Get the number of active conversations.

        Returns:
            int: Number of active conversations
        """
        # Clean up expired conversations first
        self.cleanup_expired_conversations()

        return len(self.conversations)

    def get_conversation_summary(self, conversation_id: str) -> Optional[Dict]:
        """
        Get a summary of a conversation.

        Args:
            conversation_id (str): The ID of the conversation

        Returns:
            Optional[Dict]: Summary information about the conversation, or None if not found
        """
        context = self.get_conversation(conversation_id)
        if not context:
            return None

        return {
            "conversation_id": context.conversation_id,
            "turn_count": len(context.turns),
            "active_tasks_count": len(context.active_tasks),
            "state": context.state.value,
            "created_at": context.created_at.isoformat(),
            "last_activity": context.turns[-1].timestamp.isoformat() if context.turns else context.created_at.isoformat()
        }

    def clear_all_conversations(self) -> int:
        """
        Clear all conversations.

        Returns:
            int: Number of conversations cleared
        """
        count = len(self.conversations)
        self.conversations.clear()
        return count

    def get_recent_conversations(self, limit: int = 10) -> Dict[str, Dict]:
        """
        Get a list of recent conversations with summaries.

        Args:
            limit (int): Maximum number of conversations to return

        Returns:
            Dict[str, Dict]: Dictionary mapping conversation IDs to their summaries
        """
        # Clean up expired conversations first
        self.cleanup_expired_conversations()

        # Sort conversations by last activity (most recent first)
        sorted_conversations = sorted(
            self.conversations.items(),
            key=lambda x: x[1].turns[-1].timestamp if x[1].turns else x[1].created_at,
            reverse=True
        )

        recent_summaries = {}
        for conv_id, context in sorted_conversations[:limit]:
            recent_summaries[conv_id] = self.get_conversation_summary(conv_id)

        return recent_summaries


# Global instance for easy access
conversation_manager = ConversationManager()


def get_or_create_conversation(conversation_id: Optional[str] = None) -> ConversationContext:
    """
    Get an existing conversation or create a new one if it doesn't exist.

    Args:
        conversation_id (Optional[str]): The ID of the conversation to get

    Returns:
        ConversationContext: The conversation context
    """
    if conversation_id is None:
        return conversation_manager.create_conversation()

    existing = conversation_manager.get_conversation(conversation_id)
    if existing:
        return existing

    return conversation_manager.create_conversation(conversation_id)