from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database.database import SessionLocal
from ..services.user_service import UserService
from ..models.user import UserStatus
from ..database.models import User
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from ..config.settings import settings

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)):
    return UserService(db)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = UserService(db).get_user(user_id)
    if user is None:
        raise credentials_exception
    return user

async def has_admin_permission(current_user: User = Depends(get_current_user)):
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    # 这里可以添加更复杂的权限检查逻辑
    return current_user