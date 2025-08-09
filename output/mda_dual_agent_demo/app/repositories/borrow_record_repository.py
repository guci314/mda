from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.domain import BorrowRecordDB as BorrowRecord
from app.enums import BorrowStatus


class BorrowRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, borrow_id: str) -> Optional[BorrowRecord]:
        """根据ID获取借阅记录"""
        return self.db.query(BorrowRecord).filter(BorrowRecord.borrow_id == borrow_id).first()

    def get_by_reader(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[BorrowRecord]:
        """根据读者ID获取借阅记录"""
        return self.db.query(BorrowRecord).filter(BorrowRecord.reader_id == reader_id).offset(skip).limit(limit).all()

    def get_by_book(self, isbn: str, skip: int = 0, limit: int = 100) -> List[BorrowRecord]:
        """根据ISBN获取借阅记录"""
        return self.db.query(BorrowRecord).filter(BorrowRecord.isbn == isbn).offset(skip).limit(limit).all()

    def get_active_borrows(self, skip: int = 0, limit: int = 100) -> List[BorrowRecord]:
        """获取活动借阅记录"""
        return self.db.query(BorrowRecord).filter(
            BorrowRecord.status == BorrowStatus.BORROWED
        ).offset(skip).limit(limit).all()

    def save(self, borrow_record: BorrowRecord) -> BorrowRecord:
        """保存借阅记录"""
        self.db.add(borrow_record)
        self.db.commit()
        self.db.refresh(borrow_record)
        return borrow_record

    def update(self, borrow_id: str, **kwargs) -> Optional[BorrowRecord]:
        """更新借阅记录"""
        record = self.get_by_id(borrow_id)
        if record:
            for key, value in kwargs.items():
                setattr(record, key, value)
            self.db.commit()
            self.db.refresh(record)
        return record

    def delete(self, borrow_id: str) -> bool:
        """删除借阅记录"""
        record = self.get_by_id(borrow_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return True
        return False