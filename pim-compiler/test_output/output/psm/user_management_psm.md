# FastAPI 平台特定模型 (PSM) - 用户管理系统

## 技术架构说明

本系统采用 FastAPI 作为 Web 框架，具有以下技术特点：
- 异步请求处理
- 自动生成 OpenAPI 文档
- 基于 Pydantic 的数据验证
- SQLAlchemy 2.0 ORM 层
- JWT 认证机制
- 分层架构设计（路由层、服务层、模型层）

## 数据模型实现

### SQLAlchemy 模型

```python
# models.py
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    status = Column(String(20), default=UserStatus.INACTIVE, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
```

### Pydantic 模型

```python
# schemas.py
from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

    @field_validator('username')
    def username_must_be_valid(cls, v):
        if len(v) < 3 or len(v) > 50:
            raise ValueError('Username must be between 3 and 50 characters')
        return v

class UserCreate(UserBase):
    password: str

    @field_validator('password')
    def password_must_be_strong(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        # 添加更多密码强度规则
        return v

class UserOut(UserBase):
    id: int
    status: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
```

## API 接口设计

### 路由设计

```python
# routers/auth.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

@router.post("/register", response_model=UserOut)
async def register(user_data: UserCreate):
    # 实现注册逻辑
    pass

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # 实现登录逻辑
    pass

# routers/users.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    # 实现获取用户逻辑
    pass
```

### API 文档示例

#### POST /api/v1/auth/register
**请求体**:
```json
{
  "email": "user@example.com",
  "username": "testuser",
  "password": "Str0ngP@ssword"
}
```

**成功响应**:
```json
{
  "id": 1,
  "email": "user@example.com",
  "username": "testuser",
  "status": "inactive",
  "created_at": "2023-01-01T00:00:00"
}
```

#### POST /api/v1/auth/login
**请求体** (表单数据):
```
username: testuser
password: Str0ngP@ssword
```

**成功响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 业务逻辑实现

### 服务层实现

```python
# services/user_service.py
from datetime import datetime
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from .models import User, UserStatus
from .schemas import UserCreate, UserOut

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def register_user(self, user_data: UserCreate) -> UserOut:
        # 检查邮箱和用户名是否已存在
        if self.db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if self.db.query(User).filter(User.username == user_data.username).first():
            raise HTTPException(status_code=400, detail="Username already taken")

        # 创建用户
        hashed_password = pwd_context.hash(user_data.password)
        db_user = User(
            email=user_data.email,
            username=user_data.username,
            hashed_password=hashed_password,
            status=UserStatus.INACTIVE,
            created_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return UserOut.from_orm(db_user)

    def authenticate_user(self, username: str, password: str) -> User:
        user = self.db.query(User).filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        if user.status != UserStatus.ACTIVE:
            raise HTTPException(status_code=403, detail="User is not active")
        
        return user

    def get_user(self, user_id: int) -> UserOut:
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return UserOut.from_orm(user)
```

### 认证和依赖注入

```python
# core/security.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
```

## 项目结构说明

```
user_management/
├── app/
│   ├── __init__.py
│   ├── main.py                  # FastAPI 应用入口
│   ├── core/
│   │   ├── config.py            # 应用配置
│   │   ├── security.py          # 认证相关
│   │   └── database.py          # 数据库连接
│   ├── models/                  # 数据模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/                 # Pydantic 模型
│   │   ├── __init__.py
│   │   └── user.py
│   ├── services/                # 业务逻辑
│   │   ├── __init__.py
│   │   └── user_service.py
│   ├── routers/                 # API 路由
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   └── users.py
│   └── tests/                   # 测试代码
│       ├── __init__.py
│       ├── test_models.py
│       ├── test_routers.py
│       └── test_services.py
├── alembic/                     # 数据库迁移
│   ├── env.py
│   └── versions/
├── requirements.txt             # 依赖列表
└── README.md
```

## 依赖列表

```text
# requirements.txt
fastapi==0.95.0
uvicorn==0.21.1
sqlalchemy==2.0.0
psycopg2-binary==2.9.5          # PostgreSQL 驱动
# 或 sqlite3 (Python 内置)
python-jose==3.3.0              # JWT 支持
passlib==1.7.4                  # 密码哈希
pydantic==2.0
alembic==1.10.2                 # 数据库迁移
pytest==7.2.0                   # 测试框架
httpx==0.23.3                   # 测试客户端
```

## 补充说明

1. **数据库配置**：在 `core/database.py` 中配置数据库连接
2. **迁移管理**：使用 Alembic 进行数据库迁移管理
3. **环境变量**：敏感配置应通过环境变量管理
4. **测试**：使用 pytest 编写单元测试和集成测试
5. **异步支持**：所有数据库操作应使用 SQLAlchemy 2.0 的异步 API
6. **日志**：建议添加适当的日志记录

这个 PSM 设计保持了原始 PIM 的所有业务逻辑，同时添加了 FastAPI 平台的技术实现细节，遵循了 FastAPI 的最佳实践和推荐的 Python 技术栈。