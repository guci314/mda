from typing import List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserInDB

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user: UserCreate) -> User:
        """创建用户"""
        db_user = User(
            name=user.name,
            email=user.email,
            phone=user.phone,
            status="active"
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        """根据ID获取用户"""
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return self.db.query(User).filter(User.email == email).first()
    
    def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def delete_user(self, user_id: UUID) -> bool:
        """删除用户(实际上是更新状态为INACTIVE)"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        db_user.status = "inactive"
        self.db.commit()
        return True
    
    def list_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """查询用户列表"""
        return self.db.query(User).offset(skip).limit(limit).all()