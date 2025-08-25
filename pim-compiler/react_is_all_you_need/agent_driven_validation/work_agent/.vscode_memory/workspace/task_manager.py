"""
任务管理器
"""

from typing import List, Optional, Dict
from task import Task, TaskStatus

class TaskManager:
    """
    任务管理器类，负责管理任务的增删改查
    """
    def __init__(self):
        self.tasks: Dict[int, Task] = {}
        self.next_id = 1
    
    def add_task(self, title: str, description: str = "") -> Task:
        """
        添加新任务
        
        Args:
            title: 任务标题
            description: 任务描述
            
        Returns:
            创建的任务对象
        """
        task = Task(self.next_id, title, description)
        self.tasks[self.next_id] = task
        self.next_id += 1
        return task
    
    def remove_task(self, task_id: int) -> bool:
        """
        删除任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            删除成功返回True，任务不存在返回False
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            return True
        return False
    
    def update_task(self, task_id: int, title: Optional[str] = None, 
                   description: Optional[str] = None, 
                   status: Optional[TaskStatus] = None) -> Optional[Task]:
        """
        更新任务信息
        
        Args:
            task_id: 任务ID
            title: 新标题（可选）
            description: 新描述（可选）
            status: 新状态（可选）
            
        Returns:
            更新后的任务对象，任务不存在返回None
        """
        if task_id not in self.tasks:
            return None
            
        task = self.tasks[task_id]
        
        if title is not None:
            task.update_title(title)
            
        if description is not None:
            task.update_description(description)
            
        if status is not None:
            task.update_status(status)
            
        return task
    
    def get_task(self, task_id: int) -> Optional[Task]:
        """
        获取任务
        
        Args:
            task_id: 任务ID
            
        Returns:
            任务对象，不存在返回None
        """
        return self.tasks.get(task_id)
    
    def list_tasks(self) -> List[Task]:
        """
        获取所有任务列表
        
        Returns:
            任务列表
        """
        return list(self.tasks.values())
    
    def list_tasks_by_status(self, status: TaskStatus) -> List[Task]:
        """
        根据状态获取任务列表
        
        Args:
            status: 任务状态
            
        Returns:
            符合状态的任务列表
        """
        return [task for task in self.tasks.values() if task.status == status]
    
    def get_task_count(self) -> int:
        """
        获取任务总数
        
        Returns:
            任务总数
        """
        return len(self.tasks)
    
    def clear_all_tasks(self):
        """清空所有任务"""
        self.tasks.clear()
        self.next_id = 1