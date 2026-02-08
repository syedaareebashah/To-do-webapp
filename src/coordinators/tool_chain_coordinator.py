"""
Tool Chain Coordinator for Todo AI Chatbot Agent

This module coordinates the execution of multiple tools in sequence.
"""

from typing import Dict, Any
from ..models.tool_mapping import ToolMapping
from ..models.conversation_context import ConversationContext
from ..interfaces.mcp_tool_interface import MCPTOOLInterface


class ToolChainCoordinator:
    """
    Coordinates the execution of multiple tools in sequence when needed.
    """

    def __init__(self):
        """
        Initialize the tool chain coordinator.
        """
        self.mcp_interface = MCPTOOLInterface()

    def execute_chain(self, tool_mapping: ToolMapping, conversation_context: ConversationContext) -> Dict[str, Any]:
        """
        Execute a chain of tools based on the tool mapping and conversation context.

        Args:
            tool_mapping (ToolMapping): The tool mapping that requires chaining
            conversation_context (ConversationContext): Context from the conversation

        Returns:
            Dict[str, Any]: Result from the tool chain execution
        """
        # For now, implement a basic chaining mechanism
        # In the future, this could handle complex multi-step operations

        # Example: If we need to list tasks before performing an action on a specific task
        if self._needs_task_listing(tool_mapping, conversation_context):
            # First, list the tasks to get context
            list_result = self.mcp_interface.execute_tool("list_tasks", {"filter": "all", "limit": 10})

            if not list_result.get("success"):
                return list_result

            # Then perform the original action with the context
            return self._execute_with_context(tool_mapping, list_result)

        # Default: execute the tool directly
        return self._execute_directly(tool_mapping)

    def _needs_task_listing(self, tool_mapping: ToolMapping, conversation_context: ConversationContext) -> bool:
        """
        Determine if task listing is needed before executing the tool.

        Args:
            tool_mapping (ToolMapping): The tool mapping to evaluate
            conversation_context (ConversationContext): Context from the conversation

        Returns:
            bool: True if task listing is needed, False otherwise
        """
        # For now, we'll return False as a default
        # This could be enhanced with more sophisticated logic
        return False

    def _execute_with_context(self, tool_mapping: ToolMapping, context_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with additional context from a previous operation.

        Args:
            tool_mapping (ToolMapping): The tool mapping to execute
            context_result (Dict[str, Any]): Result from the previous operation

        Returns:
            Dict[str, Any]: Result from the tool execution with context
        """
        # For now, just execute the tool directly
        # In the future, this could incorporate context from previous operations
        return self._execute_directly(tool_mapping)

    def _execute_directly(self, tool_mapping: ToolMapping) -> Dict[str, Any]:
        """
        Execute a tool directly without additional context.

        Args:
            tool_mapping (ToolMapping): The tool mapping to execute

        Returns:
            Dict[str, Any]: Result from the direct tool execution
        """
        # Extract the tool name and parameters from the mapping
        tool_name = tool_mapping.mcp_tool
        # Note: We don't have parameters in the tool_mapping object directly
        # This would need to be passed separately in a real implementation

        # For now, return an error indicating this is not fully implemented
        return {
            "success": False,
            "error": "NOT_IMPLEMENTED",
            "message": "Direct tool execution without parameters is not implemented in this context"
        }

    def execute_specific_chain(self, chain_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a specific type of tool chain.

        Args:
            chain_type (str): The type of chain to execute
            parameters (Dict[str, Any]): Parameters for the chain

        Returns:
            Dict[str, Any]: Result from the chain execution
        """
        if chain_type == "list_then_act":
            return self._execute_list_then_act_chain(parameters)
        elif chain_type == "validate_then_update":
            return self._execute_validate_then_update_chain(parameters)
        else:
            return {
                "success": False,
                "error": "UNKNOWN_CHAIN_TYPE",
                "message": f"Unknown chain type: {chain_type}"
            }

    def _execute_list_then_act_chain(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a chain that first lists tasks then performs an action.

        Args:
            parameters (Dict[str, Any]): Parameters for the chain

        Returns:
            Dict[str, Any]: Result from the chain execution
        """
        # First, list tasks
        list_params = {
            "filter": parameters.get("filter", "all"),
            "limit": parameters.get("limit", 10)
        }
        list_result = self.mcp_interface.execute_tool("list_tasks", list_params)

        if not list_result.get("success"):
            return list_result

        # Then perform the action on the specified task
        action_params = parameters.get("action_params", {})
        action_tool = parameters.get("action_tool", "")

        if not action_tool:
            return {
                "success": False,
                "error": "MISSING_ACTION_TOOL",
                "message": "Action tool not specified in parameters"
            }

        action_result = self.mcp_interface.execute_tool(action_tool, action_params)

        return {
            "success": action_result.get("success", False),
            "list_result": list_result,
            "action_result": action_result,
            "message": f"Executed {action_tool} after listing tasks"
        }

    def _execute_validate_then_update_chain(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a chain that first validates a task exists then updates it.

        Args:
            parameters (Dict[str, Any]): Parameters for the chain

        Returns:
            Dict[str, Any]: Result from the chain execution
        """
        task_id = parameters.get("task_id")
        updates = parameters.get("updates", {})

        if not task_id:
            return {
                "success": False,
                "error": "MISSING_TASK_ID",
                "message": "Task ID is required for validate-then-update chain"
            }

        # First, try to get the task to validate it exists
        list_params = {
            "filter": "all",
            "limit": 100  # Check all tasks
        }
        list_result = self.mcp_interface.execute_tool("list_tasks", list_params)

        if not list_result.get("success"):
            return list_result

        # Check if the task exists
        tasks = list_result.get("tasks", [])
        task_exists = any(task.get("id") == task_id for task in tasks)

        if not task_exists:
            return {
                "success": False,
                "error": "TASK_NOT_FOUND",
                "message": f"Task with ID {task_id} not found"
            }

        # If the task exists, proceed with the update
        update_params = {
            "task_id": task_id,
            "updates": updates
        }
        update_result = self.mcp_interface.execute_tool("update_task", update_params)

        return update_result