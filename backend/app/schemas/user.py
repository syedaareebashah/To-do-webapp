from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID
from pydantic.config import ConfigDict

class UserPublic(BaseModel):
    """Public user model (excludes password_hash)."""
    user_id: UUID = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User's email address")
    created_at: datetime = Field(..., description="Account creation timestamp")

    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "user_id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "created_at": "2026-02-04T12:00:00Z"
        }
    })
