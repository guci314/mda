from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..schemas.schemas import BorrowRecordResponse
from ..services.borrowing_service import BorrowingService
from ..dependencies import get_borrowing_service

router = APIRouter(prefix="/borrowings", tags=["borrowings"])

@router.post("/", response_model=BorrowRecordResponse)
def borrow_book(reader_id: str, isbn: str, service: BorrowingService = Depends(get_borrowing_service)):
    return service.borrow_book(reader_id, isbn)