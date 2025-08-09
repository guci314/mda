"""
依赖注入配置
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_async_db
from app.services.book_service import BookService
from app.services.reader_service import ReaderService
from app.services.borrow_service import BorrowService
from app.services.reservation_service import ReservationService


async def get_book_service(db: AsyncSession = Depends(get_async_db)) -> BookService:
    """获取图书服务"""
    return BookService(db)


async def get_reader_service(db: AsyncSession = Depends(get_async_db)) -> ReaderService:
    """获取读者服务"""
    return ReaderService(db)


async def get_borrow_service(db: AsyncSession = Depends(get_async_db)) -> BorrowService:
    """获取借阅服务"""
    return BorrowService(db)


async def get_reservation_service(db: AsyncSession = Depends(get_async_db)) -> ReservationService:
    """获取预约服务"""
    return ReservationService(db)