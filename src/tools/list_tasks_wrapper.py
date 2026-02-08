"""
LIST_TASKS Tool Wrapper for Todo AI Chatbot Agent

This module wraps the LIST_TASKS MCP tool functionality.
"""

from typing import Dict, Any
from ..interfaces.mcp_tool_interface import MCPTOOLInterface
from ..config.logging_config import logger


class ListTasksWrapper:
    """
    Wrapper for the LIST_TASKS MCP tool.
    """

    def __init__(self, mcp_interface: MCPTOOLInterface):
        """
        Initialize the LIST_TASKS wrapper.

        Args:
            mcp_interface (MCPTOOLInterface): The MCP tool interface
        """
        self.mcp_interface = mcp_interface

    def execute(self, filter_type: str = "all", sort_by: str = "created_at", sort_order: str = "asc", limit: int = 50) -> Dict[str, Any]:
        """
        Execute the LIST_TASKS tool with the given parameters.

        Args:
            filter_type (str, optional): Type of tasks to filter (default: "all")
            sort_by (str, optional): Field to sort by (default: "created_at")
            sort_order (str, optional): Sort order - "asc" or "desc" (default: "asc")
            limit (int, optional): Maximum number of tasks to return (default: 50)

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        logger.info(f"Executing LIST_TASKS tool with filter: {filter_type}, sort: {sort_by} {sort_order}")

        # Prepare parameters for the tool
        parameters = {
            "filter": filter_type,
            "sort_by": sort_by,
            "sort_order": sort_order,
            "limit": min(limit, 100)  # Cap at 100 for safety
        }

        # Execute the tool through the MCP interface
        result = self.mcp_interface.execute_tool("list_tasks", parameters)

        logger.info(f"LIST_TASKS tool result: {result}")

        return result

    def execute_with_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the LIST_TASKS tool with a dictionary of parameters.

        Args:
            params (Dict[str, Any]): Dictionary of parameters for the tool

        Returns:
            Dict[str, Any]: Result from the tool execution
        """
        filter_type = params.get("filter", "all")
        sort_by = params.get("sort_by", "created_at")
        sort_order = params.get("sort_order", "asc")
        limit = params.get("limit", 50)

        return self.execute(filter_type, sort_by, sort_order, limit)

    def validate_params(self, params: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate the parameters for the LIST_TASKS tool.

        Args:
            params (Dict[str, Any]): Dictionary of parameters to validate

        Returns:
            tuple[bool, str]: Tuple of (is_valid, error_message)
        """
        valid_filters = ["all", "pending", "completed", "overdue"]
        if "filter" in params:
            filter_val = params["filter"]
            if filter_val not in valid_filters:
                return False, f"filter must be one of: {valid_filters}, got: {filter_val}"

        valid_sort_fields = ["created_at", "due_date", "priority"]
        if "sort_by" in params:
            sort_field = params["sort_by"]
            if sort_field not in valid_sort_fields:
                return False, f"sort_by must be one of: {valid_sort_fields}, got: {sort_field}"

        valid_sort_orders = ["asc", "desc"]
        if "sort_order" in params:
            sort_order = params["sort_order"]
            if sort_order not in valid_sort_orders:
                return False, f"sort_order must be one of: {valid_sort_orders}, got: {sort_order}"

        if "limit" in params:
            limit = params["limit"]
            if not isinstance(limit, int) or limit <= 0 or limit > 100:
                return False, f"limit must be an integer between 1 and 100, got: {limit}"

        return True, "Parameters are valid"