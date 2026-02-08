"""
ADD_TASK Tool Wrapper for Todo AI Chatbot Agent

This module wraps the ADD_TASK MCP tool functionality.
"""

from typing import Dict, Any
from ..interfaces.mcp_tool_interface import MCPTOOLInterface
from ..config.logging_config import logger


class AddTaskWrapper:
    """
    Wrapper for the ADD_TASK MCP tool.
    """

    def __init__(self, mcp_interface: MCPTOOLInterface):
        """
        Initialize the ADD_TASK wrapper.

        Args:
            mcp_interface (MCPTOOLInterface): The MCP tool interface
        """
        self.mcp_interface = mcp_interface

    def execute(self, task_content: str, due_date: str = None, priority: str = "medium", tags: list = None) -> Dict[str, Any]:
        """
        Execute the ADD_TASK tool with the given parameters.

        Args:
            task_content (str): The content of the task to add
            due_date (str, optional): The due date for the task
            priority (str, optional): The priority of the task (default: "medium")
            tags (list, optional): Tags for the task

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        logger.info(f"Executing ADD_TASK tool with content: {task_content}")

        # Prepare parameters for the tool
        parameters = {
            "task_content": task_content
        }

        # Add optional parameters if provided
        if due_date:
            parameters["due_date"] = due_date
        if priority:
            parameters["priority"] = priority
        if tags:
            parameters["tags"] = tags

        # Execute the tool through the MCP interface
        result = self.mcp_interface.execute_tool("add_task", parameters)

        logger.info(f"ADD_TASK tool result: {result}")

        return result

    def execute_with_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the ADD_TASK tool with a dictionary of parameters.

        Args:
            params (Dict[str, Any]): Dictionary of parameters for the tool

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        task_content = params.get("task_content")
        if not task_content:
            return {
                "success": False,
                "error": "Missing required parameter: task_content",
                "message": "Task content is required to add a task"
            }

        due_date = params.get("due_date")
        priority = params.get("priority", "medium")
        tags = params.get("tags")

        return self.execute(task_content, due_date, priority, tags)

    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate the parameters for the ADD_TASK tool.

        Args:
            params (Dict[str, Any]): Dictionary of parameters to validate

        Returns:
            tuple[bool, str]: Tuple of (is_valid, error_message)
        """
        if "task_content" not in params or not params["task_content"]:
            return False, "task_content is required and cannot be empty"

        task_content = params["task_content"]
        if not isinstance(task_content, str) or len(task_content.strip()) == 0:
            return False, "task_content must be a non-empty string"

        if "priority" in params:
            priority = params["priority"]
            if priority not in ["low", "medium", "high"]:
                return False, f"priority must be one of: low, medium, high, got: {priority}"

        if "due_date" in params:
            # Basic validation - in a real implementation, you'd want more thorough date validation
            due_date = params["due_date"]
            if not isinstance(due_date, str):
                return False, "due_date must be a string"

        if "tags" in params:
            tags = params["tags"]
            if not isinstance(tags, list):
                return False, "tags must be a list"
            for tag in tags:
                if not isinstance(tag, str):
                    return False, f"All tags must be strings, found: {type(tag)}"

        return True, "Parameters are valid"