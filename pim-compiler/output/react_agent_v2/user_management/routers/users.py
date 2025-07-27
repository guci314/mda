from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..models.user import UserCreate, UserInDB, UserUpdate, UserStatus
from ..services.user import UserService

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],  # 默认需要认证
)

# 用户注册 (不需要认证)
@router.post(
    "/register",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    dependencies=[]
)
async def register_user(user_create: UserCreate, user_service: UserService = Depends()):
    return await user_service.register_user(user_create)

# 创建用户 (需要管理员权限)
@router.post(
    "/",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_admin_permission)]
)
async def create_user(user_create: UserCreate, user_service: UserService = Depends()):
    return await user_service.create_user(user_create)

# 查询用户列表
@router.get("/", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[UserStatus] = None,
    user_service: UserService = Depends()
):
    return await user_service.list_users(skip, limit, name, email, status)

# 查询单个用户
@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: str, user_service: UserService = Depends()):
    return await user_service.get_user(user_id)

# 更新用户
@router.patch("/{user_id}", response_model=UserInDB)
async def update_user(user_id: str, user_update: UserUpdate, user_service: UserService = Depends()):
    return await user_service.update_user(user_id, user_update)

# 删除用户 (实际上是停用)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str, user_service: UserService = Depends()):
    await user_service.delete_user(user_id)