# Platform Specific Model (PSM) - 博客系统

## 1. Domain Models（领域模型）

### Entity Definitions（实体定义）

```python
from uuid import uuid4
from datetime import datetime
from typing import Optional

class Article:
    """文章领域实体"""
    def __init__(
        self,
        title: str,
        content: str,
        summary: Optional[str] = None,
        author: str = "Anonymous",
        category_id: Optional[str] = None,
        status: str = "draft"
    ):
        self.id = str(uuid4())
        self.title = title
        self.content = content
        self.summary = summary
        self.author = author
        self.category_id = category_id
        self.status = status  # draft/published
        self.view_count = 0
        self.created_at = datetime.now()
        self.updated_at = datetime.now()

class Category:
    """分类领域实体"""
    def __init__(self, name: str, description: Optional[str] = None):
        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.article_count = 0
        self.created_at = datetime.now()

class Comment:
    """评论领域实体"""
    def __init__(
        self,
        article_id: str,
        author_name: str,
        email: str,
        content: str,
        status: str = "pending"
    ):
        self.id = str(uuid4())
        self.article_id = article_id
        self.author_name = author_name
        self.email = email
        self.content = content
        self.status = status  # pending/published/blocked
        self.created_at = datetime.now()
```

### Database Models（数据库模型）

```python
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class ArticleDB(Base):
    __tablename__ = "articles"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    author: Mapped[str] = mapped_column(String(100), nullable=False, default="Anonymous")
    category_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("categories.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft")
    view_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    
    # 关系
    category: Mapped[Optional["CategoryDB"]] = relationship("CategoryDB", back_populates="articles")
    comments: Mapped[list["CommentDB"]] = relationship("CommentDB", back_populates="article")

class CategoryDB(Base):
    __tablename__ = "categories"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    article_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    
    # 关系
    articles: Mapped[list["ArticleDB"]] = relationship("ArticleDB", back_populates="category")

class CommentDB(Base):
    __tablename__ = "comments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    article_id: Mapped[str] = mapped_column(String(36), ForeignKey("articles.id"), nullable=False)
    author_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(200), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.now)
    
    # 关系
    article: Mapped["ArticleDB"] = relationship("ArticleDB", back_populates="comments")
```

### Pydantic Schemas（验证模型）

```python
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

# Article schemas
class ArticleBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    author: str = Field("Anonymous", min_length=1, max_length=100)
    category_id: Optional[str] = None
    status: str = Field("draft", pattern="^(draft|published)$")

class ArticleCreate(ArticleBase):
    pass

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    category_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")

class ArticleResponse(ArticleBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    view_count: int
    created_at: datetime
    updated_at: datetime

class ArticleQuery(BaseModel):
    category_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")
    search: Optional[str] = Field(None, min_length=1)
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)

# Category schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class CategoryResponse(CategoryBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    article_count: int
    created_at: datetime

# Comment schemas
class CommentBase(BaseModel):
    author_name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)

class CommentCreate(CommentBase):
    pass

class CommentUpdate(BaseModel):
    status: Optional[str] = Field(None, pattern="^(pending|published|blocked)$")

class CommentResponse(CommentBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    article_id: str
    status: str
    created_at: datetime

class CommentQuery(BaseModel):
    article_id: str
    status: Optional[str] = Field(None, pattern="^(pending|published|blocked)$")
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
```

### Enums and Constants（枚举和常量）

```python
from enum import Enum

class ArticleStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"

class CommentStatus(str, Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    BLOCKED = "blocked"
```
## 2. Service Layer（服务层）

### Business Services（业务服务）

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from .models import ArticleDB, CategoryDB, CommentDB
from .schemas import (
    ArticleCreate, ArticleUpdate, ArticleResponse, ArticleQuery,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CommentCreate, CommentUpdate, CommentResponse, CommentQuery
)

class ArticleService:
    """文章业务服务"""
    
    def __init__(self, repository: "ArticleRepository"):
        self.repository = repository
    
    def create_article(self, article_data: ArticleCreate) -> ArticleResponse:
        """创建文章"""
        article = Article(
            title=article_data.title,
            content=article_data.content,
            summary=article_data.summary,
            author=article_data.author,
            category_id=article_data.category_id,
            status=article_data.status
        )
        db_article = self.repository.save(article)
        return ArticleResponse.model_validate(db_article)
    
    def get_article(self, article_id: str) -> Optional[ArticleResponse]:
        """获取文章"""
        db_article = self.repository.get_by_id(article_id)
        if db_article:
            # 增加浏览量
            db_article.view_count += 1
            self.repository.save(db_article)
            return ArticleResponse.model_validate(db_article)
        return None
    
    def update_article(self, article_id: str, article_data: ArticleUpdate) -> Optional[ArticleResponse]:
        """更新文章"""
        db_article = self.repository.get_by_id(article_id)
        if not db_article:
            return None
        
        update_data = article_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_article, field, value)
        db_article.updated_at = datetime.now()
        
        self.repository.save(db_article)
        return ArticleResponse.model_validate(db_article)
    
    def delete_article(self, article_id: str) -> bool:
        """删除文章"""
        return self.repository.delete(article_id)
    
    def list_articles(self, query: ArticleQuery) -> List[ArticleResponse]:
        """查询文章列表"""
        db_articles = self.repository.query_articles(query)
        return [ArticleResponse.model_validate(article) for article in db_articles]
    
    def publish_article(self, article_id: str) -> Optional[ArticleResponse]:
        """发布文章"""
        db_article = self.repository.get_by_id(article_id)
        if db_article and db_article.status == "draft":
            db_article.status = "published"
            db_article.updated_at = datetime.now()
            self.repository.save(db_article)
            return ArticleResponse.model_validate(db_article)
        return None

class CategoryService:
    """分类业务服务"""
    
    def __init__(self, repository: "CategoryRepository"):
        self.repository = repository
    
    def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """创建分类"""
        category = Category(
            name=category_data.name,
            description=category_data.description
        )
        db_category = self.repository.save(category)
        return CategoryResponse.model_validate(db_category)
    
    def get_category(self, category_id: str) -> Optional[CategoryResponse]:
        """获取分类"""
        db_category = self.repository.get_by_id(category_id)
        if db_category:
            return CategoryResponse.model_validate(db_category)
        return None
    
    def update_category(self, category_id: str, category_data: CategoryUpdate) -> Optional[CategoryResponse]:
        """更新分类"""
        db_category = self.repository.get_by_id(category_id)
        if not db_category:
            return None
        
        update_data = category_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_category, field, value)
        
        self.repository.save(db_category)
        return CategoryResponse.model_validate(db_category)
    
    def delete_category(self, category_id: str) -> bool:
        """删除分类"""
        return self.repository.delete(category_id)
    
    def list_categories(self) -> List[CategoryResponse]:
        """获取所有分类"""
        db_categories = self.repository.get_all()
        return [CategoryResponse.model_validate(category) for category in db_categories]

class CommentService:
    """评论业务服务"""
    
    def __init__(self, repository: "CommentRepository"):
        self.repository = repository
    
    def create_comment(self, comment_data: CommentCreate) -> CommentResponse:
        """创建评论"""
        comment = Comment(
            article_id=comment_data.article_id,
            author_name=comment_data.author_name,
            email=comment_data.email,
            content=comment_data.content
        )
        db_comment = self.repository.save(comment)
        return CommentResponse.model_validate(db_comment)
    
    def get_comment(self, comment_id: str) -> Optional[CommentResponse]:
        """获取评论"""
        db_comment = self.repository.get_by_id(comment_id)
        if db_comment:
            return CommentResponse.model_validate(db_comment)
        return None
    
    def update_comment(self, comment_id: str, comment_data: CommentUpdate) -> Optional[CommentResponse]:
        """更新评论"""
        db_comment = self.repository.get_by_id(comment_id)
        if not db_comment:
            return None
        
        update_data = comment_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_comment, field, value)
        
        self.repository.save(db_comment)
        return CommentResponse.model_validate(db_comment)
    
    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
        return self.repository.delete(comment_id)
    
    def list_comments(self, query: CommentQuery) -> List[CommentResponse]:
        """查询评论列表"""
        db_comments = self.repository.query_comments(query)
        return [CommentResponse.model_validate(comment) for comment in db_comments]
    
    def approve_comment(self, comment_id: str) -> Optional[CommentResponse]:
        """审核通过评论"""
        db_comment = self.repository.get_by_id(comment_id)
        if db_comment and db_comment.status == "pending":
            db_comment.status = "published"
            self.repository.save(db_comment)
            return CommentResponse.model_validate(db_comment)
        return None
```

### Repository Pattern（仓储模式）

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from .models import ArticleDB, CategoryDB, CommentDB
from .schemas import ArticleQuery, CommentQuery

class ArticleRepository:
    """文章仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, article: Article) -> ArticleDB:
        """保存文章"""
        db_article = ArticleDB(
            title=article.title,
            content=article.content,
            summary=article.summary,
            author=article.author,
            category_id=article.category_id,
            status=article.status,
            view_count=article.view_count,
            created_at=article.created_at,
            updated_at=article.updated_at
        )
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)
        return db_article
    
    def save(self, db_article: ArticleDB) -> ArticleDB:
        """保存或更新文章"""
        self.db.add(db_article)
        self.db.commit()
        self.db.refresh(db_article)
        return db_article
    
    def get_by_id(self, article_id: str) -> Optional[ArticleDB]:
        """根据ID获取文章"""
        return self.db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    
    def delete(self, article_id: str) -> bool:
        """删除文章"""
        db_article = self.get_by_id(article_id)
        if db_article:
            self.db.delete(db_article)
            self.db.commit()
            return True
        return False
    
    def query_articles(self, query: ArticleQuery) -> List[ArticleDB]:
        """查询文章"""
        q = self.db.query(ArticleDB)
        
        if query.category_id:
            q = q.filter(ArticleDB.category_id == query.category_id)
        
        if query.status:
            q = q.filter(ArticleDB.status == query.status)
        
        if query.search:
            search_term = f"%{query.search}%"
            q = q.filter(
                or_(
                    ArticleDB.title.ilike(search_term),
                    ArticleDB.content.ilike(search_term)
                )
            )
        
        q = q.offset(query.skip).limit(query.limit)
        return q.all()

class CategoryRepository:
    """分类仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, category: Category) -> CategoryDB:
        """保存分类"""
        db_category = CategoryDB(
            name=category.name,
            description=category.description,
            article_count=category.article_count,
            created_at=category.created_at
        )
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def save(self, db_category: CategoryDB) -> CategoryDB:
        """保存或更新分类"""
        self.db.add(db_category)
        self.db.commit()
        self.db.refresh(db_category)
        return db_category
    
    def get_by_id(self, category_id: str) -> Optional[CategoryDB]:
        """根据ID获取分类"""
        return self.db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    
    def get_all(self) -> List[CategoryDB]:
        """获取所有分类"""
        return self.db.query(CategoryDB).all()
    
    def delete(self, category_id: str) -> bool:
        """删除分类"""
        db_category = self.get_by_id(category_id)
        if db_category:
            self.db.delete(db_category)
            self.db.commit()
            return True
        return False

class CommentRepository:
    """评论仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def save(self, comment: Comment) -> CommentDB:
        """保存评论"""
        db_comment = CommentDB(
            article_id=comment.article_id,
            author_name=comment.author_name,
            email=comment.email,
            content=comment.content,
            status=comment.status,
            created_at=comment.created_at
        )
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def save(self, db_comment: CommentDB) -> CommentDB:
        """保存或更新评论"""
        self.db.add(db_comment)
        self.db.commit()
        self.db.refresh(db_comment)
        return db_comment
    
    def get_by_id(self, comment_id: str) -> Optional[CommentDB]:
        """根据ID获取评论"""
        return self.db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    
    def delete(self, comment_id: str) -> bool:
        """删除评论"""
        db_comment = self.get_by_id(comment_id)
        if db_comment:
            self.db.delete(db_comment)
            self.db.commit()
            return True
        return False
    
    def query_comments(self, query: CommentQuery) -> List[CommentDB]:
        """查询评论"""
        q = self.db.query(CommentDB).filter(CommentDB.article_id == query.article_id)
        
        if query.status:
            q = q.filter(CommentDB.status == query.status)
        
        q = q.offset(query.skip).limit(query.limit)
        return q.all()
```

### Transaction Management（事务管理）

```python
from contextlib import contextmanager
from sqlalchemy.orm import Session

@contextmanager
def get_db_session():
    """获取数据库会话上下文管理器"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def transactional(func):
    """事务装饰器"""
    def wrapper(*args, **kwargs):
        with get_db_session() as db:
            return func(db, *args, **kwargs)
    return wrapper
```

### Business Rules（业务规则）

```python
class BusinessRules:
    """业务规则验证"""
    
    @staticmethod
    def validate_article_publish(article: ArticleDB) -> None:
        """验证文章发布规则"""
        if not article.title.strip():
            raise ValueError("文章标题不能为空")
        if not article.content.strip():
            raise ValueError("文章内容不能为空")
        if len(article.title) > 200:
            raise ValueError("文章标题不能超过200字符")
    
    @staticmethod
    def validate_category_name(name: str) -> None:
        """验证分类名称规则"""
        if not name.strip():
            raise ValueError("分类名称不能为空")
        if len(name) > 100:
            raise ValueError("分类名称不能超过100字符")
    
    @staticmethod
    def validate_comment_publish(comment: CommentDB) -> None:
        """验证评论发布规则"""
        if not comment.content.strip():
            raise ValueError("评论内容不能为空")
        if len(comment.author_name) > 100:
            raise ValueError("评论者姓名不能超过100字符")
```

## 3. REST API Design（API设计）

### API Endpoints（端点定义）

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from .database import get_db
from .services import ArticleService, CategoryService, CommentService
from .repositories import ArticleRepository, CategoryRepository, CommentRepository
from .schemas import (
    ArticleCreate, ArticleUpdate, ArticleResponse, ArticleQuery,
    CategoryCreate, CategoryUpdate, CategoryResponse,
    CommentCreate, CommentUpdate, CommentResponse, CommentQuery
)

# 依赖注入函数
def get_article_service(db: Session = Depends(get_db)) -> ArticleService:
    repository = ArticleRepository(db)
    return ArticleService(repository)

def get_category_service(db: Session = Depends(get_db)) -> CategoryService:
    repository = CategoryRepository(db)
    return CategoryService(repository)

def get_comment_service(db: Session = Depends(get_db)) -> CommentService:
    repository = CommentRepository(db)
    return CommentService(repository)

# 文章路由
article_router = APIRouter(prefix="/api/articles", tags=["articles"])

@article_router.post("/", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
def create_article(
    article_data: ArticleCreate,
    service: ArticleService = Depends(get_article_service)
):
    """创建文章"""
    return service.create_article(article_data)

@article_router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """获取文章"""
    article = service.get_article(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article

@article_router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: str,
    article_data: ArticleUpdate,
    service: ArticleService = Depends(get_article_service)
):
    """更新文章"""
    article = service.update_article(article_id, article_data)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    return article

@article_router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """删除文章"""
    if not service.delete_article(article_id):
        raise HTTPException(status_code=404, detail="文章不存在")

@article_router.get("/", response_model=List[ArticleResponse])
def list_articles(
    query: ArticleQuery = Depends(),
    service: ArticleService = Depends(get_article_service)
):
    """查询文章列表"""
    return service.list_articles(query)

@article_router.post("/{article_id}/publish", response_model=ArticleResponse)
def publish_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """发布文章"""
    article = service.publish_article(article_id)
    if not article:
        raise HTTPException(status_code=400, detail="无法发布文章")
    return article

# 分类路由
category_router = APIRouter(prefix="/api/categories", tags=["categories"])

@category_router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    service: CategoryService = Depends(get_category_service)
):
    """创建分类"""
    return service.create_category(category_data)

@category_router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service)
):
    """获取分类"""
    category = service.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category

@category_router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service)
):
    """更新分类"""
    category = service.update_category(category_id, category_data)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return category

@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service)
):
    """删除分类"""
    if not service.delete_category(category_id):
        raise HTTPException(status_code=404, detail="分类不存在")

@category_router.get("/", response_model=List[CategoryResponse])
def list_categories(
    service: CategoryService = Depends(get_category_service)
):
    """获取所有分类"""
    return service.list_categories()

# 评论路由
comment_router = APIRouter(prefix="/api/comments", tags=["comments"])

@comment_router.post("/", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment(
    comment_data: CommentCreate,
    service: CommentService = Depends(get_comment_service)
):
    """创建评论"""
    return service.create_comment(comment_data)

@comment_router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """获取评论"""
    comment = service.get_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment

@comment_router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(
    comment_id: str,
    comment_data: CommentUpdate,
    service: CommentService = Depends(get_comment_service)
):
    """更新评论"""
    comment = service.update_comment(comment_id, comment_data)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return comment

@comment_router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """删除评论"""
    if not service.delete_comment(comment_id):
        raise HTTPException(status_code=404, detail="评论不存在")

@comment_router.get("/", response_model=List[CommentResponse])
def list_comments(
    query: CommentQuery = Depends(),
    service: CommentService = Depends(get_comment_service)
):
    """查询评论列表"""
    return service.list_comments(query)

@comment_router.post("/{comment_id}/approve", response_model=CommentResponse)
def approve_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """审核通过评论"""
    comment = service.approve_comment(comment_id)
    if not comment:
        raise HTTPException(status_code=400, detail="无法审核评论")
    return comment
```

### Request/Response Models（请求响应模型）

已在Domain Models章节定义。

### API Routing（路由配置）

```python
from fastapi import FastAPI
from .routers import article_router, category_router, comment_router

def create_application() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title="博客系统 API",
        description="简单的博客发布系统，支持文章发布、分类和评论功能",
        version="1.0.0"
    )
    
    # 注册路由
    app.include_router(article_router)
    app.include_router(category_router)
    app.include_router(comment_router)
    
    return app
```

### Middleware（中间件）

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

def add_middleware(app: FastAPI):
    """添加中间件"""
    # CORS中间件
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 在生产环境中应该设置具体的域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # 可信主机中间件
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=["*"]  # 在生产环境中应该设置具体的主机
    )
```

### Error Handling（错误处理）

```python
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """处理数据库完整性错误"""
    return JSONResponse(
        status_code=400,
        content={"detail": "数据完整性错误，请检查输入数据"}
    )

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    """处理业务逻辑错误"""
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(Exception)
async def general_error_handler(request: Request, exc: Exception):
    """处理一般错误"""
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )
```

## 4. Application Configuration（应用配置）

### Main Application（主应用）

```python
from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_tables, engine
from .middleware import add_middleware
from .routers import create_application

@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时
    create_tables()
    print("数据库表创建完成")
    
    yield
    
    # 关闭时
    print("应用关闭")

def create_app() -> FastAPI:
    """创建FastAPI应用实例"""
    app = FastAPI(
        title="博客系统 API",
        description="简单的博客发布系统，支持文章发布、分类和评论功能",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # 添加中间件
    add_middleware(app)
    
    # 注册路由
    from .api.routers import article_router, category_router, comment_router
    app.include_router(article_router)
    app.include_router(category_router)
    app.include_router(comment_router)
    
    # 添加异常处理器
    from .api.error_handlers import add_error_handlers
    add_error_handlers(app)
    
    return app

# 创建应用实例
app = create_app()
```

### Database Configuration（数据库配置）

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

# SQLite数据库配置
DATABASE_URL = "sqlite:///./blog.db"

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite多线程支持
    echo=True  # 开发环境开启SQL日志
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db() -> Generator[Session, None, None]:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """创建所有数据库表"""
    from .models import Base
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """删除所有数据库表"""
    from .models import Base
    Base.metadata.drop_all(bind=engine)
```

### Dependency Injection（依赖注入）

```python
from typing import Callable, Type
from functools import lru_cache

@lru_cache()
def get_article_service():
    """获取文章服务实例"""
    from .services import ArticleService
    from .repositories import ArticleRepository
    from .database import get_db
    
    def _get_service(db: Session = Depends(get_db)) -> ArticleService:
        repository = ArticleRepository(db)
        return ArticleService(repository)
    
    return _get_service

@lru_cache()
def get_category_service():
    """获取分类服务实例"""
    from .services import CategoryService
    from .repositories import CategoryRepository
    from .database import get_db
    
    def _get_service(db: Session = Depends(get_db)) -> CategoryService:
        repository = CategoryRepository(db)
        return CategoryService(repository)
    
    return _get_service

@lru_cache()
def get_comment_service():
    """获取评论服务实例"""
    from .services import CommentService
    from .repositories import CommentRepository
    from .database import get_db
    
    def _get_service(db: Session = Depends(get_db)) -> CommentService:
        repository = CommentRepository(db)
        return CommentService(repository)
    
    return _get_service
```

### Environment Settings（环境配置）

```python
from pydantic import BaseSettings, Field
from typing import Optional

class Settings(BaseSettings):
    """应用配置"""
    
    # 数据库配置
    database_url: str = Field(default="sqlite:///./blog.db", env="DATABASE_URL")
    
    # 应用配置
    app_name: str = Field(default="博客系统 API", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    
    # API配置
    api_prefix: str = Field(default="/api", env="API_PREFIX")
    api_version: str = Field(default="v1", env="API_VERSION")
    
    # CORS配置
    cors_origins: list[str] = Field(default=["*"], env="CORS_ORIGINS")
    
    # 分页配置
    default_page_size: int = Field(default=10, env="DEFAULT_PAGE_SIZE")
    max_page_size: int = Field(default=100, env="MAX_PAGE_SIZE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """获取配置实例"""
    return Settings()
```

### Startup/Shutdown Events（启动关闭事件）

```python
from fastapi import FastAPI
from .database import create_tables, engine
from .settings import get_settings

def startup_event():
    """应用启动事件"""
    settings = get_settings()
    print(f"启动 {settings.app_name} v{settings.app_version}")
    
    # 创建数据库表
    create_tables()
    print("数据库表初始化完成")
    
    # 其他启动逻辑
    if settings.debug:
        print("调试模式已启用")

def shutdown_event():
    """应用关闭事件"""
    print("应用关闭")
    
    # 清理资源
    engine.dispose()
    print("数据库连接已关闭")

def add_lifespan_events(app: FastAPI):
    """添加生命周期事件"""
    @app.on_event("startup")
    async def startup():
        startup_event()
    
    @app.on_event("shutdown")
    async def shutdown():
        shutdown_event()
```

### Logging Configuration（日志配置）

```python
import logging
from .settings import get_settings

def setup_logging():
    """配置日志"""
    settings = get_settings()
    
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("blog.log") if not settings.debug else logging.NullHandler()
        ]
    )
    
    # 设置第三方库日志级别
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)
```

### Configuration Files（配置文件）

创建 `config.py` 文件：

```python
# config.py
from .settings import Settings, get_settings

# 全局配置实例
settings = get_settings()

# 数据库配置
DATABASE_URL = settings.database_url

# API配置
API_PREFIX = settings.api_prefix
API_VERSION = settings.api_version

# 分页配置
DEFAULT_PAGE_SIZE = settings.default_page_size
MAX_PAGE_SIZE = settings.max_page_size
```

创建 `.env` 文件模板：

```bash
# .env
DATABASE_URL=sqlite:///./blog.db
APP_NAME=博客系统 API
APP_VERSION=1.0.0
DEBUG=true
API_PREFIX=/api
API_VERSION=v1
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]
DEFAULT_PAGE_SIZE=10
MAX_PAGE_SIZE=100
```

## 5. Testing Specifications（测试规范）

### Unit Tests（单元测试）

```python
import unittest
from unittest.mock import Mock, patch
from datetime import datetime
from ..models import Article, Category, Comment
from ..services import ArticleService, CategoryService, CommentService
from ..schemas import ArticleCreate, CategoryCreate, CommentCreate

class TestArticleService(unittest.TestCase):
    """文章服务单元测试"""
    
    def setUp(self):
        """测试前准备"""
        self.mock_repository = Mock()
        self.service = ArticleService(self.mock_repository)
    
    def test_create_article_success(self):
        """测试创建文章成功"""
        # 准备测试数据
        article_data = ArticleCreate(
            title="测试文章",
            content="测试内容",
            author="测试作者"
        )
        
        # Mock仓储行为
        mock_db_article = Mock()
        mock_db_article.id = "test-id"
        mock_db_article.title = article_data.title
        self.mock_repository.save.return_value = mock_db_article
        
        # 执行测试
        result = self.service.create_article(article_data)
        
        # 验证结果
        self.assertEqual(result.id, "test-id")
        self.assertEqual(result.title, "测试文章")
        self.mock_repository.save.assert_called_once()
    
    def test_get_article_success(self):
        """测试获取文章成功"""
        # Mock仓储行为
        mock_db_article = Mock()
        mock_db_article.id = "test-id"
        mock_db_article.view_count = 5
        self.mock_repository.get_by_id.return_value = mock_db_article
        
        # 执行测试
        result = self.service.get_article("test-id")
        
        # 验证结果
        self.assertIsNotNone(result)
        self.assertEqual(result.id, "test-id")
        # 验证浏览量增加
        self.assertEqual(mock_db_article.view_count, 6)
    
    def test_get_article_not_found(self):
        """测试获取不存在的文章"""
        self.mock_repository.get_by_id.return_value = None
        
        result = self.service.get_article("non-existent-id")
        
        self.assertIsNone(result)

class TestCategoryService(unittest.TestCase):
    """分类服务单元测试"""
    
    def setUp(self):
        self.mock_repository = Mock()
        self.service = CategoryService(self.mock_repository)
    
    def test_create_category_success(self):
        """测试创建分类成功"""
        category_data = CategoryCreate(
            name="测试分类",
            description="测试描述"
        )
        
        mock_db_category = Mock()
        mock_db_category.id = "test-id"
        mock_db_category.name = category_data.name
        self.mock_repository.save.return_value = mock_db_category
        
        result = self.service.create_category(category_data)
        
        self.assertEqual(result.id, "test-id")
        self.assertEqual(result.name, "测试分类")
    
    def test_list_categories(self):
        """测试获取分类列表"""
        mock_categories = [Mock(), Mock()]
        self.mock_repository.get_all.return_value = mock_categories
        
        result = self.service.list_categories()
        
        self.assertEqual(len(result), 2)
        self.mock_repository.get_all.assert_called_once()

class TestCommentService(unittest.TestCase):
    """评论服务单元测试"""
    
    def setUp(self):
        self.mock_repository = Mock()
        self.service = CommentService(self.mock_repository)
    
    def test_create_comment_success(self):
        """测试创建评论成功"""
        comment_data = CommentCreate(
            article_id="article-id",
            author_name="评论者",
            email="test@example.com",
            content="测试评论"
        )
        
        mock_db_comment = Mock()
        mock_db_comment.id = "test-id"
        self.mock_repository.save.return_value = mock_db_comment
        
        result = self.service.create_comment(comment_data)
        
        self.assertEqual(result.id, "test-id")
    
    def test_approve_comment_success(self):
        """测试审核评论成功"""
        mock_db_comment = Mock()
        mock_db_comment.status = "pending"
        self.mock_repository.get_by_id.return_value = mock_db_comment
        
        result = self.service.approve_comment("comment-id")
        
        self.assertEqual(mock_db_comment.status, "published")
        self.assertIsNotNone(result)
    
    def test_approve_comment_invalid_status(self):
        """测试审核已发布的评论"""
        mock_db_comment = Mock()
        mock_db_comment.status = "published"
        self.mock_repository.get_by_id.return_value = mock_db_comment
        
        result = self.service.approve_comment("comment-id")
        
        self.assertIsNone(result)

class TestBusinessRules(unittest.TestCase):
    """业务规则测试"""
    
    def test_validate_article_publish_valid(self):
        """测试有效的文章发布"""
        from ..services import BusinessRules
        
        mock_article = Mock()
        mock_article.title = "有效标题"
        mock_article.content = "有效内容"
        
        # 不应该抛出异常
        BusinessRules.validate_article_publish(mock_article)
    
    def test_validate_article_publish_empty_title(self):
        """测试空标题的文章发布"""
        from ..services import BusinessRules
        
        mock_article = Mock()
        mock_article.title = ""
        mock_article.content = "有效内容"
        
        with self.assertRaises(ValueError) as cm:
            BusinessRules.validate_article_publish(mock_article)
        
        self.assertIn("标题不能为空", str(cm.exception))
    
    def test_validate_category_name_valid(self):
        """测试有效的分类名称"""
        from ..services import BusinessRules
        
        # 不应该抛出异常
        BusinessRules.validate_category_name("有效分类名")
    
    def test_validate_category_name_empty(self):
        """测试空分类名称"""
        from ..services import BusinessRules
        
        with self.assertRaises(ValueError) as cm:
            BusinessRules.validate_category_name("")
        
        self.assertIn("分类名称不能为空", str(cm.exception))
```

### Integration Tests（集成测试）

```python
import unittest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..main import app
from ..database import Base, get_db
from ..models import ArticleDB, CategoryDB, CommentDB

class TestBlogAPI(unittest.TestCase):
    """博客API集成测试"""
    
    def setUp(self):
        """测试前准备"""
        # 创建测试数据库
        self.engine = create_engine("sqlite:///./test_blog.db", connect_args={"check_same_thread": False})
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # 创建表
        Base.metadata.create_all(bind=self.engine)
        
        # 依赖注入测试数据库
        def override_get_db():
            db = TestingSessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        app.dependency_overrides[get_db] = override_get_db
        self.client = TestClient(app)
    
    def tearDown(self):
        """测试后清理"""
        Base.metadata.drop_all(bind=self.engine)
        self.engine.dispose()
    
    def test_create_and_get_article(self):
        """测试创建和获取文章"""
        # 创建文章
        article_data = {
            "title": "测试文章",
            "content": "测试内容",
            "author": "测试作者",
            "status": "draft"
        }
        
        response = self.client.post("/api/articles", json=article_data)
        self.assertEqual(response.status_code, 201)
        created_article = response.json()
        article_id = created_article["id"]
        
        # 获取文章
        response = self.client.get(f"/api/articles/{article_id}")
        self.assertEqual(response.status_code, 200)
        retrieved_article = response.json()
        
        self.assertEqual(retrieved_article["title"], "测试文章")
        self.assertEqual(retrieved_article["view_count"], 1)  # 浏览量应该增加
    
    def test_create_category(self):
        """测试创建分类"""
        category_data = {
            "name": "测试分类",
            "description": "测试描述"
        }
        
        response = self.client.post("/api/categories", json=category_data)
        self.assertEqual(response.status_code, 201)
        created_category = response.json()
        
        self.assertEqual(created_category["name"], "测试分类")
        self.assertEqual(created_category["description"], "测试描述")
    
    def test_create_comment(self):
        """测试创建评论"""
        # 先创建文章
        article_data = {
            "title": "测试文章",
            "content": "测试内容",
            "author": "测试作者"
        }
        article_response = self.client.post("/api/articles", json=article_data)
        article_id = article_response.json()["id"]
        
        # 创建评论
        comment_data = {
            "article_id": article_id,
            "author_name": "评论者",
            "email": "test@example.com",
            "content": "测试评论"
        }
        
        response = self.client.post("/api/comments", json=comment_data)
        self.assertEqual(response.status_code, 201)
        created_comment = response.json()
        
        self.assertEqual(created_comment["content"], "测试评论")
        self.assertEqual(created_comment["status"], "pending")
    
    def test_publish_article(self):
        """测试发布文章"""
        # 创建草稿文章
        article_data = {
            "title": "草稿文章",
            "content": "草稿内容",
            "status": "draft"
        }
        article_response = self.client.post("/api/articles", json=article_data)
        article_id = article_response.json()["id"]
        
        # 发布文章
        response = self.client.post(f"/api/articles/{article_id}/publish")
        self.assertEqual(response.status_code, 200)
        published_article = response.json()
        
        self.assertEqual(published_article["status"], "published")
    
    def test_list_articles_with_pagination(self):
        """测试文章列表分页"""
        # 创建多个文章
        for i in range(5):
            article_data = {
                "title": f"文章{i}",
                "content": f"内容{i}",
                "author": "作者"
            }
            self.client.post("/api/articles", json=article_data)
        
        # 获取第一页
        response = self.client.get("/api/articles?skip=0&limit=3")
        self.assertEqual(response.status_code, 200)
        articles = response.json()
        
        self.assertEqual(len(articles), 3)
    
    def test_search_articles(self):
        """测试搜索文章"""
        # 创建文章
        article_data = {
            "title": "Python编程",
            "content": "学习Python编程",
            "author": "专家"
        }
        self.client.post("/api/articles", json=article_data)
        
        # 搜索
        response = self.client.get("/api/articles?search=Python")
        self.assertEqual(response.status_code, 200)
        articles = response.json()
        
        self.assertGreater(len(articles), 0)
        self.assertIn("Python", articles[0]["title"])
    
    def test_approve_comment(self):
        """测试审核评论"""
        # 创建文章和评论
        article_data = {"title": "文章", "content": "内容", "author": "作者"}
        article_response = self.client.post("/api/articles", json=article_data)
        article_id = article_response.json()["id"]
        
        comment_data = {
            "article_id": article_id,
            "author_name": "评论者",
            "email": "test@example.com",
            "content": "评论内容"
        }
        comment_response = self.client.post("/api/comments", json=comment_data)
        comment_id = comment_response.json()["id"]
        
        # 审核评论
        response = self.client.post(f"/api/comments/{comment_id}/approve")
        self.assertEqual(response.status_code, 200)
        approved_comment = response.json()
        
        self.assertEqual(approved_comment["status"], "published")
```

### Test Fixtures（测试夹具）

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..models import ArticleDB, CategoryDB, CommentDB

@pytest.fixture(scope="session")
def test_engine():
    """测试数据库引擎"""
    engine = create_engine("sqlite:///./test_blog.db", connect_args={"check_same_thread": False})
    yield engine
    engine.dispose()

@pytest.fixture(scope="session")
def tables(test_engine):
    """创建测试表"""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def db_session(test_engine, tables):
    """测试数据库会话"""
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def sample_category(db_session):
    """示例分类"""
    category = CategoryDB(
        name="技术",
        description="技术文章分类"
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture
def sample_article(db_session, sample_category):
    """示例文章"""
    article = ArticleDB(
        title="测试文章",
        content="测试内容",
        author="测试作者",
        category_id=sample_category.id,
        status="published"
    )
    db_session.add(article)
    db_session.commit()
    db_session.refresh(article)
    return article

@pytest.fixture
def sample_comment(db_session, sample_article):
    """示例评论"""
    comment = CommentDB(
        article_id=sample_article.id,
        author_name="评论者",
        email="test@example.com",
        content="测试评论",
        status="pending"
    )
    db_session.add(comment)
    db_session.commit()
    db_session.refresh(comment)
    return comment
```

### Test Configuration（测试配置）

```python
# tests/__init__.py
# 测试包初始化

# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..database import get_db
from .fixtures import db_session

@pytest.fixture
def client(db_session):
    """测试客户端"""
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    return TestClient(app)

# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
markers =
    unit: 单元测试
    integration: 集成测试
    slow: 慢速测试

# requirements-test.txt
pytest==7.4.0
pytest-cov==4.1.0
httpx==0.24.1
```

### Running Tests（运行测试）

```bash
# 运行所有测试
python -m pytest

# 运行单元测试
python -m pytest -m unit

# 运行集成测试
python -m pytest -m integration

# 生成覆盖率报告
python -m pytest --cov=src --cov-report=html

# 运行特定测试文件
python -m unittest tests.test_services.TestArticleService

# 使用测试发现
python -m unittest discover tests/
```

### Test Best Practices（测试最佳实践）

```python
# tests/test_best_practices.py
import unittest

class TestBestPractices(unittest.TestCase):
    """测试最佳实践示例"""
    
    def test_should_use_descriptive_test_names(self):
        """测试方法名应该描述测试的目的"""
        # 好的例子：test_should_return_empty_list_when_no_articles
        # 坏的例子：test_empty_list
        
        self.assertTrue(True)  # 占位符
    
    def test_should_test_one_thing_per_test(self):
        """每个测试应该只测试一件事"""
        # 不要在一个测试中测试创建和删除
        # 应该拆分为 test_create_article 和 test_delete_article
        
        self.assertTrue(True)
    
    def test_should_use_assertion_messages(self):
        """断言应该有描述性消息"""
        result = 2 + 2
        self.assertEqual(result, 4, "2 + 2 应该等于 4")
    
    def test_should_mock_external_dependencies(self):
        """应该模拟外部依赖"""
        # 使用 Mock 来隔离被测试的代码
        
        self.assertTrue(True)
    
    def test_should_test_edge_cases(self):
        """应该测试边界情况"""
        # 测试空值、无效输入、极限值等
        
        self.assertTrue(True)
```

### Continuous Integration（持续集成）

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        python -m pytest --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```
