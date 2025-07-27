from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from ..services.user import UserService
from ..schemas.user import UserCreate, UserUpdate, UserInDB, UserStatus
from ..dependencies import get_current_user, get_current_admin_user, get_current_user_or_admin

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate, user_service: UserService = Depends()):
    """
    User registration
    - Validate information completeness
    - Validate email and phone format
    - Check email uniqueness
    - Generate unique identifier
    - Set default status as active
    - Record creation time
    """
    return await user_service.register_user(user_create)

@router.post("", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, 
                     user_service: UserService = Depends(),
                     current_user: UserInDB = Depends(get_current_admin_user)):
    """Create user (admin privileges)"""
    return await user_service.create_user(user_create)

@router.get("", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[UserStatus] = None,
    user_service: UserService = Depends(),
    current_user: UserInDB = Depends(get_current_admin_user)
):
    """Query user list (pagination, conditional filtering)"""
    return await user_service.list_users(skip=skip, limit=limit, name=name, email=email, status=status)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(),
    current_user: UserInDB = Depends(get_current_user_or_admin)
):
    """Get user details"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    user_service: UserService = Depends(),
    current_user: UserInDB = Depends(get_current_user_or_admin)
):
    """Update user information"""
    return await user_service.update_user(user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(),
    current_user: UserInDB = Depends(get_current_admin_user)
):
    """Delete/deactivate user"""
    await user_service.delete_user(user_id)
    return None