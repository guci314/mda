from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.database import BorrowRecordDB

class BorrowRecordRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, borrow_id: str) -> Optional[BorrowRecordDB]:
        result = await self.db.execute(select(BorrowRecordDB).where(BorrowRecordDB.borrow_id == borrow_id))
        return result.scalars().first()

    async def save(self, record: BorrowRecordDB) -> None:
        self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)