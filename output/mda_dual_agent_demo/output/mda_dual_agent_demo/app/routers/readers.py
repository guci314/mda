"""
读者路由
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from ..database import get_async_db
from ..models.pydantic import ReaderCreate, ReaderUpdate, ReaderResponse, MessageResponse
from ..models.enums import ReaderType, ReaderStatus
from ..services.reader_service import ReaderService

router = APIRouter(
    prefix="/readers",
    tags=["读者管理"],
    responses={404: {"description": "Not found"}}
)


def get_reader_service(db: AsyncSession = Depends(get_async_db)) -> ReaderService:
    """获取读者服务"""
    return ReaderService(db)


@router.post("/", response_model=ReaderResponse, status_code=201)
async def register_reader(
    reader_data: ReaderCreate,
    service: ReaderService = Depends(get_reader_service)
):
    """注册读者"""
    try:
        return await service.register_reader(reader_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="注册读者失败")


@router.get("/{reader_id}", response_model=ReaderResponse)
async def get_reader(
    reader_id: str,
    service: ReaderService = Depends(get_reader_service)
):
    """获取读者信息"""
    reader = await service.get_reader(reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="读者不存在")
    return reader


@router.get("/", response_model=List[ReaderResponse])
async def get_readers(
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: ReaderService = Depends(get_reader_service)
):
    """获取读者列表"""
    return await service.get_readers(skip=skip, limit=limit)


@router.get("/type/{reader_type}", response_model=List[ReaderResponse])
async def get_readers_by_type(
    reader_type: ReaderType,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: ReaderService = Depends(get_reader_service)
):
    """根据类型获取读者"""
    return await service.get_readers_by_type(reader_type, skip=skip, limit=limit)


@router.get("/status/{status}", response_model=List[ReaderResponse])
async def get_readers_by_status(
    status: ReaderStatus,
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: ReaderService = Depends(get_reader_service)
):
    """根据状态获取读者"""
    return await service.get_readers_by_status(status, skip=skip, limit=limit)


@router.get("/search/name", response_model=List[ReaderResponse])
async def search_readers_by_name(
    name: str = Query(..., min_length=1, description="姓名关键词"),
    skip: int = Query(0, ge=0, description="跳过的记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回的记录数"),
    service: ReaderService = Depends(get_reader_service)
):
    """根据姓名搜索读者"""
    return await service.search_readers_by_name(name, skip=skip, limit=limit)


@router.put("/{reader_id}", response_model=ReaderResponse)
async def update_reader(
    reader_id: str,
    reader_data: ReaderUpdate,
    service: ReaderService = Depends(get_reader_service)
):
    """更新读者信息"""
    try:
        reader = await service.update_reader(reader_id, reader_data)
        if not reader:
            raise HTTPException(status_code=404, detail="读者不存在")
        return reader
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新读者失败")


@router.post("/{reader_id}/freeze", response_model=MessageResponse)
async def freeze_reader(
    reader_id: str,
    service: ReaderService = Depends(get_reader_service)
):
    """冻结读者"""
    try:
        success = await service.freeze_reader(reader_id)
        if not success:
            raise HTTPException(status_code=404, detail="读者不存在")
        return MessageResponse(message="读者已冻结")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="冻结读者失败")


@router.post("/{reader_id}/unfreeze", response_model=MessageResponse)
async def unfreeze_reader(
    reader_id: str,
    service: ReaderService = Depends(get_reader_service)
):
    """解冻读者"""
    try:
        success = await service.unfreeze_reader(reader_id)
        if not success:
            raise HTTPException(status_code=404, detail="读者不存在")
        return MessageResponse(message="读者已解冻")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="解冻读者失败")


@router.delete("/{reader_id}", response_model=MessageResponse)
async def delete_reader(
    reader_id: str,
    service: ReaderService = Depends(get_reader_service)
):
    """注销读者"""
    try:
        success = await service.delete_reader(reader_id)
        if not success:
            raise HTTPException(status_code=404, detail="读者不存在")
        return MessageResponse(message="读者已注销")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="注销读者失败")


@router.get("/{reader_id}/status", response_model=dict)
async def check_reader_status(
    reader_id: str,
    service: ReaderService = Depends(get_reader_service)
):
    """检查读者状态"""
    reader = await service.get_reader(reader_id)
    if not reader:
        raise HTTPException(status_code=404, detail="读者不存在")
    
    is_active = await service.is_reader_active(reader_id)
    is_valid = await service.is_reader_valid(reader_id)
    can_borrow, reason = await service.can_borrow(reader_id)
    
    return {
        "reader_id": reader_id,
        "name": reader.name,
        "status": reader.status,
        "is_active": is_active,
        "is_valid": is_valid,
        "can_borrow": can_borrow,
        "borrow_reason": reason,
        "credit_score": reader.credit_score,
        "valid_until": reader.valid_until
    }


@router.post("/{reader_id}/credit", response_model=MessageResponse)
async def update_credit_score(
    reader_id: str,
    score_change: int = Query(..., ge=-50, le=50, description="信用分变化"),
    service: ReaderService = Depends(get_reader_service)
):
    """更新读者信用分"""
    try:
        success = await service.update_credit_score(reader_id, score_change)
        if not success:
            raise HTTPException(status_code=404, detail="读者不存在")
        return MessageResponse(message=f"信用分已更新，变化：{score_change}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="更新信用分失败")


@router.get("/stats/count", response_model=dict)
async def get_reader_statistics(
    service: ReaderService = Depends(get_reader_service)
):
    """获取读者统计信息"""
    total_count = await service.get_reader_count()
    return {
        "total_readers": total_count
    }