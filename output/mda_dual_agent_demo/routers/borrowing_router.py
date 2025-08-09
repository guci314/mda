from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services import borrowing_service
from schemas.borrow_record import BorrowRecordResponse
from database import get_db

router = APIRouter()

@router.post("/borrow/", response_model=BorrowRecordResponse)
def borrow_book(reader_id: str, isbn: str, db: Session = Depends(get_db)):
    try:
        return borrowing_service.borrow_book(db=db, reader_id=reader_id, isbn=isbn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
