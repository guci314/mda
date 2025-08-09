from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from app.models.database import BookDB

class BookRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_isbn(self, isbn: str) -> Optional[BookDB]:
        result = await self.db.execute(select(BookDB).where(BookDB.isbn == isbn))
        return result.scalars().first()

    async def save(self, book: BookDB) -> None:
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)