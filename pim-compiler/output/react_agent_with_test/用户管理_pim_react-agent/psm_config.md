# FastAPI 用户管理 PSM (Platform Specific Model)

## 1. 应用配置

### config.py

```python
from pydantic import BaseSettings, PostgresDsn, validator
from typing import Optional

class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "用户管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: PostgresDsn = "postgresql://user:password@localhost:5432/userdb"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # 服务端口配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # 认证配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 2. 依赖配置

### dependencies.py

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import User
from .schemas import TokenData

# 数据库依赖
def get_db():
    """
    获取数据库会话，每个请求独立会话，请求结束后自动关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 认证依赖
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    获取当前认证用户，验证JWT令牌有效性
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    """
    检查用户是否处于活跃状态
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已停用")
    return current_user
```

## 3. 数据库模型

### models.py

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    """
    用户数据模型，对应数据库中的users表
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.username}>"
```

## 4. Pydantic 模式

### schemas.py

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    """
    用户基础模型，包含基本用户信息
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r"^\+?[1-9]\d{1,14}$")

    @validator("phone")
    def validate_phone(cls, v):
        if v is None:
            return v
        if not v.startswith("+"):
            raise ValueError("电话号码必须以国际区号开头，例如：+86")
        return v

class UserCreate(UserBase):
    """
    创建用户模型，包含密码字段
    """
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """
    更新用户模型，所有字段可选
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r"^\+?[1-9]\d{1,14}$")
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    """
    数据库中的用户模型，包含所有字段
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    """
    JWT令牌模型
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    JWT令牌数据模型
    """
    user_id: Optional[str] = None
```

## 5. 路由和控制器

### routers/users.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..dependencies import get_db, get_current_active_user
from ..models import User
from ..schemas import UserCreate, UserInDB, UserUpdate
from ..services import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "未找到"}},
)

@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    创建新用户
    
    - **username**: 用户名，必须唯一
    - **email**: 邮箱地址，必须唯一
    - **full_name**: 用户全名（可选）
    - **phone**: 电话号码（可选）
    - **password**: 密码，至少8个字符
    """
    return user_service.create_user(db=db, user=user)

@router.get("/", response_model=List[UserInDB])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取用户列表，支持分页
    
    - **skip**: 跳过多少条记录
    - **limit**: 返回多少条记录
    """
    return user_service.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=UserInDB)
def read_user_me(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息
    """
    return current_user

@router.get("/{user_id}", response_model=UserInDB)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    根据ID获取用户详情
    
    - **user_id**: 用户ID
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    return db_user

@router.put("/{user_id}", response_model=UserInDB)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新用户信息
    
    - **user_id**: 要更新的用户ID
    - **email**: 新邮箱地址（可选）
    - **full_name**: 新全名（可选）
    - **phone**: 新电话号码（可选）
    - **is_active**: 新状态（可选）
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    return user_service.update_user(db=db, db_user=db_user, user=user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除用户（实际上是停用用户）
    
    - **user_id**: 要删除的用户ID
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    user_service.delete_user(db=db, db_user=db_user)
    return {"ok": True}
```

## 6. 服务层

### services/user_service.py

```python
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..models import User
from ..schemas import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """
    验证密码是否正确
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """
    生成密码哈希
    """
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate):
    """
    创建新用户
    
    1. 检查用户名和邮箱是否已存在
    2. 哈希密码
    3. 创建用户记录
    """
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise ValueError("用户名已存在")
    
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise ValueError("邮箱已存在")
    
    # 创建用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    获取用户列表，支持分页
    """
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    """
    根据ID获取单个用户
    """
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, db_user: User, user: UserUpdate):
    """
    更新用户信息
    
    1. 检查邮箱是否已存在（如果修改了邮箱）
    2. 更新用户信息
    """
    if user.email and user.email != db_user.email:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("邮箱已存在")
    
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: User):
    """
    删除用户（实际上是停用用户）
    """
    db_user.is_active = False
    db.add(db_user)
    db.commit()
    return db_user
```

## 7. 认证路由

### routers/auth.py

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..config import settings
from ..dependencies import get_db, authenticate_user, create_access_token
from ..schemas import Token

router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录获取JWT令牌
    
    - **username**: 用户名
    - **password**: 密码
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

## 8. 主应用文件

### main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import users, auth

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 包含路由
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    """
    根端点，返回应用信息
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
```

## 9. 数据库配置

### database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()
```

## 10. 安全工具

### security.py

```python
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """
    验证密码是否正确
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """
    生成密码哈希
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建JWT访问令牌
    
    - **data**: 要编码的数据
    - **expires_delta**: 过期时间间隔
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
```

## 11. 部署配置

### Dockerfile

```dockerfile
# 使用官方Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### requirements.txt

```
fastapi==0.68.0
uvicorn==0.15.0
sqlalchemy==1.4.22
psycopg2-binary==2.9.1
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.5
pydantic==1.8.2
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/userdb
    depends_on:
      - db
    volumes:
      - .:/