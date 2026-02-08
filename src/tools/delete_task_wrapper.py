"""
DELETE_TASK Tool Wrapper for Todo AI Chatbot Agent

This module wraps the DELETE_TASK MCP tool functionality.
"""

from typing import Dict, Any
from ..interfaces.mcp_tool_interface import MCPTOOLInterface
from ..config.logging_config import logger


class DeleteTaskWrapper:
    """
    Wrapper for the DELETE_TASK MCP tool.
    """

    def __init__(self, mcp_interface: MCPTOOLInterface):
        """
        Initialize the DELETE_TASK wrapper.

        Args:
            mcp_interface (MCPTOOLInterface): The MCP tool interface
        """
        self.mcp_interface = mcp_interface

    def execute(self, task_id: str) -> Dict[str, Any]:
        """
        Execute the DELETE_TASK tool with the given task ID.

        Args:
            task_id (str): The ID of the task to delete

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        logger.info(f"Executing DELETE_TASK tool for task ID: {task_id}")

        # Prepare parameters for the tool
        parameters = {
            "task_id": task_id
        }

        # Execute the tool through the MCP interface
        result = self.mcp_interface.execute_tool("delete_task", parameters)

        logger.info(f"DELETE_TASK tool result: {result}")

        return result

    def execute_with_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the DELETE_TASK tool with a dictionary of parameters.

        Args:
            params (Dict[str, Any]): Dictionary of parameters for the tool

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        task_id = params.get("task_id")
        if not task_id:
            return {
                "success": False,
                "error": "Missing required parameter: task_id",
                "message": "Task ID is required to delete a task"
            }

        return self.execute(task_id)

    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate the parameters for the DELETE_TASK tool.

        Args:
            params (Dict[str, Any]): Dictionary of parameters to validate

        Returns:
            tuple[bool, str]: Tuple of (is_valid, error_message)
        """
        if "task_id" not in params or not params["task_id"]:
            return False, "task_id is required and cannot be empty"

        task_id = params["task_id"]
        if not isinstance(task_id, str) or len(task_id.strip()) == 0:
            return False, "task_id must be a non-empty string"

        return True, "Parameters are valid"