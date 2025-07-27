from typing import List, Optional
from datetime import datetime
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..repositories.user import (
    get_user, get_user_by_email, get_users, create_user, update_user, deactivate_user
)

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user: UserCreate) -> UserResponse:
        """Create a new user with validation"""
        # Check if email already exists
        db_user = get_user_by_email(self.db, email=user.email)
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Validate phone number
        if user.phone:
            try:
                PhoneNumber(user.phone)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        # Create the user
        return create_user(self.db, user=user)
    
    def get_users(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        status: Optional[str] = None
    ) -> List[UserResponse]:
        """Get a list of users with optional filtering"""
        users = get_users(self.db, skip=skip, limit=limit, status=status)
        return users
    
    def get_user(self, user_id: str) -> UserResponse:
        """Get a single user by ID"""
        db_user = get_user(self.db, user_id=user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return db_user
    
    def update_user(self, user_id: str, user: UserUpdate) -> UserResponse:
        """Update user information with validation"""
        db_user = get_user(self.db, user_id=user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Check email uniqueness if updated
        if user.email and user.email != db_user.email:
            existing_user = get_user_by_email(self.db, email=user.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Validate phone number if updated
        if user.phone:
            try:
                PhoneNumber(user.phone)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e)
                )
        
        return update_user(self.db, user_id=user_id, user=user)
    
    def delete_user(self, user_id: str) -> UserResponse:
        """Deactivate a user"""
        db_user = get_user(self.db, user_id=user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return deactivate_user(self.db, user_id=user_id)