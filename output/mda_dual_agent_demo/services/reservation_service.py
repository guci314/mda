from sqlalchemy.orm import Session
from models.reservation_record import ReservationRecordDB, ReservationStatus
from models.book import BookDB
from models.reader import ReaderDB
from datetime import datetime
import uuid

def reserve_book(db: Session, reader_id: str, isbn: str):
    book = db.query(BookDB).filter(BookDB.isbn == isbn).first()
    if not book:
        raise ValueError("图书不存在")

    reader = db.query(ReaderDB).filter(ReaderDB.reader_id == reader_id).first()
    if not reader or reader.status != '正常':
        raise ValueError("读者不存在或状态异常")

    db_reservation_record = ReservationRecordDB(
        reservation_id=str(uuid.uuid4()),
        reader_id=reader_id,
        isbn=isbn,
        reserve_date=datetime.now(),
        status=ReservationStatus.PENDING
    )
    db.add(db_reservation_record)
    db.commit()
    db.refresh(db_reservation_record)
    return db_reservation_record
