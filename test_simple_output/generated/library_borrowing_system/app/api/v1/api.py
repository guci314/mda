from fastapi import APIRouter

from app.api.v1.endpoints import books, readers, borrowing

api_router = APIRouter()

api_router.include_router(books.router, prefix="/books", tags=["Books"])
api_router.include_router(readers.router, prefix="/readers", tags=["Readers"])
api_router.include_router(borrowing.router, prefix="/borrowing", tags=["Borrowing"])
