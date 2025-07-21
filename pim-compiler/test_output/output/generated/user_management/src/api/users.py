"""
API Endpoints for User Management.

This module provides routes for accessing and managing user data.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..services.user_service import user_service
from ..schemas.user import UserPublic
from ..models.user import User
from .dependencies import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserPublic)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """
    Get the profile of the current authenticated user.
    """
    return current_user


@router.get("/{user_id}", response_model=UserPublic)
async def read_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific user by their ID.

    This endpoint is protected and requires authentication.
    """
    user = await user_service.get_user_by_id(db, user_id=user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )
    return user
