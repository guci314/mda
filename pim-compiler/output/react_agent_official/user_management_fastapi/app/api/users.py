from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from sqlalchemy.orm import Session
from ..schemas.user import UserCreate, UserUpdate, UserInDB, UserStatus
from ..services.user_service import UserService
from ..models.user import User
from ..dependencies import get_db, get_current_admin_user, get_current_user_or_admin

router = APIRouter(prefix="/api/users", tags=["users"])

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate, user_service: UserService = Depends(get_user_service)):
    """
    用户注册
    - 验证信息完整性
    - 验证邮箱和电话格式
    - 检查邮箱唯一性
    - 生成唯一标识符
    - 设置默认状态为活跃
    - 记录创建时间
    """
    return await user_service.register_user(user_create)

@router.post("", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, 
                     user_service: UserService = Depends(get_user_service),
                     current_user: UserInDB = Depends(get_current_admin_user)):
    """创建用户 (管理员权限)"""
    return await user_service.create_user(user_create)

@router.get("", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[UserStatus] = None,
    user_service: UserService = Depends(get_user_service),
    current_user: UserInDB = Depends(get_current_admin_user)
):
    """查询用户列表 (分页, 支持条件过滤)"""
    return await user_service.list_users(skip=skip, limit=limit, name=name, email=email, status=status)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserInDB = Depends(get_current_user_or_admin)
):
    """获取用户详情"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: UserInDB = Depends(get_current_user_or_admin)
):
    """更新用户信息"""
    return await user_service.update_user(user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(get_user_service),
    current_user: UserInDB = Depends(get_current_admin_user)
):
    """删除/停用用户"""
    await user_service.delete_user(user_id)
    return None