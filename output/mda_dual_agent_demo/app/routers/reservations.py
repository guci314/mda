from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.pydantic import ReservationRecordResponse
from app.services.reservation_service import ReservationService
from app.dependencies import get_reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])

@router.post("/", response_model=ReservationRecordResponse)
async def reserve_book(reader_id: str, isbn: str, service: ReservationService = Depends(get_reservation_service)):
    try:
        return await service.reserve_book(reader_id, isbn)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))