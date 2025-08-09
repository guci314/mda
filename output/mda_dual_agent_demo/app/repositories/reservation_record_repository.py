from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.database import ReservationRecordDB

class ReservationRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, reservation_id: str) -> Optional[ReservationRecordDB]:
        result = await self.db.execute(select(ReservationRecordDB).where(ReservationRecordDB.reservation_id == reservation_id))
        return result.scalars().first()

    async def save(self, record: ReservationRecordDB) -> None:
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)