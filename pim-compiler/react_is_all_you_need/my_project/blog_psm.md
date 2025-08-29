# Platform Specific Model (PSM) - 博客系统

## 1. Domain Models（领域模型）

### Entity Definitions（实体定义）

#### Article（文章实体）
```python
from datetime import datetime
from typing import Optional
from uuid import uuid4

class Article:
    """文章领域实体"""
    
    def __init__(
        self,
        title: str,
        content: str,
        summary: str,
        author: str,
        category_id: Optional[str] = None,
        id: Optional[str] = None,
        status: str = "draft",
        view_count: int = 0
    ):
        self.id = id or str(uuid4())
        self.title = title
        self.content = content
        self.summary = summary
        self.author = author
        self.category_id = category_id
        self.status = status  # draft/published
        self.view_count = view_count
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

    def publish(self):
        """发布文章"""
        self.status = "published"
        self.updated_at = datetime.now()

    def increment_view(self):
        """增加浏览量"""
        self.view_count += 1

    def update_content(self, new_title: str, new_content: str, new_summary: str):
        """更新文章内容"""
        self.title = new_title
        self.content = new_content
        self.summary = new_summary
        self.updated_at = datetime.now()
```

#### Category（分类实体）
```python
class Category:
    """分类领域实体"""
    
    def __init__(self, name: str, description: str, id: Optional[str] = None):
        self.id = id or str(uuid4())
        self.name = name
        self.description = description
        self.article_count = 0

    def increment_article_count(self):
        """增加文章数量"""
        self.article_count += 1

    def decrement_article_count(self):
        """减少文章数量"""
        self.article_count = max(0, self.article_count - 1)
```

#### Comment（评论实体）
```python
class Comment:
    """评论领域实体"""
    
    def __init__(
        self,
        article_id: str,
        author_name: str,
        email: str,
        content: str,
        id: Optional[str] = None
    ):
        self.id = id or str(uuid4())
        self.article_id = article_id
        self.author_name = author_name
        self.email = email
        self.content = content
        self.created_at = datetime.now()
        self.status = "pending"  # pending/published/blocked

    def approve(self):
        """审核通过评论"""
        self.status = "published"

    def block(self):
        """屏蔽评论"""
        self.status = "blocked"
```

### Database Models（数据库模型）

#### ArticleDB（文章数据库模型）
```python
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base

class ArticleDB(Base):
    __tablename__ = "articles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500), nullable=False)
    author = Column(String(50), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"), nullable=True)
    status = Column(String(20), default="draft")  # draft/published
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 关系
    category = relationship("CategoryDB", back_populates="articles")
    comments = relationship("CommentDB", back_populates="article", cascade="all, delete-orphan")
```

#### CategoryDB（分类数据库模型）
```python
class CategoryDB(Base):
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    article_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    articles = relationship("ArticleDB", back_populates="category")
```

#### CommentDB（评论数据库模型）
```python
class CommentDB(Base):
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id"), nullable=False)
    author_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    status = Column(String(20), default="pending")  # pending/published/blocked
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    article = relationship("ArticleDB", back_populates="comments")
```

### Pydantic Schemas（验证模型）

#### Article Schemas（文章验证模型）
```python
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime

class ArticleCreate(BaseModel):
    """创建文章的输入模型"""
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    summary: str = Field(..., min_length=1, max_length=500)
    author: str = Field(..., min_length=1, max_length=50)
    category_id: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

class ArticleUpdate(BaseModel):
    """更新文章的输入模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, min_length=1, max_length=500)
    category_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    
    model_config = ConfigDict(from_attributes=True)

class ArticleResponse(BaseModel):
    """文章响应模型"""
    id: str
    title: str
    content: str
    summary: str
    author: str
    category_id: Optional[str] = None
    status: str
    view_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)

class ArticleQuery(BaseModel):
    """文章查询参数模型"""
    category_id: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    
    model_config = ConfigDict(from_attributes=True)
```

#### Category Schemas（分类验证模型）
```python
class CategoryCreate(BaseModel):
    """创建分类的输入模型"""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)

class CategoryUpdate(BaseModel):
    """更新分类的输入模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)
    
    model_config = ConfigDict(from_attributes=True)

class CategoryResponse(BaseModel):
    """分类响应模型"""
    id: str
    name: str
    description: Optional[str] = None
    article_count: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

#### Comment Schemas（评论验证模型）
```python
class CommentCreate(BaseModel):
    """创建评论的输入模型"""
    article_id: str
    author_name: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
    content: str = Field(..., min_length=1, max_length=1000)
    
    model_config = ConfigDict(from_attributes=True)

class CommentUpdate(BaseModel):
    """更新评论的输入模型"""
    content: Optional[str] = Field(None, min_length=1, max_length=1000)
    status: Optional[str] = Field(None, pattern="^(pending|published|blocked)$")
    
    model_config = ConfigDict(from_attributes=True)

class CommentResponse(BaseModel):
    """评论响应模型"""
    id: str
    article_id: str
    author_name: str
    email: str
    content: str
    status: str
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

class CommentQuery(BaseModel):
    """评论查询参数模型"""
    article_id: Optional[str] = None
    status: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
    
    model_config = ConfigDict(from_attributes=True)
```

### Enums and Constants（枚举和常量）
```python
from enum import Enum

class ArticleStatus(str, Enum):
    """文章状态枚举"""
    DRAFT = "draft"
    PUBLISHED = "published"

class CommentStatus(str, Enum):
    """评论状态枚举"""
    PENDING = "pending"
    PUBLISHED = "published"
    BLOCKED = "blocked"

# 业务常量
MAX_TITLE_LENGTH = 200
MAX_SUMMARY_LENGTH = 500
MAX_AUTHOR_LENGTH = 50
MAX_CONTENT_LENGTH = 10000
MAX_COMMENT_LENGTH = 1000
```
## 2. Service Layer（服务层）

### Business Services（业务服务）

#### ArticleService（文章服务）
```python
from typing import List, Optional
from sqlalchemy.orm import Session
from models.article import ArticleDB, ArticleStatus
from schemas.article import ArticleCreate, ArticleUpdate
from repositories.article_repository import ArticleRepository

class ArticleService:
    """文章业务服务"""
    
    def __init__(self, repository: ArticleRepository):
        self.repository = repository
    
    def create_article(self, article_data: ArticleCreate) -> ArticleDB:
        """创建新文章（草稿状态）"""
        # 验证分类存在性
        if article_data.category_id:
            from repositories.category_repository import CategoryRepository
            category_repo = CategoryRepository(self.repository.db)
            category = category_repo.get_by_id(article_data.category_id)
            if not category:
                raise ValueError(f"分类不存在: {article_data.category_id}")
        
        article = ArticleDB(
            title=article_data.title,
            content=article_data.content,
            summary=article_data.summary,
            author=article_data.author,
            category_id=article_data.category_id,
            status=ArticleStatus.DRAFT
        )
        return self.repository.create(article)
    
    def publish_article(self, article_id: str) -> ArticleDB:
        """发布文章"""
        article = self.repository.get_by_id(article_id)
        if not article:
            raise ValueError(f"文章不存在: {article_id}")
        
        article.status = ArticleStatus.PUBLISHED
        return self.repository.update(article)
    
    def update_article(self, article_id: str, update_data: ArticleUpdate) -> ArticleDB:
        """更新文章"""
        article = self.repository.get_by_id(article_id)
        if not article:
            raise ValueError(f"文章不存在: {article_id}")
        
        # 更新字段
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(article, field, value)
        
        return self.repository.update(article)
    
    def delete_article(self, article_id: str) -> bool:
        """删除文章"""
        return self.repository.delete(article_id)
    
    def get_articles_by_category(self, category_id: str, skip: int = 0, limit: int = 10) -> List[ArticleDB]:
        """按分类获取文章列表"""
        return self.repository.get_by_category(category_id, skip, limit)
    
    def search_articles(self, query: str, skip: int = 0, limit: int = 10) -> List[ArticleDB]:
        """搜索文章（按标题或内容）"""
        return self.repository.search(query, skip, limit)
    
    def increment_view_count(self, article_id: str) -> ArticleDB:
        """增加文章浏览量"""
        article = self.repository.get_by_id(article_id)
        if article:
            article.view_count += 1
            return self.repository.update(article)
        raise ValueError(f"文章不存在: {article_id}")
    
    def get_published_articles(self, skip: int = 0, limit: int = 10) -> List[ArticleDB]:
        """获取已发布的文章列表"""
        return self.repository.get_published(skip, limit)
```

#### CategoryService（分类服务）
```python
class CategoryService:
    """分类业务服务"""
    
    def __init__(self, repository: CategoryRepository):
        self.repository = repository
    
    def create_category(self, category_data: CategoryCreate) -> CategoryDB:
        """创建新分类"""
        # 检查名称唯一性
        existing = self.repository.get_by_name(category_data.name)
        if existing:
            raise ValueError(f"分类名称已存在: {category_data.name}")
        
        category = CategoryDB(
            name=category_data.name,
            description=category_data.description
        )
        return self.repository.create(category)
    
    def update_category(self, category_id: str, update_data: CategoryUpdate) -> CategoryDB:
        """更新分类"""
        category = self.repository.get_by_id(category_id)
        if not category:
            raise ValueError(f"分类不存在: {category_id}")
        
        # 如果更新名称，检查唯一性
        if update_data.name and update_data.name != category.name:
            existing = self.repository.get_by_name(update_data.name)
            if existing:
                raise ValueError(f"分类名称已存在: {update_data.name}")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(category, field, value)
        
        return self.repository.update(category)
    
    def delete_category(self, category_id: str) -> bool:
        """删除分类"""
        # 检查是否有文章使用该分类
        article_count = self.repository.get_article_count(category_id)
        if article_count > 0:
            raise ValueError("该分类下还有文章，无法删除")
        
        return self.repository.delete(category_id)
    
    def get_all_categories(self) -> List[CategoryDB]:
        """获取所有分类"""
        return self.repository.get_all()
    
    def get_category_with_articles(self, category_id: str) -> CategoryDB:
        """获取分类及其文章"""
        return self.repository.get_with_articles(category_id)
```

#### CommentService（评论服务）
```python
class CommentService:
    """评论业务服务"""
    
    def __init__(self, repository: CommentRepository):
        self.repository = repository
    
    def create_comment(self, comment_data: CommentCreate) -> CommentDB:
        """创建新评论"""
        # 验证文章存在性
        from repositories.article_repository import ArticleRepository
        article_repo = ArticleRepository(self.repository.db)
        article = article_repo.get_by_id(comment_data.article_id)
        if not article:
            raise ValueError(f"文章不存在: {comment_data.article_id}")
        
        comment = CommentDB(
            article_id=comment_data.article_id,
            author_name=comment_data.author_name,
            email=comment_data.email,
            content=comment_data.content
        )
        return self.repository.create(comment)
    
    def approve_comment(self, comment_id: str) -> CommentDB:
        """审核通过评论"""
        comment = self.repository.get_by_id(comment_id)
        if not comment:
            raise ValueError(f"评论不存在: {comment_id}")
        
        comment.status = CommentStatus.PUBLISHED
        return self.repository.update(comment)
    
    def block_comment(self, comment_id: str) -> CommentDB:
        """屏蔽评论"""
        comment = self.repository.get_by_id(comment_id)
        if not comment:
            raise ValueError(f"评论不存在: {comment_id}")
        
        comment.status = CommentStatus.BLOCKED
        return self.repository.update(comment)
    
    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
        return self.repository.delete(comment_id)
    
    def get_comments_by_article(self, article_id: str, skip: int = 0, limit: int = 10) -> List[CommentDB]:
        """获取文章的评论列表"""
        return self.repository.get_by_article(article_id, skip, limit)
    
    def get_pending_comments(self, skip: int = 0, limit: int = 10) -> List[CommentDB]:
        """获取待审核的评论列表"""
        return self.repository.get_pending(skip, limit)
```

### Repository Pattern（仓储模式）

#### BaseRepository（基础仓储）
```python
from typing import Generic, TypeVar, List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """基础仓储类"""
    
    def __init__(self, db: Session, model_class: type):
        self.db = db
        self.model_class = model_class
    
    def create(self, entity: T) -> T:
        """创建实体"""
        try:
            self.db.add(entity)
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"创建失败: {str(e)}")
    
    def get_by_id(self, entity_id: str) -> Optional[T]:
        """根据ID获取实体"""
        return self.db.query(self.model_class).filter(self.model_class.id == entity_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """获取所有实体"""
        return self.db.query(self.model_class).offset(skip).limit(limit).all()
    
    def update(self, entity: T) -> T:
        """更新实体"""
        try:
            self.db.commit()
            self.db.refresh(entity)
            return entity
        except IntegrityError as e:
            self.db.rollback()
            raise ValueError(f"更新失败: {str(e)}")
    
    def delete(self, entity_id: str) -> bool:
        """删除实体"""
        entity = self.get_by_id(entity_id)
        if entity:
            self.db.delete(entity)
            self.db.commit()
            return True
        return False
```

#### ArticleRepository（文章仓储）
```python
from sqlalchemy import or_
from typing import List

class ArticleRepository(BaseRepository[ArticleDB]):
    """文章仓储"""
    
    def __init__(self, db: Session):
        super().__init__(db, ArticleDB)
    
    def get_by_category(self, category_id: str, skip: int = 0, limit: int = 10) -> List[ArticleDB]:
        """按分类获取文章"""
        return self.db.query(ArticleDB)\
            .filter(ArticleDB.category_id == category_id)\
            .offset(skip).limit(limit).all()
    
    def search(self, query: str, skip: int = 0, limit: int = 10) -> List[ArticleDB]:
        """搜索文章"""
        search_term = f"%{query}%"
        return self.db.query(ArticleDB)\
            .filter(
                or_(
                    ArticleDB.title.like(search_term),
                    ArticleDB.content.like(search_term)
                )
            )\
            .offset(skip).limit(limit).all()
    
    def get_published(self, skip: int = 0, limit: int = 10) -> List[ArticleDB]:
        """获取已发布的文章"""
        return self.db.query(ArticleDB)\
            .filter(ArticleDB.status == ArticleStatus.PUBLISHED)\
            .offset(skip).limit(limit).all()
```

#### CategoryRepository（分类仓储）
```python
class CategoryRepository(BaseRepository[CategoryDB]):
    """分类仓储"""
    
    def __init__(self, db: Session):
        super().__init__(db, CategoryDB)
    
    def get_by_name(self, name: str) -> Optional[CategoryDB]:
        """根据名称获取分类"""
        return self.db.query(CategoryDB).filter(CategoryDB.name == name).first()
    
    def get_article_count(self, category_id: str) -> int:
        """获取分类下的文章数量"""
        from models.article import ArticleDB
        return self.db.query(ArticleDB)\
            .filter(ArticleDB.category_id == category_id)\
            .count()
    
    def get_with_articles(self, category_id: str) -> Optional[CategoryDB]:
        """获取分类及其文章"""
        return self.db.query(CategoryDB)\
            .filter(CategoryDB.id == category_id)\
            .first()
```

#### CommentRepository（评论仓储）
```python
class CommentRepository(BaseRepository[CommentDB]):
    """评论仓储"""
    
    def __init__(self, db: Session):
        super().__init__(db, CommentDB)
    
    def get_by_article(self, article_id: str, skip: int = 0, limit: int = 10) -> List[CommentDB]:
        """获取文章的评论"""
        return self.db.query(CommentDB)\
            .filter(CommentDB.article_id == article_id)\
            .order_by(CommentDB.created_at.desc())\
            .offset(skip).limit(limit).all()
    
    def get_pending(self, skip: int = 0, limit: int = 10) -> List[CommentDB]:
        """获取待审核的评论"""
        return self.db.query(CommentDB)\
            .filter(CommentDB.status == CommentStatus.PENDING)\
            .order_by(CommentDB.created_at.desc())\
            .offset(skip).limit(limit).all()
```

### Transaction Management（事务管理）
```python
from contextlib import contextmanager
from sqlalchemy.orm import Session

class TransactionManager:
    """事务管理器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        try:
            yield self.db
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise e
    
    def commit(self):
        """提交事务"""
        self.db.commit()
    
    def rollback(self):
        """回滚事务"""
        self.db.rollback()
```

### Business Rules（业务规则）
```python
class BusinessRules:
    """业务规则验证器"""
    
    @staticmethod
    def validate_article_creation(article_data: ArticleCreate):
        """验证文章创建规则"""
        if len(article_data.title) > MAX_TITLE_LENGTH:
            raise ValueError(f"标题长度不能超过 {MAX_TITLE_LENGTH} 字符")
        
        if len(article_data.summary) > MAX_SUMMARY_LENGTH:
            raise ValueError(f"摘要长度不能超过 {MAX_SUMMARY_LENGTH} 字符")
        
        if len(article_data.author) > MAX_AUTHOR_LENGTH:
            raise ValueError(f"作者名称长度不能超过 {MAX_AUTHOR_LENGTH} 字符")
    
    @staticmethod
    def validate_comment_creation(comment_data: CommentCreate):
        """验证评论创建规则"""
        if len(comment_data.content) > MAX_COMMENT_LENGTH:
            raise ValueError(f"评论内容长度不能超过 {MAX_COMMENT_LENGTH} 字符")
        
        if len(comment_data.author_name) > MAX_AUTHOR_LENGTH:
            raise ValueError(f"评论者名称长度不能超过 {MAX_AUTHOR_LENGTH} 字符")
```

## 3. REST API Design（API设计）

### API Endpoints（端点定义）

#### Articles API（文章API）

##### 文章列表查询
```python
GET /api/v1/articles
```
- **描述**：获取文章列表，支持分页和过滤
- **参数**：
  - `category_id` (可选): 分类ID过滤
  - `status` (可选): 状态过滤 (draft/published)
  - `search` (可选): 搜索关键词
  - `skip` (可选): 跳过记录数，默认0
  - `limit` (可选): 返回记录数，默认10，最大100
- **响应**：200 OK
```json
{
  "items": [
    {
      "id": "uuid-string",
      "title": "文章标题",
      "summary": "文章摘要",
      "author": "作者名称",
      "category_id": "uuid-string",
      "status": "published",
      "view_count": 100,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-01-01T00:00:00Z"
    }
  ],
  "total": 50,
  "skip": 0,
  "limit": 10
}
```

##### 获取单个文章
```python
GET /api/v1/articles/{article_id}
```
- **描述**：根据ID获取文章详情
- **响应**：200 OK 或 404 Not Found
```json
{
  "id": "uuid-string",
  "title": "文章标题",
  "content": "文章内容...",
  "summary": "文章摘要",
  "author": "作者名称",
  "category_id": "uuid-string",
  "status": "published",
  "view_count": 100,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

##### 创建文章
```python
POST /api/v1/articles
```
- **描述**：创建新文章（默认为草稿状态）
- **请求体**：
```json
{
  "title": "新文章标题",
  "content": "文章内容...",
  "summary": "文章摘要",
  "author": "作者名称",
  "category_id": "uuid-string"
}
```
- **响应**：201 Created
```json
{
  "id": "uuid-string",
  "title": "新文章标题",
  "content": "文章内容...",
  "summary": "文章摘要",
  "author": "作者名称",
  "category_id": "uuid-string",
  "status": "draft",
  "view_count": 0,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": null
}
```

##### 更新文章
```python
PUT /api/v1/articles/{article_id}
```
- **描述**：更新文章信息
- **请求体**：
```json
{
  "title": "更新后的标题",
  "content": "更新后的内容...",
  "summary": "更新后的摘要",
  "category_id": "uuid-string"
}
```
- **响应**：200 OK 或 404 Not Found

##### 删除文章
```python
DELETE /api/v1/articles/{article_id}
```
- **描述**：删除文章
- **响应**：204 No Content 或 404 Not Found

##### 发布文章
```python
POST /api/v1/articles/{article_id}/publish
```
- **描述**：将草稿文章发布
- **响应**：200 OK

##### 增加浏览量
```python
POST /api/v1/articles/{article_id}/view
```
- **描述**：增加文章浏览量计数
- **响应**：200 OK

#### Categories API（分类API）

##### 获取所有分类
```python
GET /api/v1/categories
```
- **描述**：获取所有分类列表
- **响应**：200 OK
```json
[
  {
    "id": "uuid-string",
    "name": "技术",
    "description": "技术相关文章",
    "article_count": 25,
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

##### 创建分类
```python
POST /api/v1/categories
```
- **描述**：创建新分类
- **请求体**：
```json
{
  "name": "新分类",
  "description": "分类描述"
}
```
- **响应**：201 Created

##### 更新分类
```python
PUT /api/v1/categories/{category_id}
```
- **描述**：更新分类信息
- **请求体**：
```json
{
  "name": "更新后的分类名称",
  "description": "更新后的描述"
}
```
- **响应**：200 OK

##### 删除分类
```python
DELETE /api/v1/categories/{category_id}
```
- **描述**：删除分类（分类下无文章时才能删除）
- **响应**：204 No Content 或 400 Bad Request

#### Comments API（评论API）

##### 获取文章评论
```python
GET /api/v1/articles/{article_id}/comments
```
- **描述**：获取指定文章的所有评论
- **参数**：
  - `skip` (可选): 跳过记录数，默认0
  - `limit` (可选): 返回记录数，默认10，最大100
- **响应**：200 OK
```json
[
  {
    "id": "uuid-string",
    "article_id": "uuid-string",
    "author_name": "评论者",
    "email": "commenter@example.com",
    "content": "评论内容",
    "status": "published",
    "created_at": "2024-01-01T00:00:00Z"
  }
]
```

##### 发表评论
```python
POST /api/v1/articles/{article_id}/comments
```
- **描述**：为文章添加评论
- **请求体**：
```json
{
  "author_name": "评论者名称",
  "email": "commenter@example.com",
  "content": "评论内容"
}
```
- **响应**：201 Created

##### 审核评论
```python
POST /api/v1/comments/{comment_id}/approve
```
- **描述**：审核通过评论
- **响应**：200 OK

##### 屏蔽评论
```python
POST /api/v1/comments/{comment_id}/block
```
- **描述**：屏蔽评论
- **响应**：200 OK

##### 删除评论
```python
DELETE /api/v1/comments/{comment_id}
```
- **描述**：删除评论
- **响应**：204 No Content

##### 获取待审核评论
```python
GET /api/v1/comments/pending
```
- **描述**：获取所有待审核的评论（管理员功能）
- **参数**：
  - `skip` (可选): 跳过记录数，默认0
  - `limit` (可选): 返回记录数，默认10，最大100
- **响应**：200 OK

### Request/Response Models（请求响应模型）

#### 统一响应格式
```python
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    """统一API响应格式"""
    code: int = 200
    message: str = "success"
    data: Optional[T] = None

class ErrorResponse(BaseModel):
    """错误响应格式"""
    code: int
    message: str
    detail: Optional[str] = None
```

#### 分页响应模型
```python
from typing import List, Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模型"""
    items: List[T]
    total: int
    skip: int
    limit: int
```

### API Routing（路由配置）

#### 主路由配置
```python
from fastapi import FastAPI
from api.v1.articles import router as articles_router
from api.v1.categories import router as categories_router
from api.v1.comments import router as comments_router

app = FastAPI(
    title="博客系统API",
    description="一个简单的博客发布系统API",
    version="1.0.0"
)

# 注册路由
app.include_router(articles_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
```

#### 文章路由
```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy.orm import Session
from schemas.article import ArticleCreate, ArticleUpdate, ArticleResponse
from services.article_service import ArticleService
from api.v1.deps import get_article_service

router = APIRouter(prefix="/articles", tags=["articles"])

@router.get("/", response_model=PaginatedResponse[ArticleResponse])
def get_articles(
    category_id: Optional[str] = Query(None, description="分类ID"),
    status: Optional[str] = Query(None, description="文章状态"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(10, ge=1, le=100, description="返回记录数"),
    service: ArticleService = Depends(get_article_service)
):
    """获取文章列表"""
    articles = service.get_published_articles(skip, limit)
    total = len(articles)  # 实际应该查询总数
    return PaginatedResponse(items=articles, total=total, skip=skip, limit=limit)

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """获取文章详情"""
    article = service.repository.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article

@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article(
    article_data: ArticleCreate,
    service: ArticleService = Depends(get_article_service)
):
    """创建新文章"""
    try:
        article = service.create_article(article_data)
        return article
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: str,
    article_data: ArticleUpdate,
    service: ArticleService = Depends(get_article_service)
):
    """更新文章"""
    try:
        article = service.update_article(article_id, article_data)
        return article
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/{article_id}", status_code=204)
def delete_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """删除文章"""
    if not service.delete_article(article_id):
        raise HTTPException(status_code=404, detail="文章不存在")

@router.post("/{article_id}/publish", response_model=ArticleResponse)
def publish_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """发布文章"""
    try:
        article = service.publish_article(article_id)
        return article
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{article_id}/view", response_model=ArticleResponse)
def increment_view(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """增加文章浏览量"""
    try:
        article = service.increment_view_count(article_id)
        return article
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

### Middleware（中间件）

#### 错误处理中间件
```python
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """值错误处理"""
    return JSONResponse(
        status_code=400,
        content={"code": 400, "message": str(exc), "detail": "请求参数错误"}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """404错误处理"""
    return JSONResponse(
        status_code=404,
        content={"code": 404, "message": "资源不存在", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """500错误处理"""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"code": 500, "message": "服务器内部错误", "detail": "请联系管理员"}
    )
```

#### 日志中间件
```python
import time
from fastapi import Request

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """请求日志中间件"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Time: {process_time:.4f}s"
    )
    
    return response
```

#### CORS中间件
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该配置具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 4. Application Configuration（应用配置）

### Main Application（主应用）

#### 主应用入口
```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.session import engine
from db.base import Base
from api.v1.router import api_router
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("Starting up...")
    
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created")
    
    # 初始化数据（可选）
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("Shutting down...")

async def init_db():
    """初始化数据库数据"""
    from sqlalchemy.orm import Session
    from db.session import SessionLocal
    from models.category import CategoryDB
    
    db = SessionLocal()
    try:
        # 检查是否已存在分类
        category_count = db.query(CategoryDB).count()
        if category_count == 0:
            # 创建默认分类
            default_categories = [
                CategoryDB(name="技术", description="技术相关文章"),
                CategoryDB(name="生活", description="生活随笔"),
                CategoryDB(name="学习", description="学习笔记")
            ]
            for category in default_categories:
                db.add(category)
            db.commit()
            logger.info("Default categories created")
    finally:
        db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
```

### Database Configuration（数据库配置）

#### 数据库连接配置
```python
# db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=settings.DEBUG  # 调试模式下打印SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 数据库依赖
from typing import Generator

def get_db() -> Generator:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

#### 数据库基础模型
```python
# db/base.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
```

### Dependency Injection（依赖注入）

#### 服务依赖注入配置
```python
# api/v1/deps.py
from typing import Generator
from sqlalchemy.orm import Session
from db.session import get_db
from repositories.article_repository import ArticleRepository
from repositories.category_repository import CategoryRepository
from repositories.comment_repository import CommentRepository
from services.article_service import ArticleService
from services.category_service import CategoryService
from services.comment_service import CommentService

def get_article_repository(db: Session = Depends(get_db)) -> ArticleRepository:
    """获取文章仓储"""
    return ArticleRepository(db)

def get_category_repository(db: Session = Depends(get_db)) -> CategoryRepository:
    """获取分类仓储"""
    return CategoryRepository(db)

def get_comment_repository(db: Session = Depends(get_db)) -> CommentRepository:
    """获取评论仓储"""
    return CommentRepository(db)

def get_article_service(
    repository: ArticleRepository = Depends(get_article_repository)
) -> ArticleService:
    """获取文章服务"""
    return ArticleService(repository)

def get_category_service(
    repository: CategoryRepository = Depends(get_category_repository)
) -> CategoryService:
    """获取分类服务"""
    return CategoryService(repository)

def get_comment_service(
    repository: CommentRepository = Depends(get_comment_repository)
) -> CommentService:
    """获取评论服务"""
    return CommentService(repository)
```

#### API路由配置
```python
# api/v1/router.py
from fastapi import APIRouter
from api.v1.articles import router as articles_router
from api.v1.categories import router as categories_router
from api.v1.comments import router as comments_router

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(articles_router, prefix="/articles", tags=["articles"])
api_router.include_router(categories_router, prefix="/categories", tags=["categories"])
api_router.include_router(comments_router, prefix="/comments", tags=["comments"])
```

### Environment Settings（环境配置）

#### 配置管理
```python
# core/config.py
from pydantic import BaseSettings, validator
from typing import List, Union
import os

class Settings(BaseSettings):
    """应用配置"""
    
    # 项目信息
    PROJECT_NAME: str = "博客系统API"
    PROJECT_DESCRIPTION: str = "一个简单的博客发布系统API"
    VERSION: str = "1.0.0"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = True
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./blog.db"
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        """组装CORS源配置"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
```

#### 环境变量文件示例
```bash
# .env.example
# 项目配置
PROJECT_NAME="博客系统API"
PROJECT_DESCRIPTION="一个简单的博客发布系统API"
VERSION="1.0.0"

# 服务器配置
HOST="0.0.0.0"
PORT=8000
DEBUG=true

# 数据库配置
DATABASE_URL="sqlite:///./blog.db"

# CORS配置
BACKEND_CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]
```

### Startup/Shutdown Events（启动关闭事件）

#### 数据库初始化
```python
# db/init_db.py
from sqlalchemy.orm import Session
from models.category import CategoryDB
from models.article import ArticleDB
from models.comment import CommentDB

def init_database(db: Session):
    """初始化数据库"""
    # 创建表
    from db.base import Base
    from db.session import engine
    Base.metadata.create_all(bind=engine)
    
    # 检查是否需要初始化数据
    category_count = db.query(CategoryDB).count()
    if category_count == 0:
        # 创建示例分类
        categories = [
            CategoryDB(name="技术", description="技术相关文章和教程"),
            CategoryDB(name="生活", description="日常生活记录和感悟"),
            CategoryDB(name="学习", description="学习笔记和经验分享"),
            CategoryDB(name="随笔", description="随意记录的想法和观点")
        ]
        
        for category in categories:
            db.add(category)
        
        db.commit()
        print("示例分类已创建")
```

#### 健康检查端点
```python
# api/health.py
from fastapi import APIRouter
from sqlalchemy.orm import Session
from db.session import get_db

router = APIRouter()

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    """健康检查"""
    try:
        # 检查数据库连接
        db.execute("SELECT 1")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}
```

### 项目结构组织

#### 推荐项目结构
```
src/
├── api/
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── articles.py          # 文章API
│   │   ├── categories.py        # 分类API
│   │   ├── comments.py          # 评论API
│   │   ├── deps.py              # 依赖注入
│   │   └── router.py            # 路由配置
│   └── health.py                # 健康检查
├── core/
│   ├── __init__.py
│   └── config.py                # 配置管理
├── db/
│   ├── __init__.py
│   ├── base.py                  # 基础模型
│   ├── init_db.py               # 数据库初始化
│   └── session.py               # 数据库会话
├── models/
│   ├── __init__.py
│   ├── article.py               # 文章模型
│   ├── category.py              # 分类模型
│   └── comment.py               # 评论模型
├── schemas/
│   ├── __init__.py
│   ├── article.py               # 文章验证模型
│   ├── category.py              # 分类验证模型
│   └── comment.py               # 评论验证模型
├── repositories/
│   ├── __init__.py
│   ├── base.py                  # 基础仓储
│   ├── article_repository.py    # 文章仓储
│   ├── category_repository.py   # 分类仓储
│   └── comment_repository.py    # 评论仓储
├── services/
│   ├── __init__.py
│   ├── article_service.py       # 文章服务
│   ├── category_service.py      # 分类服务
│   └── comment_service.py       # 评论服务
├── tests/
│   ├── __init__.py
│   ├── test_articles.py         # 文章测试
│   ├── test_categories.py       # 分类测试
│   └── test_comments.py         # 评论测试
├── requirements.txt             # 依赖列表
├── .env.example                 # 环境变量示例
└── main.py                      # 应用入口
```

#### 依赖安装
```bash
# requirements.txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
email-validator==2.1.0
python-dotenv==1.0.0
```

#### 启动脚本
```bash
#!/bin/bash
# start.sh

echo "启动博客系统API..."

# 检查Python版本
python_version=$(python --version 2>&1 | awk '{print $2}')
echo "Python版本: $python_version"

# 安装依赖
pip install -r requirements.txt

# 启动应用
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

## 5. Testing Specifications（测试规范）

### Unit Tests（单元测试）

#### 服务层单元测试
```python
# tests/test_article_service.py
import unittest
from unittest.mock import Mock
from services.article_service import ArticleService
from models.article import ArticleDB, ArticleStatus
from schemas.article import ArticleCreate, ArticleUpdate

class TestArticleService(unittest.TestCase):
    """文章服务单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_repository = Mock()
        self.service = ArticleService(self.mock_repository)
    
    def test_create_article_success(self):
        """测试成功创建文章"""
        article_data = ArticleCreate(
            title="测试文章",
            content="测试内容",
            summary="测试摘要",
            author="测试作者"
        )
        
        mock_article = ArticleDB(
            id="test-id",
            title="测试文章",
            content="测试内容",
            summary="测试摘要",
            author="测试作者",
            status=ArticleStatus.DRAFT
        )
        self.mock_repository.create.return_value = mock_article
        
        result = self.service.create_article(article_data)
        
        self.assertEqual(result.title, "测试文章")
        self.assertEqual(result.status, ArticleStatus.DRAFT)
    
    def test_publish_article_success(self):
        """测试成功发布文章"""
        mock_article = ArticleDB(
            id="test-id",
            title="测试文章",
            status=ArticleStatus.DRAFT
        )
        self.mock_repository.get_by_id.return_value = mock_article
        self.mock_repository.update.return_value = mock_article
        
        result = self.service.publish_article("test-id")
        
        self.assertEqual(result.status, ArticleStatus.PUBLISHED)
```

### Integration Tests（集成测试）

#### API集成测试
```python
# tests/test_api_integration.py
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from db.base import Base
from db.session import get_db

# 测试数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_blog.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 覆盖数据库依赖
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

class TestArticleAPI(unittest.TestCase):
    """文章API集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = TestClient(app)
        Base.metadata.create_all(bind=engine)
    
    def tearDown(self):
        """测试后清理"""
        Base.metadata.drop_all(bind=engine)
    
    def test_create_and_get_article(self):
        """测试创建和获取文章"""
        article_data = {
            "title": "测试文章",
            "content": "这是测试内容",
            "summary": "测试摘要",
            "author": "测试作者"
        }
        
        response = self.client.post("/api/v1/articles/", json=article_data)
        self.assertEqual(response.status_code, 201)
        
        article = response.json()
        article_id = article["id"]
        
        response = self.client.get(f"/api/v1/articles/{article_id}")
        self.assertEqual(response.status_code, 200)
        
        retrieved_article = response.json()
        self.assertEqual(retrieved_article["title"], "测试文章")
    
    def test_list_articles(self):
        """测试文章列表"""
        for i in range(3):
            article_data = {
                "title": f"文章{i}",
                "content": f"内容{i}",
                "summary": f"摘要{i}",
                "author": "作者"
            }
            self.client.post("/api/v1/articles/", json=article_data)
        
        response = self.client.get("/api/v1/articles/")
        self.assertEqual(response.status_code, 200)
        
        data = response.json()
        self.assertEqual(len(data["items"]), 3)
```

### Test Fixtures（测试夹具）

#### 测试数据工厂
```python
# tests/fixtures.py
class ArticleFactory:
    """文章测试数据工厂"""
    
    @staticmethod
    def create_article_data(**overrides):
        """创建文章测试数据"""
        data = {
            "title": "测试文章",
            "content": "这是测试内容",
            "summary": "测试摘要",
            "author": "测试作者"
        }
        data.update(overrides)
        return data

class CategoryFactory:
    """分类测试数据工厂"""
    
    @staticmethod
    def create_category_data(**overrides):
        """创建分类测试数据"""
        data = {
            "name": "测试分类",
            "description": "测试分类描述"
        }
        data.update(overrides)
        return data
```

### Test Configuration（测试配置）

#### 测试配置文件
```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app
from db.base import Base
from db.session import get_db

# 测试数据库
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_blog.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client():
    """测试客户端"""
    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()
```

#### 测试运行配置
```bash
# 运行所有测试
python -m unittest discover tests/

# 运行特定测试文件
python -m unittest tests/test_article_service.py

# 运行特定测试类
python -m unittest tests.test_api_integration.TestArticleAPI

# 使用pytest运行测试（需要安装pytest）
pytest tests/
```

#### 测试覆盖率
```bash
# 安装覆盖率工具
pip install coverage

# 运行测试并生成覆盖率报告
coverage run -m unittest discover tests/
coverage report
coverage html  # 生成HTML报告
```

### 测试策略总结

#### 测试金字塔
1. **单元测试** (70%)
   - 服务层逻辑测试
   - 仓储层CRUD操作测试
   - 验证模型和验证器

2. **集成测试** (20%)
   - API端点测试
   - 数据库操作测试
   - 服务间交互测试

3. **端到端测试** (10%)
   - 完整业务流程测试
   - 错误处理测试
   - 性能测试

#### 测试最佳实践
- 使用内存数据库进行隔离测试
- 每个测试后清理数据
- 使用工厂模式创建测试数据
- 测试覆盖率目标：>80%
- 包含边界条件测试
- 包含错误场景测试

#### 持续集成
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```
