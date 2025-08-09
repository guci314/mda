from sqlalchemy.orm import Session
from typing import Optional, List
from app.models.domain import ReservationRecordDB as ReservationRecord
from app.enums import ReservationStatus


class ReservationRecordRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reservation_id: str) -> Optional[ReservationRecord]:
        """根据ID获取预约记录"""
        return self.db.query(ReservationRecord).filter(ReservationRecord.reservation_id == reservation_id).first()

    def get_by_reader(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[ReservationRecord]:
        """根据读者ID获取预约记录"""
        return self.db.query(ReservationRecord).filter(ReservationRecord.reader_id == reader_id).offset(skip).limit(limit).all()

    def get_by_book(self, isbn: str, skip: int = 0, limit: int = 100) -> List[ReservationRecord]:
        """根据ISBN获取预约记录"""
        return self.db.query(ReservationRecord).filter(ReservationRecord.isbn == isbn).offset(skip).limit(limit).all()

    def get_pending_reservations(self, skip: int = 0, limit: int = 100) -> List[ReservationRecord]:
        """获取等待中的预约"""
        return self.db.query(ReservationRecord).filter(
            ReservationRecord.status == ReservationStatus.PENDING
        ).offset(skip).limit(limit).all()

    def save(self, reservation_record: ReservationRecord) -> ReservationRecord:
        """保存预约记录"""
        self.db.add(reservation_record)
        self.db.commit()
        self.db.refresh(reservation_record)
        return reservation_record

    def update(self, reservation_id: str, **kwargs) -> Optional[ReservationRecord]:
        """更新预约记录"""
        record = self.get_by_id(reservation_id)
        if record:
            for key, value in kwargs.items():
                setattr(record, key, value)
            self.db.commit()
            self.db.refresh(record)
        return record

    def delete(self, reservation_id: str) -> bool:
        """删除预约记录"""
        record = self.get_by_id(reservation_id)
        if record:
            self.db.delete(record)
            self.db.commit()
            return True
        return False