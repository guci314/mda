"""
API Endpoints for Tasks
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session
from app.schemas import TaskCreate, TaskRead, TaskUpdate, TaskStatusUpdate
from app.services.task_service import task_service
from app.models import TaskStatus

router = APIRouter()

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: TaskCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    创建新任务，可选择关联一个或多个标签。
    """
    return await task_service.create_task(db=db, task_in=task_in)

@router.get("/", response_model=List[TaskRead])
async def get_all_tasks(
    status: Optional[TaskStatus] = Query(None, description="按任务状态筛选"),
    priority: Optional[str] = Query(None, description="按优先级筛选"),
    tag_ids: Optional[List[int]] = Query(None, description="按标签ID筛选，可多选"),
    skip: int = Query(0, ge=0, description="分页查询的起始位置"),
    limit: int = Query(100, ge=1, le=200, description="每页查询的数量"),
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取任务列表，支持按状态、优先级、标签进行筛选，并支持分页。
    """
    tasks = await task_service.get_all_tasks(
        db=db, status=status, priority=priority, tag_ids=tag_ids, skip=skip, limit=limit
    )
    return tasks

@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    根据 ID 获取单个任务的详细信息。
    """
    db_task = await task_service.get_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务未找到")
    return db_task

@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    更新指定 ID 的任务。
    """
    return await task_service.update_task(db=db, task_id=task_id, task_in=task_in)

@router.patch("/{task_id}/status", response_model=TaskRead)
async def update_task_status(
    task_id: int,
    status_in: TaskStatusUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    更新指定 ID 任务的状态。
    """
    return await task_service.update_task_status(db=db, task_id=task_id, status_in=status_in)

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    删除指定 ID 的任务。
    只有已完成或已取消的任务才能被删除。
    """
    await task_service.delete_task(db=db, task_id=task_id)
    return
