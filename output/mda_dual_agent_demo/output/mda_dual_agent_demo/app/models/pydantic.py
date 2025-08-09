"""
Pydantic模型定义
用于API请求和响应的数据传输对象(DTO)
"""
from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal
from .enums import BookStatus, ReaderType, ReaderStatus, BorrowStatus, ReservationStatus


# 图书相关模型
class BookBase(BaseModel):
    """图书基础模型"""
    title: str = Field(..., min_length=1, max_length=100, description="书名")
    author: str = Field(..., min_length=1, max_length=50, description="作者")
    publisher: str = Field(..., min_length=1, max_length=50, description="出版社")
    publish_year: int = Field(..., gt=1900, le=2030, description="出版年份")
    category: str = Field(..., min_length=1, max_length=20, description="分类")
    total_quantity: int = Field(..., gt=0, description="总库存")
    available_quantity: int = Field(..., ge=0, description="可借数量")
    location: str = Field(..., min_length=1, max_length=20, description="存放位置")
    description: Optional[str] = Field(None, description="图书描述")


class BookCreate(BookBase):
    """创建图书请求模型"""
    isbn: str = Field(..., min_length=10, max_length=20, description="ISBN号")


class BookUpdate(BookBase):
    """更新图书请求模型"""
    pass


class BookResponse(BookBase):
    """图书响应模型"""
    isbn: str
    status: BookStatus
    
    model_config = ConfigDict(from_attributes=True)


# 读者相关模型
class ReaderBase(BaseModel):
    """读者基础模型"""
    name: str = Field(..., min_length=1, max_length=50, description="姓名")
    id_card: str = Field(..., min_length=15, max_length=18, description="身份证号")
    phone: str = Field(..., min_length=11, max_length=11, description="手机号")
    email: Optional[EmailStr] = Field(None, description="邮箱")
    reader_type: ReaderType = Field(..., description="读者类型")


class ReaderCreate(ReaderBase):
    """创建读者请求模型"""
    pass


class ReaderUpdate(ReaderBase):
    """更新读者请求模型"""
    pass


class ReaderResponse(ReaderBase):
    """读者响应模型"""
    reader_id: str
    register_date: datetime
    valid_until: date
    status: ReaderStatus
    credit_score: int
    
    model_config = ConfigDict(from_attributes=True)


# 借阅记录相关模型
class BorrowRecordCreate(BaseModel):
    """创建借阅记录请求模型"""
    reader_id: str = Field(..., description="读者ID")
    isbn: str = Field(..., description="图书ISBN")


class BorrowRecordResponse(BaseModel):
    """借阅记录响应模型"""
    borrow_id: str
    reader_id: str
    isbn: str
    borrow_date: datetime
    due_date: date
    return_date: Optional[datetime]
    renew_count: int
    status: BorrowStatus
    fine: Optional[Decimal]
    
    model_config = ConfigDict(from_attributes=True)


# 预约记录相关模型
class ReservationRecordCreate(BaseModel):
    """创建预约记录请求模型"""
    reader_id: str = Field(..., description="读者ID")
    isbn: str = Field(..., description="图书ISBN")


class ReservationRecordResponse(BaseModel):
    """预约记录响应模型"""
    reservation_id: str
    reader_id: str
    isbn: str
    reserve_date: datetime
    status: ReservationStatus
    notify_date: Optional[datetime]
    expire_date: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# 通用响应模型
class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None


# 分页模型
class PaginationParams(BaseModel):
    """分页参数模型"""
    page: int = Field(1, ge=1, description="页码")
    size: int = Field(10, ge=1, le=100, description="每页数量")


class PaginatedResponse(BaseModel):
    """分页响应模型"""
    items: List[dict]
    total: int
    page: int
    size: int
    pages: int