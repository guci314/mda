"""
借阅记录仓储层
"""
from typing import Optional, List
from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload
from ..models.database import BorrowRecordDB
from ..models.enums import BorrowStatus


class BorrowRepository:
    """借阅记录仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, borrow_id: str) -> Optional[BorrowRecordDB]:
        """根据ID获取借阅记录"""
        result = await self.db.execute(
            select(BorrowRecordDB)
            .options(selectinload(BorrowRecordDB.reader), selectinload(BorrowRecordDB.book))
            .where(BorrowRecordDB.borrow_id == borrow_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_reader(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[BorrowRecordDB]:
        """获取读者的借阅记录"""
        result = await self.db.execute(
            select(BorrowRecordDB)
            .options(selectinload(BorrowRecordDB.book))
            .where(BorrowRecordDB.reader_id == reader_id)
            .order_by(BorrowRecordDB.borrow_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_book(self, isbn: str, skip: int = 0, limit: int = 100) -> List[BorrowRecordDB]:
        """获取图书的借阅记录"""
        result = await self.db.execute(
            select(BorrowRecordDB)
            .options(selectinload(BorrowRecordDB.reader))
            .where(BorrowRecordDB.isbn == isbn)
            .order_by(BorrowRecordDB.borrow_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_borrows_by_reader(self, reader_id: str) -> List[BorrowRecordDB]:
        """获取读者的活跃借阅记录"""
        result = await self.db.execute(
            select(BorrowRecordDB)
            .options(selectinload(BorrowRecordDB.book))
            .where(
                and_(
                    BorrowRecordDB.reader_id == reader_id,
                    or_(
                        BorrowRecordDB.status == BorrowStatus.BORROWED,
                        BorrowRecordDB.status == BorrowStatus.OVERDUE
                    )
                )
            )
            .order_by(BorrowRecordDB.due_date.asc())
        )
        return result.scalars().all()
    
    async def get_active_borrow_by_reader_and_book(self, reader_id: str, isbn: str) -> Optional[BorrowRecordDB]:
        """获取读者对特定图书的活跃借阅记录"""
        result = await self.db.execute(
            select(BorrowRecordDB)
            .where(
                and_(
                    BorrowRecordDB.reader_id == reader_id,
                    BorrowRecordDB.isbn == isbn,
                    or_(
                        BorrowRecordDB.status == BorrowStatus.BORROWED,
                        BorrowRecordDB.status == BorrowStatus.OVERDUE
                    )
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_overdue_borrows(self, current_date: date = None) -> List[BorrowRecordDB]:
        """获取逾期的借阅记录"""
        if current_date is None:
            current_date = date.today()
        
        result = await self.db.execute(
            select(BorrowRecordDB)
            .options(selectinload(BorrowRecordDB.reader), selectinload(BorrowRecordDB.book))
            .where(
                and_(
                    BorrowRecordDB.status == BorrowStatus.BORROWED,
                    BorrowRecordDB.due_date < current_date
                )
            )
            .order_by(BorrowRecordDB.due_date.asc())
        )
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BorrowRecordDB]:
        """获取所有借阅记录"""
        result = await self.db.execute(
            select(BorrowRecordDB)
            .options(selectinload(BorrowRecordDB.reader), selectinload(BorrowRecordDB.book))
            .order_by(BorrowRecordDB.borrow_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(self, status: BorrowStatus, skip: int = 0, limit: int = 100) -> List[BorrowRecordDB]:
        """根据状态获取借阅记录"""
        result = await self.db.execute(
            select(BorrowRecordDB)
            .options(selectinload(BorrowRecordDB.reader), selectinload(BorrowRecordDB.book))
            .where(BorrowRecordDB.status == status)
            .order_by(BorrowRecordDB.borrow_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, borrow_record: BorrowRecordDB) -> BorrowRecordDB:
        """创建借阅记录"""
        self.db.add(borrow_record)
        await self.db.commit()
        await self.db.refresh(borrow_record)
        return borrow_record
    
    async def update(self, borrow_id: str, **kwargs) -> Optional[BorrowRecordDB]:
        """更新借阅记录"""
        await self.db.execute(
            update(BorrowRecordDB)
            .where(BorrowRecordDB.borrow_id == borrow_id)
            .values(**kwargs)
        )
        await self.db.commit()
        return await self.get_by_id(borrow_id)
    
    async def return_book(self, borrow_id: str, return_date: datetime = None, fine: float = None) -> bool:
        """归还图书"""
        if return_date is None:
            return_date = datetime.now()
        
        update_data = {
            "return_date": return_date,
            "status": BorrowStatus.RETURNED
        }
        if fine is not None:
            update_data["fine"] = fine
        
        record = await self.update(borrow_id, **update_data)
        return record is not None
    
    async def renew_book(self, borrow_id: str, new_due_date: date) -> bool:
        """续借图书"""
        borrow_record = await self.get_by_id(borrow_id)
        if not borrow_record:
            return False
        
        new_renew_count = borrow_record.renew_count + 1
        record = await self.update(
            borrow_id,
            due_date=new_due_date,
            renew_count=new_renew_count
        )
        return record is not None
    
    async def mark_overdue(self, borrow_id: str) -> bool:
        """标记为逾期"""
        record = await self.update(borrow_id, status=BorrowStatus.OVERDUE)
        return record is not None
    
    async def mark_lost(self, borrow_id: str, fine: float = None) -> bool:
        """标记为丢失"""
        update_data = {"status": BorrowStatus.LOST}
        if fine is not None:
            update_data["fine"] = fine
        
        record = await self.update(borrow_id, **update_data)
        return record is not None
    
    async def count_active_borrows_by_reader(self, reader_id: str) -> int:
        """统计读者的活跃借阅数量"""
        result = await self.db.execute(
            select(BorrowRecordDB)
            .where(
                and_(
                    BorrowRecordDB.reader_id == reader_id,
                    or_(
                        BorrowRecordDB.status == BorrowStatus.BORROWED,
                        BorrowRecordDB.status == BorrowStatus.OVERDUE
                    )
                )
            )
        )
        return len(result.scalars().all())
    
    async def count_total(self) -> int:
        """统计借阅记录总数"""
        result = await self.db.execute(select(BorrowRecordDB))
        return len(result.scalars().all())
    
    async def exists(self, borrow_id: str) -> bool:
        """检查借阅记录是否存在"""
        record = await self.get_by_id(borrow_id)
        return record is not None