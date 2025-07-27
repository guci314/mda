from typing import Optional, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User, UserStatus
from ..schemas.user import UserCreate, UserUpdate, UserInDB
from ..repositories.user_repository import UserRepository
from ..exceptions.exceptions import EmailAlreadyExistsException, UserNotFoundException

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    def register_user(self, user: UserCreate) -> UserInDB:
        """注册用户"""
        # 检查邮箱是否已存在
        existing_user = self.user_repo.get_user_by_email(user.email)
        if existing_user:
            raise EmailAlreadyExistsException()
        
        # 创建用户
        db_user = self.user_repo.create_user(user)
        return UserInDB.from_orm(db_user)
    
    def get_user(self, user_id: UUID) -> UserInDB:
        """获取用户详情"""
        db_user = self.user_repo.get_user_by_id(user_id)
        if not db_user:
            raise UserNotFoundException()
        return UserInDB.from_orm(db_user)
    
    def update_user(self, user_id: UUID, user_update: UserUpdate) -> UserInDB:
        """更新用户信息"""
        db_user = self.user_repo.get_user_by_id(user_id)
        if not db_user:
            raise UserNotFoundException()
        
        # 检查邮箱唯一性
        if user_update.email and user_update.email != db_user.email:
            existing_user = self.user_repo.get_user_by_email(user_update.email)
            if existing_user:
                raise EmailAlreadyExistsException()
        
        updated_user = self.user_repo.update_user(user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")
        return UserInDB.from_orm(updated_user)
    
    def delete_user(self, user_id: UUID) -> None:
        """删除用户"""
        success = self.user_repo.delete_user(user_id)
        if not success:
            raise UserNotFoundException()
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """查询用户列表"""
        users = self.user_repo.list_users(skip, limit)
        return [UserInDB.from_orm(user) for user in users]