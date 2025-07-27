from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User
from ..repositories.user_repository import UserRepository
from ..schemas.user import UserCreate, UserUpdate, UserInDB

class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def create_user(self, user: UserCreate) -> UserInDB:
        """创建用户"""
        existing_user = self.user_repository.get_user_by_email(user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="该邮箱已被注册"
            )
        
        db_user = self.user_repository.create_user(user)
        return UserInDB.from_orm(db_user)
    
    def get_user_by_id(self, user_id: UUID) -> UserInDB:
        """根据ID获取用户"""
        db_user = self.user_repository.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return UserInDB.from_orm(db_user)
    
    def update_user(self, user_id: UUID, user_update: UserUpdate) -> UserInDB:
        """更新用户信息"""
        db_user = self.user_repository.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        if user_update.email and user_update.email != db_user.email:
            existing_user = self.user_repository.get_user_by_email(user_update.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="该邮箱已被注册"
                )
        
        updated_user = self.user_repository.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="更新用户失败"
            )
        return UserInDB.from_orm(updated_user)
    
    def delete_user(self, user_id: UUID) -> None:
        """删除用户"""
        success = self.user_repository.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """查询用户列表"""
        users = self.user_repository.list_users(skip, limit)
        return [UserInDB.from_orm(user) for user in users]