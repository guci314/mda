"""
图书仓储层
"""
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from sqlalchemy.orm import selectinload
from ..models.database import BookDB
from ..models.enums import BookStatus


class BookRepository:
    """图书仓储类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_isbn(self, isbn: str) -> Optional[BookDB]:
        """根据ISBN获取图书"""
        result = await self.db.execute(
            select(BookDB).where(BookDB.isbn == isbn)
        )
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[BookDB]:
        """获取所有图书"""
        result = await self.db.execute(
            select(BookDB)
            .where(BookDB.status == BookStatus.AVAILABLE)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_by_title(self, title: str, skip: int = 0, limit: int = 100) -> List[BookDB]:
        """根据书名搜索图书"""
        result = await self.db.execute(
            select(BookDB)
            .where(
                and_(
                    BookDB.title.ilike(f"%{title}%"),
                    BookDB.status == BookStatus.AVAILABLE
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_by_author(self, author: str, skip: int = 0, limit: int = 100) -> List[BookDB]:
        """根据作者搜索图书"""
        result = await self.db.execute(
            select(BookDB)
            .where(
                and_(
                    BookDB.author.ilike(f"%{author}%"),
                    BookDB.status == BookStatus.AVAILABLE
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def search_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[BookDB]:
        """根据分类搜索图书"""
        result = await self.db.execute(
            select(BookDB)
            .where(
                and_(
                    BookDB.category == category,
                    BookDB.status == BookStatus.AVAILABLE
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def get_available_books(self, skip: int = 0, limit: int = 100) -> List[BookDB]:
        """获取可借阅的图书"""
        result = await self.db.execute(
            select(BookDB)
            .where(
                and_(
                    BookDB.status == BookStatus.AVAILABLE,
                    BookDB.available_quantity > 0
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
    
    async def create(self, book: BookDB) -> BookDB:
        """创建图书"""
        self.db.add(book)
        await self.db.commit()
        await self.db.refresh(book)
        return book
    
    async def update(self, isbn: str, **kwargs) -> Optional[BookDB]:
        """更新图书信息"""
        await self.db.execute(
            update(BookDB)
            .where(BookDB.isbn == isbn)
            .values(**kwargs)
        )
        await self.db.commit()
        return await self.get_by_isbn(isbn)
    
    async def update_available_quantity(self, isbn: str, quantity_change: int) -> bool:
        """更新可借数量"""
        book = await self.get_by_isbn(isbn)
        if not book:
            return False
        
        new_quantity = book.available_quantity + quantity_change
        if new_quantity < 0 or new_quantity > book.total_quantity:
            return False
        
        await self.update(isbn, available_quantity=new_quantity)
        return True
    
    async def remove(self, isbn: str) -> bool:
        """下架图书（软删除）"""
        book = await self.get_by_isbn(isbn)
        if not book:
            return False
        
        await self.update(isbn, status=BookStatus.REMOVED)
        return True
    
    async def count_total(self) -> int:
        """统计图书总数"""
        result = await self.db.execute(
            select(BookDB).where(BookDB.status == BookStatus.AVAILABLE)
        )
        return len(result.scalars().all())
    
    async def exists(self, isbn: str) -> bool:
        """检查图书是否存在"""
        book = await self.get_by_isbn(isbn)
        return book is not None and book.status == BookStatus.AVAILABLE