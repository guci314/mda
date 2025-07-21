# FastAPI 平台特定模型 (PSM) - 博客系统

本文档基于 `pim/blog.md` 中定义的平台无关模型，为博客系统设计了基于 FastAPI 框架的平台特定模型。

## 1. 技术架构说明

本系统将采用基于 FastAPI 的现代化分层架构，以实现高性能、高可维护性和可扩展性。

- **Web 层 (Web Layer)**: 使用 FastAPI 的 `APIRouter` 构建，负责处理 HTTP 请求、解析和验证输入数据（通过 Pydantic）、调用业务逻辑层，并格式化返回的 JSON 响应。FastAPI 的异步特性 (ASGI) 确保了高并发处理能力。
- **业务逻辑层 (Service Layer)**: 独立的 Python 模块，封装所有核心业务规则（例如：创建文章、审核评论）。该层不直接依赖 Web 框架，通过依赖注入（FastAPI `Depends`）与 Web 层解耦。
- **数据访问层 (Data Access Layer)**: 使用 SQLAlchemy 2.0 (ORM) 作为数据访问接口。通过定义数据模型（Models）和仓库（Repository）模式，将业务逻辑与数据库实现细节分离。
- **数据库层 (Database Layer)**: 选用 PostgreSQL 作为生产环境数据库，因其稳定性、功能丰富和对 JSON 的良好支持。开发和测试环境可使用 SQLite 以简化部署。数据库迁移将由 Alembic 管理。

![Architecture Diagram](https://i.imgur.com/8y6gJcf.png)

## 2. 数据模型设计 (SQLAlchemy 2.0)

数据模型使用 SQLAlchemy 2.0 的声明式映射（Declarative Mapping）和类型注解（Type Annotation）风格定义，与 Pydantic 模型严格分离。

### 实体关系图 (ERD)

```mermaid
erdiagram
    USER {
        int id PK
        varchar username UK
        varchar hashed_password
        datetime created_at
    }

    POST {
        int id PK
        varchar title
        text content
        varchar summary
        int author_id FK
        datetime created_at
        datetime updated_at
        varchar status "default: 'draft'"
        int view_count "default: 0"
    }

    CATEGORY {
        int id PK
        varchar name UK
        text description
    }

    COMMENT {
        int id PK
        int post_id FK
        varchar author_name
        varchar email
        text content
        datetime created_at
        varchar status "default: 'pending'"
    }

    POST_CATEGORY {
        int post_id PK, FK
        int category_id PK, FK
    }

    USER ||--o{ POST : "writes"
    POST }o--o{ CATEGORY : "has" (via POST_CATEGORY)
    POST ||--o{ COMMENT : "has"
    POST_CATEGORY }|..| POST : "links"
    POST_CATEGORY }|..| CATEGORY : "links"

```

### 模型定义 (`app/models.py`)

为了更好地实践，PIM 中的“文章(Article)”在此处实现为 `Post`，“作者”抽象为 `User` 模型。

```python
# app/models.py
import datetime
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, Table
)
from sqlalchemy.orm import relationship, Mapped, mapped_column
from app.db.base import Base

# 多对多关联表
post_category_association = Table(
    'post_category',
    Base.metadata,
    Column('post_id', Integer, ForeignKey('posts.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)

    posts: Mapped[list["Post"]] = relationship("Post", back_populates="author")

class Post(Base):
    __tablename__ = 'posts'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(String(500))
    author_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default='draft', nullable=False) # 'draft', 'published'
    view_count: Mapped[int] = mapped_column(Integer, default=0)

    author: Mapped["User"] = relationship("User", back_populates="posts")
    comments: Mapped[list["Comment"]] = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    categories: Mapped[list["Category"]] = relationship("Category", secondary=post_category_association, back_populates="posts")

class Category(Base):
    __tablename__ = 'categories'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)

    posts: Mapped[list["Post"]] = relationship("Post", secondary=post_category_association, back_populates="categories")

class Comment(Base):
    __tablename__ = 'comments'
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    post_id: Mapped[int] = mapped_column(ForeignKey('posts.id'), nullable=False)
    author_name: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=datetime.datetime.utcnow)
    status: Mapped[str] = mapped_column(String(20), default='pending', nullable=False) # 'pending', 'approved', 'rejected'

    post: Mapped["Post"] = relationship("Post", back_populates="comments")
```

## 3. API 接口设计 (RESTful)

API 设计遵循 RESTful 原则，使用 Pydantic V2 模型进行数据验证和序列化。

### Pydantic Schemas (`app/schemas.py`)

```python
# app/schemas.py
import datetime
from pydantic import BaseModel, ConfigDict, EmailStr

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: str | None = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime.datetime
    model_config = ConfigDict(from_attributes=True)

# Comment Schemas
class CommentBase(BaseModel):
    author_name: str
    email: EmailStr
    content: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    post_id: int
    created_at: datetime.datetime
    status: str
    model_config = ConfigDict(from_attributes=True)

# Post Schemas
class PostBase(BaseModel):
    title: str
    content: str
    summary: str | None = None

class PostCreate(PostBase):
    category_ids: list[int] = []

class PostUpdate(PostBase):
    category_ids: list[int] | None = None

class Post(PostBase):
    id: int
    author: User
    created_at: datetime.datetime
    updated_at: datetime.datetime
    status: str
    view_count: int
    comments: list[Comment] = []
    categories: list[Category] = []
    model_config = ConfigDict(from_attributes=True)
```

### Endpoints

| 功能 | HTTP Method | 路由 (Path) | 成功状态码 | 失败状态码 | 描述 |
|---|---|---|---|---|---|
| **文章服务** | | | | | |
| 创建文章 | `POST` | `/posts/` | `201 Created` | `401`, `422` | 创建一篇新文章（默认为草稿） |
| 发布文章 | `POST` | `/posts/{id}/publish` | `200 OK` | `401`, `404` | 将草稿���章状态更新为已发布 |
| 获取文章列表 | `GET` | `/posts/` | `200 OK` | - | 支持按分类、状态过滤和分页 |
| 获取单篇文章 | `GET` | `/posts/{id}` | `200 OK` | `404` | 获取文章详情，并增加浏览量 |
| 更新文章 | `PUT` | `/posts/{id}` | `200 OK` | `401`, `404`, `422` | 更新文章内容 |
| 删除文章 | `DELETE` | `/posts/{id}` | `204 No Content` | `401`, `404` | 删除一篇文章 |
| **评论服务** | | | | | |
| 发表评论 | `POST` | `/posts/{id}/comments/` | `201 Created` | `404`, `422` | 为指定文章添加一条评论 |
| 获取评论列表 | `GET` | `/posts/{id}/comments/` | `200 OK` | `404` | 获取文章下所有已批准的评论 |
| 审核评论 | `PATCH` | `/comments/{id}/approve` | `200 OK` | `401`, `404` | 管理员批准评论 |
| 删除评论 | `DELETE` | `/comments/{id}` | `204 No Content` | `401`, `404` | 管理员或作者删除评论 |
| **分类服务** | | | | | |
| 创建分类 | `POST` | `/categories/` | `201 Created` | `401`, `422` | 创建一个新的文章分类 |
| 获取分类列表 | `GET` | `/categories/` | `200 OK` | - | 获取所有分类 |

## 4. 业务逻辑实现方�� (服务层)

业务逻辑将被封装在 `app/services` 目录中，每个模块对应一个核心实体。服务函数接收 Pydantic schema 作为输入，并返回 SQLAlchemy model 实例。

### 示例：创建文章服务 (`app/services/post_service.py`)

```python
# app/services/post_service.py
from sqlalchemy.orm import Session
from app import models, schemas

def create_post(db: Session, post_in: schemas.PostCreate, author_id: int) -> models.Post:
    """
    创建一篇新文章并关联分类
    """
    # 1. 创建 Post 对象，但不包括分类
    db_post = models.Post(
        title=post_in.title,
        content=post_in.content,
        summary=post_in.summary,
        author_id=author_id,
        status='draft' # PIM 规定，初始为草稿
    )
    
    # 2. 查询并关联分类
    if post_in.category_ids:
        categories = db.query(models.Category).filter(models.Category.id.in_(post_in.category_ids)).all()
        db_post.categories = categories

    # 3. 存入数据库
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    
    return db_post

def increment_view_count(db: Session, post: models.Post):
    """
    增加文章浏览量
    """
    post.view_count += 1
    db.commit()
    db.refresh(post)
```

## 5. 项目结构说明

项目将采用模块化的结构，便于维护和扩展。

```
.
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── posts.py
│   │   │   │   ├── comments.py
│   │   │   │   └── categories.py
│   │   │   └── deps.py         # 依赖注入
│   │   └── api.py              # API 路由器聚合
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py           # 配置管理
│   ├── db/
│   │   ├── __init__.py
│   │   └── base.py             # SQLAlchemy Base 和 Session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── post.py
│   │   ├── user.py
│   │   ├── category.py
│   │   └── comment.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── post.py
│   │   ├── user.py
│   │   └── ...
│   ├── services/
│   │   ├── __init__.py
│   │   ├── post_service.py
│   │   └── comment_service.py
│   └── main.py                 # FastAPI 应用入口
├── tests/                      # Pytest 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   └── test_posts.py
├── alembic/                    # Alembic 数据库迁移
│   └── ...
├── alembic.ini
├── .env                        # 环境变量
└── requirements.txt            # Python 依赖
```

## 6. 技术栈和依赖列表

以下是本 PSM 所需的核心技术和 Python 库。

- **框架**: FastAPI
- **Web 服务器**: Uvicorn
- **ORM**: SQLAlchemy 2.0
- **数据库驱动 (PostgreSQL)**: psycopg2-binary
- **数据验证**: Pydantic V2
- **数据库迁移**: Alembic
- **配置管理**: pydantic-settings
- **密码安全**: passlib[bcrypt]
- **认证**: python-jose[cryptography] (JWT)
- **测试**: pytest, httpx

### `requirements.txt`

```
fastapi
uvicorn[standard]
sqlalchemy
psycopg2-binary
pydantic[email]
pydantic-settings
alembic
passlib[bcrypt]
python-jose[cryptography]

# Testing
pytest
httpx
```
