"""
Logging Utilities for Todo AI Chatbot System

This module provides centralized logging functionality for the application.
"""

import logging
import sys
from datetime import datetime
from typing import Any, Dict
from pathlib import Path
import json
from logging.handlers import RotatingFileHandler


class JSONFormatter(logging.Formatter):
    """
    Custom formatter that outputs logs in JSON format.
    """

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.

        Args:
            record (logging.LogRecord): The log record to format

        Returns:
            str: JSON-formatted log message
        """
        log_entry = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)

        # Add any extra fields
        for key, value in record.__dict__.items():
            if key not in (
                'name', 'msg', 'args', 'levelname', 'levelno', 'pathname',
                'filename', 'module', 'lineno', 'funcName', 'created',
                'msecs', 'relativeCreated', 'thread', 'threadName',
                'processName', 'process', 'getMessage', 'exc_info',
                'exc_text', 'stack_info'
            ):
                log_entry[key] = value

        return json.dumps(log_entry)


def setup_logger(
    name: str = "todo_chatbot",
    level: int = logging.INFO,
    log_file: str = None,
    max_bytes: int = 10 * 1024 * 1024,  # 10 MB
    backup_count: int = 5,
    use_json: bool = True
) -> logging.Logger:
    """
    Set up a logger with the specified configuration.

    Args:
        name (str): Name of the logger
        level (int): Logging level (default: logging.INFO)
        log_file (str, optional): Path to log file (optional)
        max_bytes (int): Maximum size of log file before rotation (default: 10MB)
        backup_count (int): Number of backup files to keep (default: 5)
        use_json (bool): Whether to use JSON formatting (default: True)

    Returns:
        logging.Logger: Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers if logger already has handlers
    if logger.handlers:
        return logger

    # Create formatter
    if use_json:
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Add file handler if log_file is specified
    if log_file:
        # Create directory if it doesn't exist
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str = "todo_chatbot") -> logging.Logger:
    """
    Get a logger instance with the specified name.

    Args:
        name (str): Name of the logger (default: "todo_chatbot")

    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


def log_api_request(
    logger: logging.Logger,
    user_id: str,
    endpoint: str,
    method: str,
    response_status: int,
    response_time_ms: float,
    details: Dict[str, Any] = None
) -> None:
    """
    Log an API request with relevant details.

    Args:
        logger (logging.Logger): Logger instance to use
        user_id (str): ID of the user making the request
        endpoint (str): API endpoint that was called
        method (str): HTTP method used (GET, POST, etc.)
        response_status (int): HTTP response status code
        response_time_ms (float): Time taken to process the request in milliseconds
        details (Dict[str, Any], optional): Additional details to log
    """
    log_data = {
        "event_type": "api_request",
        "user_id": user_id,
        "endpoint": endpoint,
        "method": method,
        "response_status": response_status,
        "response_time_ms": response_time_ms
    }

    if details:
        log_data.update(details)

    logger.info("API request processed", extra=log_data)


def log_mcp_tool_call(
    logger: logging.Logger,
    user_id: str,
    tool_name: str,
    parameters: Dict[str, Any],
    success: bool,
    execution_time_ms: float,
    result: Dict[str, Any] = None
) -> None:
    """
    Log an MCP tool call with relevant details.

    Args:
        logger (logging.Logger): Logger instance to use
        user_id (str): ID of the user who triggered the tool call
        tool_name (str): Name of the MCP tool that was called
        parameters (Dict[str, Any]): Parameters passed to the tool
        success (bool): Whether the tool call was successful
        execution_time_ms (float): Time taken to execute the tool in milliseconds
        result (Dict[str, Any], optional): Result of the tool call
    """
    log_data = {
        "event_type": "mcp_tool_call",
        "user_id": user_id,
        "tool_name": tool_name,
        "parameters": parameters,
        "success": success,
        "execution_time_ms": execution_time_ms
    }

    if result:
        log_data["result"] = result

    if success:
        logger.info("MCP tool executed successfully", extra=log_data)
    else:
        logger.warning("MCP tool execution failed", extra=log_data)


def log_database_operation(
    logger: logging.Logger,
    operation: str,
    table: str,
    success: bool,
    execution_time_ms: float,
    record_count: int = None,
    details: Dict[str, Any] = None
) -> None:
    """
    Log a database operation with relevant details.

    Args:
        logger (logging.Logger): Logger instance to use
        operation (str): Type of database operation (SELECT, INSERT, UPDATE, DELETE)
        table (str): Name of the table involved in the operation
        success (bool): Whether the operation was successful
        execution_time_ms (float): Time taken to execute the operation in milliseconds
        record_count (int, optional): Number of records affected (for INSERT/UPDATE/DELETE)
        details (Dict[str, Any], optional): Additional details to log
    """
    log_data = {
        "event_type": "database_operation",
        "operation": operation,
        "table": table,
        "success": success,
        "execution_time_ms": execution_time_ms
    }

    if record_count is not None:
        log_data["record_count"] = record_count

    if details:
        log_data.update(details)

    if success:
        logger.info("Database operation completed", extra=log_data)
    else:
        logger.warning("Database operation failed", extra=log_data)


def log_error(
    logger: logging.Logger,
    error_type: str,
    error_message: str,
    user_id: str = None,
    endpoint: str = None,
    details: Dict[str, Any] = None
) -> None:
    """
    Log an error with relevant context.

    Args:
        logger (logging.Logger): Logger instance to use
        error_type (str): Type/classification of the error
        error_message (str): Description of the error
        user_id (str, optional): ID of the user involved in the error
        endpoint (str, optional): Endpoint where the error occurred
        details (Dict[str, Any], optional): Additional details about the error
    """
    log_data = {
        "event_type": "error",
        "error_type": error_type,
        "error_message": error_message
    }

    if user_id:
        log_data["user_id"] = user_id

    if endpoint:
        log_data["endpoint"] = endpoint

    if details:
        log_data.update(details)

    logger.error("Error occurred in system", extra=log_data)


def log_conversation_state(
    logger: logging.Logger,
    user_id: str,
    conversation_id: str,
    state_change: str,
    details: Dict[str, Any] = None
) -> None:
    """
    Log conversation state changes.

    Args:
        logger (logging.Logger): Logger instance to use
        user_id (str): ID of the user whose conversation state changed
        conversation_id (str): ID of the conversation
        state_change (str): Description of the state change
        details (Dict[str, Any], optional): Additional details about the state change
    """
    log_data = {
        "event_type": "conversation_state_change",
        "user_id": user_id,
        "conversation_id": conversation_id,
        "state_change": state_change
    }

    if details:
        log_data.update(details)

    logger.info("Conversation state updated", extra=log_data)


def log_system_metric(
    logger: logging.Logger,
    metric_name: str,
    metric_value: float,
    unit: str = None,
    details: Dict[str, Any] = None
) -> None:
    """
    Log system metrics for monitoring and observability.

    Args:
        logger (logging.Logger): Logger instance to use
        metric_name (str): Name of the metric being logged
        metric_value (float): Value of the metric
        unit (str, optional): Unit of measurement for the metric
        details (Dict[str, Any], optional): Additional details about the metric
    """
    log_data = {
        "event_type": "system_metric",
        "metric_name": metric_name,
        "metric_value": metric_value
    }

    if unit:
        log_data["unit"] = unit

    if details:
        log_data.update(details)

    logger.info("System metric recorded", extra=log_data)


# Create a default logger for the application
default_logger = setup_logger(
    name="todo_chatbot",
    level=logging.INFO,
    log_file="logs/todo_chatbot.log",
    use_json=True
)


def get_default_logger() -> logging.Logger:
    """
    Get the default application logger.

    Returns:
        logging.Logger: Default logger instance
    """
    return default_logger