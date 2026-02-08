"""
Tool Mapper for Todo AI Chatbot Agent

This module maps intents to appropriate MCP tools.
"""

from typing import Dict, Any, Optional
from ..models.intent import Intent, IntentType
from ..models.tool_mapping import PREDEFINED_MAPPINGS, ToolMapping


class ToolMappingResult:
    """
    Represents the result of mapping an intent to a tool.
    """
    def __init__(self, tool_name: str, parameters: Dict[str, Any], tool_mapping: ToolMapping):
        self.tool_name = tool_name
        self.parameters = parameters
        self.tool_mapping = tool_mapping

    def requires_tool_chaining(self) -> bool:
        """
        Check if this tool mapping requires chaining with other tools.

        Returns:
            bool: True if tool chaining is required, False otherwise
        """
        return self.tool_mapping.requires_tool_chaining()


class ToolMapper:
    """
    Maps intents to appropriate MCP tools based on predefined mappings.
    """

    def __init__(self):
        """
        Initialize the tool mapper with predefined mappings.
        """
        self.mappings = PREDEFINED_MAPPINGS

    def map_intent_to_tool(self, intent: Intent) -> ToolMappingResult:
        """
        Map an intent to the appropriate MCP tool.

        Args:
            intent (Intent): The intent to map to a tool

        Returns:
            ToolMappingResult: The result of mapping the intent to a tool
        """
        # Get the mapping for this intent type
        mapping = self.mappings.get(intent.type)

        if not mapping:
            # If no mapping exists, raise an exception
            raise ValueError(f"No tool mapping found for intent type: {intent.type.value}")

        # Validate the parameters against the mapping requirements
        required_params = mapping.required_parameters
        provided_params = intent.parameters

        # Check if all required parameters are provided
        missing_params = []
        for param in required_params:
            if param not in provided_params:
                missing_params.append(param)

        if missing_params:
            raise ValueError(f"Missing required parameters for {intent.type.value}: {missing_params}")

        # Validate that provided parameters match the mapping
        if not mapping.validate_parameters(provided_params):
            invalid_params = set(provided_params.keys()) - set(mapping.get_all_parameters())
            raise ValueError(f"Invalid parameters provided for {intent.type.value}: {list(invalid_params)}")

        # Determine the tool name based on the mapping
        tool_name = mapping.mcp_tool

        # Prepare the parameters for the tool
        tool_params = self._prepare_tool_parameters(intent, mapping)

        return ToolMappingResult(tool_name, tool_params, mapping)

    def _prepare_tool_parameters(self, intent: Intent, mapping: ToolMapping) -> Dict[str, Any]:
        """
        Prepare the parameters for the tool based on the intent and mapping.

        Args:
            intent (Intent): The intent with parameters
            mapping (ToolMapping): The tool mapping

        Returns:
            Dict[str, Any]: Prepared parameters for the tool
        """
        # Start with the intent's parameters
        tool_params = intent.parameters.copy()

        # For certain intent types, we may need to transform parameters
        if intent.type == IntentType.ADD_TASK:
            # For add_task, ensure task_content is properly formatted
            if 'task_content' in tool_params:
                # Clean up the task content if needed
                content = tool_params['task_content'].strip()
                tool_params['task_content'] = content

        elif intent.type == IntentType.COMPLETE_TASK or intent.type == IntentType.DELETE_TASK:
            # For complete/delete tasks, ensure task_id is properly formatted
            if 'task_id' in tool_params:
                task_id = tool_params['task_id']
                # Ensure task_id is in the expected format
                if not task_id.startswith('task_'):
                    # If it's just a number, format it properly
                    if task_id.isdigit():
                        tool_params['task_id'] = f'task_{task_id}'
                    else:
                        # If it's some other format, try to normalize
                        tool_params['task_id'] = f'task_{task_id}'

        elif intent.type == IntentType.UPDATE_TASK:
            # For update_task, ensure updates are properly formatted
            if 'updates' in tool_params and isinstance(tool_params['updates'], dict):
                # Ensure the updates are in the correct format
                updates = tool_params['updates']
                tool_params['updates'] = updates

        elif intent.type == IntentType.LIST_TASKS:
            # For list_tasks, ensure filters are properly formatted
            if 'filter' in tool_params:
                # Validate the filter value
                valid_filters = ['all', 'pending', 'completed', 'overdue']
                if tool_params['filter'] not in valid_filters:
                    # Default to 'all' if invalid filter provided
                    tool_params['filter'] = 'all'

        return tool_params

    def register_custom_mapping(self, intent_type: IntentType, mapping: ToolMapping):
        """
        Register a custom tool mapping for a specific intent type.

        Args:
            intent_type (IntentType): The intent type to map
            mapping (ToolMapping): The tool mapping to register
        """
        self.mappings[intent_type] = mapping

    def get_mapping(self, intent_type: IntentType) -> Optional[ToolMapping]:
        """
        Get the tool mapping for a specific intent type.

        Args:
            intent_type (IntentType): The intent type

        Returns:
            Optional[ToolMapping]: The tool mapping if found, None otherwise
        """
        return self.mappings.get(intent_type)

    def validate_intent_parameters(self, intent: Intent) -> bool:
        """
        Validate that the intent's parameters match the expected mapping requirements.

        Args:
            intent (Intent): The intent to validate

        Returns:
            bool: True if parameters are valid, False otherwise
        """
        mapping = self.get_mapping(intent.type)
        if not mapping:
            return False

        return mapping.validate_parameters(intent.parameters)

    def get_required_parameters(self, intent_type: IntentType) -> list:
        """
        Get the required parameters for a specific intent type.

        Args:
            intent_type (IntentType): The intent type

        Returns:
            list: List of required parameter names
        """
        mapping = self.get_mapping(intent_type)
        if mapping:
            return mapping.required_parameters
        return []

    def get_optional_parameters(self, intent_type: IntentType) -> list:
        """
        Get the optional parameters for a specific intent type.

        Args:
            intent_type (IntentType): The intent type

        Returns:
            list: List of optional parameter names
        """
        mapping = self.get_mapping(intent_type)
        if mapping:
            return mapping.optional_parameters
        return []