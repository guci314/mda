"""
Tag (标签) ORM 模型定义。
"""
from typing import List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base
from app.models.task_tag import task_tag_association

class Tag(Base):
    """
    标签模型，代表一个可以分配给任务的标签。
    """
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    color: Mapped[str] = mapped_column(String(7), default="#FFFFFF")  # Hex color format
    description: Mapped[Optional[str]] = mapped_column(String(255))

    # 多对多关系: 一个标签可以有多个任务
    # lazy="selectin" 会在加载 Tag 时，通过一个单独的 SELECT 语句预加载所有相关的 Task
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        secondary=task_tag_association, 
        back_populates="tags", 
        lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}')>"
