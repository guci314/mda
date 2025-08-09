from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from ..models.domain import ReservationRecordDB, BookDB
from ..schemas.schemas import ReservationRecordResponse

class ReservationService:
    def __init__(self, db: Session):
        self.db = db

    def reserve_book(self, reader_id: str, isbn: str) -> ReservationRecordResponse:
        """预约图书"""
        book = self.db.query(BookDB).filter(BookDB.isbn == isbn).first()
        if not book or book.status != "在架":
            raise ValueError("图书不可预约")
        reservation = ReservationRecordDB(
            reservation_id=str(uuid4()),
            reader_id=reader_id,
            isbn=isbn,
            reserve_date=datetime.now(),
            status="等待中",
            expire_date=datetime.now() + timedelta(days=7)
        )
        self.db.add(reservation)
        self.db.commit()
        self.db.refresh(reservation)
        return ReservationRecordResponse(**reservation.__dict__)