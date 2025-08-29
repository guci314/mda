from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from services.category_service import CategoryService
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse

router = APIRouter()


@router.post("/", response_model=CategoryResponse)
def create_category(
    category: CategoryCreate,
    db: Session = Depends(get_db)
):
    """创建新分类"""
    service = CategoryService(db)
    try:
        return service.create_category(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[CategoryResponse])
def get_categories(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=100, description="返回记录数"),
    db: Session = Depends(get_db)
):
    """获取分类列表"""
    service = CategoryService(db)
    return service.get_categories(skip=skip, limit=limit)


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """根据ID获取分类"""
    service = CategoryService(db)
    category = service.get_category_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    category: CategoryUpdate,
    db: Session = Depends(get_db)
):
    """更新分类"""
    service = CategoryService(db)
    try:
        updated_category = service.update_category(category_id, category)
        if not updated_category:
            raise HTTPException(status_code=404, detail="分类不存在")
        return updated_category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{category_id}")
def delete_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """删除分类"""
    service = CategoryService(db)
    success = service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "分类删除成功"}