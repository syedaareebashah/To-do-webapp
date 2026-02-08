"""
complete_task MCP tool for the Todo AI Chatbot System.

This module implements the complete_task MCP tool for marking tasks as completed.
"""

from typing import Dict, Any
from src.mcp_server.server import mcp_server


async def complete_task(user_id: str, task_id: str) -> Dict[str, Any]:
    """
    MCP tool to mark a task as completed.

    Args:
        user_id (str): ID of the user who owns the task
        task_id (str): ID of the task to complete

    Returns:
        Dict[str, Any]: Result of the operation
    """
    # Call the method from the MCP server instance
    return await mcp_server.complete_task(
        user_id=user_id,
        task_id=task_id
    )