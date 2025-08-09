"""
借阅路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_db
from ..models.pydantic import BorrowRecordCreate, BorrowRecordResponse, MessageResponse
from ..services.borrow_service import BorrowService

router = APIRouter(
    prefix="/borrows",
    tags=["借阅管理"],
    responses={404: {"description": "Not found"}}
)


def get_borrow_service(db: AsyncSession = Depends(get_async_db)) -> BorrowService:
    """获取借阅服务"""
    return BorrowService(db)


@router.post("/", response_model=BorrowRecordResponse, status_code=201)
async def borrow_book(
    borrow_data: BorrowRecordCreate,
    service: BorrowService = Depends(get_borrow_service)
):
    """借阅图书"""
    try:
        return await service.borrow_book(borrow_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="借阅图书失败")


@router.post("/simple", response_model=BorrowRecordResponse, status_code=201)
async def borrow_book_simple(
    reader_id: str = Query(..., description="读者ID"),
    isbn: str = Query(..., description="图书ISBN"),
    service: BorrowService = Depends(get_borrow_service)
):
    """借阅图书（简化接口）"""
    try:
        borrow_data = BorrowRecordCreate(reader_id=reader_id, isbn=isbn)
        return await service.borrow_book(borrow_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="借阅图书失败")


@router.get("/{borrow_id}", response_model=BorrowRecordResponse)
async def get_borrow_record(
    borrow_id: str,
    service: BorrowService = Depends(get_borrow_service)
):
    """获取借阅记录"""
    record = await service.get_borrow_record(borrow_id)
    if not record:
        raise HTTPException(status_code=404, detail="借阅记录不存在")
    return record


@router.get("/", response_model=List[BorrowRecordResponse])
async def get_all_borrows(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: BorrowService = Depends(get_borrow_service)
):
    """获取所有借阅记录"""
    return await service.get_all_borrows(skip=skip, limit=limit)


@router.get("/reader/{reader_id}", response_model=List[BorrowRecordResponse])
async def get_reader_borrows(
    reader_id: str,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: BorrowService = Depends(get_borrow_service)
):
    """获取读者的借阅记录"""
    return await service.get_reader_borrows(reader_id, skip=skip, limit=limit)


@router.get("/reader/{reader_id}/active", response_model=List[BorrowRecordResponse])
async def get_reader_active_borrows(
    reader_id: str,
    service: BorrowService = Depends(get_borrow_service)
):
    """获取读者的活跃借阅记录"""
    return await service.get_reader_active_borrows(reader_id)


@router.get("/book/{isbn}", response_model=List[BorrowRecordResponse])
async def get_book_borrows(
    isbn: str,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: BorrowService = Depends(get_borrow_service)
):
    """获取图书的借阅记录"""
    return await service.get_book_borrows(isbn, skip=skip, limit=limit)


@router.get("/overdue/list", response_model=List[BorrowRecordResponse])
async def get_overdue_borrows(
    service: BorrowService = Depends(get_borrow_service)
):
    """获取逾期的借阅记录"""
    return await service.get_overdue_borrows()


@router.post("/{borrow_id}/return", response_model=BorrowRecordResponse)
async def return_book(
    borrow_id: str,
    service: BorrowService = Depends(get_borrow_service)
):
    """归还图书"""
    try:
        return await service.return_book(borrow_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="归还图书失败")


@router.post("/{borrow_id}/renew", response_model=BorrowRecordResponse)
async def renew_book(
    borrow_id: str,
    service: BorrowService = Depends(get_borrow_service)
):
    """续借图书"""
    try:
        return await service.renew_book(borrow_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="续借图书失败")


@router.post("/{borrow_id}/overdue", response_model=MessageResponse)
async def mark_overdue(
    borrow_id: str,
    service: BorrowService = Depends(get_borrow_service)
):
    """标记为逾期"""
    try:
        success = await service.mark_overdue(borrow_id)
        if not success:
            raise HTTPException(status_code=404, detail="借阅记录不存在")
        return MessageResponse(message="已标记为逾期")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="标记逾期失败")


@router.post("/{borrow_id}/lost", response_model=MessageResponse)
async def mark_lost(
    borrow_id: str,
    fine: float = Query(None, ge=0, description="罚金金额"),
    service: BorrowService = Depends(get_borrow_service)
):
    """标记为丢失"""
    try:
        success = await service.mark_lost(borrow_id, fine)
        if not success:
            raise HTTPException(status_code=404, detail="借阅记录不存在")
        return MessageResponse(message="已标记为丢失")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="标记丢失失败")


@router.post("/process/overdue", response_model=dict)
async def process_overdue_books(
    service: BorrowService = Depends(get_borrow_service)
):
    """处理逾期图书"""
    try:
        processed_count = await service.process_overdue_books()
        return {
            "message": "逾期图书处理完成",
            "processed_count": processed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="处理逾期图书失败")


@router.get("/stats/count", response_model=dict)
async def get_borrow_statistics(
    service: BorrowService = Depends(get_borrow_service)
):
    """获取借阅统计信息"""
    total_count = await service.get_borrow_count()
    return {
        "total_borrows": total_count
    }