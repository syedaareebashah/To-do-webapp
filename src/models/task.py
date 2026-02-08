"""
Task database model for the Todo AI Chatbot System.

This module defines the Task entity with its fields, relationships, and constraints.
"""

from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from enum import Enum


if TYPE_CHECKING:
    from src.models.user import User


class TaskStatus(str, Enum):
    """
    Enum for task status values.
    """
    PENDING = "pending"
    COMPLETED = "completed"


class TaskPriority(str, Enum):
    """
    Enum for task priority values.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskBase(SQLModel):
    """
    Base class for Task model containing common fields.
    """
    content: str = Field(nullable=False, max_length=500)
    status: TaskStatus = Field(default=TaskStatus.PENDING)
    due_date: Optional[datetime] = Field(default=None)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)


class Task(TaskBase, table=True):
    """
    Task model representing a user's task in the todo system.

    Attributes:
        id (uuid.UUID): Unique identifier for the task
        user_id (uuid.UUID): References the User who owns the task
        content (str): The content/description of the task
        status (TaskStatus): Current status of the task (pending, completed)
        due_date (Optional[datetime]): Deadline for the task
        priority (TaskPriority): Priority level (low, medium, high)
        created_at (datetime): Timestamp when the task was created
        completed_at (Optional[datetime]): Timestamp when the task was completed
        user (User): The user who owns this task
    """
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    completed_at: Optional[datetime] = Field(default=None)

    # Relationship
    user: "User" = Relationship(back_populates="tasks")


class TaskRead(TaskBase):
    """
    Schema for reading Task data.

    Attributes:
        id (uuid.UUID): Unique identifier for the task
        user_id (uuid.UUID): ID of the user who owns the task
        created_at (datetime): Timestamp when the task was created
        completed_at (Optional[datetime]): Timestamp when the task was completed
    """
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    completed_at: Optional[datetime]


class TaskCreate(TaskBase):
    """
    Schema for creating a new Task.

    Attributes:
        user_id (uuid.UUID): ID of the user who owns the task
    """
    user_id: uuid.UUID


class TaskUpdate(SQLModel):
    """
    Schema for updating Task data.

    Attributes:
        content (Optional[str]): New content for the task
        status (Optional[TaskStatus]): New status for the task
        due_date (Optional[datetime]): New due date for the task
        priority (Optional[TaskPriority]): New priority for the task
        completed_at (Optional[datetime]): New completion timestamp
    """
    content: Optional[str] = None
    status: Optional[TaskStatus] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    completed_at: Optional[datetime] = None