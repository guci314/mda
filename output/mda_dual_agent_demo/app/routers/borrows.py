from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pydantic import BorrowRecordResponse
from app.services.borrowing_service import BorrowingService
from app.dependencies import get_borrowing_service

router = APIRouter(prefix="/borrows", tags=["borrows"])

@router.post("/", response_model=BorrowRecordResponse)
async def borrow_book(reader_id: str, isbn: str, service: BorrowingService = Depends(get_borrowing_service)):
    try:
        return await service.borrow_book(reader_id, isbn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{borrow_id}/return")
async def return_book(borrow_id: str, service: BorrowingService = Depends(get_borrowing_service)):
    try:
        await service.return_book(borrow_id)
        return {"message": "Book returned successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

from datetime import datetime

@router.put("/{borrow_id}/renew", response_model=datetime)
async def renew_book(borrow_id: str, service: BorrowingService = Depends(get_borrowing_service)):
    try:
        return await service.renew_book(borrow_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))