"""
API Schemas for Todo AI Chatbot System

This module defines the request/response schemas for API endpoints.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """
    Enum for user roles.
    """
    USER = "user"
    ASSISTANT = "assistant"


class TaskStatus(str, Enum):
    """
    Enum for task statuses.
    """
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """
    Enum for task priorities.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class MessageCreateRequest(BaseModel):
    """
    Schema for creating a new message in a conversation.

    Attributes:
        content (str): The content of the message (1-5000 characters)
        role (UserRole): The role of the message sender (user or assistant)
    """
    content: str = Field(..., min_length=1, max_length=5000, description="Content of the message")
    role: UserRole = Field(..., description="Role of the message sender")

    @validator('content')
    def validate_content(cls, v):
        """
        Validate that content is not empty or just whitespace.

        Args:
            v (str): The content to validate

        Returns:
            str: The validated content
        """
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or just whitespace')
        return v.strip()


class MessageResponse(BaseModel):
    """
    Schema for message response.

    Attributes:
        id (UUID): Unique identifier for the message
        conversation_id (UUID): ID of the conversation the message belongs to
        content (str): Content of the message
        role (UserRole): Role of the message sender
        timestamp (datetime): When the message was created
    """
    id: UUID
    conversation_id: UUID
    content: str
    role: UserRole
    timestamp: datetime


class TaskCreateRequest(BaseModel):
    """
    Schema for creating a new task.

    Attributes:
        content (str): Content/description of the task (1-500 characters)
        due_date (Optional[datetime]): Due date for the task
        priority (TaskPriority): Priority level of the task
    """
    content: str = Field(..., min_length=1, max_length=500, description="Content of the task")
    due_date: Optional[datetime] = Field(None, description="Due date for the task")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Priority of the task")

    @validator('content')
    def validate_task_content(cls, v):
        """
        Validate that task content is not empty or just whitespace.

        Args:
            v (str): The task content to validate

        Returns:
            str: The validated task content
        """
        if not v or not v.strip():
            raise ValueError('Task content cannot be empty or just whitespace')
        return v.strip()


class TaskResponse(BaseModel):
    """
    Schema for task response.

    Attributes:
        id (UUID): Unique identifier for the task
        user_id (UUID): ID of the user who owns the task
        content (str): Content of the task
        status (TaskStatus): Current status of the task
        due_date (Optional[datetime]): Due date for the task
        priority (TaskPriority): Priority level of the task
        created_at (datetime): When the task was created
        completed_at (Optional[datetime]): When the task was completed
    """
    id: UUID
    user_id: UUID
    content: str
    status: TaskStatus
    due_date: Optional[datetime]
    priority: TaskPriority
    created_at: datetime
    completed_at: Optional[datetime]


class TaskUpdateRequest(BaseModel):
    """
    Schema for updating a task.

    Attributes:
        content (Optional[str]): New content for the task
        status (Optional[TaskStatus]): New status for the task
        due_date (Optional[datetime]): New due date for the task
        priority (Optional[TaskPriority]): New priority for the task
    """
    content: Optional[str] = Field(None, min_length=1, max_length=500)
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None

    @validator('content')
    def validate_updated_content(cls, v):
        """
        Validate that updated content is not just whitespace if provided.

        Args:
            v (str): The updated content to validate

        Returns:
            str: The validated content
        """
        if v is not None and (not v or not v.strip()):
            raise ValueError('Updated content cannot be empty or just whitespace')
        return v.strip() if v else v


class ConversationCreateRequest(BaseModel):
    """
    Schema for creating a new conversation.

    Attributes:
        user_id (UUID): ID of the user who owns the conversation
    """
    user_id: UUID


class ConversationResponse(BaseModel):
    """
    Schema for conversation response.

    Attributes:
        id (UUID): Unique identifier for the conversation
        user_id (UUID): ID of the user who owns the conversation
        created_at (datetime): When the conversation was created
        updated_at (datetime): When the conversation was last updated
    """
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime


class ChatRequest(BaseModel):
    """
    Schema for chat endpoint request.

    Attributes:
        message (str): The user's message content (1-2000 characters)
        conversation_id (Optional[str]): ID of the conversation (if continuing existing)
    """
    message: str = Field(..., min_length=1, max_length=2000, description="User's message")
    conversation_id: Optional[str] = Field(None, description="ID of the conversation to continue")

    @validator('message')
    def validate_message(cls, v):
        """
        Validate that the message is not empty or just whitespace.

        Args:
            v (str): The message to validate

        Returns:
            str: The validated message
        """
        if not v or not v.strip():
            raise ValueError('Message cannot be empty or just whitespace')
        return v.strip()


class ToolCall(BaseModel):
    """
    Schema for representing a tool call in the response.

    Attributes:
        tool_name (str): Name of the tool that was called
        parameters (Dict[str, Any]): Parameters passed to the tool
        result (Dict[str, Any]): Result returned by the tool
    """
    tool_name: str
    parameters: Dict[str, Any]
    result: Dict[str, Any]


class ChatResponse(BaseModel):
    """
    Schema for chat endpoint response.

    Attributes:
        conversation_id (str): ID of the conversation
        response (str): The AI agent's response
        tool_calls (List[ToolCall]): List of tools called during processing
        message_id (str): ID of the assistant's response message
    """
    conversation_id: str
    response: str
    tool_calls: List[ToolCall]
    message_id: str


class HealthResponse(BaseModel):
    """
    Schema for health check endpoint response.

    Attributes:
        status (str): Overall health status
        timestamp (datetime): When the health check was performed
        services (Dict[str, str]): Status of individual services
    """
    status: str
    timestamp: datetime
    services: Dict[str, str]


class ErrorResponse(BaseModel):
    """
    Schema for error responses.

    Attributes:
        success (bool): Whether the request was successful (always False for errors)
        error_code (str): Code identifying the type of error
        message (str): Human-readable error message
        details (Optional[Dict[str, Any]]): Additional error details
    """
    success: bool = False
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None