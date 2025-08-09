"""
模型包初始化
"""
from .enums import BookStatus, ReaderType, ReaderStatus, BorrowStatus, ReservationStatus
from .database import Base, BookDB, ReaderDB, BorrowRecordDB, ReservationRecordDB
from .pydantic import (
    BookCreate, BookUpdate, BookResponse,
    ReaderCreate, ReaderUpdate, ReaderResponse,
    BorrowRecordCreate, BorrowRecordResponse,
    ReservationRecordCreate, ReservationRecordResponse,
    MessageResponse, ErrorResponse,
    PaginationParams, PaginatedResponse
)

__all__ = [
    # 枚举
    "BookStatus", "ReaderType", "ReaderStatus", "BorrowStatus", "ReservationStatus",
    # 数据库模型
    "Base", "BookDB", "ReaderDB", "BorrowRecordDB", "ReservationRecordDB",
    # Pydantic模型
    "BookCreate", "BookUpdate", "BookResponse",
    "ReaderCreate", "ReaderUpdate", "ReaderResponse",
    "BorrowRecordCreate", "BorrowRecordResponse",
    "ReservationRecordCreate", "ReservationRecordResponse",
    "MessageResponse", "ErrorResponse",
    "PaginationParams", "PaginatedResponse"
]