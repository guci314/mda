# Hello World Service - Platform Specific Model (PSM)

## 技术架构说明

本项目采用 FastAPI 框架构建 RESTful API 服务。FastAPI 具有高性能、易于使用、自动生成 API 文档等优点，非常适合构建现代化的 Web API。

- **框架**: FastAPI
- **编程语言**: Python 3.10+
- **数据库**: SQLite (默认) 或 PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **数据验证**: Pydantic v2
- **测试框架**: pytest
- **部署**: Docker (可选)

## 数据模型设计

### 数据库表: greetings

| 字段名    | 类型       | 约束     | 索引 | 描述     |
| --------- | ---------- | -------- | ---- | -------- |
| id        | INTEGER    | PRIMARY KEY, AUTOINCREMENT | 是   | 主键     |
| message   | VARCHAR(255) | NOT NULL | 否   | 问候消息   |
| created_at | TIMESTAMP  | DEFAULT CURRENT_TIMESTAMP | 否   | 创建时间 |

**SQLAlchemy 模型定义 (SQLite 示例)**:

```python
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

Base = declarative_base()

class Greeting(Base):
    __tablename__ = "greetings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

# SQLite 数据库连接
engine = create_engine("sqlite:///./hello_world.db")
Base.metadata.create_all(engine)

# 创建 Session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

## API 接口设计

### 1. 获取问候消息 (GET /hello)

- **路由**: `/hello`
- **方法**: GET
- **请求格式**: 无
- **响应格式**: JSON

```json
{
  "message": "Hello World!"
}
```

- **状态码**:
    - 200 OK: 成功返回问候消息

**FastAPI 代码示例**:

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/hello")
async def read_root():
    return {"message": "Hello World!"}
```

### 2. 创建问候消息 (POST /greetings)

- **路由**: `/greetings`
- **方法**: POST
- **请求格式**: JSON

```json
{
  "message": "Custom Greeting"
}
```

- **响应格式**: JSON

```json
{
  "id": 1,
  "message": "Custom Greeting",
  "created_at": "2025-07-23T10:00:00"
}
```

- **状态码**:
    - 201 Created: 成功创建问候消息
    - 422 Unprocessable Entity: 请求体验证失败

**Pydantic 模型定义**:

```python
from pydantic import BaseModel
from datetime import datetime

class GreetingCreate(BaseModel):
    message: str

class GreetingResponse(BaseModel):
    id: int
    message: str
    created_at: datetime
```

**FastAPI 代码示例**:

```python
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/greetings/", response_model=schemas.GreetingResponse, status_code=201)
async def create_greeting(greeting: schemas.GreetingCreate, db: Session = Depends(get_db)):
    db_greeting = models.Greeting(**greeting.dict())
    db.add(db_greeting)
    db.commit()
    db.refresh(db_greeting)
    return db_greeting
```

## 业务逻辑实现方案

### 服务层设计

创建一个 `GreetingService` 类，用于处理问候消息的业务逻辑。

```python
from sqlalchemy.orm import Session
from . import models, schemas

class GreetingService:
    def __init__(self, db: Session):
        self.db = db

    def create_greeting(self, greeting: schemas.GreetingCreate):
        db_greeting = models.Greeting(**greeting.dict())
        self.db.add(db_greeting)
        self.db.commit()
        self.db.refresh(db_greeting)
        return db_greeting
```

**在 API 中使用服务层**:

```python
from fastapi import Depends
from .services import GreetingService

@app.post("/greetings/", response_model=schemas.GreetingResponse, status_code=201)
async def create_greeting(greeting: schemas.GreetingCreate, service: GreetingService = Depends()):
    return service.create_greeting(greeting)
```

## 项目结构说明

```
hello_world_pim/
├── app/
│   ├── __init__.py
│   ├── models.py       # SQLAlchemy 模型定义
│   ├── schemas.py      # Pydantic 模型定义
│   ├── database.py     # 数据库连接和 Session 管理
│   ├── services.py     # 业务逻辑服务
│   ├── main.py         # FastAPI 应用入口
├── tests/
│   ├── __init__.py
│   └── test_main.py    # pytest 单元测试
├── hello_world.db      # SQLite 数据库文件 (可选)
├── Dockerfile          # Docker 配置文件 (可选)
└── README.md           # 项目说明文档
```

## 技术栈和依赖列表

- Python 3.10+
- FastAPI
- SQLAlchemy 2.0
- Pydantic v2
- pytest
- uvicorn (ASGI server)

**requirements.txt**:

```
fastapi==0.100.0
SQLAlchemy==2.0
pydantic[standard]==2.0
pytest==7.0
uvicorn[standard]==0.23.0
```

**安装依赖**:

```bash
pip install -r requirements.txt
```

This PSM provides a detailed blueprint for implementing the Hello World service using FastAPI, SQLAlchemy, and Pydantic. It covers the technical architecture, data model, API design, business logic, project structure, and technology stack.
