from sqlalchemy.orm import Session
import uuid
from typing import Optional

from ..models.user import User
from ..schemas.user import UserResponse

def get_user(db: Session, user_id: str):
    """Get a single user by ID"""
    return db.query(User).filter(User.id == uuid.UUID(user_id)).first()

def get_user_by_email(db: Session, email: str):
    """Get a user by email"""
    return db.query(User).filter(User.email == email).first()

def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[str] = None
):
    """Get a list of users with pagination and status filtering"""
    query = db.query(User)
    if status:
        query = query.filter(User.status == status)
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: UserCreate):
    """Create a new user"""
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user: UserUpdate):
    """Update user information"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: str):
    """Deactivate a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.status = "inactive"
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user