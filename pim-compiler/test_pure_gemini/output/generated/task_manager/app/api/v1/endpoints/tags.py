"""
API Endpoints for Tags
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_db_session
from app.schemas import TagCreate, TagRead, TagUpdate
from app.services.tag_service import tag_service

router = APIRouter()

@router.post("/", response_model=TagRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_in: TagCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    创建新标签。
    """
    return await tag_service.create_tag(db=db, tag_in=tag_in)

@router.get("/", response_model=List[TagRead])
async def get_all_tags(
    db: AsyncSession = Depends(get_db_session)
):
    """
    获取所有标签列表。
    """
    return await tag_service.get_all_tags(db=db)

@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    根据 ID 获取单个标签。
    """
    db_tag = await tag_service.get_tag_by_id(db, tag_id=tag_id)
    if not db_tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签未找到")
    return db_tag

@router.put("/{tag_id}", response_model=TagRead)
async def update_tag(
    tag_id: int,
    tag_in: TagUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """
    更新指定 ID 的标签。
    """
    return await tag_service.update_tag(db=db, tag_id=tag_id, tag_in=tag_in)

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: AsyncSession = Depends(get_db_session)
):
    """
    删除指定 ID 的标签。
    如果标签仍被任务使用，将无法删除。
    """
    await tag_service.delete_tag(db=db, tag_id=tag_id)
    return
