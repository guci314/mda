from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas, models
from app.db.session import get_db
from app.services.book_service import book_service
from app.crud import book as crud_book

router = APIRouter()

@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def create_book(
    *,
    db: Session = Depends(get_db),
    book_in: schemas.BookCreate,
):
    """
    Add a new book.
    """
    return book_service.create_book(db=db, book_in=book_in)

@router.get("/", response_model=List[schemas.Book])
def search_books(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search term for title or author"),
    category: Optional[str] = Query(None, description="Filter by category"),
    skip: int = 0,
    limit: int = 100,
):
    """
    Search for books.
    """
    books = crud_book.book.search(db, q=q, category=category, skip=skip, limit=limit)
    return books

@router.get("/{isbn}", response_model=schemas.Book)
def get_book(
    *,
    db: Session = Depends(get_db),
    isbn: str,
):
    """
    Get a book by its ISBN.
    """
    return book_service.get_book_by_isbn(db=db, isbn=isbn)

@router.put("/{isbn}", response_model=schemas.Book)
def update_book(
    *,
    db: Session = Depends(get_db),
    isbn: str,
    book_in: schemas.BookUpdate,
):
    """
    Update book information.
    """
    return book_service.update_book(db=db, isbn=isbn, book_in=book_in)

@router.post("/{isbn}/remove", response_model=schemas.Message)
def remove_book(
    *,
    db: Session = Depends(get_db),
    isbn: str,
):
    """
    Remove a book (set status to OFF_SHELF).
    """
    book_service.remove_book(db=db, isbn=isbn)
    return {"message": "Book removed successfully"}
