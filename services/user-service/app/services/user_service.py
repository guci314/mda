# MDA-GENERATED-START: user-service
"""
User service business logic with debug flow support
"""
from typing import List, Optional
from uuid import UUID
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from app.models.user import User, UserCreate, UserUpdate, UserStatus
from app.debug.decorators import flow, step

logger = logging.getLogger(__name__)


class UserService:
    """User management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @flow(name="创建用户流程", description="处理用户注册的完整流程")
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user with complete validation flow"""
        
        @step(name="验证用户数据", step_type="validation")
        async def validate_data():
            # Validate required fields
            if not user_data.name or not user_data.name.strip():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Name cannot be empty"
                )
            
            # Email validation is handled by Pydantic EmailStr
            return {"validated": True, "data": user_data}
        
        @step(name="检查邮箱唯一性", step_type="validation")
        async def check_email_exists():
            existing = self.db.query(User).filter(User.email == user_data.email).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email {user_data.email} already registered"
                )
            return {"email_available": True}
        
        @step(name="创建用户记录", step_type="action")
        async def create_user_record():
            try:
                user = User(
                    name=user_data.name,
                    email=user_data.email,
                    phone=user_data.phone,
                    status=UserStatus.ACTIVE
                )
                self.db.add(user)
                self.db.commit()
                self.db.refresh(user)
                logger.info(f"User created successfully: {user.id}")
                return {"user": user}
            except IntegrityError as e:
                self.db.rollback()
                logger.error(f"Database error creating user: {e}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="User with this email already exists"
                )
        
        @step(name="发送欢迎通知", step_type="action")
        async def send_welcome_notification(user: User):
            # In a real application, this would send an email or notification
            logger.info(f"Welcome notification would be sent to {user.email}")
            return {"notification_sent": True}
        
        # Execute the flow
        await validate_data()
        await check_email_exists()
        user_result = await create_user_record()
        await send_welcome_notification(user_result["user"])
        
        return user_result["user"]
    
    def get_user(self, user_id: UUID) -> User:
        """Get a user by ID"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found"
            )
        return user
    
    def get_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get a list of users with pagination"""
        return self.db.query(User).offset(skip).limit(limit).all()
    
    def get_users_count(self) -> int:
        """Get total count of users"""
        return self.db.query(User).count()
    
    def update_user(self, user_id: UUID, user_update: UserUpdate) -> User:
        """Update user information"""
        user = self.get_user(user_id)
        
        # Update only provided fields
        update_data = user_update.model_dump(exclude_unset=True)
        
        # Check email uniqueness if email is being updated
        if "email" in update_data and update_data["email"] != user.email:
            existing = self.db.query(User).filter(
                User.email == update_data["email"],
                User.id != user_id
            ).first()
            if existing:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Email {update_data['email']} is already in use"
                )
        
        # Apply updates
        for field, value in update_data.items():
            setattr(user, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"User {user_id} updated successfully")
            return user
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Database error updating user: {e}")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Update failed due to data conflict"
            )
    
    def delete_user(self, user_id: UUID) -> bool:
        """Soft delete a user by setting status to INACTIVE"""
        user = self.get_user(user_id)
        
        # Soft delete by changing status
        user.status = UserStatus.INACTIVE
        
        self.db.commit()
        logger.info(f"User {user_id} soft deleted (status set to INACTIVE)")
        return True
    
    def check_email_exists(self, email: str, exclude_id: Optional[UUID] = None) -> bool:
        """Check if an email already exists in the database"""
        query = self.db.query(User).filter(User.email == email)
        if exclude_id:
            query = query.filter(User.id != exclude_id)
        return query.first() is not None
# MDA-GENERATED-END: user-service