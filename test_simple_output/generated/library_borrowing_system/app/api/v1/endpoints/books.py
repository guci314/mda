from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app import schemas, services, dependencies

router = APIRouter()

@router.post("/", response_model=schemas.Book, status_code=status.HTTP_201_CREATED)
def add_book(
    book: schemas.BookCreate, 
    db: Session = Depends(dependencies.get_db)
):
    """
    Add a new book to the library.
    """
    return services.book.create_book(db=db, book=book)

@router.get("/{isbn}", response_model=schemas.Book)
def get_book_by_isbn(
    isbn: str, 
    db: Session = Depends(dependencies.get_db)
):
    """
    Get a specific book by its ISBN.
    """
    db_book = services.book.get_book(db=db, isbn=isbn)
    if db_book is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")
    return db_book

@router.put("/{isbn}", response_model=schemas.Book)
def update_book_info(
    isbn: str, 
    book_update: schemas.BookUpdate, 
    db: Session = Depends(dependencies.get_db)
):
    """
    Update a book's information.
    """
    return services.book.update_book(db=db, isbn=isbn, book_update=book_update)

@router.get("/search/", response_model=List[schemas.Book])
def search_books(
    query: Optional[str] = Query(None, min_length=1, description="Search by title, author, or ISBN"),
    category: Optional[str] = None,
    db: Session = Depends(dependencies.get_db)
):
    """
    Search for books by title, author, ISBN, or category.
    """
    if not query and not category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A search query or category must be provided")
    
    books = services.book.search_books(db=db, query=query, category=category)
    return books

@router.delete("/{isbn}", status_code=status.HTTP_204_NO_CONTENT)
def remove_book(
    isbn: str,
    db: Session = Depends(dependencies.get_db)
):
    """
    Remove a book from the system (marks it as REMOVED).
    """
    services.book.remove_book(db=db, isbn=isbn)
    return
