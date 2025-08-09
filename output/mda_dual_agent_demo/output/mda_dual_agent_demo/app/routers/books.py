from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..schemas.schemas import BookCreate, BookResponse
from ..services.book_service import BookService
from ..dependencies import get_book_service

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookResponse)
def add_book(book_data: BookCreate, service: BookService = Depends(get_book_service)):
    return service.add_book(book_data)

@router.get("/{isbn}", response_model=BookResponse)
def get_book(isbn: str, service: BookService = Depends(get_book_service)):
    book = service.get_book(isbn)
    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")
    return book