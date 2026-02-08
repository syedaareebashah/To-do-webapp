from sqlmodel import SQLModel, Field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional

class User(SQLModel, table=True):
    """User model for authentication."""

    __tablename__ = "users"

    user_id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        nullable=False
    )
    email: str = Field(
        unique=True,
        index=True,
        nullable=False,
        max_length=255
    )
    password_hash: str = Field(
        nullable=False,
        max_length=255
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "user_id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "created_at": "2026-02-04T12:00:00Z",
                "updated_at": "2026-02-04T12:00:00Z"
            }
        }
