"""
delete_task MCP tool for the Todo AI Chatbot System.

This module implements the delete_task MCP tool for removing tasks.
"""

from typing import Dict, Any
from src.mcp_server.server import mcp_server


async def delete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    MCP tool to delete a task.

    Args:
        user_id (str): ID of the user who owns the task
        task_id (str): ID of the task to delete

    Returns:
        Dict[str, Any]: Result of the operation
    """
    # Call the method from the MCP server instance
    return await mcp_server.delete_task(
        user_id=user_id,
        task_id=task_id
    )