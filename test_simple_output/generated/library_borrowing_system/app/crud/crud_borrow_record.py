from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date

from app.crud.base import CRUDBase
from app.models.borrow_record import BorrowRecord
from app.models.enums import BorrowStatus
from app.schemas.borrow import BorrowCreate, BorrowUpdate

class CRUDBorrowRecord(CRUDBase[BorrowRecord, BorrowCreate, BorrowUpdate]):
    def get_by_borrow_id(self, db: Session, *, borrow_id: str) -> Optional[BorrowRecord]:
        return db.query(BorrowRecord).filter(BorrowRecord.borrow_id == borrow_id).first()

    def get_by_reader_and_book(
        self, db: Session, *, reader_id: str, isbn: str
    ) -> List[BorrowRecord]:
        return (
            db.query(BorrowRecord)
            .filter(
                and_(
                    BorrowRecord.reader_id == reader_id,
                    BorrowRecord.isbn == isbn,
                    BorrowRecord.status == BorrowStatus.BORROWED,
                )
            )
            .all()
        )

    def get_all_by_reader_id(self, db: Session, *, reader_id: str) -> List[BorrowRecord]:
        return db.query(BorrowRecord).filter(BorrowRecord.reader_id == reader_id).order_by(BorrowRecord.borrow_date.desc()).all()

    def get_active_borrows_by_reader(self, db: Session, *, reader_id: str) -> List[BorrowRecord]:
        return db.query(BorrowRecord).filter(
            and_(
                BorrowRecord.reader_id == reader_id,
                BorrowRecord.status == BorrowStatus.BORROWED
            )
        ).all()

    def get_overdue_records(self, db: Session) -> List[BorrowRecord]:
        return db.query(BorrowRecord).filter(
            and_(
                BorrowRecord.status == BorrowStatus.BORROWED,
                BorrowRecord.due_date < date.today()
            )
        ).all()


borrow_record = CRUDBorrowRecord(BorrowRecord)
