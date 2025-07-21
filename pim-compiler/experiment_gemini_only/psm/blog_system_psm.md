# PSM: 基于 FastAPI 的博客系统

本文档是根据平台无关模型（PIM）生成的平台特定模型（PSM），目标技术栈为 FastAPI。

## 1. 技术架构

本系统将采用现代、高性能的 Python 技术栈，遵循关注点分离（SoC）原则。

- **Web 框架**: **FastAPI**
  - 用于构建高性能、异步的 RESTful API。
  - 内置基于 Pydantic 的数据校验和自动 API 文档生成（Swagger UI & ReDoc）。
- **数据库 ORM**: **SQLAlchemy 2.0 (Asyncio)**
  - 使用其异步能力与数据库进行非阻塞式交互，充分发挥 FastAPI 的性能优势。
  - 用于定义数据模型并与数据库交互。
- **数据库**: **PostgreSQL**
  - 功能强大、稳定可靠的开源关系型数据库，支持 JSON、全文搜索等高级功能。
- **数据校验**: **Pydantic V2**
  - 用于定义 API 的请求和响应模型，确保数据类型和格式的正确性。
- **数据库迁移**: **Alembic**
  - SQLAlchemy 的官方迁移工具，用于管理数据�� schema 的版本演进。
- **��证**: **JWT (JSON Web Tokens)**
  - 使用 `python-jose` 库实现基于 OAuth2 的 token 认证。
- **密码处理**: **Passlib**
  - 用于安全地哈希和验证用户密码。

## 2. 数据模型设计 (SQLAlchemy)

基于 PIM，我们将实体具体化为 SQLAlchemy 的 ORM 模型。我们新增了 `User` 和 `Tag` 实体，并将 `Article` 重命名为 `Post` 以符合通用约定。

### 2.1. 关联表 (Association Table)

为了实现 Post 和 Tag 之间的多对多关系，需要一个关联表。

```python
# app/models/association.py
from sqlalchemy import Table, Column, ForeignKey
from app.db.base_class import Base

post_tag_association = Table(
    'post_tag',
    Base.metadata,
    Column('post_id', ForeignKey('posts.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)
```

### 2.2. User 模型

管理用户，用于认证和内容归属。

```python
# app/models/user.py
import datetime
from sqlalchemy import func, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    posts: Mapped[list["Post"]] = relationship(back_populates="author")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")
```

### 2.3. Post (Article) 模型

博客文章模型。

```python
# app/models/post.py
import datetime
from enum import Enum as PyEnum
from sqlalchemy import func, ForeignKey, Text, String, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from .association import post_tag_association

class PostStatus(str, PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"

class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[PostStatus] = mapped_column(Enum(PostStatus), default=PostStatus.DRAFT)
    
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    author: Mapped["User"] = relationship(back_populates="posts")

    comments: Mapped[list["Comment"]] = relationship(back_populates="post", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(secondary=post_tag_association, back_populates="posts")
```

### 2.4. Comment 模型

文章评论模型。

```python
# app/models/comment.py
import datetime
from sqlalchemy import func, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base

class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=func.now())

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"), index=True)
    post: Mapped["Post"] = relationship(back_populates="comments")

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    author: Mapped["User"] = relationship(back_populates="comments")
```

### 2.5. Tag 模型

标签模型。

```python
# app/models/tag.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base_class import Base
from .association import post_tag_association

class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)

    posts: Mapped[list["Post"]] = relationship(secondary=post_tag_association, back_populates="tags")
```

## 3. API 接口设计 (RESTful)

API 将遵循 RESTful 设计原则，使用 Pydantic 模型进行数据校验和序列化。

### 3.1. Pydantic Schemas

为每个模型创�� `Create`, `Update`, `InDB`, `Public` 等 schemas。

```python
# app/schemas/post.py
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from .user import UserPublic
from .tag import TagPublic
from .comment import CommentPublic
from app.models.post import PostStatus

class PostBase(BaseModel):
    title: str
    content: str

class PostCreate(PostBase):
    tags: list[str] = [] # 创建时通过 tag 名称关联

class PostUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    tags: list[str] | None = None

class PostPublic(PostBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: PostStatus
    created_at: datetime
    updated_at: datetime
    author: UserPublic
    tags: list[TagPublic] = []
    comments: list[CommentPublic] = []
```
*(其他实体的 Schema 省略，设计思路类似)*

### 3.2. API Endpoints

#### Authentication
- `POST /token`
  - **说明**: 用户登录，获取 JWT.
  - **请求体**: `application/x-www-form-urlencoded` (username, password).
  - **响应**: `{ "access_token": "...", "token_type": "bearer" }`

#### Users
- `POST /users/`
  - **说明**: 创建新用户。
  - **请求体**: `UserCreate` schema.
  - **响应**: `UserPublic` schema.
- `GET /users/me`
  - **说明**: 获取当前登录用户的信息。
  - **认证**: 需要 JWT.
  - **响应**: `UserPublic` schema.

#### Posts
- `POST /posts/`
  - **说明**: 创建一篇新文章（默认为草稿）。
  - **认证**: 需要 JWT.
  - **请求体**: `PostCreate` schema.
  - **响应**: `PostPublic` schema.
- `PUT /posts/{post_id}/publish`
  - **说明**: 发布一篇文章。
  - **认证**: 需要 JWT, 仅作者可操作。
  - **响应**: `PostPublic` schema.
- `GET /posts/`
  - **说明**: 获取已发布的文章列表，支持分页和标签过滤。
  - **查询参数**: `skip: int = 0`, `limit: int = 10`, `tag: str | None = None`.
  - **响应**: `list[PostPublic]`.
- `GET /posts/{post_id}`
  - **说明**: 获取单篇文章详情。
  - **响应**: `PostPublic` schema.
- `PUT /posts/{post_id}`
  - **说明**: 更新文章。
  - **认证**: 需要 JWT, 仅作者可操作。
  - **请求体**: `PostUpdate` schema.
  - **响应**: `PostPublic` schema.
- `DELETE /posts/{post_id}`
  - **说明**: 删除文章。
  - **认证**: 需要 JWT, 仅作者可操作。
  - **响应**: `204 No Content`.

#### Comments
- `POST /posts/{post_id}/comments/`
  - **说明**: 为文章添加评论。
  - **认证**: 需要 JWT.
  - **请求体**: `CommentCreate` schema.
  - **响应**: `CommentPublic` schema.
- `DELETE /comments/{comment_id}`
  - **说明**: 删除评论。
  - **认证**: 需要 JWT, 仅评论作者或文章作者可操作。
  - **响应**: `204 No Content`.

## 4. 业务逻辑实现方案

业务逻辑将被封装在 `CRUD` (Create, Read, Update, Delete) 函数中，保持 API 路由层的简洁。

- **数据库会话管理**: 使用 FastAPI 的依赖注入系统 (`Depends`) 来管理每个请求的 `AsyncSession` 生命周期。
- **认证与授权**:
  - 创建一个 `get_current_user` 依赖，从 `Authorization` header 中解析 JWT，验证并返回对应的用户模型。
  - 在需要授权的端点（如更新文章），注入此依赖，并添加检查逻辑（如 `if post.author_id != current_user.id: raise HTTPException(...)`）。
- **密码安全**: 使用 `passlib.context.CryptContext` 在创���用户时对密码进行哈希处理，在登录时进行验证。
- **多对多关系处理**:
  - 创建文章时，`crud` 函数会接收一个标签名称列表。
  - 它会查询已存在的标签，并创建不存在的新标签，然后将这些标签关联到新创建的文章上。
- **性能考虑**:
  - 在查询列表（如文章列表）时，使用 `select(Post).offset(skip).limit(limit)` 实现分页。
  - 在查询需要关联数据的模型时（如获取带作者和标签的文章），使用 SQLAlchemy 的 `options(selectinload(Post.author), selectinload(Post.tags))` 来避免 N+1 查询问题。

## 5. 项目结构说明

推荐采用分层、模块化的项目结构，便于维护和扩展。

```
.
├── alembic/              # Alembic 数据库迁移脚本
├── app/
│   ├── api/              # API 路由
│   │   ├── deps.py       # API 依赖项 (如 get_current_user)
│   │   └── routers/
│   │       ├── auth.py
│   │       ├── posts.py
│   │       └── users.py
│   ├── core/             # 核心逻辑，如配置、安全
│   │   ├── config.py     # 配置管理 (Pydantic Settings)
│   │   └── security.py   # 密码哈希、JWT 创建
│   ├── crud/             # CRUD 数据库操作
│   │   ├── crud_post.py
│   │   ├── crud_user.py
│   │   └── ...
│   ├── db/               # 数据库配置和会话
│   │   ├── base.py       # 包含所有模型的 Base
│   │   ├── base_class.py # Declarative Base
│   │   └── session.py    # 数据库引擎和会话工厂
│   ├── models/           # SQLAlchemy ORM 模型
│   │   ├── association.py
│   │   ├── comment.py
│   │   ├── post.py
│   │   ├── tag.py
│   │   └── user.py
│   ├── schemas/          # Pydantic Schemas
│   │   ├── comment.py
│   │   ├── post.py
│   │   ├── tag.py
│   │   ├── token.py
│   │   └── user.py
│   └── main.py           # FastAPI 应用实例和主路由
├── tests/                # 测试代码
├── .env                  # 环境变量
├── alembic.ini           # Alembic 配置文件
└���─ requirements.txt      # Python 依赖
```

## 6. 依赖列表

`requirements.txt` 文件内容：

```txt
fastapi
uvicorn[standard]
sqlalchemy[asyncio]
asyncpg
pydantic[email]
pydantic-settings
alembic
python-jose[cryptography]
passlib[bcrypt]
tenacity # 用于数据库连接重试
```
