"""
Chat Response Models for Todo AI Chatbot System

This module defines the response models for the chat API.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class ToolCallResponse(BaseModel):
    """
    Model for representing a tool call result in the response.

    Attributes:
        tool_name (str): Name of the tool that was called
        arguments (Dict[str, Any]): Arguments passed to the tool
        result (Dict[str, Any]): Result returned by the tool
    """
    tool_name: str
    arguments: Dict[str, Any]
    result: Dict[str, Any]


class ChatResponse(BaseModel):
    """
    Response model for the chat endpoint.

    Attributes:
        conversation_id (str): ID of the conversation
        response (str): The AI agent's response to the user
        tool_calls (List[ToolCallResponse]): List of tool calls made during processing
        message_id (str): ID of the assistant's response message
    """
    conversation_id: str
    response: str
    tool_calls: List[ToolCallResponse]
    message_id: str


class ErrorResponse(BaseModel):
    """
    Model for error responses from the API.

    Attributes:
        error_code (str): Code identifying the type of error
        message (str): Human-readable error message
        details (Optional[Dict[str, Any]]): Additional error details
    """
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    """
    Response model for the health check endpoint.

    Attributes:
        status (str): Overall system status
        timestamp (datetime): When the health check was performed
        services (Dict[str, str]): Status of individual services
    """
    status: str
    timestamp: datetime
    services: Dict[str, str]