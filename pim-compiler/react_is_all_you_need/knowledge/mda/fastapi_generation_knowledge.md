# FastAPI 代码生成先验知识

## 概述

本文档包含生成 FastAPI 应用代码的领域知识和最佳实践。

## 系统性修复策略

### 测试失败的系统性修复方法

当遇到测试失败时，必须采用以下系统性方法，而不是"头痛医头"的局部修复：

#### 1. 问题诊断阶段
1. **完整读取错误信息** - 不要只看第一行错误，要看完整的错误栈
2. **识别错误类型**：
   - 模块导入错误 (ModuleNotFoundError)
   - 路径不一致错误
   - fixture定义错误
   - 实际测试逻辑错误

#### 2. 全局检查阶段
在修复前，必须先执行以下检查：
```bash
# 检查目录结构
ls -la .
find . -type f -name "*.py" | head -20

# 检查实际文件位置
find . -name "database.py"
find . -name "Base" -type f

# 检查所有导入语句
grep -r "from.*import.*Base" .
grep -r "from.*db.*import" .
```

#### 3. 系统性修复原则

**原则1：统一目录命名**
- 选择`app`或`src`，全项目统一使用
- 如果改名，必须：
  1. 重命名目录：`mv src app`
  2. 批量修改所有导入：`grep -rl 'from src' . | xargs sed -i 's/from src/from app/g'`
  3. 批量修改所有导入：`grep -rl 'import src' . | xargs sed -i 's/import src/import app/g'`

**原则2：验证每次修改**
- 修改文件后，立即读取验证内容完整性
- 不要假设修改成功，要验证

**原则3：依赖关系顺序**
修复顺序必须遵循依赖关系：
1. 先修复`database.py`和模型文件
2. 再修复`conftest.py`
3. 最后修复测试文件

**原则4：避免循环修复**
- 建立修复清单，记录已修复的问题
- 不要重复修改同一个文件超过2次
- 如果2次修复无效，说明问题在其他地方

#### 4. 常见错误的标准修复方案

**错误1: ModuleNotFoundError: No module named 'app.db.database'**
```python
# 错误原因：文件在app/models/database.py，但导入是app.db.database
# 修复方案：
# 1. 确认文件实际位置
find . -name "database.py"
# 2. 修改导入语句
sed -i 's/from app.db.database/from app.models.database/g' tests/conftest.py
```

**错误2: NameError: name 'pytest' is not defined**
```python
# 错误原因：conftest.py缺少import pytest
# 修复方案：在文件开头添加
import pytest
```

**错误3: 文件内容被截断**
```python
# 错误原因：write_file工具可能有长度限制
# 修复方案：分段写入或使用edit_lines逐行修改
```

#### 5. 修复后验证清单
每次修复后必须验证：
- [ ] 文件内容完整（read_file验证）
- [ ] 导入路径正确（grep验证）
- [ ] 所有__init__.py存在
- [ ] pytest.ini配置正确
- [ ] 运行简单测试验证环境

### 测试100%通过的执行策略

当任务要求"所有测试必须100%通过"时：

1. **建立测试修复循环**
```python
while True:
    # 运行测试
    result = execute_command("pytest -v")
    
    # 解析结果
    if "failed" not in result:
        break  # 所有测试通过
    
    # 分析失败原因
    error_type = identify_error_type(result)
    
    # 应用对应的修复策略
    if error_type == "ModuleNotFoundError":
        apply_module_fix()
    elif error_type == "ImportError":
        apply_import_fix()
    elif error_type == "AssertionError":
        apply_logic_fix()
    
    # 验证修复
    verify_fix()
```

2. **记录修复历史**
- 维护已尝试的修复列表
- 避免重复同样的修复
- 如果同一修复尝试3次仍失败，寻找其他方案

3. **优先级策略**
- 优先修复环境和配置问题
- 其次修复导入和路径问题
- 最后修复业务逻辑问题

## 项目结构规范

### 标准 FastAPI 项目结构

```
myapp/
├── __init__.py          # Python 包标识（必需）
├── main.py              # 应用入口
├── config.py            # 配置管理
├── database.py          # 数据库连接
├── models/              # 数据模型
│   ├── __init__.py
│   └── user.py
├── schemas/             # Pydantic 模型
│   ├── __init__.py
│   └── user.py
├── routers/             # API 路由
│   ├── __init__.py
│   └── users.py
├── services/            # 业务逻辑
│   ├── __init__.py
│   └── user_service.py
├── utils/               # 工具函数
│   ├── __init__.py
│   └── security.py
├── tests/               # 测试代码
│   ├── __init__.py
│   ├── conftest.py
│   └── test_users.py
├── requirements.txt     # 依赖列表
├── .env                 # 环境变量
└── README.md           # 项目说明
```

### Python 包规则

1. **每个目录必须包含 `__init__.py` 文件**
2. **导入规则**：
   - 应用内部：使用相对导入 `from .models import User`
   - 测试代码：使用绝对导入 `from myapp.models import User`

## 代码生成规范

### 1. 主应用文件 (main.py)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users
from .database import engine, Base

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建应用
app = FastAPI(
    title="API Title",
    description="API Description",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to API"}
```

### 2. 数据库配置 (database.py)

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
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

### 3. 数据模型 (models/user.py)

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from ..database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### 4. Pydantic 模型 (schemas/user.py)

```python
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        orm_mode = True
```

### 5. API 路由 (routers/users.py)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..schemas import user as user_schemas
from ..services import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=user_schemas.User)
def create_user(
    user: user_schemas.UserCreate,
    db: Session = Depends(get_db)
):
    return user_service.create_user(db, user)

@router.get("/", response_model=List[user_schemas.User])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    return user_service.get_users(db, skip, limit)

@router.get("/{user_id}", response_model=user_schemas.User)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    user = user_service.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

### 6. 业务逻辑 (services/user_service.py)

```python
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..models import user as user_models
from ..schemas import user as user_schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: user_schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = user_models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(user_models.User).filter(user_models.User.id == user_id).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(user_models.User).offset(skip).limit(limit).all()
```

### 7. 测试文件 (tests/test_users.py)

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from myapp.main import app
from myapp.database import Base, engine

# 创建测试客户端
client = TestClient(app)

def setup_module():
    """测试前创建表"""
    Base.metadata.create_all(bind=engine)

def teardown_module():
    """测试后清理"""
    Base.metadata.drop_all(bind=engine)

def test_create_user():
    response = client.post(
        "/users/",
        json={"username": "testuser", "email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_read_users():
    response = client.get("/users/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## 依赖管理

### 标准 requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic[email]
python-multipart==0.0.6
passlib[bcrypt]==1.7.4
python-jose[cryptography]==3.3.0
python-dotenv==1.0.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

## 生成流程

### 推荐的代码生成顺序

1. **创建项目结构**
   - 创建所有必要的目录
   - 为每个目录创建 `__init__.py`

2. **生成核心文件**
   - `database.py` - 数据库配置
   - `config.py` - 应用配置（如果需要）

3. **生成数据层**
   - `models/*.py` - 数据模型
   - `schemas/*.py` - Pydantic 模型

4. **生成业务层**
   - `services/*.py` - 业务逻辑

5. **生成 API 层**
   - `routers/*.py` - API 路由
   - `main.py` - 应用入口

6. **生成测试**
   - `tests/conftest.py` - 测试配置
   - `tests/test_*.py` - 测试文件

7. **生成配置文件**
   - `requirements.txt` - 依赖列表
   - `.env.example` - 环境变量示例
   - `README.md` - 项目说明

## 执行命令

### 安装依赖
```bash
pip install -r requirements.txt
```

### 运行应用
```bash
uvicorn myapp.main:app --reload
```

### 运行测试
```bash
pytest tests/ -v
```

## 注意事项

1. **导入路径问题**
   - 确保所有目录都有 `__init__.py`
   - 测试文件需要正确设置 Python 路径

2. **数据库迁移**
   - 对于生产环境，建议使用 Alembic 进行数据库迁移
   - 开发环境可以使用 `Base.metadata.create_all()`

3. **安全性**
   - 密码必须加密存储
   - 使用环境变量管理敏感信息
   - 配置适当的 CORS 策略

4. **性能优化**
   - 使用异步函数处理 I/O 操作
   - 合理使用数据库索引
   - 实现适当的缓存策略

## PSM 转换指南

当接收到 PSM（Platform Specific Model）时，按以下规则转换：

1. **数据模型** → SQLAlchemy 模型 + Pydantic Schema
2. **API 端点** → FastAPI 路由
3. **业务规则** → Service 层方法
4. **认证要求** → 中间件或依赖注入
5. **数据验证** → Pydantic 验证器

## 错误处理

标准错误响应格式：
```python
{
    "detail": "错误描述",
    "status_code": 400,
    "type": "validation_error"
}
```

常见 HTTP 状态码：
- 200: 成功
- 201: 创建成功
- 400: 请求错误
- 401: 未认证
- 403: 无权限
- 404: 未找到
- 422: 验证错误
- 500: 服务器错误