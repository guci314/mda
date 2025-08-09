"""
预约路由
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_db
from ..models.pydantic import ReservationRecordCreate, ReservationRecordResponse, MessageResponse
from ..services.reservation_service import ReservationService

router = APIRouter(
    prefix="/reservations",
    tags=["预约管理"],
    responses={404: {"description": "Not found"}}
)


def get_reservation_service(db: AsyncSession = Depends(get_async_db)) -> ReservationService:
    """获取预约服务"""
    return ReservationService(db)


@router.post("/", response_model=ReservationRecordResponse, status_code=201)
async def reserve_book(
    reservation_data: ReservationRecordCreate,
    service: ReservationService = Depends(get_reservation_service)
):
    """预约图书"""
    try:
        return await service.reserve_book(reservation_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="预约图书失败")


@router.post("/simple", response_model=ReservationRecordResponse, status_code=201)
async def reserve_book_simple(
    reader_id: str = Query(..., description="读者ID"),
    isbn: str = Query(..., description="图书ISBN"),
    service: ReservationService = Depends(get_reservation_service)
):
    """预约图书（简化接口）"""
    try:
        reservation_data = ReservationRecordCreate(reader_id=reader_id, isbn=isbn)
        return await service.reserve_book(reservation_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="预约图书失败")


@router.get("/{reservation_id}", response_model=ReservationRecordResponse)
async def get_reservation(
    reservation_id: str,
    service: ReservationService = Depends(get_reservation_service)
):
    """获取预约记录"""
    record = await service.get_reservation(reservation_id)
    if not record:
        raise HTTPException(status_code=404, detail="预约记录不存在")
    return record


@router.get("/", response_model=List[ReservationRecordResponse])
async def get_all_reservations(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: ReservationService = Depends(get_reservation_service)
):
    """获取所有预约记录"""
    return await service.get_all_reservations(skip=skip, limit=limit)


@router.get("/reader/{reader_id}", response_model=List[ReservationRecordResponse])
async def get_reader_reservations(
    reader_id: str,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: ReservationService = Depends(get_reservation_service)
):
    """获取读者的预约记录"""
    return await service.get_reader_reservations(reader_id, skip=skip, limit=limit)


@router.get("/reader/{reader_id}/active", response_model=List[ReservationRecordResponse])
async def get_reader_active_reservations(
    reader_id: str,
    service: ReservationService = Depends(get_reservation_service)
):
    """获取读者的活跃预约记录"""
    return await service.get_reader_active_reservations(reader_id)


@router.get("/book/{isbn}", response_model=List[ReservationRecordResponse])
async def get_book_reservations(
    isbn: str,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: ReservationService = Depends(get_reservation_service)
):
    """获取图书的预约记录"""
    return await service.get_book_reservations(isbn, skip=skip, limit=limit)


@router.get("/book/{isbn}/pending", response_model=List[ReservationRecordResponse])
async def get_book_pending_reservations(
    isbn: str,
    service: ReservationService = Depends(get_reservation_service)
):
    """获取图书的等待预约记录"""
    return await service.get_book_pending_reservations(isbn)


@router.get("/ready/list", response_model=List[ReservationRecordResponse])
async def get_ready_reservations(
    service: ReservationService = Depends(get_reservation_service)
):
    """获取可借阅状态的预约记录"""
    return await service.get_ready_reservations()


@router.post("/{reservation_id}/cancel", response_model=MessageResponse)
async def cancel_reservation(
    reservation_id: str,
    service: ReservationService = Depends(get_reservation_service)
):
    """取消预约"""
    try:
        success = await service.cancel_reservation(reservation_id)
        if not success:
            raise HTTPException(status_code=404, detail="预约记录不存在")
        return MessageResponse(message="预约已取消")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="取消预约失败")


@router.post("/{reservation_id}/notify", response_model=MessageResponse)
async def notify_reservation_ready(
    reservation_id: str,
    service: ReservationService = Depends(get_reservation_service)
):
    """通知预约可借阅"""
    try:
        success = await service.notify_reservation_ready(reservation_id)
        if not success:
            raise HTTPException(status_code=404, detail="预约记录不存在")
        return MessageResponse(message="已通知预约可借阅")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="通知预约失败")


@router.post("/{reservation_id}/complete", response_model=MessageResponse)
async def complete_reservation(
    reservation_id: str,
    service: ReservationService = Depends(get_reservation_service)
):
    """完成预约（已借阅）"""
    try:
        success = await service.complete_reservation(reservation_id)
        if not success:
            raise HTTPException(status_code=404, detail="预约记录不存在")
        return MessageResponse(message="预约已完成")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="完成预约失败")


@router.get("/queue/{reader_id}/{isbn}", response_model=dict)
async def get_reservation_queue_position(
    reader_id: str,
    isbn: str,
    service: ReservationService = Depends(get_reservation_service)
):
    """获取读者在图书预约队列中的位置"""
    position = await service.get_reservation_queue_position(reader_id, isbn)
    
    if position is None:
        return {
            "reader_id": reader_id,
            "isbn": isbn,
            "has_reservation": False,
            "queue_position": None
        }
    
    return {
        "reader_id": reader_id,
        "isbn": isbn,
        "has_reservation": True,
        "queue_position": position
    }


@router.post("/process/book-return/{isbn}", response_model=dict)
async def process_book_return(
    isbn: str,
    service: ReservationService = Depends(get_reservation_service)
):
    """处理图书归还后的预约通知"""
    try:
        notified_count = await service.process_book_return(isbn)
        return {
            "message": "图书归还处理完成",
            "notified_count": notified_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="处理图书归还失败")


@router.post("/process/expired", response_model=dict)
async def process_expired_reservations(
    service: ReservationService = Depends(get_reservation_service)
):
    """处理过期的预约"""
    try:
        processed_count = await service.process_expired_reservations()
        return {
            "message": "过期预约处理完成",
            "processed_count": processed_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="处理过期预约失败")


@router.get("/stats/count", response_model=dict)
async def get_reservation_statistics(
    service: ReservationService = Depends(get_reservation_service)
):
    """获取预约统计信息"""
    total_count = await service.get_reservation_count()
    return {
        "total_reservations": total_count
    }