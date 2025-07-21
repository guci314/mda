from typing import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from app.core.security import create_access_token
from app.core.config import settings
from datetime import timedelta

router = APIRouter()


@router.post("/register", response_model=schemas.UserPublic)
async def register_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_in: schemas.UserCreate,
):
    """
    Create new user.
    """
    user = await crud.crud_user.get_by_email(db, email=user_in.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = await crud.crud_user.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = await crud.crud_user.create(db, obj_in=user_in)
    return user


@router.post("/login/access-token", response_model=schemas.Token)
async def login_for_access_token(
    db: AsyncSession = Depends(deps.get_db),
    username: str = Body(...),
    password: str = Body(...),
):
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = await crud.crud_user.get_by_username(db, username=username)
    if not user or not user.password_hash:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    from app.core.security import verify_password

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        user.username, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=schemas.UserPublic)
async def read_users_me(
    current_user: models.User = Depends(deps.get_current_user),
):
    """
    Get current user.
    """
    return current_user
