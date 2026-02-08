"""
ConversationContext Entity Model for Todo AI Chatbot Agent

This module defines the ConversationContext entity that represents
the current state of the conversation.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from uuid import uuid4
from .intent import Intent


class ConversationState(Enum):
    """Enumeration of possible conversation states."""
    ACTIVE = "ACTIVE"
    WAITING_FOR_CLARIFICATION = "WAITING_FOR_CLARIFICATION"
    COMPLETED = "COMPLETED"
    EXPIRED = "EXPIRED"


class Turn:
    """
    Represents a single turn in the conversation (either user or agent).
    """
    def __init__(self, text: str, speaker: str, timestamp: Optional[datetime] = None):
        """
        Initialize a conversation turn.

        Args:
            text (str): The text of the turn
            speaker (str): Who spoke ('user' or 'agent')
            timestamp (Optional[datetime]): When the turn occurred
        """
        self.text = text
        self.speaker = speaker
        self.timestamp = timestamp or datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the turn to a dictionary representation."""
        return {
            "text": self.text,
            "speaker": self.speaker,
            "timestamp": self.timestamp.isoformat()
        }


class ConversationContext:
    """
    Represents the current state of the conversation.
    """

    def __init__(
        self,
        conversation_id: Optional[str] = None,
        max_turns: int = 20
    ):
        """
        Initialize a ConversationContext object.

        Args:
            conversation_id (Optional[str]): Unique identifier for the conversation
            max_turns (int): Maximum number of turns to keep in context (default: 20)
        """
        self.conversation_id = conversation_id or str(uuid4())
        self.turns: List[Turn] = []
        self.active_tasks: List[str] = []
        self.last_intent: Optional[Intent] = None
        self.summary: Optional[str] = None
        self.state = ConversationState.ACTIVE
        self.max_turns = max_turns
        self.created_at = datetime.now()

    def add_user_turn(self, text: str) -> None:
        """
        Add a user turn to the conversation.

        Args:
            text (str): The user's input text
        """
        turn = Turn(text, "user")
        self.turns.append(turn)

        # Trim conversation if it exceeds max turns
        self._trim_conversation()

    def add_agent_turn(self, text: str) -> None:
        """
        Add an agent turn to the conversation.

        Args:
            text (str): The agent's response text
        """
        turn = Turn(text, "agent")
        self.turns.append(turn)

        # Trim conversation if it exceeds max turns
        self._trim_conversation()

    def _trim_conversation(self) -> None:
        """
        Trim the conversation to the maximum number of turns by removing older turns.
        """
        if len(self.turns) > self.max_turns:
            # Keep the most recent turns
            self.turns = self.turns[-self.max_turns:]

    def set_state(self, state: ConversationState) -> None:
        """
        Set the state of the conversation.

        Args:
            state (ConversationState): The new state
        """
        self.state = state

    def add_active_task(self, task_id: str) -> None:
        """
        Add a task ID to the active tasks list.

        Args:
            task_id (str): The ID of the active task
        """
        if task_id not in self.active_tasks:
            self.active_tasks.append(task_id)

    def remove_active_task(self, task_id: str) -> None:
        """
        Remove a task ID from the active tasks list.

        Args:
            task_id (str): The ID of the task to remove
        """
        if task_id in self.active_tasks:
            self.active_tasks.remove(task_id)

    def get_recent_turns(self, count: int = 5) -> List[Turn]:
        """
        Get the most recent turns from the conversation.

        Args:
            count (int): Number of recent turns to return

        Returns:
            List[Turn]: The most recent turns
        """
        return self.turns[-count:] if len(self.turns) >= count else self.turns[:]

    def get_conversation_history(self) -> str:
        """
        Get a string representation of the conversation history.

        Returns:
            str: Formatted conversation history
        """
        history_lines = []
        for turn in self.turns:
            speaker_prefix = "User:" if turn.speaker == "user" else "Agent:"
            history_lines.append(f"{speaker_prefix} {turn.text}")

        return "\n".join(history_lines)

    def get_user_inputs(self) -> List[str]:
        """
        Get all user inputs from the conversation.

        Returns:
            List[str]: List of user inputs
        """
        return [turn.text for turn in self.turns if turn.speaker == "user"]

    def get_agent_responses(self) -> List[str]:
        """
        Get all agent responses from the conversation.

        Returns:
            List[str]: List of agent responses
        """
        return [turn.text for turn in self.turns if turn.speaker == "agent"]

    def is_expired(self) -> bool:
        """
        Check if the conversation has expired based on inactivity.

        Returns:
            bool: True if conversation is expired, False otherwise
        """
        # For now, we'll consider a conversation expired if it's been inactive for 1 hour
        # This can be adjusted based on requirements
        time_since_created = datetime.now() - self.created_at
        return time_since_created.total_seconds() > 3600  # 1 hour in seconds

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the conversation context to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the conversation context
        """
        return {
            "conversation_id": self.conversation_id,
            "turns": [turn.to_dict() for turn in self.turns],
            "active_tasks": self.active_tasks,
            "last_intent": self.last_intent.to_dict() if self.last_intent else None,
            "summary": self.summary,
            "state": self.state.value,
            "max_turns": self.max_turns,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ConversationContext':
        """
        Create a ConversationContext from a dictionary representation.

        Args:
            data (Dict[str, Any]): Dictionary representation of the conversation context

        Returns:
            ConversationContext: The reconstructed ConversationContext object
        """
        context = cls(conversation_id=data['conversation_id'], max_turns=data['max_turns'])

        # Restore turns
        for turn_data in data['turns']:
            turn = Turn(
                text=turn_data['text'],
                speaker=turn_data['speaker'],
                timestamp=datetime.fromisoformat(turn_data['timestamp'])
            )
            context.turns.append(turn)

        # Restore other attributes
        context.active_tasks = data['active_tasks']
        context.summary = data['summary']
        context.state = ConversationState(data['state'])
        context.created_at = datetime.fromisoformat(data['created_at'])

        # Restore last intent if present
        last_intent_data = data.get('last_intent')
        if last_intent_data:
            from .intent import Intent
            context.last_intent = Intent.from_dict(last_intent_data)

        return context