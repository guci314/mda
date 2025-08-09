"""
图书路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_db
from ..models.pydantic import BookCreate, BookUpdate, BookResponse, MessageResponse
from ..services.book_service import BookService

router = APIRouter(
    prefix="/books",
    tags=["图书管理"],
    responses={404: {"description": "Not found"}}
)


def get_book_service(db: AsyncSession = Depends(get_async_db)) -> BookService:
    """获取图书服务"""
    return BookService(db)


@router.post("/", response_model=BookResponse, status_code=201)
async def create_book(
    book_data: BookCreate,
    service: BookService = Depends(get_book_service)
):
    """创建图书"""
    try:
        return await service.create_book(book_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="创建图书失败")


@router.get("/{isbn}", response_model=BookResponse)
async def get_book(
    isbn: str,
    service: BookService = Depends(get_book_service)
):
    """获取图书信息"""
    book = await service.get_book(isbn)
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    return book


@router.get("/", response_model=List[BookResponse])
async def get_books(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: BookService = Depends(get_book_service)
):
    """获取图书列表"""
    return await service.get_books(skip=skip, limit=limit)


@router.get("/search/title", response_model=List[BookResponse])
async def search_books_by_title(
    title: str = Query(..., min_length=1, description="书名关键词"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: BookService = Depends(get_book_service)
):
    """根据书名搜索图书"""
    return await service.search_books_by_title(title, skip=skip, limit=limit)


@router.get("/search/author", response_model=List[BookResponse])
async def search_books_by_author(
    author: str = Query(..., min_length=1, description="作者关键词"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: BookService = Depends(get_book_service)
):
    """根据作者搜索图书"""
    return await service.search_books_by_author(author, skip=skip, limit=limit)


@router.get("/search/category", response_model=List[BookResponse])
async def search_books_by_category(
    category: str = Query(..., min_length=1, description="分类"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: BookService = Depends(get_book_service)
):
    """根据分类搜索图书"""
    return await service.search_books_by_category(category, skip=skip, limit=limit)


@router.get("/available/list", response_model=List[BookResponse])
async def get_available_books(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: BookService = Depends(get_book_service)
):
    """获取可借阅的图书"""
    return await service.get_available_books(skip=skip, limit=limit)


@router.put("/{isbn}", response_model=BookResponse)
async def update_book(
    isbn: str,
    book_data: BookUpdate,
    service: BookService = Depends(get_book_service)
):
    """更新图书信息"""
    try:
        book = await service.update_book(isbn, book_data)
        if not book:
            raise HTTPException(status_code=404, detail="图书不存在")
        return book
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新图书失败")


@router.delete("/{isbn}", response_model=MessageResponse)
async def remove_book(
    isbn: str,
    service: BookService = Depends(get_book_service)
):
    """下架图书"""
    try:
        success = await service.remove_book(isbn)
        if not success:
            raise HTTPException(status_code=404, detail="图书不存在")
        return MessageResponse(message="图书已下架")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="下架图书失败")


@router.get("/{isbn}/availability", response_model=dict)
async def check_book_availability(
    isbn: str,
    service: BookService = Depends(get_book_service)
):
    """检查图书可借状态"""
    is_available = await service.is_available_for_borrow(isbn)
    book = await service.get_book(isbn)
    
    if not book:
        raise HTTPException(status_code=404, detail="图书不存在")
    
    return {
        "isbn": isbn,
        "title": book.title,
        "is_available": is_available,
        "available_quantity": book.available_quantity,
        "total_quantity": book.total_quantity
    }


@router.get("/stats/count", response_model=dict)
async def get_book_statistics(
    service: BookService = Depends(get_book_service)
):
    """获取图书统计信息"""
    total_count = await service.get_book_count()
    return {
        "total_books": total_count
    }