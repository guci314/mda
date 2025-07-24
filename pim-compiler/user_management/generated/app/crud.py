from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID

from .models import User
from .schemas import UserCreate, UserUpdate


def get_user(db: Session, user_id: UUID) -> Optional[User]:
    """获取单个用户"""
    return db.query(User).filter(User.id == user_id).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """获取用户列表（分页）"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """创建用户"""
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        status="active"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
    """更新用户信息"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: UUID) -> bool:
    """删除用户（软删除）"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db_user.status = "inactive"
    db.add(db_user)
    db.commit()
    return True


def check_email_exists(db: Session, email: str, exclude_id: UUID = None) -> bool:
    """检查邮箱是否已存在"""
    query = db.query(User).filter(User.email == email)
    if exclude_id:
        query = query.filter(User.id != exclude_id)
    return query.first() is not None