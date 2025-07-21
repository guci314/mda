"""
SQLAlchemy ORM models for the application.
"""
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, DateTime, Integer, String, Text, Enum
from sqlalchemy.orm import Mapped, mapped_column

from ..core.database import Base


class TodoStatus(str, PyEnum):
    """Enum for Todo status."""
    PENDING = "pending"
    COMPLETED = "completed"


class Todo(Base):
    """
    Todo item ORM model.
    """
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[TodoStatus] = mapped_column(
        Enum(TodoStatus), default=TodoStatus.PENDING, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Todo(id={self.id}, title='{self.title}')>"
