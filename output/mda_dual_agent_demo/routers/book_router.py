from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services import book_service
from schemas.book import BookCreate, BookResponse
from database import get_db

router = APIRouter()

@router.post("/books/", response_model=BookResponse)
def add_book(book: BookCreate, db: Session = Depends(get_db)):
    try:
        return book_service.add_book(db=db, book=book)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/books/{isbn}", response_model=BookResponse)
def get_book(isbn: str, db: Session = Depends(get_db)):
    db_book = book_service.get_book(db, isbn=isbn)
    if db_book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book
