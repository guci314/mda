# FastAPI 最佳实践

## 项目结构

### 推荐的目录结构
```
app/
├── api/            # API endpoints
│   ├── deps.py     # Dependencies
│   └── v1/         # API version 1
├── core/           # Application configuration
│   ├── config.py   # Settings management
│   └── security.py # Security utilities
├── crud/           # CRUD operations
├── db/             # Database configuration
├── models/         # SQLAlchemy models
├── schemas/        # Pydantic models
└── services/       # Business logic
```

## 依赖注入模式

### 数据库会话管理
```python
from typing import Generator
from sqlalchemy.orm import Session
from db.session import SessionLocal

def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 获取当前用户
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login")

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
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
    
    user = crud.user.get(db, id=user_id)
    if user is None:
        raise credentials_exception
    return user
```

## 错误处理

### 全局异常处理器
```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )
```

### 业务逻辑异常
```python
class BusinessException(Exception):
    def __init__(self, message: str, code: str = "BUSINESS_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)
```

## 性能优化

### 使用异步数据库驱动
```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

engine = create_async_engine(settings.DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
```

### 缓存策略
```python
from functools import lru_cache
from typing import Optional
import redis

redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)

def cache_key_wrapper(prefix: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_key = f"{prefix}:{':'.join(map(str, args))}"
            
            # 尝试从缓存获取
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)
            
            # 执行函数
            result = await func(*args, **kwargs)
            
            # 存入缓存
            redis_client.setex(cache_key, 3600, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## 安全最佳实践

### 密码哈希
```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)
```

### CORS 配置
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 测试策略

### 测试数据库设置
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
```