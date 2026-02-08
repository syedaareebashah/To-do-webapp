"""
update_task MCP tool for the Todo AI Chatbot System.

This module implements the update_task MCP tool for modifying existing tasks.
"""

from typing import Dict, Any
from src.mcp_server.server import mcp_server


async def update_task(user_id: str, task_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP tool to update a task.

    Args:
        user_id (str): ID of the user who owns the task
        task_id (str): ID of the task to update
        updates (Dict[str, Any]): Fields to update

    Returns:
        Dict[str, Any]: Result of the operation
    """
    # Call the method from the MCP server instance
    return await mcp_server.update_task(
        user_id=user_id,
        task_id=task_id,
        updates=updates
    )