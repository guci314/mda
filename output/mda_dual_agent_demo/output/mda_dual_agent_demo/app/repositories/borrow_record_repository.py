from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.borrow_record import BorrowRecordDB
from app.enums import BorrowStatus


class BorrowRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, borrow_id: str) -> Optional[BorrowRecordDB]:
        """根据ID获取借阅记录"""
        return self.db.query(BorrowRecordDB).filter(BorrowRecordDB.borrow_id == borrow_id).first()

    def get_by_reader(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[BorrowRecordDB]:
        """获取读者的借阅记录"""
        return self.db.query(BorrowRecordDB).filter(
            BorrowRecordDB.reader_id == reader_id
        ).offset(skip).limit(limit).all()

    def get_active_by_reader(self, reader_id: str) -> List[BorrowRecordDB]:
        """获取读者的活跃借阅记录"""
        return self.db.query(BorrowRecordDB).filter(
            BorrowRecordDB.reader_id == reader_id,
            BorrowRecordDB.status == BorrowStatus.BORROWED
        ).all()

    def save(self, borrow_record: BorrowRecordDB) -> BorrowRecordDB:
        """保存借阅记录"""
        self.db.add(borrow_record)
        self.db.commit()
        self.db.refresh(borrow_record)
        return borrow_record

    def update(self, borrow_record: BorrowRecordDB) -> BorrowRecordDB:
        """更新借阅记录"""
        self.db.commit()
        self.db.refresh(borrow_record)
        return borrow_record