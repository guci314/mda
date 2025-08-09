from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..schemas.schemas import ReservationRecordResponse
from ..services.reservation_service import ReservationService
from ..dependencies import get_db, get_reservation_service

router = APIRouter(prefix="/reservation", tags=["reservation"])

@router.post("/", response_model=ReservationRecordResponse)
def reserve_book(reader_id: str, isbn: str, service: ReservationService = Depends(get_reservation_service)):
    return service.reserve_book(reader_id, isbn)