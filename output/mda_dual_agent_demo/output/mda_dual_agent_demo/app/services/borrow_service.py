"""
借阅服务层
"""
import uuid
from typing import List, Optional
from datetime import datetime, date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import BorrowRecordDB
from ..models.pydantic import BorrowRecordCreate, BorrowRecordResponse
from ..models.enums import BorrowStatus, ReaderType
from ..repositories.borrow_repository import BorrowRepository
from ..repositories.book_repository import BookRepository
from ..repositories.reader_repository import ReaderRepository
from .book_service import BookService
from .reader_service import ReaderService


class BorrowService:
    """借阅服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BorrowRepository(db)
        self.book_repository = BookRepository(db)
        self.reader_repository = ReaderRepository(db)
        self.book_service = BookService(db)
        self.reader_service = ReaderService(db)
    
    def _generate_borrow_id(self) -> str:
        """生成借阅ID"""
        return f"B{uuid.uuid4().hex[:8].upper()}"
    
    def _calculate_due_date(self, reader_type: ReaderType, borrow_date: datetime = None) -> date:
        """计算应还日期"""
        if borrow_date is None:
            borrow_date = datetime.now()
        
        borrow_date = borrow_date.date()
        
        if reader_type == ReaderType.STUDENT:
            # 学生借期30天
            return borrow_date + timedelta(days=30)
        elif reader_type == ReaderType.TEACHER:
            # 教师借期60天
            return borrow_date + timedelta(days=60)
        else:
            # 社会人员借期15天
            return borrow_date + timedelta(days=15)
    
    def _calculate_fine(self, due_date: date, return_date: datetime = None) -> Decimal:
        """计算罚金"""
        if return_date is None:
            return_date = datetime.now()
        
        return_date = return_date.date()
        
        if return_date <= due_date:
            return Decimal('0.00')
        
        # 每天罚金1元
        overdue_days = (return_date - due_date).days
        return Decimal(str(overdue_days))
    
    async def borrow_book(self, borrow_data: BorrowRecordCreate) -> BorrowRecordResponse:
        """借阅图书"""
        reader_id = borrow_data.reader_id
        isbn = borrow_data.isbn
        
        # 检查读者是否可以借阅
        can_borrow, reason = await self.reader_service.can_borrow(reader_id)
        if not can_borrow:
            raise ValueError(f"读者无法借阅：{reason}")
        
        # 检查图书是否可借
        if not await self.book_service.is_available_for_borrow(isbn):
            raise ValueError("图书不可借阅")
        
        # 检查读者是否已借阅此书
        existing_borrow = await self.repository.get_active_borrow_by_reader_and_book(reader_id, isbn)
        if existing_borrow:
            raise ValueError("读者已借阅此书，不能重复借阅")
        
        # 检查读者借阅数量限制
        active_borrows_count = await self.repository.count_active_borrows_by_reader(reader_id)
        reader = await self.reader_repository.get_by_id(reader_id)
        
        max_borrow_count = 5  # 默认最大借阅数量
        if reader.reader_type == ReaderType.TEACHER:
            max_borrow_count = 10
        elif reader.reader_type == ReaderType.STUDENT:
            max_borrow_count = 5
        else:  # 社会人员
            max_borrow_count = 3
        
        if active_borrows_count >= max_borrow_count:
            raise ValueError(f"借阅数量已达上限（{max_borrow_count}本）")
        
        # 减少图书可借数量
        if not await self.book_service.decrease_available_quantity(isbn):
            raise ValueError("更新图书库存失败")
        
        try:
            # 创建借阅记录
            borrow_id = self._generate_borrow_id()
            borrow_date = datetime.now()
            due_date = self._calculate_due_date(reader.reader_type, borrow_date)
            
            borrow_record = BorrowRecordDB(
                borrow_id=borrow_id,
                reader_id=reader_id,
                isbn=isbn,
                borrow_date=borrow_date,
                due_date=due_date,
                status=BorrowStatus.BORROWED
            )
            
            created_record = await self.repository.create(borrow_record)
            return BorrowRecordResponse.model_validate(created_record)
            
        except Exception as e:
            # 回滚图书库存
            await self.book_service.increase_available_quantity(isbn)
            raise e
    
    async def return_book(self, borrow_id: str) -> BorrowRecordResponse:
        """归还图书"""
        # 获取借阅记录
        borrow_record = await self.repository.get_by_id(borrow_id)
        if not borrow_record:
            raise ValueError(f"借阅记录 {borrow_id} 不存在")
        
        if borrow_record.status not in [BorrowStatus.BORROWED, BorrowStatus.OVERDUE]:
            raise ValueError("图书已归还或状态异常")
        
        # 计算罚金
        return_date = datetime.now()
        fine = self._calculate_fine(borrow_record.due_date, return_date)
        
        # 更新借阅记录
        await self.repository.return_book(borrow_id, return_date, float(fine))
        
        # 增加图书可借数量
        await self.book_service.increase_available_quantity(borrow_record.isbn)
        
        # 如果有罚金，扣除信用分
        if fine > 0:
            # 每1元罚金扣1分信用分
            score_deduction = min(int(fine), 10)  # 最多扣10分
            await self.reader_service.update_credit_score(borrow_record.reader_id, -score_deduction)
        
        # 返回更新后的记录
        updated_record = await self.repository.get_by_id(borrow_id)
        return BorrowRecordResponse.model_validate(updated_record)
    
    async def renew_book(self, borrow_id: str) -> BorrowRecordResponse:
        """续借图书"""
        # 获取借阅记录
        borrow_record = await self.repository.get_by_id(borrow_id)
        if not borrow_record:
            raise ValueError(f"借阅记录 {borrow_id} 不存在")
        
        if borrow_record.status != BorrowStatus.BORROWED:
            raise ValueError("只有借阅中的图书才能续借")
        
        # 检查续借次数限制
        if borrow_record.renew_count >= 2:
            raise ValueError("续借次数已达上限（2次）")
        
        # 检查读者状态
        can_borrow, reason = await self.reader_service.can_borrow(borrow_record.reader_id)
        if not can_borrow:
            raise ValueError(f"读者状态异常，无法续借：{reason}")
        
        # 检查是否已逾期
        if borrow_record.due_date < date.today():
            raise ValueError("图书已逾期，无法续借")
        
        # 计算新的应还日期
        reader = await self.reader_repository.get_by_id(borrow_record.reader_id)
        current_due_date = borrow_record.due_date
        
        if reader.reader_type == ReaderType.STUDENT:
            new_due_date = current_due_date + timedelta(days=30)
        elif reader.reader_type == ReaderType.TEACHER:
            new_due_date = current_due_date + timedelta(days=60)
        else:
            new_due_date = current_due_date + timedelta(days=15)
        
        # 更新借阅记录
        await self.repository.renew_book(borrow_id, new_due_date)
        
        # 返回更新后的记录
        updated_record = await self.repository.get_by_id(borrow_id)
        return BorrowRecordResponse.model_validate(updated_record)
    
    async def get_borrow_record(self, borrow_id: str) -> Optional[BorrowRecordResponse]:
        """获取借阅记录"""
        record = await self.repository.get_by_id(borrow_id)
        if not record:
            return None
        
        return BorrowRecordResponse.model_validate(record)
    
    async def get_reader_borrows(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[BorrowRecordResponse]:
        """获取读者的借阅记录"""
        records = await self.repository.get_by_reader(reader_id, skip=skip, limit=limit)
        return [BorrowRecordResponse.model_validate(record) for record in records]
    
    async def get_reader_active_borrows(self, reader_id: str) -> List[BorrowRecordResponse]:
        """获取读者的活跃借阅记录"""
        records = await self.repository.get_active_borrows_by_reader(reader_id)
        return [BorrowRecordResponse.model_validate(record) for record in records]
    
    async def get_book_borrows(self, isbn: str, skip: int = 0, limit: int = 100) -> List[BorrowRecordResponse]:
        """获取图书的借阅记录"""
        records = await self.repository.get_by_book(isbn, skip=skip, limit=limit)
        return [BorrowRecordResponse.model_validate(record) for record in records]
    
    async def get_all_borrows(self, skip: int = 0, limit: int = 100) -> List[BorrowRecordResponse]:
        """获取所有借阅记录"""
        records = await self.repository.get_all(skip=skip, limit=limit)
        return [BorrowRecordResponse.model_validate(record) for record in records]
    
    async def get_overdue_borrows(self) -> List[BorrowRecordResponse]:
        """获取逾期的借阅记录"""
        records = await self.repository.get_overdue_borrows()
        return [BorrowRecordResponse.model_validate(record) for record in records]
    
    async def mark_overdue(self, borrow_id: str) -> bool:
        """标记为逾期"""
        record = await self.repository.get_by_id(borrow_id)
        if not record:
            raise ValueError(f"借阅记录 {borrow_id} 不存在")
        
        if record.status != BorrowStatus.BORROWED:
            raise ValueError("只有借阅中的记录才能标记为逾期")
        
        return await self.repository.mark_overdue(borrow_id)
    
    async def mark_lost(self, borrow_id: str, fine: float = None) -> bool:
        """标记为丢失"""
        record = await self.repository.get_by_id(borrow_id)
        if not record:
            raise ValueError(f"借阅记录 {borrow_id} 不存在")
        
        if record.status not in [BorrowStatus.BORROWED, BorrowStatus.OVERDUE]:
            raise ValueError("只有借阅中或逾期的记录才能标记为丢失")
        
        # 如果没有指定罚金，使用默认值（图书价格的2倍，这里简化为50元）
        if fine is None:
            fine = 50.0
        
        success = await self.repository.mark_lost(borrow_id, fine)
        
        if success:
            # 扣除信用分
            score_deduction = min(int(fine / 5), 20)  # 每5元扣1分，最多扣20分
            await self.reader_service.update_credit_score(record.reader_id, -score_deduction)
        
        return success
    
    async def process_overdue_books(self) -> int:
        """处理逾期图书"""
        today = date.today()
        overdue_records = await self.repository.get_overdue_borrows(today)
        
        processed_count = 0
        for record in overdue_records:
            if record.status == BorrowStatus.BORROWED:
                await self.repository.mark_overdue(record.borrow_id)
                # 扣除信用分
                overdue_days = (today - record.due_date).days
                score_deduction = min(overdue_days, 10)  # 每天扣1分，最多扣10分
                await self.reader_service.update_credit_score(record.reader_id, -score_deduction)
                processed_count += 1
        
        return processed_count
    
    async def get_borrow_count(self) -> int:
        """获取借阅记录总数"""
        return await self.repository.count_total()