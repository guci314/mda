# FastAPI 待办事项系统 PSM 文档

## 技术架构说明

本系统采用 FastAPI 作为 Web 框架，基于 Python 3.10+ 构建。架构遵循以下分层设计：

1. **表现层**：FastAPI 路由和控制器
2. **业务逻辑层**：服务类和领域模型
3. **数据访问层**：SQLAlchemy 2.0 ORM
4. **基础设施层**：数据库和外部依赖

架构特点：
- 使用依赖注入管理组件
- 异步 I/O 处理
- OpenAPI 自动文档生成
- Pydantic 数据验证
- Alembic 数据库迁移

## 数据模型实现

### SQLAlchemy 模型

```python
# models.py
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class TodoStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class Todo(Base):
    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(20), default=TodoStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column(DateTime, nullable=True)
```

### Pydantic 模式

```python
# schemas.py
from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel

class TodoStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"

class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None

class TodoCreate(TodoBase):
    pass

class TodoUpdate(BaseModel):
    status: Optional[TodoStatus] = None

class Todo(TodoBase):
    id: int
    status: TodoStatus
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True
```

## API 接口设计

### 路由定义

```python
# api.py
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/", response_model=schemas.Todo)
async def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    pass

@router.get("/", response_model=List[schemas.Todo])
async def get_todos(db: Session = Depends(get_db)):
    pass

@router.patch("/{todo_id}", response_model=schemas.Todo)
async def update_todo_status(
    todo_id: int, 
    status: schemas.TodoUpdate, 
    db: Session = Depends(get_db)
):
    pass

@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    pass
```

### API 端点详情

#### 1. 创建待办事项

- **路径**: POST /todos/
- **请求体**:
  ```json
  {
    "title": "string",
    "description": "string"
  }
  ```
- **响应**:
  - 201 Created
  ```json
  {
    "id": 1,
    "title": "string",
    "description": "string",
    "status": "pending",
    "created_at": "2023-07-20T12:00:00",
    "completed_at": null
  }
  ```

#### 2. 获取所有待办事项

- **路径**: GET /todos/
- **响应**:
  - 200 OK
  ```json
  [
    {
      "id": 1,
      "title": "string",
      "description": "string",
      "status": "pending",
      "created_at": "2023-07-20T12:00:00",
      "completed_at": null
    }
  ]
  ```

#### 3. 更新待办事项状态

- **路径**: PATCH /todos/{todo_id}
- **请求体**:
  ```json
  {
    "status": "completed"
  }
  ```
- **响应**:
  - 200 OK
  ```json
  {
    "id": 1,
    "title": "string",
    "description": "string",
    "status": "completed",
    "created_at": "2023-07-20T12:00:00",
    "completed_at": "2023-07-20T12:30:00"
  }
  ```

#### 4. 删除待办事项

- **路径**: DELETE /todos/{todo_id}
- **响应**:
  - 204 No Content

## 业务逻辑实现

### 服务层实现

```python
# services.py
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session

from . import models, schemas

class TodoService:
    @staticmethod
    def create_todo(db: Session, todo: schemas.TodoCreate) -> models.Todo:
        db_todo = models.Todo(
            title=todo.title,
            description=todo.description
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo

    @staticmethod
    def get_todos(db: Session) -> List[models.Todo]:
        return db.query(models.Todo).all()

    @staticmethod
    def update_todo_status(
        db: Session, 
        todo_id: int, 
        status: schemas.TodoStatus
    ) -> models.Todo:
        db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        db_todo.status = status
        if status == schemas.TodoStatus.COMPLETED:
            db_todo.completed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(db_todo)
        return db_todo

    @staticmethod
    def delete_todo(db: Session, todo_id: int) -> None:
        db_todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        
        db.delete(db_todo)
        db.commit()
```

### 控制器实现

```python
# api.py (完整实现)
@router.post("/", response_model=schemas.Todo)
async def create_todo(todo: schemas.TodoCreate, db: Session = Depends(get_db)):
    return TodoService.create_todo(db, todo)

@router.get("/", response_model=List[schemas.Todo])
async def get_todos(db: Session = Depends(get_db)):
    return TodoService.get_todos(db)

@router.patch("/{todo_id}", response_model=schemas.Todo)
async def update_todo_status(
    todo_id: int, 
    status_update: schemas.TodoUpdate, 
    db: Session = Depends(get_db)
):
    return TodoService.update_todo_status(db, todo_id, status_update.status)

@router.delete("/{todo_id}")
async def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    TodoService.delete_todo(db, todo_id)
    return Response(status_code=204)
```

## 项目结构说明

```
todo_system/
├── alembic/                  # 数据库迁移脚本
├── tests/                    # 测试代码
├── app/                      # 主应用代码
│   ├── __init__.py
│   ├── main.py               # FastAPI 应用入口
│   ├── api.py                # API 路由
│   ├── models.py             # SQLAlchemy 模型
│   ├── schemas.py            # Pydantic 模型
│   ├── services.py           # 业务逻辑
│   ├── database.py           # 数据库连接
│   └── config.py             # 应用配置
├── requirements.txt          # 依赖列表
└── README.md
```

## 依赖列表

```text
# requirements.txt
fastapi==0.95.2
uvicorn==0.22.0
sqlalchemy==2.0.15
psycopg2-binary==2.9.6  # 或 sqlite3（Python 内置）
pydantic==2.0.2
alembic==1.11.1
python-dotenv==1.0.0
pytest==7.3.1
httpx==0.24.1
```

## 数据库配置

```python
# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"
# 或 SQLite: "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 应用入口

```python
# main.py
from fastapi import FastAPI
from .api import router as todo_router
from .database import engine, Base

app = FastAPI(title="Todo System", version="1.0.0")

# 创建数据库表（生产环境应使用迁移工具）
Base.metadata.create_all(bind=engine)

app.include_router(todo_router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}
```

## 测试示例

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_todo():
    response = client.post(
        "/todos/",
        json={"title": "Test Todo", "description": "Test Description"}
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Todo"
```

这个 PSM 文档提供了从 PIM 到 FastAPI 平台的完整转换，包含了所有必要的技术实现细节，同时保持了原始的业务逻辑不变。