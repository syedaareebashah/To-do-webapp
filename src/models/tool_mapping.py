"""
ToolMapping Entity Model for Todo AI Chatbot Agent

This module defines the ToolMapping entity that defines the relationship
between recognized intents and MCP tools.
"""

from enum import Enum
from typing import Dict, List, Any, Optional
from .intent import IntentType


class ToolMapping:
    """
    Defines the relationship between recognized intents and MCP tools.
    """

    def __init__(
        self,
        intent_type: IntentType,
        mcp_tool: str,
        required_parameters: Optional[List[str]] = None,
        optional_parameters: Optional[List[str]] = None,
        tool_mapping_id: Optional[str] = None
    ):
        """
        Initialize a ToolMapping object.

        Args:
            intent_type (IntentType): The type of intent that maps to the tool
            mcp_tool (str): Name of the corresponding MCP tool
            required_parameters (Optional[List[str]]): Required parameter names
            optional_parameters (Optional[List[str]]): Optional parameter names
            tool_mapping_id (Optional[str]): Unique identifier for the mapping
        """
        self.id = tool_mapping_id
        self.intent_type = intent_type
        self.mcp_tool = mcp_tool
        self.required_parameters = required_parameters or []
        self.optional_parameters = optional_parameters or []

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """
        Validate that the provided parameters match the mapping requirements.

        Args:
            parameters (Dict[str, Any]): Parameters to validate

        Returns:
            bool: True if parameters are valid for this mapping, False otherwise
        """
        # Check that all required parameters are present
        for param in self.required_parameters:
            if param not in parameters:
                return False

        # Check that only allowed parameters are provided
        all_allowed_params = set(self.required_parameters + self.optional_parameters)
        provided_params = set(parameters.keys())

        # If there are any parameters that aren't allowed, return False
        if not provided_params.issubset(all_allowed_params):
            return False

        return True

    def get_all_parameters(self) -> List[str]:
        """
        Get all possible parameters (required + optional) for this mapping.

        Returns:
            List[str]: Combined list of required and optional parameters
        """
        return self.required_parameters + self.optional_parameters

    def requires_tool_chaining(self) -> bool:
        """
        Check if this tool mapping requires chaining with other tools.

        Returns:
            bool: True if tool chaining is required, False otherwise
        """
        # For now, assume no tool chaining is needed for basic mappings
        # This can be extended based on specific business logic
        return False

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the tool mapping to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary representation of the tool mapping
        """
        return {
            "id": self.id,
            "intent_type": self.intent_type.value,
            "mcp_tool": self.mcp_tool,
            "required_parameters": self.required_parameters,
            "optional_parameters": self.optional_parameters
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolMapping':
        """
        Create a ToolMapping from a dictionary representation.

        Args:
            data (Dict[str, Any]): Dictionary representation of the tool mapping

        Returns:
            ToolMapping: The reconstructed ToolMapping object
        """
        from .intent import IntentType

        intent_type = IntentType(data['intent_type'])
        mcp_tool = data['mcp_tool']
        required_params = data.get('required_parameters', [])
        optional_params = data.get('optional_parameters', [])
        mapping_id = data.get('id')

        return cls(intent_type, mcp_tool, required_params, optional_params, mapping_id)


# Predefined tool mappings for the supported intents
PREDEFINED_MAPPINGS = {
    IntentType.ADD_TASK: ToolMapping(
        intent_type=IntentType.ADD_TASK,
        mcp_tool="add_task",
        required_parameters=["task_content"],
        optional_parameters=["due_date", "priority", "tags"]
    ),
    IntentType.LIST_TASKS: ToolMapping(
        intent_type=IntentType.LIST_TASKS,
        mcp_tool="list_tasks",
        optional_parameters=["filter", "sort_by", "sort_order", "limit"]
    ),
    IntentType.COMPLETE_TASK: ToolMapping(
        intent_type=IntentType.COMPLETE_TASK,
        mcp_tool="complete_task",
        required_parameters=["task_id"]
    ),
    IntentType.DELETE_TASK: ToolMapping(
        intent_type=IntentType.DELETE_TASK,
        mcp_tool="delete_task",
        required_parameters=["task_id"]
    ),
    IntentType.UPDATE_TASK: ToolMapping(
        intent_type=IntentType.UPDATE_TASK,
        mcp_tool="update_task",
        required_parameters=["task_id", "updates"]
    )
}