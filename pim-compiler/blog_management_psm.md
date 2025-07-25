# 博客管理系统 PSM (Platform Specific Model)

## 系统概述
一个基于 FastAPI 的博客管理系统，支持文章发布、分类管理、标签系统和评论功能。

## 技术栈
- 框架：FastAPI
- 数据库：SQLAlchemy + SQLite/PostgreSQL
- 认证：JWT
- Python 版本：3.8+

## 数据模型

### 1. User (用户)
```python
class User:
    id: int (primary_key)
    username: str (unique, max_length=50)
    email: str (unique, max_length=120)
    password_hash: str
    is_active: bool (default=True)
    is_admin: bool (default=False)
    created_at: datetime
    updated_at: datetime
    
    # 关系
    posts: List[Post]
    comments: List[Comment]
```

### 2. Category (分类)
```python
class Category:
    id: int (primary_key)
    name: str (unique, max_length=50)
    slug: str (unique, max_length=50)
    description: str (max_length=200, nullable)
    created_at: datetime
    
    # 关系
    posts: List[Post]
```

### 3. Tag (标签)
```python
class Tag:
    id: int (primary_key)
    name: str (unique, max_length=30)
    slug: str (unique, max_length=30)
    
    # 关系
    posts: List[Post] (many-to-many)
```

### 4. Post (文章)
```python
class Post:
    id: int (primary_key)
    title: str (max_length=200)
    slug: str (unique, max_length=200)
    content: str (text)
    excerpt: str (max_length=500, nullable)
    status: str (enum: draft, published, archived)
    author_id: int (foreign_key -> User)
    category_id: int (foreign_key -> Category, nullable)
    view_count: int (default=0)
    published_at: datetime (nullable)
    created_at: datetime
    updated_at: datetime
    
    # 关系
    author: User
    category: Category
    tags: List[Tag]
    comments: List[Comment]
```

### 5. Comment (评论)
```python
class Comment:
    id: int (primary_key)
    content: str (max_length=1000)
    author_id: int (foreign_key -> User, nullable)
    post_id: int (foreign_key -> Post)
    parent_id: int (foreign_key -> Comment, nullable)
    is_approved: bool (default=True)
    created_at: datetime
    
    # 关系
    author: User
    post: Post
    parent: Comment
    replies: List[Comment]
```

## API 端点

### 认证相关
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/refresh` - 刷新令牌
- `GET /api/auth/me` - 获取当前用户信息

### 用户管理
- `GET /api/users` - 获取用户列表（管理员）
- `GET /api/users/{id}` - 获取用户详情
- `PUT /api/users/{id}` - 更新用户信息
- `DELETE /api/users/{id}` - 删除用户（管理员）

### 分类管理
- `GET /api/categories` - 获取分类列表
- `POST /api/categories` - 创建分类（管理员）
- `GET /api/categories/{slug}` - 获取分类详情
- `PUT /api/categories/{id}` - 更新分类（管理员）
- `DELETE /api/categories/{id}` - 删除分类（管理员）

### 标签管理
- `GET /api/tags` - 获取标签列表
- `POST /api/tags` - 创建标签
- `GET /api/tags/{slug}` - 获取标签详情
- `PUT /api/tags/{id}` - 更新标签
- `DELETE /api/tags/{id}` - 删除标签

### 文章管理
- `GET /api/posts` - 获取文章列表（支持分页、筛选）
- `POST /api/posts` - 创建文章
- `GET /api/posts/{slug}` - 获取文章详情
- `PUT /api/posts/{id}` - 更新文章
- `DELETE /api/posts/{id}` - 删除文章
- `GET /api/posts/category/{category_slug}` - 按分类获取文章
- `GET /api/posts/tag/{tag_slug}` - 按标签获取文章
- `GET /api/posts/author/{user_id}` - 按作者获取文章

### 评论管理
- `GET /api/posts/{post_id}/comments` - 获取文章评论
- `POST /api/posts/{post_id}/comments` - 发表评论
- `PUT /api/comments/{id}` - 更新评论
- `DELETE /api/comments/{id}` - 删除评论
- `POST /api/comments/{id}/approve` - 审核评论（管理员）

### 统计相关
- `GET /api/stats/overview` - 获取系统统计概览
- `GET /api/stats/popular-posts` - 获取热门文章
- `GET /api/stats/recent-comments` - 获取最近评论

## 请求/响应模型

### UserCreate
```python
class UserCreate:
    username: str
    email: str
    password: str
```

### UserResponse
```python
class UserResponse:
    id: int
    username: str
    email: str
    is_active: bool
    is_admin: bool
    created_at: datetime
```

### PostCreate
```python
class PostCreate:
    title: str
    content: str
    excerpt: Optional[str]
    category_id: Optional[int]
    tag_ids: List[int]
    status: str = "draft"
```

### PostResponse
```python
class PostResponse:
    id: int
    title: str
    slug: str
    content: str
    excerpt: Optional[str]
    status: str
    author: UserResponse
    category: Optional[CategoryResponse]
    tags: List[TagResponse]
    view_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
```

### CommentCreate
```python
class CommentCreate:
    content: str
    parent_id: Optional[int]
```

### PaginatedResponse
```python
class PaginatedResponse:
    items: List[Any]
    total: int
    page: int
    per_page: int
    pages: int
```

## 业务规则

1. **用户权限**
   - 未登录用户只能查看已发布的文章和已审核的评论
   - 登录用户可以发表评论和创建文章
   - 作者只能编辑自己的文章和评论
   - 管理员拥有所有权限

2. **文章发布**
   - 文章有三种状态：草稿、已发布、已归档
   - 只有已发布的文章对外可见
   - 发布时自动生成 slug（基于标题）
   - 更新文章时自动更新 updated_at

3. **评论系统**
   - 支持嵌套评论（回复）
   - 可配置是否需要审核
   - 登录用户和匿名用户都可以评论

4. **分类和标签**
   - 每篇文章只能属于一个分类
   - 每篇文章可以有多个标签
   - 删除分类时，相关文章的分类设为空
   - 删除标签时，自动解除与文章的关联

## 中间件和安全

1. **CORS 配置**
   ```python
   origins = ["http://localhost:3000", "https://yourdomain.com"]
   ```

2. **认证中间件**
   - 使用 JWT Bearer token
   - Token 有效期：24小时
   - Refresh token 有效期：7天

3. **请求限流**
   - API 限流：100请求/分钟
   - 登录尝试限制：5次/5分钟

4. **数据验证**
   - 使用 Pydantic 模型验证
   - SQL 注入防护
   - XSS 防护

## 项目结构
```
blog_management/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   └── comment.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── post.py
│   │   ├── category.py
│   │   ├── tag.py
│   │   └── comment.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── posts.py
│   │   ├── categories.py
│   │   ├── tags.py
│   │   ├── comments.py
│   │   └── stats.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   └── dependencies.py
│   └── utils/
│       ├── __init__.py
│       └── slug.py
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_posts.py
│   └── test_comments.py
├── alembic/
├── requirements.txt
├── .env.example
└── README.md
```

## 环境变量
```env
DATABASE_URL=sqlite:///./blog.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

## 启动命令
```bash
# 开发环境
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 生产环境
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```