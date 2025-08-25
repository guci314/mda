"""
任务数据模型
"""

from datetime import datetime
from enum import Enum
from typing import Optional

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Task:
    """
    任务数据模型类
    """
    def __init__(self, task_id: int, title: str, description: str = "", 
                 status: TaskStatus = TaskStatus.PENDING, 
                 created_at: Optional[datetime] = None,
                 updated_at: Optional[datetime] = None):
        self.id = task_id
        self.title = title
        self.description = description
        self.status = status
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
    def update_status(self, status: TaskStatus):
        """更新任务状态"""
        self.status = status
        self.updated_at = datetime.now()
    
    def update_title(self, title: str):
        """更新任务标题"""
        self.title = title
        self.updated_at = datetime.now()
    
    def update_description(self, description: str):
        """更新任务描述"""
        self.description = description
        self.updated_at = datetime.now()
    
    def to_dict(self):
        """将任务转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        """从字典创建任务"""
        task = cls(
            task_id=data["id"],
            title=data["title"],
            description=data.get("description", ""),
            status=TaskStatus(data.get("status", "pending")),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else None,
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else None
        )
        return task
    
    def __str__(self):
        return f"Task(id={self.id}, title='{self.title}', status={self.status.value})"
    
    def __repr__(self):
        return self.__str__()