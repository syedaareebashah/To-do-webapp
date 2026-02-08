"""
Logging Configuration for Todo AI Chatbot Agent

This module sets up logging for the agent with appropriate levels and formatting.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler


def setup_logging(level=logging.INFO):
    """
    Set up logging for the application.

    Args:
        level: Logging level (default: INFO)
    """
    # Create logger
    logger = logging.getLogger('todo_chatbot_agent')
    logger.setLevel(level)

    # Prevent adding multiple handlers if already configured
    if logger.handlers:
        return logger

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create file handler with rotation
    file_handler = RotatingFileHandler(
        'todo_chatbot_agent.log',
        maxBytes=1024*1024,  # 1MB
        backupCount=5
    )
    file_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


# Set up default logging
logger = setup_logging()