"""
服务层: Task (任务)

封装与任务相关的业务逻辑。
"""
import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import Task, Tag, TaskStatus
from app.schemas import TaskCreate, TaskUpdate, TaskStatusUpdate

class TaskService:
    """
    处理任务相关业务逻辑的服务类。
    """

    async def get_task_by_id(self, db: AsyncSession, task_id: int) -> Task | None:
        """
        根据 ID 获取单个任务，并预加载其关联的标签。
        """
        stmt = select(Task).options(selectinload(Task.tags)).where(Task.id == task_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_tasks(
        self, 
        db: AsyncSession,
        status: Optional[TaskStatus] = None,
        priority: Optional[str] = None,
        tag_ids: Optional[List[int]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        获取任务列表，支持过滤、排序和分页。
        """
        stmt = select(Task).options(selectinload(Task.tags)).order_by(Task.created_at.desc())

        if status:
            stmt = stmt.where(Task.status == status)
        if priority:
            stmt = stmt.where(Task.priority == priority)
        if tag_ids:
            stmt = stmt.join(Task.tags).where(Tag.id.in_(tag_ids))

        stmt = stmt.offset(skip).limit(limit)
        
        result = await db.execute(stmt)
        return list(result.scalars().unique().all())

    async def create_task(self, db: AsyncSession, task_in: TaskCreate) -> Task:
        """
        创建新任务。

        - 验证提供的 tag_ids 是否都有效。
        - 创建任务并建立与标签的关联。
        """
        task_data = task_in.model_dump(exclude={"tag_ids"})
        db_task = Task(**task_data)

        if task_in.tag_ids:
            stmt = select(Tag).where(Tag.id.in_(task_in.tag_ids))
            result = await db.execute(stmt)
            tags = result.scalars().all()
            if len(tags) != len(task_in.tag_ids):
                raise HTTPException(status_code=404, detail="一个或多个标签ID无效")
            db_task.tags = list(tags)

        db.add(db_task)
        await db.commit()
        await db.refresh(db_task)
        return db_task

    async def update_task(
        self, db: AsyncSession, task_id: int, task_in: TaskUpdate
    ) -> Task:
        """
        更新任务信息。
        """
        db_task = await self.get_task_by_id(db, task_id=task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="任务未找到")

        update_data = task_in.model_dump(exclude_unset=True)

        if "tag_ids" in update_data:
            tag_ids = update_data.pop("tag_ids")
            if tag_ids is not None:
                stmt = select(Tag).where(Tag.id.in_(tag_ids))
                result = await db.execute(stmt)
                tags = result.scalars().all()
                if len(tags) != len(tag_ids):
                    raise HTTPException(status_code=404, detail="一个或多个标签ID无效")
                db_task.tags = list(tags)

        for field, value in update_data.items():
            setattr(db_task, field, value)

        await db.commit()
        await db.refresh(db_task)
        return db_task

    async def update_task_status(
        self, db: AsyncSession, task_id: int, status_in: TaskStatusUpdate
    ) -> Task:
        """
        更新任务的状态。

        - 业务规则: 已取消的任务不能更改状态。
        - 业务规则: 状态变为“已完成”时，记录完成时间。
        """
        db_task = await self.get_task_by_id(db, task_id=task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="任务未找到")

        if db_task.status == TaskStatus.CANCELED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="已取消的任务不能更改状态",
            )

        db_task.status = status_in.status
        if status_in.status == TaskStatus.DONE:
            db_task.completed_at = datetime.datetime.now(datetime.timezone.utc)
        else:
            db_task.completed_at = None # 如果从 DONE 变回其他状态，清除完成时间

        await db.commit()
        await db.refresh(db_task)
        return db_task

    async def delete_task(self, db: AsyncSession, task_id: int) -> None:
        """
        删除任务。

        - 业务规则: 只能删除“已完成”或“已取消”的任务。
        """
        db_task = await self.get_task_by_id(db, task_id=task_id)
        if not db_task:
            raise HTTPException(status_code=404, detail="任务未找到")

        if db_task.status not in [TaskStatus.DONE, TaskStatus.CANCELED]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="只能删除已完成或已取消的任务",
            )

        await db.delete(db_task)
        await db.commit()
        return

# 创建一个服务实例，以便在 API 路由中作为依赖项使用
task_service = TaskService()
