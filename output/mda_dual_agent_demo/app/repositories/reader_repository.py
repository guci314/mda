from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.database import ReaderDB

class ReaderRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, reader_id: str) -> Optional[ReaderDB]:
        result = await self.db.execute(select(ReaderDB).where(ReaderDB.reader_id == reader_id))
        return result.scalars().first()

    async def save(self, reader: ReaderDB) -> None:
        self.db.add(reader)
        await self.db.commit()
        await self.db.refresh(reader)