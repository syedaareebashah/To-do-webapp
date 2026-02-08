"""
ResponseTemplate Entity Model for Todo AI Chatbot Agent

This module defines the ResponseTemplate entity that provides standardized
templates for agent responses based on action type.
"""

from enum import Enum
from typing import Dict, Any, Optional
import re


class ActionType(Enum):
    """Enumeration of possible action types."""
    SUCCESS = "SUCCESS"
    ERROR = "ERROR"
    CLARIFICATION = "CLARIFICATION"


class Tone(Enum):
    """Enumeration of possible response tones."""
    FRIENDLY = "FRIENDLY"
    PROFESSIONAL = "PROFESSIONAL"
    NEUTRAL = "NEUTRAL"


class ResponseTemplate:
    """
    Standardized template for agent responses based on action type.
    """

    def __init__(
        self,
        action_type: ActionType,
        template: str,
        tone: Tone = Tone.FRIENDLY,
        template_id: Optional[str] = None
    ):
        """
        Initialize a ResponseTemplate object.

        Args:
            action_type (ActionType): Type of action (SUCCESS, ERROR, CLARIFICATION)
            template (str): Template string with placeholders
            tone (Tone): Tone of the response (default: FRIENDLY)
            template_id (Optional[str]): Unique identifier for the template
        """
        self.id = template_id
        self.action_type = action_type
        self.template = template
        self.tone = tone

        # Validate that template contains valid placeholders
        self._validate_template()

    def _validate_template(self):
        """
        Validate that the template contains valid placeholders.
        Placeholders should be in the format {variable_name}.
        """
        # Find all placeholders in the template
        placeholders = re.findall(r'\{(\w+)\}', self.template)

        # Check that the template has valid format
        if not isinstance(self.template, str):
            raise ValueError("Template must be a string")

    def format(self, **kwargs) -> str:
        """
        Format the template with the provided keyword arguments.

        Args:
            **kwargs: Keyword arguments to substitute into the template

        Returns:
            str: Formatted response string
        """
        try:
            return self.template.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required placeholder in template: {e}")
        except Exception as e:
            raise ValueError(f"Error formatting template: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the response template to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the response template
        """
        return {
            "id": self.id,
            "action_type": self.action_type.value,
            "template": self.template,
            "tone": self.tone.value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResponseTemplate':
        """
        Create a ResponseTemplate from a dictionary representation.

        Args:
            data (Dict[str, Any]): Dictionary representation of the response template

        Returns:
            ResponseTemplate: The reconstructed ResponseTemplate object
        """
        action_type = ActionType(data['action_type'])
        template = data['template']
        tone = Tone(data['tone'])
        template_id = data.get('id')

        return cls(action_type, template, tone, template_id)


# Predefined response templates for different action types
PREDEFINED_TEMPLATES = {
    # Success templates
    "add_task_success": ResponseTemplate(
        action_type=ActionType.SUCCESS,
        template="Added task: '{task_content}'",
        tone=Tone.FRIENDLY
    ),
    "list_tasks_success": ResponseTemplate(
        action_type=ActionType.SUCCESS,
        template="Here are your tasks: {task_list}",
        tone=Tone.FRIENDLY
    ),
    "complete_task_success": ResponseTemplate(
        action_type=ActionType.SUCCESS,
        template="Task {task_id} marked as complete",
        tone=Tone.FRIENDLY
    ),
    "delete_task_success": ResponseTemplate(
        action_type=ActionType.SUCCESS,
        template="Task {task_id} has been deleted",
        tone=Tone.FRIENDLY
    ),
    "update_task_success": ResponseTemplate(
        action_type=ActionType.SUCCESS,
        template="Task {task_id} has been updated",
        tone=Tone.FRIENDLY
    ),

    # Error templates
    "task_not_found_error": ResponseTemplate(
        action_type=ActionType.ERROR,
        template="I couldn't find that task. Would you like to see your current tasks?",
        tone=Tone.FRIENDLY
    ),
    "invalid_parameter_error": ResponseTemplate(
        action_type=ActionType.ERROR,
        template="I had trouble understanding your request. {error_details}",
        tone=Tone.FRIENDLY
    ),
    "tool_execution_error": ResponseTemplate(
        action_type=ActionType.ERROR,
        template="Sorry, I couldn't complete that action. Please try again.",
        tone=Tone.FRIENDLY
    ),

    # Clarification templates
    "clarification_request": ResponseTemplate(
        action_type=ActionType.CLARIFICATION,
        template="Could you clarify {aspect}? For example, which task would you like me to {action}?",
        tone=Tone.FRIENDLY
    )
}