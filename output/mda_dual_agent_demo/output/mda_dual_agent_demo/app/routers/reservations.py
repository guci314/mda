from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from ..schemas.schemas import ReservationRecordResponse
from ..services.reservation_service import ReservationService
from ..dependencies import get_reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=ReservationRecordResponse)
def reserve_book(reader_id: str, isbn: str, service: ReservationService = Depends(get_reservation_service)):
    return service.reserve_book(reader_id, isbn)