"""
Task (任务) ORM 模型定义。
"""
import datetime
from typing import List, Optional
from sqlalchemy import String, Text, DateTime, func, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.enums import TaskStatus, TaskPriority
from app.models.task_tag import task_tag_association

class Task(Base):
    """
    任务模型，代表一个需要完成的事项。
    """
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO, index=True)
    
    due_date: Mapped[Optional[datetime.date]] = mapped_column(Date)
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    # 多对多关系: 一个任务可以有多个标签
    # lazy="selectin" 会在加载 Task 时，通过一个单独的 SELECT 语句预加载所有相关的 Tag
    tags: Mapped[List["Tag"]] = relationship(
        "Tag",
        secondary=task_tag_association, 
        back_populates="tasks", 
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, title='{self.title}')>"
