# 任务管理系统 - 平台特定模型 (PSM) for FastAPI

## 0. 文档概述

本文档定义了基于平台无关模型 (PIM) 的任务管理系统的平台特定模型 (PSM)。本 PSM 专为 FastAPI 技术栈设计，详细说明了从技术架构到代码实现的关键设计决策。

- **目标平台**: FastAPI
- **数据库**: PostgreSQL (兼容 SQLite)
- **ORM**: SQLAlchemy 2.0 (异步)
- **数据验证**: Pydantic V2
- **异步驱动**: `asyncpg` for PostgreSQL

---

## 1. 技术架构说明

本系统将采用经典的分层架构，以实现关注点分离 (Separation of Concerns)，提高代码的可维护性、可扩展性和可测试性。

- **表示层 (Presentation Layer)**: 由 FastAPI 的路由 (Router) 组成。负责处理 HTTP 请求，调用服务层，并返回格式化的 HTTP 响应。使用 Pydantic 模型进行数据验证和序列化。
- **服务层 (Service Layer)**: 封装核心业务逻辑。例如，`TaskService` 负责处理创建任务、更新状态等操作。该层不直接与数据库交互，而是通过数据访问层。
- **数据访问层 (Data Access Layer)**: 使用 SQLAlchemy 2.0 ORM 和异步会话 (`AsyncSession`) 与数据库进行交互。提供 CRUD (创建、读取、更新、删除) 操作的封装，供服务层调用。
- **模型层 (Model Layer)**:
    - **ORM 模型**: 使用 SQLAlchemy `DeclarativeBase` 定义的数据库表结构。
    - **数据模式 (Schema)**: 使用 Pydantic `BaseModel` 定义 API 的数据传输对象 (DTO)，用于请求体验证和响应体序列化。

![Architecture Diagram](https://i.imgur.com/sA2fWJp.png)

---

## 2. 数据模型设计 (SQLAlchemy)

数据模型将使用 SQLAlchemy 2.0 的声明式异步模型进行定义。

### 2.1. 辅助模型

**任务状态和优先级枚举**
为了保证数据一致性，使用 Python 的 `enum` 类型。

```python
# app/models/enums.py
import enum

class TaskStatus(str, enum.Enum):
    TODO = "待办"
    IN_PROGRESS = "进行中"
    DONE = "已完成"
    CANCELED = "已取消"

class TaskPriority(str, enum.Enum):
    LOW = "低"
    MEDIUM = "中"
    HIGH = "高"
```

### 2.2. 核心实体模型

**任务与标签���多对多关联表**

```python
# app/models/task_tag.py
from sqlalchemy import Table, Column, ForeignKey
from app.core.db import Base

task_tag_association = Table(
    "task_tag_association",
    Base.metadata,
    Column("task_id", ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)
```

**任务 (Task) 模型**

```python
# app/models/task.py
import datetime
from typing import List, Optional
from sqlalchemy import String, Text, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models.enums import TaskStatus, TaskPriority
from app.models.task_tag import task_tag_association

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.MEDIUM)
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO, index=True)
    
    due_date: Mapped[Optional[datetime.date]]
    
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))

    tags: Mapped[List["Tag"]] = relationship(
        secondary=task_tag_association, back_populates="tasks", lazy="selectin"
    )
```

**标签 (Tag) 模型**

```python
# app/models/tag.py
from typing import List, Optional
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base
from app.models.task_tag import task_tag_association

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    color: Mapped[str] = mapped_column(String(7), default="#FFFFFF") # Hex color
    description: Mapped[Optional[str]] = mapped_column(String(255))

    tasks: Mapped[List["Task"]] = relationship(
        secondary=task_tag_association, back_populates="tags", lazy="selectin"
    )
```

---

## 3. API 接口设计 (RESTful with Pydantic)

API 将遵循 RESTful 设计原则，使用 Pydantic 模型进行数据校验和序列化。

### 3.1. 数据模式 (Pydantic Schemas)

**Tag Schemas**
```python
# app/schemas/tag.py
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field(default="#FFFFFF", pattern=r"^#[0-9a-fA-F]{6}$")
    description: Optional[str] = Field(None, max_length=255)

class TagCreate(TagBase):
    pass

class TagUpdate(TagBase):
    pass

class TagRead(TagBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
```

**Task Schemas**
```python
# app/schemas/task.py
import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from app.models.enums import TaskStatus, TaskPriority
from app.schemas.tag import TagRead

class TaskBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime.date] = None

class TaskCreate(TaskBase):
    tag_ids: Optional[List[int]] = []

    @field_validator('due_date')
    def validate_due_date(cls, v):
        if v and v < datetime.date.today():
            raise ValueError('截止日期必须是未来时间')
        return v

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime.date] = None
    tag_ids: Optional[List[int]] = None

class TaskStatusUpdate(BaseModel):
    status: TaskStatus

class TaskRead(TaskBase):
    id: int
    status: TaskStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime
    completed_at: Optional[datetime.datetime]
    tags: List[TagRead] = []
    
    model_config = ConfigDict(from_attributes=True)
```

### 3.2. API Endpoints

#### 任务接口 (`/tasks`)

| 描述 | HTTP 方法 | 路��� | 请求体 | 响应体 | 成功状态码 | 错误状态码 |
|---|---|---|---|---|---|---|
| 创建任务 | `POST` | `/tasks/` | `TaskCreate` | `TaskRead` | `201 Created` | `422` |
| 查询任务 | `GET` | `/tasks/` | - | `List[TaskRead]` | `200 OK` | `422` |
| 获取任务 | `GET` | `/tasks/{task_id}` | - | `TaskRead` | `200 OK` | `404` |
| 更新任务 | `PUT` | `/tasks/{task_id}` | `TaskUpdate` | `TaskRead` | `200 OK` | `404`, `422` |
| 更新任务状态 | `PATCH` | `/tasks/{task_id}/status` | `TaskStatusUpdate` | `TaskRead` | `200 OK` | `400`, `404` |
| 删除任务 | `DELETE` | `/tasks/{task_id}` | - | - | `204 No Content` | `400`, `404` |

#### 标签接口 (`/tags`)

| 描述 | HTTP 方法 | 路由 | 请求体 | 响应体 | 成功状态码 | 错误状态码 |
|---|---|---|---|---|---|---|
| 创建标签 | `POST` | `/tags/` | `TagCreate` | `TagRead` | `201 Created` | `422` |
| 获取所有标签 | `GET` | `/tags/` | - | `List[TagRead]` | `200 OK` | - |
| 更新标签 | `PUT` | `/tags/{tag_id}` | `TagUpdate` | `TagRead` | `200 OK` | `404`, `422` |
| 删除标签 | `DELETE` | `/tags/{tag_id}` | - | - | `204 No Content` | `400`, `404` |

---

## 4. 业务逻辑实现方案 (服务层)

服务层将包含所有 PIM 中定义的业务规则。

### `TaskService`
- `create_task(db, task_data)`:
  - 接收 `TaskCreate` schema。
  - 验证 `tag_ids` 是否存在。
  - 创建 `Task` 对象并保存到数据库。
- `update_task_status(db, task_id, new_status)`:
  - 获取任务。
  - **业务规则**: 检查任务当前状态，如果为 `CANCELED`，则引发 `HTTPException(400, "已取消的任务不能更改状态")`。
  - **业务规则**: 如果新状态为 `DONE`，则设置 `completed_at` 为当前时间。
  - 更新并保存任务。
- `delete_task(db, task_id)`:
  - 获取任务。
  - **业务规则**: 检查任务状态，如果不是 `DONE` 或 `CANCELED`，则引发 `HTTPException(400, "只能删除已完成或已取消的任务")`。
  - 删除任务。
- `get_tasks(db, filters, sorting, pagination)`:
  - 构建动态的 SQLAlchemy 查询，支持按状态、优先级、标签筛选。
  - 支持按创建时间、截止日期排序。
  - 实现分页逻辑。

### `TagService`
- `delete_tag(db, tag_id)`:
  - 获取标签及其关联的任务数。
  - **业务规则**: 如果关联的任务数大于 0，则引发 `HTTPException(400, "无法删除正在被使用的标签")`。
  - 删除标签。

---

## 5. 项目结构说明

推荐采用模块化的项目结构，便于未来扩展。

```
task_manager/
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 应用实例和全局中间件
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── deps.py     # 依赖注入 (e.g., get_db_session)
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── tasks.py  # 任务 API 路由
│   │           └── tags.py   # 标签 API 路由
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py       # 应用配置 (e.g., 数据库 URL)
│   │   └── db.py           # 数据库引擎和会话管理
│   ├── models/
│   │   ├── __init__.py
│   │   ├── enums.py
│   │   ├── tag.py
│   │   ├── task.py
│   │   └── task_tag.py
��   ├── schemas/
│   │   ├── __init__.py
│   │   ├── task.py
│   │   └── tag.py
│   └── services/
│       ├── __init__.py
│       ├── task_service.py # 任务业务逻辑
│       └── tag_service.py  # 标签业务逻辑
├── tests/                  # Pytest 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   └── test_api/
│       └── test_tasks.py
├── alembic/                # Alembic 数据库迁移
├── alembic.ini
├── .env.example            # 环境变量示例
└── requirements.txt        # 项目依赖
```

---

## 6. 技术栈和依赖列表

以下是 `requirements.txt` 文件的建议内容：

```txt
# Web Framework
fastapi

# ASGI Server
uvicorn[standard]

# ORM and Database Driver
sqlalchemy[asyncio]
alembic
asyncpg # For PostgreSQL

# Pydantic for data validation
pydantic[email]
pydantic-settings

# Testing
pytest
pytest-cov
httpx
```

此 PSM 文档为任务管理系统的 FastAPI 实现提供了全面的蓝图。开发团队可以此为依据，进行具体的编码工作。
