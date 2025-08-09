"""
预约记录仓储层
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_
from sqlalchemy.orm import selectinload
from ..models.database import ReservationRecordDB
from ..models.enums import ReservationStatus


class ReservationRepository:
    """预约记录仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, reservation_id: str) -> Optional[ReservationRecordDB]:
        """根据ID获取预约记录"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.reader), selectinload(ReservationRecordDB.book))
            .where(ReservationRecordDB.reservation_id == reservation_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_reader(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[ReservationRecordDB]:
        """获取读者的预约记录"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.book))
            .where(ReservationRecordDB.reader_id == reader_id)
            .order_by(ReservationRecordDB.reserve_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_book(self, isbn: str, skip: int = 0, limit: int = 100) -> List[ReservationRecordDB]:
        """获取图书的预约记录"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.reader))
            .where(ReservationRecordDB.isbn == isbn)
            .order_by(ReservationRecordDB.reserve_date.asc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_active_reservations_by_reader(self, reader_id: str) -> List[ReservationRecordDB]:
        """获取读者的活跃预约记录"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.book))
            .where(
                and_(
                    ReservationRecordDB.reader_id == reader_id,
                    or_(
                        ReservationRecordDB.status == ReservationStatus.PENDING,
                        ReservationRecordDB.status == ReservationStatus.READY
                    )
                )
            )
            .order_by(ReservationRecordDB.reserve_date.asc())
        )
        return result.scalars().all()
    
    async def get_active_reservation_by_reader_and_book(self, reader_id: str, isbn: str) -> Optional[ReservationRecordDB]:
        """获取读者对特定图书的活跃预约记录"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .where(
                and_(
                    ReservationRecordDB.reader_id == reader_id,
                    ReservationRecordDB.isbn == isbn,
                    or_(
                        ReservationRecordDB.status == ReservationStatus.PENDING,
                        ReservationRecordDB.status == ReservationStatus.READY
                    )
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_pending_reservations_by_book(self, isbn: str) -> List[ReservationRecordDB]:
        """获取图书的等待中预约记录（按预约时间排序）"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.reader))
            .where(
                and_(
                    ReservationRecordDB.isbn == isbn,
                    ReservationRecordDB.status == ReservationStatus.PENDING
                )
            )
            .order_by(ReservationRecordDB.reserve_date.asc())
        )
        return result.scalars().all()
    
    async def get_ready_reservations(self) -> List[ReservationRecordDB]:
        """获取可借阅状态的预约记录"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.reader), selectinload(ReservationRecordDB.book))
            .where(ReservationRecordDB.status == ReservationStatus.READY)
            .order_by(ReservationRecordDB.notify_date.asc())
        )
        return result.scalars().all()
    
    async def get_expired_reservations(self, current_time: datetime = None) -> List[ReservationRecordDB]:
        """获取已过期的预约记录"""
        if current_time is None:
            current_time = datetime.now()
        
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.reader), selectinload(ReservationRecordDB.book))
            .where(
                and_(
                    ReservationRecordDB.status == ReservationStatus.READY,
                    ReservationRecordDB.expire_date < current_time
                )
            )
            .order_by(ReservationRecordDB.expire_date.asc())
        )
        return result.scalars().all()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[ReservationRecordDB]:
        """获取所有预约记录"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.reader), selectinload(ReservationRecordDB.book))
            .order_by(ReservationRecordDB.reserve_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_by_status(self, status: ReservationStatus, skip: int = 0, limit: int = 100) -> List[ReservationRecordDB]:
        """根据状态获取预约记录"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .options(selectinload(ReservationRecordDB.reader), selectinload(ReservationRecordDB.book))
            .where(ReservationRecordDB.status == status)
            .order_by(ReservationRecordDB.reserve_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, reservation: ReservationRecordDB) -> ReservationRecordDB:
        """创建预约记录"""
        self.db.add(reservation)
        await self.db.commit()
        await self.db.refresh(reservation)
        return reservation
    
    async def update(self, reservation_id: str, **kwargs) -> Optional[ReservationRecordDB]:
        """更新预约记录"""
        await self.db.execute(
            update(ReservationRecordDB)
            .where(ReservationRecordDB.reservation_id == reservation_id)
            .values(**kwargs)
        )
        await self.db.commit()
        return await self.get_by_id(reservation_id)
    
    async def mark_ready(self, reservation_id: str, notify_date: datetime = None, expire_date: datetime = None) -> bool:
        """标记为可借阅状态"""
        if notify_date is None:
            notify_date = datetime.now()
        
        update_data = {
            "status": ReservationStatus.READY,
            "notify_date": notify_date
        }
        if expire_date:
            update_data["expire_date"] = expire_date
        
        record = await self.update(reservation_id, **update_data)
        return record is not None
    
    async def cancel(self, reservation_id: str) -> bool:
        """取消预约"""
        record = await self.update(reservation_id, status=ReservationStatus.CANCELLED)
        return record is not None
    
    async def complete(self, reservation_id: str) -> bool:
        """完成预约（已借阅）"""
        record = await self.update(reservation_id, status=ReservationStatus.COMPLETED)
        return record is not None
    
    async def expire(self, reservation_id: str) -> bool:
        """过期预约"""
        record = await self.update(reservation_id, status=ReservationStatus.CANCELLED)
        return record is not None
    
    async def count_active_reservations_by_reader(self, reader_id: str) -> int:
        """统计读者的活跃预约数量"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .where(
                and_(
                    ReservationRecordDB.reader_id == reader_id,
                    or_(
                        ReservationRecordDB.status == ReservationStatus.PENDING,
                        ReservationRecordDB.status == ReservationStatus.READY
                    )
                )
            )
        )
        return len(result.scalars().all())
    
    async def count_pending_reservations_by_book(self, isbn: str) -> int:
        """统计图书的等待预约数量"""
        result = await self.db.execute(
            select(ReservationRecordDB)
            .where(
                and_(
                    ReservationRecordDB.isbn == isbn,
                    ReservationRecordDB.status == ReservationStatus.PENDING
                )
            )
        )
        return len(result.scalars().all())
    
    async def count_total(self) -> int:
        """统计预约记录总数"""
        result = await self.db.execute(select(ReservationRecordDB))
        return len(result.scalars().all())
    
    async def exists(self, reservation_id: str) -> bool:
        """检查预约记录是否存在"""
        record = await self.get_by_id(reservation_id)
        return record is not None