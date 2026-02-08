"""
Error Response Models for Todo AI Chatbot System

This module defines response models for error responses.
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any


class ErrorResponse(BaseModel):
    """
    Model for error responses from the API.

    Attributes:
        success (bool): Indicates if the request was successful (always False for errors)
        error_code (str): Code identifying the type of error
        message (str): Human-readable error message
        details (Optional[Dict[str, Any]]): Additional error details
    """
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None