"""
list_tasks MCP tool for the Todo AI Chatbot System.

This module implements the list_tasks MCP tool for retrieving tasks.
"""

from typing import Dict, Any
from src.mcp_server.server import mcp_server


async def list_tasks(user_id: str, filter_type: str = "all",
                    sort_by: str = "created_at", sort_order: str = "asc",
                    limit: int = 50) -> Dict[str, Any]:
    """
    MCP tool to list tasks for a user.

    Args:
        user_id (str): ID of the user whose tasks to list
        filter_type (str): Type of tasks to filter (all, pending, completed, overdue)
        sort_by (str): Field to sort by (created_at, due_date, priority)
        sort_order (str): Sort order (asc, desc)
        limit (int): Maximum number of tasks to return

    Returns:
        Dict[str, Any]: List of tasks and metadata
    """
    # Call the method from the MCP server instance
    return await mcp_server.list_tasks(
        user_id=user_id,
        filter_type=filter_type,
        sort_by=sort_by,
        sort_order=sort_order,
        limit=limit
    )