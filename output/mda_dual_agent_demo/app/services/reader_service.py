from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.database import ReaderDB
from app.models.pydantic import ReaderCreate, ReaderResponse
from app.repositories.reader_repository import ReaderRepository

class ReaderService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = ReaderRepository(db)

    async def register_reader(self, reader_data: ReaderCreate) -> ReaderResponse:
        reader = ReaderDB(**reader_data.dict(), status="正常", credit_score=100)
        await self.repository.save(reader)
        return ReaderResponse.from_orm(reader)

    async def update_reader(self, reader_id: str, reader_data: ReaderCreate) -> ReaderResponse:
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            raise ValueError("读者不存在")
        for key, value in reader_data.dict().items():
            setattr(reader, key, value)
        await self.repository.save(reader)
        return ReaderResponse.from_orm(reader)

    async def freeze_reader(self, reader_id: str) -> None:
        reader = await self.repository.get_by_id(reader_id)
        if not reader:
            raise ValueError("读者不存在")
        reader.status = "冻结"
        await self.repository.save(reader)