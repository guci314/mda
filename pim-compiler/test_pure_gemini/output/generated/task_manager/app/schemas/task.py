"""
Task (任务) Pydantic 模式定义。

这些模式用于 API 的数据验证、序列化和文档生成。
"""
import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import TaskStatus, TaskPriority
from app.schemas.tag import TagRead

class TaskBase(BaseModel):
    """
    任务的基础模式，包含了所有任务共有的字段。
    """
    title: str = Field(..., min_length=1, max_length=100, description="任务标题")
    description: Optional[str] = Field(None, description="任务详细描述")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="任务优先级")
    due_date: Optional[datetime.date] = Field(None, description="任务截止日期")

class TaskCreate(TaskBase):
    """
    创建任务时使用的模式。
    允许指定关联的标签ID列表。
    """
    tag_ids: Optional[List[int]] = Field([], description="关联的标签ID列表")

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: datetime.date | None) -> datetime.date | None:
        """
        验证截止日期不能是过去的时间。
        """
        if v and v < datetime.date.today():
            raise ValueError('截止日期不能是过去的时间')
        return v

class TaskUpdate(BaseModel):
    """
    更新任务时使用的模式。
    所有字段都是可选的，允许部分更新。
    """
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="任务标题")
    description: Optional[str] = Field(None, description="任务详细描述")
    priority: Optional[TaskPriority] = Field(None, description="任务优先级")
    due_date: Optional[datetime.date] = Field(None, description="任务截止日期")
    tag_ids: Optional[List[int]] = Field(None, description="要设置的完整标签ID列表")

    @field_validator('due_date')
    @classmethod
    def validate_due_date(cls, v: datetime.date | None) -> datetime.date | None:
        """
        验证截止日期不能是过去的时间。
        """
        if v and v < datetime.date.today():
            raise ValueError('截止日期不能是过去的时间')
        return v

class TaskStatusUpdate(BaseModel):
    """
    专门用于更新任务状态的模式。
    """
    status: TaskStatus = Field(..., description="新的任务状态")

class TaskRead(TaskBase):
    """
    从 API 读取（返回）任务数据时使用的模式。
    包含了数据库生成的字段，如 id, status, created_at 等。
    """
    id: int
    status: TaskStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
    completed_at: Optional[datetime.datetime] = None
    tags: List[TagRead] = []
    
    model_config = ConfigDict(from_attributes=True)
