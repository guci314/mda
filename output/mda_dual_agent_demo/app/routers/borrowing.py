from fastapi import APIRouter, Depends
from app.schemas.schemas import BorrowRecordResponse
from app.services.borrowing_service import BorrowingService
from app.dependencies import get_borrowing_service

router = APIRouter()

@router.post("/borrow/", response_model=BorrowRecordResponse)
def borrow_book(reader_id: str, isbn: str, service: BorrowingService = Depends(get_borrowing_service)):
    return service.borrow_book(reader_id, isbn)
