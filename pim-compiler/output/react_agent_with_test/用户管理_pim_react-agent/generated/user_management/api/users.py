from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from ..models.user import UserCreate, UserUpdate, UserInDB
from ..services.user_service import UserService
from ..repositories.user_repository import UserRepository
from ..database.database import get_db

router = APIRouter(prefix="/users", tags=["users"])

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    """获取用户服务实例"""
    user_repo = UserRepository(db)
    return UserService(user_repo)

@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, user_service: UserService = Depends(get_user_service)):
    """注册用户"""
    return user_service.register_user(user)

@router.get("/", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    user_service: UserService = Depends(get_user_service)
):
    """查询用户列表"""
    return user_service.list_users(skip, limit)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: UUID, user_service: UserService = Depends(get_user_service)):
    """获取用户详情"""
    return user_service.get_user(user_id)

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """更新用户信息"""
    return user_service.update_user(user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: UUID, user_service: UserService = Depends(get_user_service)):
    """删除用户"""
    user_service.delete_user(user_id)