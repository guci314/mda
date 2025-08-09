from fastapi import APIRouter, Depends
from app.schemas.schemas import ReservationRecordResponse
from app.services.reservation_service import ReservationService
from app.dependencies import get_reservation_service

router = APIRouter()

@router.post("/reservations/", response_model=ReservationRecordResponse)
def reserve_book(reader_id: str, isbn: str, service: ReservationService = Depends(get_reservation_service)):
    return service.reserve_book(reader_id, isbn)
