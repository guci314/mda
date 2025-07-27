根据提供的PSM，我将生成对应的配置文件。以下是完整的配置文件内容：

```python
# config.py

from pydantic import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "User Management API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    DATABASE_POOL_SIZE: int = 5
    DATABASE_MAX_OVERFLOW: int = 10
    
    # 认证配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # 速率限制配置
    RATE_LIMIT: str = "100/minute"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

```python
# database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import settings

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    connect_args={"check_same_thread": False} if "sqlite" in SQLALCHEMY_DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

```python
# security.py

from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from typing import Optional
from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
```

```python
# dependencies.py

from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from security import oauth2_scheme, decode_token
from models import UserModel
from services import UserService

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = UserService(db).get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

def get_current_admin(
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def get_current_user_or_admin(
    user_id: str,
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return current_user
```

```python
# models.py

from sqlalchemy import Column, String, Enum, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
import enum
from datetime import datetime

Base = declarative_base()

class UserStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
```

```python
# schemas.py

from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    password: constr(min_length=8)

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r"^\+?[1-9]\d{1,14}$")] = None
    status: Optional[UserStatus] = None
    password: Optional[constr(min_length=8)] = None

class UserInDB(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    is_admin: bool = False

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None
```

```python
# services.py

from typing import Optional, List
from sqlalchemy.orm import Session
from models import UserModel
from schemas import UserCreate, UserUpdate, UserInDB, UserStatus
from datetime import datetime
import uuid
from fastapi import HTTPException, status
from security import get_password_hash

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_create: UserCreate) -> UserModel:
        if self.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        user_id = str(uuid.uuid4())
        hashed_password = get_password_hash(user_create.password)
        
        db_user = UserModel(
            id=user_id,
            name=user_create.name,
            email=user_create.email,
            phone=user_create.phone,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            hashed_password=hashed_password,
            is_admin=False
        )
        
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        return db_user
    
    def create_user(self, user_create: UserCreate) -> UserModel:
        return self.register_user(user_create)
    
    def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[UserStatus] = None
    ) -> List[UserModel]:
        query = self.db.query(UserModel)
        
        if name:
            query = query.filter(UserModel.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(UserModel.email.ilike(f"%{email}%"))
        if status:
            query = query.filter(UserModel.status == status)
            
        return query.offset(skip).limit(limit).all()
    
    def update_user(self, user_id: str, user_update: UserUpdate) -> UserModel:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if user_update.email and user_update.email != db_user.email:
            if self.get_user_by_email(user_update.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
        
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(db_user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        
        return db_user
    
    def delete_user(self, user_id: str) -> None:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.status = UserStatus.INACTIVE
        db_user.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
```

```python
# main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from datetime import timedelta
from config import settings
from database import Base, engine
from schemas import UserCreate, UserUpdate, UserInDB, Token
from services import UserService
from security import create_access_token, verify_password, get_password_hash
from dependencies import get_current_user, get_current_admin, get_current_user_or_admin
from models import UserModel

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 设置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 创建数据库表
Base.metadata.create_all(bind=engine)

@app.post("/api/auth/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_service: UserService = Depends(UserService)
):
    user = user_service.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.id}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/users/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    user_service: UserService = Depends(UserService)
):
    return user_service.register_user(user_create)

@app.post("/api/users", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    current_user: UserModel = Depends(get_current_admin),
    user_service: UserService = Depends(UserService)
):
    return user_service.create_user(user_create)

@app.get("/api/users", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[str] = None,
    current_user: UserModel = Depends(get_current_user),
    user_service: UserService = Depends(UserService)
):
    return user_service.list_users(skip=skip, limit=limit, name=name, email=email, status=status)

@app.get("/api/users/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str,
    current_user: UserModel = Depends(get_current_user),
    user_service: UserService = Depends(UserService)
):
    user = user_service.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return user

@app.put("/api/users/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user_or_admin),
    user_service: UserService = Depends(UserService)
):
    return user_service.update_user(user_id, user_update)

@app.delete("/api/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: UserModel = Depends(get_current_admin),
    user_service: UserService = Depends(UserService)
):
    user_service.delete_user(user_id)
    return None
```