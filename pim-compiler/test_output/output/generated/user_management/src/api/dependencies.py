"""
API Dependencies.

This module contains common dependencies used across multiple API endpoints,
such as getting the database session and retrieving the current authenticated user.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..core.security import decode_token
from ..services.user_service import user_service
from ..models.user import User
from ..schemas.user import TokenPayload
from ..core.config import settings

# This tells FastAPI where to find the token for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency to get the current authenticated user.

    Decodes the JWT token from the request, validates it, and fetches
    the corresponding user from the database.

    Args:
        db: The database session.
        token: The OAuth2 token.

    Returns:
        The authenticated user object.

    Raises:
        HTTPException: If credentials cannot be validated.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception

    token_data = TokenPayload(**payload)
    if token_data.sub is None:
        raise credentials_exception

    user = await user_service.get_user_by_username(db, username=token_data.sub)
    if user is None:
        raise credentials_exception
        
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency to get the current active user.
    Checks if the user returned by get_current_user is active.
    """
    if current_user.status != "active":
        raise HTTPException(status_code=403, detail="Inactive user")
    return current_user
