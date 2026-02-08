"""
Validation Utilities for Todo AI Chatbot System

This module provides validation functions for various data types and formats.
"""

from typing import Any, Dict, List, Union
from datetime import datetime
import re
from uuid import UUID


def validate_user_id(user_id: str) -> bool:
    """
    Validate that a user ID is in the correct format.

    Args:
        user_id (str): The user ID to validate

    Returns:
        bool: True if the user ID is valid, False otherwise
    """
    if not user_id or not isinstance(user_id, str):
        return False

    # Check if it's a valid UUID string
    try:
        UUID(user_id)
        return True
    except ValueError:
        # If not a UUID, check if it's a valid string format
        # Allow alphanumeric characters, underscores, and hyphens
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, user_id))


def validate_task_content(content: str) -> tuple[bool, str]:
    """
    Validate task content.

    Args:
        content (str): The task content to validate

    Returns:
        tuple[bool, str]: Tuple of (is_valid, error_message)
    """
    if not content or not isinstance(content, str):
        return False, "Task content must be a non-empty string"

    stripped_content = content.strip()
    if not stripped_content:
        return False, "Task content cannot be just whitespace"

    if len(stripped_content) > 500:
        return False, "Task content must be 500 characters or less"

    return True, "Valid"


def validate_task_status(status: str) -> bool:
    """
    Validate that a task status is one of the allowed values.

    Args:
        status (str): The task status to validate

    Returns:
        bool: True if the status is valid, False otherwise
    """
    if not status or not isinstance(status, str):
        return False

    valid_statuses = ['pending', 'completed']
    return status.lower() in valid_statuses


def validate_task_priority(priority: str) -> bool:
    """
    Validate that a task priority is one of the allowed values.

    Args:
        priority (str): The task priority to validate

    Returns:
        bool: True if the priority is valid, False otherwise
    """
    if not priority or not isinstance(priority, str):
        return False

    valid_priorities = ['low', 'medium', 'high']
    return priority.lower() in valid_priorities


def validate_conversation_id(conversation_id: str) -> bool:
    """
    Validate that a conversation ID is in the correct format.

    Args:
        conversation_id (str): The conversation ID to validate

    Returns:
        bool: True if the conversation ID is valid, False otherwise
    """
    if not conversation_id or not isinstance(conversation_id, str):
        return False

    # Check if it's a valid UUID string
    try:
        UUID(conversation_id)
        return True
    except ValueError:
        return False


def validate_task_id(task_id: str) -> bool:
    """
    Validate that a task ID is in the correct format.

    Args:
        task_id (str): The task ID to validate

    Returns:
        bool: True if the task ID is valid, False otherwise
    """
    if not task_id or not isinstance(task_id, str):
        return False

    # Check if it's a valid UUID string
    try:
        UUID(task_id)
        return True
    except ValueError:
        # Also allow task IDs in the format "task_{uuid}"
        pattern = r'^task_[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'
        return bool(re.match(pattern, task_id))


def validate_datetime_format(dt_str: str) -> bool:
    """
    Validate that a string is in a valid datetime format.

    Args:
        dt_str (str): The datetime string to validate

    Returns:
        bool: True if the datetime string is valid, False otherwise
    """
    if not dt_str or not isinstance(dt_str, str):
        return False

    # Try ISO format first
    try:
        datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return True
    except ValueError:
        pass

    # Try other common formats
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%fZ"
    ]

    for fmt in formats:
        try:
            datetime.strptime(dt_str, fmt)
            return True
        except ValueError:
            continue

    return False


def validate_email(email: str) -> bool:
    """
    Validate that a string is in a valid email format.

    Args:
        email (str): The email string to validate

    Returns:
        bool: True if the email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> bool:
    """
    Validate that a username is in the correct format.

    Args:
        username (str): The username to validate

    Returns:
        bool: True if the username is valid, False otherwise
    """
    if not username or not isinstance(username, str):
        return False

    # Username should be 3-50 characters, alphanumeric with underscores and hyphens
    pattern = r'^[a-zA-Z0-9_-]{3,50}$'
    return bool(re.match(pattern, username))


def validate_message_role(role: str) -> bool:
    """
    Validate that a message role is one of the allowed values.

    Args:
        role (str): The message role to validate

    Returns:
        bool: True if the role is valid, False otherwise
    """
    if not role or not isinstance(role, str):
        return False

    valid_roles = ['user', 'assistant']
    return role.lower() in valid_roles


def validate_tool_call(tool_call: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate that a tool call dictionary has the required structure.

    Args:
        tool_call (Dict[str, Any]): The tool call to validate

    Returns:
        tuple[bool, str]: Tuple of (is_valid, error_message)
    """
    if not isinstance(tool_call, dict):
        return False, "Tool call must be a dictionary"

    required_keys = ['tool_name', 'arguments']
    for key in required_keys:
        if key not in tool_call:
            return False, f"Missing required key: {key}"

    if not isinstance(tool_call['tool_name'], str) or not tool_call['tool_name'].strip():
        return False, "tool_name must be a non-empty string"

    if not isinstance(tool_call['arguments'], dict):
        return False, "arguments must be a dictionary"

    return True, "Valid"


def validate_chat_request(request_data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a chat request dictionary.

    Args:
        request_data (Dict[str, Any]): The chat request to validate

    Returns:
        tuple[bool, str]: Tuple of (is_valid, error_message)
    """
    if not isinstance(request_data, dict):
        return False, "Request data must be a dictionary"

    # Check for required 'message' field
    if 'message' not in request_data:
        return False, "Missing required field: message"

    message = request_data['message']
    if not isinstance(message, str) or not message.strip():
        return False, "Message must be a non-empty string"

    if len(message.strip()) > 2000:
        return False, "Message must be 2000 characters or less"

    # Validate conversation_id if provided
    if 'conversation_id' in request_data:
        conv_id = request_data['conversation_id']
        if conv_id is not None:
            if not isinstance(conv_id, str) or not validate_conversation_id(conv_id):
                return False, "conversation_id must be a valid UUID string if provided"

    return True, "Valid"


def validate_task_request(request_data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate a task creation/update request dictionary.

    Args:
        request_data (Dict[str, Any]): The task request to validate

    Returns:
        tuple[bool, str]: Tuple of (is_valid, error_message)
    """
    if not isinstance(request_data, dict):
        return False, "Request data must be a dictionary"

    # Check for required 'content' field
    if 'content' not in request_data:
        return False, "Missing required field: content"

    content = request_data['content']
    is_valid, error_msg = validate_task_content(content)
    if not is_valid:
        return False, error_msg

    # Validate optional 'due_date' field
    if 'due_date' in request_data and request_data['due_date'] is not None:
        if not isinstance(request_data['due_date'], str) or not validate_datetime_format(request_data['due_date']):
            return False, "due_date must be a valid datetime string if provided"

    # Validate optional 'priority' field
    if 'priority' in request_data and request_data['priority'] is not None:
        if not isinstance(request_data['priority'], str) or not validate_task_priority(request_data['priority']):
            return False, "priority must be one of: low, medium, high if provided"

    # Validate optional 'status' field
    if 'status' in request_data and request_data['status'] is not None:
        if not isinstance(request_data['status'], str) or not validate_task_status(request_data['status']):
            return False, "status must be one of: pending, completed if provided"

    return True, "Valid"


def sanitize_input(user_input: str) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.

    Args:
        user_input (str): The user input to sanitize

    Returns:
        str: Sanitized input
    """
    if not isinstance(user_input, str):
        return ""

    # Remove null bytes and control characters (except common whitespace)
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', user_input)

    # Additional sanitization could be added here as needed
    # For example, removing script tags, etc.

    return sanitized


def validate_user_isolation(user_id_1: str, user_id_2: str) -> bool:
    """
    Validate that two user IDs are the same (for user isolation checks).

    Args:
        user_id_1 (str): First user ID
        user_id_2 (str): Second user ID

    Returns:
        bool: True if the user IDs match, False otherwise
    """
    return user_id_1 == user_id_2


def validate_pagination_params(skip: int, limit: int) -> tuple[bool, str]:
    """
    Validate pagination parameters.

    Args:
        skip (int): Number of records to skip
        limit (int): Maximum number of records to return

    Returns:
        tuple[bool, str]: Tuple of (is_valid, error_message)
    """
    if not isinstance(skip, int) or skip < 0:
        return False, "skip must be a non-negative integer"

    if not isinstance(limit, int) or limit <= 0 or limit > 100:
        return False, "limit must be a positive integer between 1 and 100"

    return True, "Valid"