"""
UPDATE_TASK Tool Wrapper for Todo AI Chatbot Agent

This module wraps the UPDATE_TASK MCP tool functionality.
"""

from typing import Dict, Any
from ..interfaces.mcp_tool_interface import MCPTOOLInterface
from ..config.logging_config import logger


class UpdateTaskWrapper:
    """
    Wrapper for the UPDATE_TASK MCP tool.
    """

    def __init__(self, mcp_interface: MCPTOOLInterface):
        """
        Initialize the UPDATE_TASK wrapper.

        Args:
            mcp_interface (MCPTOOLInterface): The MCP tool interface
        """
        self.mcp_interface = mcp_interface

    def execute(self, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the UPDATE_TASK tool with the given task ID and updates.

        Args:
            task_id (str): The ID of the task to update
            updates (Dict[str, Any]): Dictionary of fields to update

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        logger.info(f"Executing UPDATE_TASK tool for task ID: {task_id} with updates: {updates}")

        # Prepare parameters for the tool
        parameters = {
            "task_id": task_id,
            "updates": updates
        }

        # Execute the tool through the MCP interface
        result = self.mcp_interface.execute_tool("update_task", parameters)

        logger.info(f"UPDATE_TASK tool result: {result}")

        return result

    def execute_with_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the UPDATE_TASK tool with a dictionary of parameters.

        Args:
            params (Dict[str, Any]): Dictionary of parameters for the tool

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        task_id = params.get("task_id")
        updates = params.get("updates")

        if not task_id:
            return {
                "success": False,
                "error": "Missing required parameter: task_id",
                "message": "Task ID is required to update a task"
            }

        if not updates:
            return {
                "success": False,
                "error": "Missing required parameter: updates",
                "message": "Updates are required to update a task"
            }

        return self.execute(task_id, updates)

    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate the parameters for the UPDATE_TASK tool.

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

        if "updates" not in params or not params["updates"]:
            return False, "updates is required and cannot be empty"

        updates = params["updates"]
        if not isinstance(updates, dict):
            return False, "updates must be a dictionary"

        # Validate update fields
        valid_fields = ["content", "due_date", "priority", "status"]
        for field in updates:
            if field not in valid_fields:
                return False, f"Field '{field}' is not a valid update field. Valid fields are: {valid_fields}"

        # Validate specific field values
        if "priority" in updates:
            priority = updates["priority"]
            if priority not in ["low", "medium", "high"]:
                return False, f"priority must be one of: low, medium, high, got: {priority}"

        if "status" in updates:
            status = updates["status"]
            if status not in ["pending", "completed"]:
                return False, f"status must be one of: pending, completed, got: {status}"

        if "due_date" in updates:
            due_date = updates["due_date"]
            if not isinstance(due_date, str):
                return False, "due_date must be a string"

        if "content" in updates:
            content = updates["content"]
            if not isinstance(content, str) or len(content.strip()) == 0:
                return False, "content must be a non-empty string"

        return True, "Parameters are valid"