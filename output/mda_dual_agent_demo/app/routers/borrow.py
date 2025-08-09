from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.schemas import BorrowRecordResponse
from ..services.borrowing_service import BorrowingService
from ..dependencies import get_db, get_borrowing_service

router = APIRouter(prefix="/borrow", tags=["borrow"])

@router.post("/", response_model=BorrowRecordResponse)
def borrow_book(reader_id: str, isbn: str, service: BorrowingService = Depends(get_borrowing_service)):
    return service.borrow_book(reader_id, isbn)