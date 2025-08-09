from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta
from ..models.domain import BorrowRecordDB, BookDB
from ..schemas.schemas import BorrowRecordResponse

class BorrowingService:
    def __init__(self, db: Session):
        self.db = db

    def borrow_book(self, reader_id: str, isbn: str) -> BorrowRecordResponse:
        """借阅图书"""
        book = self.db.query(BookDB).filter(BookDB.isbn == isbn).first()
        if not book or book.status != "在架":
            raise ValueError("图书不可借")
        if book.available_quantity <= 0:
            raise ValueError("图书库存不足")
        borrow_record = BorrowRecordDB(
            borrow_id=str(uuid4()),
            reader_id=reader_id,
            isbn=isbn,
            borrow_date=datetime.now(),
            due_date=datetime.now() + timedelta(days=30),
            status="借阅中"
        )
        book.available_quantity -= 1
        self.db.add(borrow_record)
        self.db.commit()
        self.db.refresh(borrow_record)
        return BorrowRecordResponse(**borrow_record.__dict__)

    def return_book(self, borrow_id: str) -> None:
        """归还图书"""
        borrow_record = self.db.query(BorrowRecordDB).filter(BorrowRecordDB.borrow_id == borrow_id).first()
        if not borrow_record:
            raise ValueError("借阅记录不存在")
        book = self.db.query(BookDB).filter(BookDB.isbn == borrow_record.isbn).first()
        if book:
            book.available_quantity += 1
        borrow_record.status = "已归还"
        borrow_record.return_date = datetime.now()
        self.db.commit()

    def renew_book(self, borrow_id: str) -> date:
        """续借图书"""
        borrow_record = self.db.query(BorrowRecordDB).filter(BorrowRecordDB.borrow_id == borrow_id).first()
        if not borrow_record:
            raise ValueError("借阅记录不存在")
        if borrow_record.renew_count >= 2:
            raise ValueError("已达到最大续借次数")
        borrow_record.due_date += timedelta(days=30)
        borrow_record.renew_count += 1
        self.db.commit()
        return borrow_record.due_date