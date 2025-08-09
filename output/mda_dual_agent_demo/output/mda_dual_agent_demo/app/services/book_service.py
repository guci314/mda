"""
图书服务层
"""
import uuid
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ..models.database import BookDB
from ..models.pydantic import BookCreate, BookUpdate, BookResponse
from ..models.enums import BookStatus
from ..repositories.book_repository import BookRepository


class BookService:
    """图书服务类"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repository = BookRepository(db)
    
    async def create_book(self, book_data: BookCreate) -> BookResponse:
        """创建图书"""
        # 检查ISBN是否已存在
        existing_book = await self.repository.get_by_isbn(book_data.isbn)
        if existing_book:
            raise ValueError(f"图书ISBN {book_data.isbn} 已存在")
        
        # 验证数据
        if book_data.available_quantity > book_data.total_quantity:
            raise ValueError("可借数量不能大于总库存")
        
        if book_data.available_quantity < 0:
            raise ValueError("可借数量不能为负数")
        
        # 创建数据库模型
        book_db = BookDB(
            isbn=book_data.isbn,
            title=book_data.title,
            author=book_data.author,
            publisher=book_data.publisher,
            publish_year=book_data.publish_year,
            category=book_data.category,
            total_quantity=book_data.total_quantity,
            available_quantity=book_data.available_quantity,
            location=book_data.location,
            description=book_data.description,
            status=BookStatus.AVAILABLE
        )
        
        # 保存到数据库
        created_book = await self.repository.create(book_db)
        
        # 转换为响应模型
        return BookResponse.model_validate(created_book)
    
    async def get_book(self, isbn: str) -> Optional[BookResponse]:
        """获取图书信息"""
        book = await self.repository.get_by_isbn(isbn)
        if not book:
            return None
        
        return BookResponse.model_validate(book)
    
    async def get_books(self, skip: int = 0, limit: int = 100) -> List[BookResponse]:
        """获取图书列表"""
        books = await self.repository.get_all(skip=skip, limit=limit)
        return [BookResponse.model_validate(book) for book in books]
    
    async def search_books_by_title(self, title: str, skip: int = 0, limit: int = 100) -> List[BookResponse]:
        """根据书名搜索图书"""
        books = await self.repository.search_by_title(title, skip=skip, limit=limit)
        return [BookResponse.model_validate(book) for book in books]
    
    async def search_books_by_author(self, author: str, skip: int = 0, limit: int = 100) -> List[BookResponse]:
        """根据作者搜索图书"""
        books = await self.repository.search_by_author(author, skip=skip, limit=limit)
        return [BookResponse.model_validate(book) for book in books]
    
    async def search_books_by_category(self, category: str, skip: int = 0, limit: int = 100) -> List[BookResponse]:
        """根据分类搜索图书"""
        books = await self.repository.search_by_category(category, skip=skip, limit=limit)
        return [BookResponse.model_validate(book) for book in books]
    
    async def get_available_books(self, skip: int = 0, limit: int = 100) -> List[BookResponse]:
        """获取可借阅的图书"""
        books = await self.repository.get_available_books(skip=skip, limit=limit)
        return [BookResponse.model_validate(book) for book in books]
    
    async def update_book(self, isbn: str, book_data: BookUpdate) -> Optional[BookResponse]:
        """更新图书信息"""
        # 检查图书是否存在
        existing_book = await self.repository.get_by_isbn(isbn)
        if not existing_book:
            raise ValueError(f"图书ISBN {isbn} 不存在")
        
        # 验证数据
        if book_data.available_quantity > book_data.total_quantity:
            raise ValueError("可借数量不能大于总库存")
        
        if book_data.available_quantity < 0:
            raise ValueError("可借数量不能为负数")
        
        # 更新图书信息
        updated_book = await self.repository.update(
            isbn,
            title=book_data.title,
            author=book_data.author,
            publisher=book_data.publisher,
            publish_year=book_data.publish_year,
            category=book_data.category,
            total_quantity=book_data.total_quantity,
            available_quantity=book_data.available_quantity,
            location=book_data.location,
            description=book_data.description
        )
        
        if not updated_book:
            return None
        
        return BookResponse.model_validate(updated_book)
    
    async def remove_book(self, isbn: str) -> bool:
        """下架图书"""
        # 检查图书是否存在
        book = await self.repository.get_by_isbn(isbn)
        if not book:
            raise ValueError(f"图书ISBN {isbn} 不存在")
        
        # 检查是否有未归还的借阅记录
        # 这里应该调用借阅服务检查，为简化直接在仓储层处理
        
        return await self.repository.remove(isbn)
    
    async def increase_available_quantity(self, isbn: str, quantity: int = 1) -> bool:
        """增加可借数量（归还时调用）"""
        if quantity <= 0:
            raise ValueError("数量必须大于0")
        
        return await self.repository.update_available_quantity(isbn, quantity)
    
    async def decrease_available_quantity(self, isbn: str, quantity: int = 1) -> bool:
        """减少可借数量（借阅时调用）"""
        if quantity <= 0:
            raise ValueError("数量必须大于0")
        
        book = await self.repository.get_by_isbn(isbn)
        if not book:
            raise ValueError(f"图书ISBN {isbn} 不存在")
        
        if book.available_quantity < quantity:
            raise ValueError("可借数量不足")
        
        return await self.repository.update_available_quantity(isbn, -quantity)
    
    async def is_available_for_borrow(self, isbn: str) -> bool:
        """检查图书是否可借"""
        book = await self.repository.get_by_isbn(isbn)
        if not book:
            return False
        
        return (book.status == BookStatus.AVAILABLE and 
                book.available_quantity > 0)
    
    async def get_book_count(self) -> int:
        """获取图书总数"""
        return await self.repository.count_total()
    
    async def book_exists(self, isbn: str) -> bool:
        """检查图书是否存在"""
        return await self.repository.exists(isbn)