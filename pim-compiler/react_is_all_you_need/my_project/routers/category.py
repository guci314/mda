from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from repositories.category import CategoryRepository
from services.category import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])

def get_category_service(db: Session = Depends(get_db)):
    """获取分类服务依赖"""
    repository = CategoryRepository(db)
    return CategoryService(repository)

@router.get("/", response_model=List[CategoryResponse])
async def list_categories(service: CategoryService = Depends(get_category_service)):
    """获取分类列表"""
    categories = service.list_categories()
    return categories

@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_data: CategoryCreate,
    service: CategoryService = Depends(get_category_service)
):
    """创建分类"""
    try:
        category = service.create_category(category_data)
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service)
):
    """获取分类详情"""
    category = service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service)
):
    """更新分类"""
    try:
        category = service.update_category(category_id, category_data)
        if not category:
            raise HTTPException(status_code=404, detail="分类不存在")
        return category
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}")
async def delete_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service)
):
    """删除分类"""
    success = service.delete_category(category_id)
    if not success:
        raise HTTPException(status_code=404, detail="分类不存在")
    return {"message": "分类删除成功"}