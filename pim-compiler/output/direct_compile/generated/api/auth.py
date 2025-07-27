from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from db.database import get_db
from schemas.user import UserCreate, UserInDB, Token
from services.user_service import UserService
from services.auth_service import AuthService
from core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserInDB)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    if user_service.get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if user_service.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(user_data)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    auth_service = AuthService()
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    user_service.update_last_login(user)
    return {"access_token": access_token, "token_type": "bearer"}
