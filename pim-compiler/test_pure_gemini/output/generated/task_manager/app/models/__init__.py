"""
模型层导出模块

这个 __init__.py 文件使得从其他模块导入模型更加方便。
同时，它也是 Alembic 能够自动发现模型定义的关键。
Alembic 在执行 `revision --autogenerate` 时，会导入 `Base.metadata`，
而这个文件确保了所有继承自 `Base` 的模型都已经被加载，
从而可以让 Alembic 检测到模型的变化。
"""
from app.core.db import Base
from .tag import Tag
from .task import Task
from .task_tag import task_tag_association
from .enums import TaskStatus, TaskPriority

__all__ = ["Base", "Tag", "Task", "task_tag_association", "TaskStatus", "TaskPriority"]
