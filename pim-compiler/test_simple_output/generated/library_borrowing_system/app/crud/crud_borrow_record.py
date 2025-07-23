from typing import List, Optional
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.borrow_record import BorrowRecord, BorrowStatus
from app.schemas.borrow_record import BorrowRecordCreate, BorrowRecordUpdate

class CRUDBorrowRecord(CRUDBase[BorrowRecord, BorrowRecordCreate, BorrowRecordUpdate]):
    def get_by_borrow_id(self, db: Session, *, borrow_id: str) -> Optional[BorrowRecord]:
        return db.query(BorrowRecord).filter(BorrowRecord.borrow_id == borrow_id).first()

    def get_active_borrow_by_book(self, db: Session, *, reader_id: str, isbn: str) -> Optional[BorrowRecord]:
        return db.query(BorrowRecord).filter(
            BorrowRecord.reader_id == reader_id,
            BorrowRecord.isbn == isbn,
            BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.OVERDUE])
        ).first()

    def get_borrow_history_by_reader(self, db: Session, *, reader_id: str, skip: int = 0, limit: int = 100) -> List[BorrowRecord]:
        return db.query(BorrowRecord).filter(BorrowRecord.reader_id == reader_id).order_by(
            BorrowRecord.borrow_date.desc()
        ).offset(skip).limit(limit).all()

    def count_active_borrows_by_reader(self, db: Session, *, reader_id: str) -> int:
        return db.query(BorrowRecord).filter(
            BorrowRecord.reader_id == reader_id,
            BorrowRecord.status.in_([BorrowStatus.BORROWED, BorrowStatus.OVERDUE])
        ).count()

borrow_record = CRUDBorrowRecord(BorrowRecord)
