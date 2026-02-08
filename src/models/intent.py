"""
Intent Entity Model for Todo AI Chatbot Agent

This module defines the Intent entity that represents the user's intention
extracted from natural language input.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, Optional


class IntentType(Enum):
    """Enumeration of possible intent types."""
    ADD_TASK = "ADD_TASK"
    LIST_TASKS = "LIST_TASKS"
    COMPLETE_TASK = "COMPLETE_TASK"
    DELETE_TASK = "DELETE_TASK"
    UPDATE_TASK = "UPDATE_TASK"
    AMBIGUOUS = "AMBIGUOUS"


class IntentState(Enum):
    """Enumeration of possible intent states."""
    RECOGNIZED = "RECOGNIZED"
    VALIDATED = "VALIDATED"
    EXECUTED = "EXECUTED"
    FAILED = "FAILED"


class Intent:
    """
    Represents the user's intention extracted from natural language input.
    """

    def __init__(
        self,
        intent_type: IntentType,
        confidence: float,
        parameters: Optional[Dict[str, Any]] = None,
        intent_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ):
        """
        Initialize an Intent object.

        Args:
            intent_type (IntentType): The type of intent
            confidence (float): Confidence score between 0.0 and 1.0
            parameters (Optional[Dict[str, Any]]): Parameters extracted from user input
            intent_id (Optional[str]): Unique identifier for the intent
            timestamp (Optional[datetime]): When the intent was recognized
        """
        # Validate confidence score
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"Confidence must be between 0.0 and 1.0, got {confidence}")

        self.id = intent_id
        self.type = intent_type
        self.confidence = confidence
        self.parameters = parameters or {}
        self.timestamp = timestamp or datetime.now()
        self.state = IntentState.RECOGNIZED

    def validate_parameters(self, required_params: list) -> bool:
        """
        Validate that required parameters are present.

        Args:
            required_params (list): List of required parameter names

        Returns:
            bool: True if all required parameters are present, False otherwise
        """
        for param in required_params:
            if param not in self.parameters:
                return False
        return True

    def set_state(self, state: IntentState):
        """
        Set the state of the intent.

        Args:
            state (IntentState): The new state
        """
        self.state = state

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the intent to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the intent
        """
        return {
            "id": self.id,
            "type": self.type.value,
            "confidence": self.confidence,
            "parameters": self.parameters,
            "timestamp": self.timestamp.isoformat(),
            "state": self.state.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Intent':
        """
        Create an Intent from a dictionary representation.

        Args:
            data (Dict[str, Any]): Dictionary representation of the intent

        Returns:
            Intent: The reconstructed Intent object
        """
        intent_type = IntentType(data['type'])
        confidence = data['confidence']
        parameters = data.get('parameters', {})
        intent_id = data.get('id')

        # Convert timestamp string back to datetime
        timestamp_str = data.get('timestamp')
        timestamp = datetime.fromisoformat(timestamp_str) if timestamp_str else None

        intent_state = IntentState(data.get('state', IntentState.RECOGNIZED.value))

        intent = cls(intent_type, confidence, parameters, intent_id, timestamp)
        intent.state = intent_state

        return intent