"""
Pydantic schemas for data validation and serialization.
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from ..models.todo import TodoStatus


# Base schema for common attributes
class TodoBase(BaseModel):
    """Base schema for a Todo item."""
    title: str
    description: Optional[str] = None


# Schema for creating a new Todo item
class TodoCreate(TodoBase):
    """Schema used for creating a new Todo."""
    pass


# Schema for updating a Todo item's status
class TodoUpdate(BaseModel):
    """Schema used for updating a Todo's status."""
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TodoStatus] = None


# Schema for representing a Todo item in API responses
class Todo(TodoBase):
    """
    Schema for a full Todo item, used in API responses.
    Inherits from TodoBase and adds database-generated fields.
    """
    id: int
    status: TodoStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    # Pydantic V2 config
    model_config = ConfigDict(
        from_attributes=True,
    )
