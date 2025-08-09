from sqlalchemy.orm import Session
from typing import List, Optional
from app.models.reservation_record import ReservationRecordDBDB
from app.enums import ReservationStatus


class ReservationRecordDBRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, reservation_id: str) -> Optional[ReservationRecordDB]:
        """根据ID获取预约记录"""
        return self.db.query(ReservationRecordDB).filter(
            ReservationRecordDB.reservation_id == reservation_id
        ).first()

    def get_by_reader(self, reader_id: str, skip: int = 0, limit: int = 100) -> List[ReservationRecordDB]:
        """获取读者的预约记录"""
        return self.db.query(ReservationRecordDB).filter(
            ReservationRecordDB.reader_id == reader_id
        ).offset(skip).limit(limit).all()

    def get_active_by_book(self, isbn: str) -> List[ReservationRecordDB]:
        """获取图书的活跃预约记录"""
        return self.db.query(ReservationRecordDB).filter(
            ReservationRecordDB.isbn == isbn,
            ReservationRecordDB.status == ReservationStatus.PENDING
        ).all()

    def save(self, reservation_record: ReservationRecordDB) -> ReservationRecordDB:
        """保存预约记录"""
        self.db.add(reservation_record)
        self.db.commit()
        self.db.refresh(reservation_record)
        return reservation_record

    def update(self, reservation_record: ReservationRecordDB) -> ReservationRecordDB:
        """更新预约记录"""
        self.db.commit()
        self.db.refresh(reservation_record)
        return reservation_record