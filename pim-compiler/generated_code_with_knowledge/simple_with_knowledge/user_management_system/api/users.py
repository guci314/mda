from fastapi import APIRouter, Depends, HTTPException
from typing import List

from schemas.user import UserCreate, UserResponse, UserUpdate
from services.user_service import UserService

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, service: UserService = Depends()):
    return service.create_user(user)

@router.get("/", response_model=List[UserResponse])
def get_users(skip: int = 0, limit: int = 100, service: UserService = Depends()):
    return service.get_users(skip, limit)

@router.get("/{user_id}", response_model=UserResponse)
def get_user(user_id: int, service: UserService = Depends()):
    user = service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserUpdate, service: UserService = Depends()):
    updated_user = service.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.delete("/{user_id}", response_model=UserResponse)
def delete_user(user_id: int, service: UserService = Depends()):
    deleted_user = service.delete_user(user_id)
    if not deleted_user:
        raise HTTPException(status_code=404, detail="User not found")
    return deleted_user