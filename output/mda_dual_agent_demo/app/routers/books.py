from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.schemas import BookCreate, BookResponse
from ..services.book_service import BookService
from ..database import get_db

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookResponse)
def add_book(book_data: BookCreate, db: Session = Depends(get_db)):
    service = BookService(db)
    return service.add_book(book_data)

@router.get("/{isbn}", response_model=BookResponse)
def get_book(isbn: str, db: Session = Depends(get_db)):
    service = BookService(db)
    book = service.get_book(isbn)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book