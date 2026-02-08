"""
Error Handlers for MCP Server in Todo AI Chatbot System

This module handles errors specifically for the MCP tools.
"""

from typing import Dict, Any
from src.api.responses.error_response import ErrorResponse
from src.config.logging_config import logger


class MCPServerErrorHandler:
    """
    Error handler for the MCP server and its tools.
    """

    @staticmethod
    def handle_task_not_found(task_id: str, user_id: str) -> ErrorResponse:
        """
        Handle the error when a task is not found.

        Args:
            task_id (str): The ID of the task that wasn't found
            user_id (str): The ID of the user requesting the task

        Returns:
            ErrorResponse: Formatted error response
        """
        error_msg = f"Task with ID {task_id} not found for user {user_id}"
        logger.warning(f"MCP Tool Error - Task Not Found: {error_msg}")

        return ErrorResponse(
            success=False,
            error_code="TASK_NOT_FOUND",
            message=error_msg,
            details={
                "task_id": task_id,
                "user_id": user_id
            }
        )

    @staticmethod
    def handle_invalid_task_data(error_details: str) -> ErrorResponse:
        """
        Handle the error when task data is invalid.

        Args:
            error_details (str): Details about the validation error

        Returns:
            ErrorResponse: Formatted error response
        """
        error_msg = f"Invalid task data provided: {error_details}"
        logger.warning(f"MCP Tool Error - Invalid Task Data: {error_msg}")

        return ErrorResponse(
            success=False,
            error_code="INVALID_TASK_DATA",
            message=error_msg,
            details={
                "validation_error": error_details
            }
        )

    @staticmethod
    def handle_permission_denied(task_id: str, user_id: str) -> ErrorResponse:
        """
        Handle the error when a user doesn't have permission to access a task.

        Args:
            task_id (str): The ID of the task the user tried to access
            user_id (str): The ID of the user requesting access

        Returns:
            ErrorResponse: Formatted error response
        """
        error_msg = f"Permission denied: User {user_id} cannot access task {task_id}"
        logger.warning(f"MCP Tool Error - Permission Denied: {error_msg}")

        return ErrorResponse(
            success=False,
            error_code="PERMISSION_DENIED",
            message=error_msg,
            details={
                "task_id": task_id,
                "user_id": user_id
            }
        )

    @staticmethod
    def handle_database_connection_error(error_details: str) -> ErrorResponse:
        """
        Handle the error when there's a database connection issue.

        Args:
            error_details (str): Details about the database error

        Returns:
            ErrorResponse: Formatted error response
        """
        error_msg = f"Database connection error: {error_details}"
        logger.error(f"MCP Tool Error - Database Connection: {error_msg}")

        return ErrorResponse(
            success=False,
            error_code="DATABASE_CONNECTION_ERROR",
            message="A database error occurred. Please try again later.",
            details={
                "error_details": error_details
            }
        )

    @staticmethod
    def handle_tool_execution_error(tool_name: str, error_details: str) -> ErrorResponse:
        """
        Handle the error when an MCP tool fails to execute.

        Args:
            tool_name (str): Name of the tool that failed
            error_details (str): Details about the execution error

        Returns:
            ErrorResponse: Formatted error response
        """
        error_msg = f"Failed to execute tool '{tool_name}': {error_details}"
        logger.error(f"MCP Tool Error - Execution Failed: {error_msg}")

        return ErrorResponse(
            success=False,
            error_code="TOOL_EXECUTION_ERROR",
            message=f"The tool '{tool_name}' failed to execute. Please try again.",
            details={
                "tool_name": tool_name,
                "error_details": error_details
            }
        )

    @staticmethod
    def handle_conversation_not_found(conversation_id: str, user_id: str) -> ErrorResponse:
        """
        Handle the error when a conversation is not found.

        Args:
            conversation_id (str): The ID of the conversation that wasn't found
            user_id (str): The ID of the user requesting the conversation

        Returns:
            ErrorResponse: Formatted error response
        """
        error_msg = f"Conversation with ID {conversation_id} not found for user {user_id}"
        logger.warning(f"MCP Tool Error - Conversation Not Found: {error_msg}")

        return ErrorResponse(
            success=False,
            error_code="CONVERSATION_NOT_FOUND",
            message=error_msg,
            details={
                "conversation_id": conversation_id,
                "user_id": user_id
            }
        )

    @staticmethod
    def handle_unexpected_error(error_details: str) -> ErrorResponse:
        """
        Handle unexpected errors in MCP tools.

        Args:
            error_details (str): Details about the unexpected error

        Returns:
            ErrorResponse: Formatted error response
        """
        error_msg = f"An unexpected error occurred in the MCP tool: {error_details}"
        logger.error(f"MCP Tool Error - Unexpected: {error_msg}")

        return ErrorResponse(
            success=False,
            error_code="UNEXPECTED_ERROR",
            message="An unexpected error occurred. Our team has been notified.",
            details={
                "error_details": error_details
            }
        )


# Singleton instance for convenience
mcp_error_handler = MCPServerErrorHandler()


def handle_mcp_tool_error(error_type: str, **kwargs) -> ErrorResponse:
    """
    Convenience function to handle different types of MCP tool errors.

    Args:
        error_type (str): Type of error to handle
        **kwargs: Additional arguments specific to the error type

    Returns:
        ErrorResponse: Formatted error response
    """
    if error_type == "TASK_NOT_FOUND":
        return mcp_error_handler.handle_task_not_found(
            kwargs.get("task_id"),
            kwargs.get("user_id")
        )
    elif error_type == "INVALID_TASK_DATA":
        return mcp_error_handler.handle_invalid_task_data(
            kwargs.get("error_details", "")
        )
    elif error_type == "PERMISSION_DENIED":
        return mcp_error_handler.handle_permission_denied(
            kwargs.get("task_id"),
            kwargs.get("user_id")
        )
    elif error_type == "DATABASE_CONNECTION_ERROR":
        return mcp_error_handler.handle_database_connection_error(
            kwargs.get("error_details", "")
        )
    elif error_type == "TOOL_EXECUTION_ERROR":
        return mcp_error_handler.handle_tool_execution_error(
            kwargs.get("tool_name", "unknown"),
            kwargs.get("error_details", "")
        )
    elif error_type == "CONVERSATION_NOT_FOUND":
        return mcp_error_handler.handle_conversation_not_found(
            kwargs.get("conversation_id"),
            kwargs.get("user_id")
        )
    else:
        return mcp_error_handler.handle_unexpected_error(
            kwargs.get("error_details", "Unknown error occurred")
        )