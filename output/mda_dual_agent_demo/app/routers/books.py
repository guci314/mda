from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pydantic import BookCreate, BookResponse
from app.services.book_service import BookService
from app.dependencies import get_book_service

router = APIRouter(prefix="/books", tags=["books"])

@router.post("/", response_model=BookResponse)
async def add_book(book_data: BookCreate, service: BookService = Depends(get_book_service)):
    try:
        return await service.add_book(book_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{isbn}", response_model=BookResponse)
async def get_book(isbn: str, service: BookService = Depends(get_book_service)):
    book = await service.get_by_isbn(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@router.put("/{isbn}", response_model=BookResponse)
async def update_book(isbn: str, book_data: BookCreate, service: BookService = Depends(get_book_service)):
    try:
        return await service.update_book(isbn, book_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{isbn}")
async def remove_book(isbn: str, service: BookService = Depends(get_book_service)):
    try:
        await service.remove_book(isbn)
        return {"message": "Book removed successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))