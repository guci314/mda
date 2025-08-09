"""
读者仓储层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from ..models.database import ReaderDB
from ..models.enums import ReaderStatus, ReaderType


class ReaderRepository:
    """读者仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, reader_id: str) -> Optional[ReaderDB]:
        """根据ID获取读者"""
        result = await self.db.execute(
            select(ReaderDB).where(ReaderDB.reader_id == reader_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id_card(self, id_card: str) -> Optional[ReaderDB]:
        """根据身份证号获取读者"""
        result = await self.db.execute(
            select(ReaderDB).where(ReaderDB.id_card == id_card)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[ReaderDB]:
        """根据手机号获取读者"""
        result = await self.db.execute(
            select(ReaderDB).where(ReaderDB.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ReaderDB]:
        """获取所有读者"""
        result = await self.db.execute(
            select(ReaderDB)
            .where(ReaderDB.status != ReaderStatus.DELETED)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_type(self, reader_type: ReaderType, skip: int = 0, limit: int = 100) -> List[ReaderDB]:
        """根据类型获取读者"""
        result = await self.db.execute(
            select(ReaderDB)
            .where(
                and_(
                    ReaderDB.reader_type == reader_type,
                    ReaderDB.status != ReaderStatus.DELETED
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(self, status: ReaderStatus, skip: int = 0, limit: int = 100) -> List[ReaderDB]:
        """根据状态获取读者"""
        result = await self.db.execute(
            select(ReaderDB)
            .where(ReaderDB.status == status)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_by_name(self, name: str, skip: int = 0, limit: int = 100) -> List[ReaderDB]:
        """根据姓名搜索读者"""
        result = await self.db.execute(
            select(ReaderDB)
            .where(
                and_(
                    ReaderDB.name.ilike(f"%{name}%"),
                    ReaderDB.status != ReaderStatus.DELETED
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, reader: ReaderDB) -> ReaderDB:
        """创建读者"""
        self.db.add(reader)
        await self.db.commit()
        await self.db.refresh(reader)
        return reader
    
    async def update(self, reader_id: str, **kwargs) -> Optional[ReaderDB]:
        """更新读者信息"""
        await self.db.execute(
            update(ReaderDB)
            .where(ReaderDB.reader_id == reader_id)
            .values(**kwargs)
        )
        await self.db.commit()
        return await self.get_by_id(reader_id)
    
    async def update_credit_score(self, reader_id: str, score_change: int) -> bool:
        """更新信用分"""
        reader = await self.get_by_id(reader_id)
        if not reader:
            return False
        
        new_score = reader.credit_score + score_change
        new_score = max(0, min(100, new_score))  # 限制在0-100之间
        
        await self.update(reader_id, credit_score=new_score)
        return True
    
    async def freeze(self, reader_id: str) -> bool:
        """冻结读者"""
        reader = await self.get_by_id(reader_id)
        if not reader or reader.status == ReaderStatus.DELETED:
            return False
        
        await self.update(reader_id, status=ReaderStatus.FROZEN)
        return True
    
    async def unfreeze(self, reader_id: str) -> bool:
        """解冻读者"""
        reader = await self.get_by_id(reader_id)
        if not reader or reader.status == ReaderStatus.DELETED:
            return False
        
        await self.update(reader_id, status=ReaderStatus.ACTIVE)
        return True
    
    async def delete(self, reader_id: str) -> bool:
        """删除读者（软删除）"""
        reader = await self.get_by_id(reader_id)
        if not reader:
            return False
        
        await self.update(reader_id, status=ReaderStatus.DELETED)
        return True
    
    async def count_total(self) -> int:
        """统计读者总数"""
        result = await self.db.execute(
            select(ReaderDB).where(ReaderDB.status != ReaderStatus.DELETED)
        )
        return len(result.scalars().all())
    
    async def exists(self, reader_id: str) -> bool:
        """检查读者是否存在且有效"""
        reader = await self.get_by_id(reader_id)
        return reader is not None and reader.status != ReaderStatus.DELETED
    
    async def is_active(self, reader_id: str) -> bool:
        """检查读者是否处于活跃状态"""
        reader = await self.get_by_id(reader_id)
        return reader is not None and reader.status == ReaderStatus.ACTIVE
    
    async def id_card_exists(self, id_card: str) -> bool:
        """检查身份证号是否已存在"""
        reader = await self.get_by_id_card(id_card)
        return reader is not None and reader.status != ReaderStatus.DELETED