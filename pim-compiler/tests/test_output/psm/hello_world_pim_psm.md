# Hello World Service - Platform Specific Model (FastAPI)

## 1. 技术架构说明

本 PSM 基于 FastAPI 框架构建 Hello World 服务。FastAPI 是一个现代、高性能的 Python Web 框架，特别适合构建 API。

-   **框架**: FastAPI
-   **编程语言**: Python 3.10+
-   **数据库**: SQLite (默认，可配置为 PostgreSQL)
-   **ORM**: SQLAlchemy 2.0
-   **数据验证**: Pydantic v2
-   **测试框架**: pytest

## 2. 数据模型设计

### 2.1. 数据模型

由于 Hello World 服务非常简单，我们不需要复杂的数据库模型。但是，为了演示 SQLAlchemy 的使用，我们可以创建一个简单的配置表。

```python
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库配置
DATABASE_URL = "sqlite:///./hello_world.db"  # 默认使用 SQLite，可配置为 PostgreSQL

# 创建 SQLAlchemy 引擎
engine = create_engine(DATABASE_URL)

# 创建 SessionLocal 类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Base 类
Base = declarative_base()

# 定义配置模型
class Config(Base):
    __tablename__ = "config"

    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String, unique=True, index=True)
    version = Column(String)

# 创建数据库表
Base.metadata.create_all(bind=engine)
```

### 2.2. 数据库连接

```python
# 依赖注入，获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 3. API 接口设计

### 3.1. API 接口

-   **GET /hello**: 返回 "Hello World!" 消息。

### 3.2. 请求/响应格式

**请求**:

-   无请求参数

**响应**:

```json
{
    "message": "Hello World!"
}
```

### 3.3. 状态码

-   200 OK: 成功返回问候消息。

### 3.4. FastAPI 实现

```python
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import models

app = FastAPI()

@app.get("/hello")
def say_hello(db: Session = Depends(get_db)):
    # 从数据库中获取配置信息
    config = db.query(models.Config).filter(models.Config.service_name == "hello-world").first()
    if config:
        return {"message": f"Hello World! (Version: {config.version})"}
    else:
        return {"message": "Hello World!"}
```

## 4. 业务逻辑实现方案

### 4.1. 服务层设计

由于业务逻辑非常简单，我们直接在 API 接口中实现。对于更复杂的应用，可以创建一个独立的服务层。

### 4.2. 业务逻辑

-   当调用 `/hello` 接口时，服务返回 "Hello World!" 消息。

## 5. 项目结构说明

```
hello_world_service/
├── app/                  # 应用代码
│   ├── __init__.py
│   ├── main.py           # FastAPI 应用入口
│   ├── models.py         # SQLAlchemy 模型定义
│   └── database.py       # 数据库连接和配置
├── tests/                # 测试代码
│   ├── __init__.py
│   └── test_main.py      # 测试用例
├── pyproject.toml        # 项目依赖和配置 (Poetry)
└── README.md             # 项目说明
```

## 6. 技术栈和依赖列表

-   FastAPI
-   SQLAlchemy 2.0
-   Pydantic v2
-   pytest
-   uvicorn (ASGI server)
-   Poetry (依赖管理)

### 6.1. pyproject.toml 示例

```toml
[tool.poetry]
name = "hello-world-service"
version = "0.1.0"
description = "A simple Hello World service with FastAPI"
authors = ["PIM Engine Demo"]

[tool.poetry.dependencies]
python = "^3.10"
fastapi = "^0.100.0"
uvicorn = {extras = ["standard"], version = "^0.23.0"}
SQLAlchemy = "^2.0"
pydantic = "^2.0"
pytest = "^7.0"
pytest-asyncio = "^0.21.0"
psycopg2-binary = "^2.9" # 如果使用 PostgreSQL

[tool.poetry.dev-dependencies]
pytest = "^7.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

## 7. 测试

### 7.1. 测试用例 (tests/test_main.py)

```python
from fastapi.testclient import TestClient
from app.main import app
from app.database import engine, SessionLocal
from app import models
import pytest

@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    models.Base.metadata.create_all(bind=engine)
    yield
    models.Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def test_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

client = TestClient(app)

def test_hello_world(test_db):
    # 插入测试数据
    config = models.Config(service_name="hello-world", version="1.0.0")
    test_db.add(config)
    test_db.commit()
    test_db.refresh(config)

    response = client.get("/hello")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World! (Version: 1.0.0)"}
```

### 7.2. 运行测试

```bash
pytest
```
