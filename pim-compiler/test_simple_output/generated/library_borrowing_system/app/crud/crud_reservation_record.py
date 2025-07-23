from typing import Optional, List
from sqlalchemy.orm import Session
from app.crud.base import CRUDBase
from app.models.reservation_record import ReservationRecord, ReservationStatus
from app.schemas.reservation_record import ReservationRecordCreate, ReservationRecordUpdate

class CRUDReservationRecord(CRUDBase[ReservationRecord, ReservationRecordCreate, ReservationRecordUpdate]):
    def get_by_reservation_id(self, db: Session, *, reservation_id: str) -> Optional[ReservationRecord]:
        return db.query(ReservationRecord).filter(ReservationRecord.reservation_id == reservation_id).first()

    def get_active_reservation_by_book(self, db: Session, *, reader_id: str, isbn: str) -> Optional[ReservationRecord]:
        return db.query(ReservationRecord).filter(
            ReservationRecord.reader_id == reader_id,
            ReservationRecord.isbn == isbn,
            ReservationRecord.status.in_([ReservationStatus.WAITING, ReservationStatus.AVAILABLE])
        ).first()
        
    def get_waiting_list_for_book(self, db: Session, *, isbn: str) -> List[ReservationRecord]:
        return db.query(ReservationRecord).filter(
            ReservationRecord.isbn == isbn,
            ReservationRecord.status == ReservationStatus.WAITING
        ).order_by(ReservationRecord.reservation_date.asc()).all()

reservation_record = CRUDReservationRecord(ReservationRecord)
