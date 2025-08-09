from fastapi import APIRouter, Depends
from ..services.borrowing_service import BorrowingService
from ..schemas.schemas import BorrowRecordResponse

router = APIRouter(prefix="/borrow", tags=["borrowing"])

@router.post("/", response_model=BorrowRecordResponse)
async def borrow_book(reader_id: str, isbn: str, service: BorrowingService = Depends(BorrowingService)):
    """借阅图书"""
    return await service.borrow_book(reader_id, isbn)