"""
服务层: Tag (标签)

封装与标签相关的业务逻辑。
"""
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status

from app.models import Tag
from app.schemas import TagCreate, TagUpdate

class TagService:
    """
    处理标签相关业务逻辑的服务类。
    """

    async def get_tag_by_id(self, db: AsyncSession, tag_id: int) -> Tag | None:
        """根据 ID 获取单个标签"""
        stmt = select(Tag).where(Tag.id == tag_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_tag_by_name(self, db: AsyncSession, name: str) -> Tag | None:
        """根据名称获取单个标签"""
        stmt = select(Tag).where(Tag.name == name)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_all_tags(self, db: AsyncSession) -> List[Tag]:
        """获取所有标签"""
        stmt = select(Tag).order_by(Tag.name)
        result = await db.execute(stmt)
        return list(result.scalars().all())

    async def create_tag(self, db: AsyncSession, tag_in: TagCreate) -> Tag:
        """
        创建新标签。

        - 检查标签名是否已存在。
        - 创建并返回新的 Tag 对象。
        """
        existing_tag = await self.get_tag_by_name(db, name=tag_in.name)
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"名为 '{tag_in.name}' 的标签已存在",
            )
        
        db_tag = Tag(**tag_in.model_dump())
        db.add(db_tag)
        await db.commit()
        await db.refresh(db_tag)
        return db_tag

    async def update_tag(
        self, db: AsyncSession, tag_id: int, tag_in: TagUpdate
    ) -> Tag:
        """
        更新标签信息。

        - 检查标签是否存在。
        - 检查新标签名是否与其它标签冲突。
        - 更新数据并返回。
        """
        db_tag = await self.get_tag_by_id(db, tag_id=tag_id)
        if not db_tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签未找到")

        update_data = tag_in.model_dump(exclude_unset=True)

        if "name" in update_data and update_data["name"] != db_tag.name:
            existing_tag = await self.get_tag_by_name(db, name=update_data["name"])
            if existing_tag and existing_tag.id != tag_id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"名为 '{update_data['name']}' 的标签已存在",
                )

        for field, value in update_data.items():
            setattr(db_tag, field, value)

        await db.commit()
        await db.refresh(db_tag)
        return db_tag

    async def delete_tag(self, db: AsyncSession, tag_id: int) -> None:
        """
        删除标签。

        - 业务规则: 如果标签仍关联着任何任务，则禁止删除。
        """
        # 使用 selectinload 预加载关联的任务，以检查是否有关联
        stmt = select(Tag).options(selectinload(Tag.tasks)).where(Tag.id == tag_id)
        result = await db.execute(stmt)
        db_tag = result.scalar_one_or_none()

        if not db_tag:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="标签未找到")

        if db_tag.tasks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无法删除正在被任务使用的标签",
            )

        await db.delete(db_tag)
        await db.commit()
        return

# 创建一个服务实例，以便在 API 路由中作为依赖项使用
tag_service = TagService()
