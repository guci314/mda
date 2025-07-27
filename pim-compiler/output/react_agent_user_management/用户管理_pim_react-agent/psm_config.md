# FastAPI 用户管理系统 PSM (Platform Specific Model)

## 1. 应用配置

### 1.1 数据库连接配置

```python
# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/user_management"
    # 服务端口配置
    API_PORT: int = 8000
    # 环境变量
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()

# SQLAlchemy 配置
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### 1.2 服务端口配置

```python
# main.py
from fastapi import FastAPI
from config.database import settings

app = FastAPI(
    title="用户管理系统",
    description="基于FastAPI的用户管理服务",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
```

## 2. 依赖配置

### 2.1 第三方服务配置

```python
# config/external_services.py
from pydantic import BaseSettings, AnyHttpUrl

class ExternalServicesSettings(BaseSettings):
    # 邮件服务配置
    EMAIL_SERVICE_URL: AnyHttpUrl = "https://api.email-service.com/v1"
    EMAIL_SERVICE_API_KEY: str
    
    # 短信服务配置
    SMS_SERVICE_URL: AnyHttpUrl = "https://api.sms-service.com/v1"
    SMS_SERVICE_API_KEY: str
    
    class Config:
        env_file = ".env"

external_services_settings = ExternalServicesSettings()
```

### 2.2 中间件配置

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# 仅在生产环境启用HTTPS重定向
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [
        "https://your-production-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 3. 安全配置

### 3.1 认证方式

```python
# config/security.py
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseSettings

class SecuritySettings(BaseSettings):
    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

security_settings = SecuritySettings()

# OAuth2密码认证流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

### 3.2 授权策略

```python
# utils/security.py
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from config.security import security_settings, oauth2_scheme

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security_settings.SECRET_KEY, algorithms=[security_settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 这里可以添加从数据库获取用户的逻辑
    return {"user_id": user_id}

# 基于角色的权限检查
async def check_admin_role(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user
```

### 3.3 CORS 设置

已在中间件配置部分实现

## 4. 部署配置

### 4.1 Docker 配置

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 环境变量
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# 运行应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/user_management
      - ENVIRONMENT=production
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=user_management
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 4.2 环境差异配置

```python
# config/environment.py
from enum import Enum
from pydantic import BaseSettings

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    
    class Config:
        env_file = ".env"

env_settings = EnvironmentSettings()

def get_database_url():
    if env_settings.ENVIRONMENT == Environment.TESTING:
        return "sqlite:///./test.db"
    return settings.DATABASE_URL
```

## 5. 领域模型实现

### 5.1 用户模型 (SQLAlchemy)

```python
# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from config.database import Base

class UserDB(Base):
    """用户数据库模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)  # 用户姓名
    email = Column(String(100), unique=True, index=True, nullable=False)  # 用户邮箱
    phone = Column(String(20), nullable=False)  # 用户电话
    is_active = Column(Boolean, default=True)  # 用户状态
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 创建时间
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # 更新时间
```

### 5.2 用户模型 (Pydantic)

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """用户基础模型"""
    name: str
    email: EmailStr
    phone: str

    @validator('phone')
    def validate_phone(cls, v):
        # 简单的电话号码验证
        if not v.isdigit() or len(v) < 10:
            raise ValueError("电话号码格式不正确")
        return v

class UserCreate(UserBase):
    """创建用户模型"""
    pass

class UserUpdate(BaseModel):
    """更新用户模型"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @validator('phone', pre=True, always=True)
    def validate_phone(cls, v):
        if v is not None and (not v.isdigit() or len(v) < 10):
            raise ValueError("电话号码格式不正确")
        return v

class UserInDB(UserBase):
    """数据库用户模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

## 6. 领域服务实现

### 6.1 用户服务实现

```python
# services/user.py
from sqlalchemy.orm import Session
from models.user import UserDB
from schemas.user import UserCreate, UserUpdate, UserInDB
from fastapi import HTTPException, status
from typing import List, Optional

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> UserInDB:
        """创建用户"""
        # 检查邮箱唯一性
        db_user = self.db.query(UserDB).filter(UserDB.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建用户
        db_user = UserDB(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserInDB.from_orm(db_user)

    def get_user(self, user_id: int) -> Optional[UserInDB]:
        """根据ID查询用户"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            return None
        return UserInDB.from_orm(db_user)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """查询用户列表"""
        db_users = self.db.query(UserDB).offset(skip).limit(limit).all()
        return [UserInDB.from_orm(user) for user in db_users]

    def update_user(self, user_id: int, user: UserUpdate) -> Optional[UserInDB]:
        """更新用户信息"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserInDB.from_orm(db_user)

    def delete_user(self, user_id: int) -> bool:
        """删除用户（实际上是停用）"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            return False
        
        db_user.is_active = False
        self.db.add(db_user)
        self.db.commit()
        return True
```

## 7. API路由实现

```python
# api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.user import UserDB
from schemas.user import UserCreate, UserUpdate, UserInDB
from services.user import UserService
from config.database import SessionLocal

router = APIRouter(prefix="/users", tags=["users"])

# 依赖项 - 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    user_service = UserService(db)
    return user_service.create_user(user)

@router.get("/", response_model=List[UserInDB])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """查询用户列表"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """根据ID查询用户"""
    user_service = UserService(db)
    db_user = user_service.get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.put("/{user_id}", response_model=UserInDB)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user_service = UserService(db)
    db_user = user_service.update_user(user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return None
```

## 8. 主应用集成

```python
# main.py
from fastapi import FastAPI
from config.database import settings
from api.users import router as users_router

app = FastAPI(
    title="用户管理系统",
    description="基于FastAPI的用户管理服务",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

# 添加路由
app.include_router(users_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
```

## 9. 测试配置

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from config.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
```

## 10. 业务规则实现

### 10.1 唯一性规则实现

```python
# services/user.py 中的 create_user 方法
def create_user(self, user: UserCreate) -> UserInDB:
    """创建用户"""
    # 检查邮箱唯一性
    db_user = self.db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    ...
```

### 10.2 数据完整性规则实现

```python
# schemas/user.py 中的验证器
@validator('phone')
def validate_phone(cls, v):
    # 简单的电话号码验证
    if not v.isdigit() or len(v) < 10:
        raise ValueError("电话号码格式不正确")
    return v
```

### 10.3 状态规则实现

```python
# services/user.py 中的 delete_user 方法
def delete_user(self, user_id: int) -> bool:
    """删除用户（实际上是停用）"""
    db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
    if not db_user:
        return False
    
    db_user.is_active = False
    self.db.add(db_user)
    self.db.commit()
    return True
```

## 11. 性能优化

```python
# services/user.py
def get_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
    """查询用户列表 - 使用分页优化性能"""
    db_users = self.db.query(UserDB).filter(UserDB.is_active == True).offset(skip).limit(limit).all()
    return [UserInDB.from_orm(user) for user in db_users]

# 添加索引优化查询性能
# models/user.py
from sqlalchemy import Index

# 在UserDB类定义后添加
Index("idx_user_email", UserDB.email)
Index("idx_user_status", UserDB.is_active)
```

## 12. 错误处理

```python
# exceptions.py
from fastapi import HTTPException, status

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

class EmailAlreadyRegisteredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

class InvalidPhoneNumberException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="