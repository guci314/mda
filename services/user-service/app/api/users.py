# MDA-GENERATED-START: users-api
"""
User API endpoints
"""
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.config import settings
from app.models.user import UserCreate, UserUpdate, UserResponse, PaginatedUsers
from app.services.user_service import UserService

router = APIRouter()


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new user
    
    - **name**: User's full name (required)
    - **email**: Valid email address (required, must be unique)
    - **phone**: Phone number (optional, international format supported)
    """
    service = UserService(db)
    user = await service.create_user(user_data)
    return user


@router.get("/", response_model=PaginatedUsers)
async def get_users(
    skip: int = Query(default=settings.DEFAULT_SKIP, ge=0, description="Number of records to skip"),
    limit: int = Query(default=settings.DEFAULT_LIMIT, ge=1, le=settings.MAX_LIMIT, description="Number of records to return"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of users
    
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 20, max: 100)
    """
    service = UserService(db)
    users = service.get_users(skip=skip, limit=limit)
    total = service.get_users_count()
    
    return PaginatedUsers(
        items=users,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Get a specific user by ID
    
    - **user_id**: The UUID of the user to retrieve
    """
    service = UserService(db)
    user = service.get_user(user_id)
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    Update user information
    
    - **user_id**: The UUID of the user to update
    - **name**: New name (optional)
    - **email**: New email (optional, must be unique)
    - **phone**: New phone number (optional)
    - **status**: New status (optional: active/inactive)
    """
    service = UserService(db)
    user = service.update_user(user_id, user_update)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db)
):
    """
    Soft delete a user (sets status to INACTIVE)
    
    - **user_id**: The UUID of the user to delete
    """
    service = UserService(db)
    service.delete_user(user_id)
    return None
# MDA-GENERATED-END: users-api