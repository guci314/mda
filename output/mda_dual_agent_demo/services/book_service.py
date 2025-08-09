from sqlalchemy.orm import Session
from models.book import BookDB, BookStatus
from schemas.book import BookCreate

def add_book(db: Session, book: BookCreate):
    db_book = db.query(BookDB).filter(BookDB.isbn == book.isbn).first()
    if db_book:
        raise ValueError("Book with this ISBN already exists")
    
    db_book = BookDB(**book.model_dump(), status=BookStatus.AVAILABLE)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

def get_book(db: Session, isbn: str):
    return db.query(BookDB).filter(BookDB.isbn == isbn).first()
