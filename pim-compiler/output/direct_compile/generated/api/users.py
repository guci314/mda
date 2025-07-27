from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.user import UserInDB, UserUpdate
from services.user_service import UserService
from core.dependencies import get_current_active_user
from models.user import User

router = APIRouter()

@router.get("/me", response_model=UserInDB)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserInDB)
def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.update_user(current_user, update_data)
