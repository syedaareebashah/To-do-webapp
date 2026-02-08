"""
Validation utilities for the Todo AI Chatbot System MCP Server.

This module provides validation functions for MCP tools and their inputs.
"""

from typing import Any, Dict, List
from src.models.task import TaskPriority, TaskStatus


def validate_user_id(user_id: str) -> bool:
    """
    Validate the user ID format.

    Args:
        user_id (str): User ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not user_id or not isinstance(user_id, str):
        return False

    # Basic validation: user_id should be a non-empty string
    # In a real implementation, this would check for UUID format or other specific format
    return len(user_id.strip()) > 0


def validate_task_id(task_id: str) -> bool:
    """
    Validate the task ID format.

    Args:
        task_id (str): Task ID to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not task_id or not isinstance(task_id, str):
        return False

    # Basic validation: task_id should be a non-empty string
    # In a real implementation, this would check for UUID format or other specific format
    return len(task_id.strip()) > 0


def validate_task_content(content: str) -> bool:
    """
    Validate task content.

    Args:
        content (str): Task content to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not content or not isinstance(content, str):
        return False

    content = content.strip()
    return 0 < len(content) <= 500  # Max length is 500 as defined in the model


def validate_priority(priority: str) -> bool:
    """
    Validate task priority.

    Args:
        priority (str): Priority to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        TaskPriority(priority.lower())
        return True
    except ValueError:
        return False


def validate_status(status: str) -> bool:
    """
    Validate task status.

    Args:
        status (str): Status to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        TaskStatus(status.lower())
        return True
    except ValueError:
        return False


def validate_due_date_format(due_date: str) -> bool:
    """
    Validate due date format (ISO 8601 format).

    Args:
        due_date (str): Due date to validate

    Returns:
        bool: True if valid, False otherwise
    """
    if not due_date or not isinstance(due_date, str):
        return False

    from datetime import datetime
    try:
        # Try to parse the date in ISO format
        datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def validate_task_parameters(params: Dict[str, Any]) -> Dict[str, str]:
    """
    Validate task-related parameters and return any errors.

    Args:
        params (Dict[str, Any]): Parameters to validate

    Returns:
        Dict[str, str]: Dictionary of validation errors (field -> error message)
    """
    errors = {}

    # Validate content
    if "content" in params:
        if not validate_task_content(params["content"]):
            errors["content"] = "Content must be a non-empty string with max length 500"

    # Validate priority
    if "priority" in params:
        if not validate_priority(params["priority"]):
            errors["priority"] = f"Priority must be one of: {[p.value for p in TaskPriority]}"

    # Validate status
    if "status" in params:
        if not validate_status(params["status"]):
            errors["status"] = f"Status must be one of: {[s.value for s in TaskStatus]}"

    # Validate due date
    if "due_date" in params and params["due_date"]:
        if not validate_due_date_format(params["due_date"]):
            errors["due_date"] = "Due date must be in ISO 8601 format"

    # Validate user_id
    if "user_id" in params:
        if not validate_user_id(params["user_id"]):
            errors["user_id"] = "User ID must be a non-empty string"

    # Validate task_id
    if "task_id" in params:
        if not validate_task_id(params["task_id"]):
            errors["task_id"] = "Task ID must be a non-empty string"

    return errors


def validate_list_filter(filter_type: str) -> bool:
    """
    Validate list filter type.

    Args:
        filter_type (str): Filter type to validate

    Returns:
        bool: True if valid, False otherwise
    """
    valid_filters = ["all", "pending", "completed", "overdue"]
    return filter_type.lower() in valid_filters


def validate_sort_params(sort_by: str, sort_order: str) -> Dict[str, str]:
    """
    Validate sort parameters.

    Args:
        sort_by (str): Field to sort by
        sort_order (str): Sort order

    Returns:
        Dict[str, str]: Dictionary of validation errors
    """
    errors = {}

    valid_sort_fields = ["created_at", "due_date", "priority"]
    if sort_by not in valid_sort_fields:
        errors["sort_by"] = f"Sort by must be one of: {valid_sort_fields}"

    valid_sort_orders = ["asc", "desc"]
    if sort_order not in valid_sort_orders:
        errors["sort_order"] = f"Sort order must be one of: {valid_sort_orders}"

    return errors


def sanitize_input(value: str) -> str:
    """
    Sanitize input by removing potentially dangerous characters.

    Args:
        value (str): Input value to sanitize

    Returns:
        str: Sanitized input
    """
    if not isinstance(value, str):
        return value

    # Remove potentially dangerous characters but preserve legitimate ones
    # This is a basic sanitization - in production, use a proper sanitization library
    sanitized = value.strip()

    # Prevent basic injection attempts
    dangerous_chars = ["<script", "javascript:", "vbscript:", "onerror", "onclick"]
    for char in dangerous_chars:
        if char.lower() in sanitized.lower():
            sanitized = sanitized.replace(char, "", 1)

    return sanitized