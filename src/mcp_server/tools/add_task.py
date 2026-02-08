"""
add_task MCP tool for the Todo AI Chatbot System.

This module implements the add_task MCP tool for creating new tasks.
"""

from typing import Dict, Any, Optional
from src.mcp_server.server import mcp_server


async def add_task(user_id: str, content: str, due_date: Optional[str] = None,
                  priority: str = "medium", tags: Optional[list] = None) -> Dict[str, Any]:
    """
    MCP tool to add a new task.

    Args:
        user_id (str): ID of the user creating the task
        content (str): Content/description of the task
        due_date (Optional[str]): Due date for the task (ISO format)
        priority (str): Priority level (low, medium, high)
        tags (Optional[list]): List of tags for the task

    Returns:
        Dict[str, Any]: Result of the operation with task details
    """
    # Call the method from the MCP server instance
    return await mcp_server.add_task(
        user_id=user_id,
        content=content,
        due_date=due_date,
        priority=priority,
        tags=tags
    )