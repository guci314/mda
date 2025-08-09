from sqlalchemy.orm import Session
from models.borrow_record import BorrowRecordDB, BorrowStatus
from models.book import BookDB
from models.reader import ReaderDB
from datetime import datetime, date, timedelta
import uuid

def borrow_book(db: Session, reader_id: str, isbn: str):
    book = db.query(BookDB).filter(BookDB.isbn == isbn).first()
    if not book or book.available_quantity <= 0:
        raise ValueError("图书不存在或已借完")

    reader = db.query(ReaderDB).filter(ReaderDB.reader_id == reader_id).first()
    if not reader or reader.status != '正常':
        raise ValueError("读者不存在或状态异常")

    borrow_date = datetime.now()
    due_date = date.today() + timedelta(days=30)

    db_borrow_record = BorrowRecordDB(
        borrow_id=str(uuid.uuid4()),
        reader_id=reader_id,
        isbn=isbn,
        borrow_date=borrow_date,
        due_date=due_date,
        status=BorrowStatus.BORROWED
    )

    book.available_quantity -= 1
    db.add(db_borrow_record)
    db.commit()
    db.refresh(db_borrow_record)
    return db_borrow_record
