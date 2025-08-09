from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from services import reservation_service
from schemas.reservation_record import ReservationRecordResponse
from database import get_db

router = APIRouter()

@router.post("/reserve/", response_model=ReservationRecordResponse)
def reserve_book(reader_id: str, isbn: str, db: Session = Depends(get_db)):
    try:
        return reservation_service.reserve_book(db=db, reader_id=reader_id, isbn=isbn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
