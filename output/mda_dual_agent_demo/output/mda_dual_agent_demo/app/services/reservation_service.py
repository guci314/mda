"""
预约服务层
"""
import uuid
from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import ReservationRecordDB
from ..models.pydantic import ReservationRecordCreate, ReservationRecordResponse
from ..models.enums import ReservationStatus
from ..repositories.reservation_repository import ReservationRepository
from ..repositories.book_repository import BookRepository
from ..repositories.reader_repository import ReaderRepository
from ..repositories.borrow_repository import BorrowRepository
from .reader_service import ReaderService
from .book_service import BookService


class ReservationService:
    """预约服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReservationRepository(db)
        self.book_repository = BookRepository(db)
        self.reader_repository = ReaderRepository(db)
        self.borrow_repository = BorrowRepository(db)
        self.reader_service = ReaderService(db)
        self.book_service = BookService(db)
    
    def _generate_reservation_id(self) -> str:
        """生成预约ID"""
        return f"R{uuid.uuid4().hex[:8].upper()}"
    
    async def reserve_book(self, reservation_data: ReservationRecordCreate) -> ReservationRecordResponse:
        """预约图书"""
        reader_id = reservation_data.reader_id
        isbn = reservation_data.isbn
        
        # 检查读者是否可以借阅
        can_borrow, reason = await self.reader_service.can_borrow(reader_id)
        if not can_borrow:
            raise ValueError(f"读者无法预约：{reason}")
        
        # 检查图书是否存在
        if not await self.book_service.book_exists(isbn):
            raise ValueError("图书不存在")
        
        # 检查读者是否已借阅此书
        existing_borrow = await self.borrow_repository.get_active_borrow_by_reader_and_book(reader_id, isbn)
        if existing_borrow:
            raise ValueError("读者已借阅此书，无需预约")
        
        # 检查读者是否已预约此书
        existing_reservation = await self.repository.get_active_reservation_by_reader_and_book(reader_id, isbn)
        if existing_reservation:
            raise ValueError("读者已预约此书，不能重复预约")
        
        # 检查图书是否可直接借阅
        if await self.book_service.is_available_for_borrow(isbn):
            raise ValueError("图书当前可借阅，无需预约")
        
        # 检查读者预约数量限制
        active_reservations_count = await self.repository.count_active_reservations_by_reader(reader_id)
        max_reservation_count = 3  # 最大预约数量
        
        if active_reservations_count >= max_reservation_count:
            raise ValueError(f"预约数量已达上限（{max_reservation_count}本）")
        
        # 创建预约记录
        reservation_id = self._generate_reservation_id()
        reservation_record = ReservationRecordDB(
            reservation_id=reservation_id,
            reader_id=reader_id,
            isbn=isbn,
            reserve_date=datetime.now(),
            status=ReservationStatus.PENDING
        )
        
        created_record = await self.repository.create(reservation_record)
        return ReservationRecordResponse.model_validate(created_record)
    
    async def cancel_reservation(self, reservation_id: str) -> bool:
        """取消预约"""
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"预约记录 {reservation_id} 不存在")
        
        if reservation.status not in [ReservationStatus.PENDING, ReservationStatus.READY]:
            raise ValueError("只有等待中或可借阅状态的预约才能取消")
        
        return await self.repository.cancel(reservation_id)
    
    async def notify_reservation_ready(self, reservation_id: str) -> bool:
        """通知预约可借阅"""
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"预约记录 {reservation_id} 不存在")
        
        if reservation.status != ReservationStatus.PENDING:
            raise ValueError("只有等待中的预约才能通知")
        
        # 设置过期时间（3天后过期）
        notify_date = datetime.now()
        expire_date = notify_date + timedelta(days=3)
        
        return await self.repository.mark_ready(reservation_id, notify_date, expire_date)
    
    async def complete_reservation(self, reservation_id: str) -> bool:
        """完成预约（已借阅）"""
        reservation = await self.repository.get_by_id(reservation_id)
        if not reservation:
            raise ValueError(f"预约记录 {reservation_id} 不存在")
        
        if reservation.status != ReservationStatus.READY:
            raise ValueError("只有可借阅状态的预约才能完成")
        
        return await self.repository.complete(reservation_id)
    
    async def get_reservation(self, reservation_id: str) -> Optional[ReservationRecordResponse]:
        """获取预约记录"""
        record = await self.repository.get_by_id(reservation_id)
        if not record:
            return None
        
        return ReservationRecordResponse.model_validate(record)
    
    async def get_reader_reservations(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[ReservationRecordResponse]:
        """获取读者的预约记录"""
        records = await self.repository.get_by_reader(reader_id, skip=skip, limit=limit)
        return [ReservationRecordResponse.model_validate(record) for record in records]
    
    async def get_reader_active_reservations(self, reader_id: str) -> List[ReservationRecordResponse]:
        """获取读者的活跃预约记录"""
        records = await self.repository.get_active_reservations_by_reader(reader_id)
        return [ReservationRecordResponse.model_validate(record) for record in records]
    
    async def get_book_reservations(self, isbn: str, skip: int = 0, limit: int = 100) -> List[ReservationRecordResponse]:
        """获取图书的预约记录"""
        records = await self.repository.get_by_book(isbn, skip=skip, limit=limit)
        return [ReservationRecordResponse.model_validate(record) for record in records]
    
    async def get_book_pending_reservations(self, isbn: str) -> List[ReservationRecordResponse]:
        """获取图书的等待预约记录"""
        records = await self.repository.get_pending_reservations_by_book(isbn)
        return [ReservationRecordResponse.model_validate(record) for record in records]
    
    async def get_all_reservations(self, skip: int = 0, limit: int = 100) -> List[ReservationRecordResponse]:
        """获取所有预约记录"""
        records = await self.repository.get_all(skip=skip, limit=limit)
        return [ReservationRecordResponse.model_validate(record) for record in records]
    
    async def get_ready_reservations(self) -> List[ReservationRecordResponse]:
        """获取可借阅状态的预约记录"""
        records = await self.repository.get_ready_reservations()
        return [ReservationRecordResponse.model_validate(record) for record in records]
    
    async def process_book_return(self, isbn: str) -> int:
        """处理图书归还后的预约通知"""
        # 获取该图书的等待预约记录（按预约时间排序）
        pending_reservations = await self.repository.get_pending_reservations_by_book(isbn)
        
        if not pending_reservations:
            return 0
        
        # 检查图书是否有可借数量
        book = await self.book_repository.get_by_isbn(isbn)
        if not book or book.available_quantity <= 0:
            return 0
        
        # 通知第一个等待的预约
        first_reservation = pending_reservations[0]
        
        # 检查读者状态是否仍然有效
        can_borrow, _ = await self.reader_service.can_borrow(first_reservation.reader_id)
        if can_borrow:
            await self.notify_reservation_ready(first_reservation.reservation_id)
            return 1
        else:
            # 如果读者状态无效，取消预约并处理下一个
            await self.repository.cancel(first_reservation.reservation_id)
            return await self.process_book_return(isbn)
    
    async def process_expired_reservations(self) -> int:
        """处理过期的预约"""
        expired_reservations = await self.repository.get_expired_reservations()
        
        processed_count = 0
        for reservation in expired_reservations:
            await self.repository.expire(reservation.reservation_id)
            
            # 处理该图书的下一个预约
            await self.process_book_return(reservation.isbn)
            processed_count += 1
        
        return processed_count
    
    async def get_reservation_queue_position(self, reader_id: str, isbn: str) -> Optional[int]:
        """获取读者在图书预约队列中的位置"""
        reservation = await self.repository.get_active_reservation_by_reader_and_book(reader_id, isbn)
        if not reservation:
            return None
        
        if reservation.status != ReservationStatus.PENDING:
            return 0  # 已经可借阅或其他状态
        
        # 获取该图书的所有等待预约（按时间排序）
        pending_reservations = await self.repository.get_pending_reservations_by_book(isbn)
        
        for i, res in enumerate(pending_reservations):
            if res.reservation_id == reservation.reservation_id:
                return i + 1
        
        return None
    
    async def get_reservation_count(self) -> int:
        """获取预约记录总数"""
        return await self.repository.count_total()