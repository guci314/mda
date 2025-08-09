from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.reservation_record import ReservationRecord
from app.enums import ReservationStatus


class ReservationRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reservation_id: str) -> Optional[ReservationRecord]:
        """根据ID获取预约记录"""
        return self.db.query(ReservationRecord).filter(
            ReservationRecord.reservation_id == reservation_id
        ).first()

    def get_by_reader(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[ReservationRecord]:
        """获取读者的预约记录"""
        return self.db.query(ReservationRecord).filter(
            ReservationRecord.reader_id == reader_id
        ).offset(skip).limit(limit).all()

    def get_active_by_book(self, isbn: str) -> List[ReservationRecord]:
        """获取图书的活跃预约记录"""
        return self.db.query(ReservationRecord).filter(
            ReservationRecord.isbn == isbn,
            ReservationRecord.status == ReservationStatus.PENDING
        ).all()

    def save(self, reservation_record: ReservationRecord) -> ReservationRecord:
        """保存预约记录"""
        self.db.add(reservation_record)
        self.db.commit()
        self.db.refresh(reservation_record)
        return reservation_record

    def update(self, reservation_record: ReservationRecord) -> ReservationRecord:
        """更新预约记录"""
        self.db.commit()
        self.db.refresh(reservation_record)
        return reservation_record