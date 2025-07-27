from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..schemas.user import UserCreate, UserUpdate, UserResponse
from ..services.user import UserService
from ..database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    user_service = UserService(db)
    return user_service.create_user(user)

@router.get("/", response_model=List[UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get a list of users with pagination and status filtering"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit, status=status)

@router.get("/{user_id}", response_model=UserResponse)
def read_user(user_id: str, db: Session = Depends(get_db)):
    """Get a single user by ID"""
    user_service = UserService(db)
    return user_service.get_user(user_id)

@router.put("/{user_id}", response_model=UserResponse)
def update_user(
    user_id: str,
    user: UserUpdate,
    db: Session = Depends(get_db)
):
    """Update user information"""
    user_service = UserService(db)
    return user_service.update_user(user_id, user)

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """Deactivate a user"""
    user_service = UserService(db)
    return user_service.delete_user(user_id)