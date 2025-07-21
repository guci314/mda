"""
任务与标签的多对多关联表定义。

使用 SQLAlchemy 的 Table 对象来定义一个纯粹的关联表，因为它不包含除外键之外的任何其他信息。
"""
from sqlalchemy import Table, Column, ForeignKey
from app.core.db import Base

task_tag_association = Table(
    "task_tag_association",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
)
