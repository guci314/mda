# Platform Specific Model (PSM) - 博客系统

## 1. Domain Models（领域模型）

### Entity Definitions（实体定义）

```python
from datetime import datetime
from typing import Optional
from uuid import uuid4

class Article:
    """文章领域实体"""
    def __init__(self, title: str, content: str, author: str, 
                 summary: Optional[str] = None, category_id: Optional[str] = None):
        self.id = str(uuid4())
        self.title = title
        self.content = content
        self.summary = summary or content[:200]  # 默认取前200字符作为摘要
        self.author = author
        self.category_id = category_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.status = "draft"  # draft/published
        self.view_count = 0

class Category:
    """分类领域实体"""
    def __init__(self, name: str, description: str = ""):
        self.id = str(uuid4())
        self.name = name
        self.description = description
        self.article_count = 0

class Comment:
    """评论领域实体"""
    def __init__(self, article_id: str, author_name: str, 
                 email: str, content: str):
        self.id = str(uuid4())
        self.article_id = article_id
        self.author_name = author_name
        self.email = email
        self.content = content
        self.created_at = datetime.now()
        self.status = "pending"  # pending/approved/rejected
```

### Database Models（数据库模型）

```python
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class ArticleDB(Base):
    __tablename__ = "articles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    author = Column(String(50), nullable=False)
    category_id = Column(String(36), ForeignKey("categories.id"))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    status = Column(String(20), default="draft")  # draft/published
    view_count = Column(Integer, default=0)
    
    # 关系
    category = relationship("CategoryDB", back_populates="articles")
    comments = relationship("CommentDB", back_populates="article", cascade="all, delete-orphan")

class CategoryDB(Base):
    __tablename__ = "categories"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(500))
    article_count = Column(Integer, default=0)
    
    # 关系
    articles = relationship("ArticleDB", back_populates="category")

class CommentDB(Base):
    __tablename__ = "comments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    article_id = Column(String(36), ForeignKey("articles.id"), nullable=False)
    author_name = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    status = Column(String(20), default="pending")  # pending/approved/rejected
    
    # 关系
    article = relationship("ArticleDB", back_populates="comments")
```

### Pydantic Schemas（验证模型）

```python
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from typing import Optional
from datetime import datetime

# Article schemas
class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    author: str = Field(..., min_length=1, max_length=50)
    category_id: Optional[str] = None

class ArticleUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    category_id: Optional[str] = None
    status: Optional[str] = Field(None, pattern="^(draft|published)$")

class ArticleResponse(BaseModel):
    id: str
    title: str
    content: str
    summary: str
    author: str
    category_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    status: str
    view_count: int
    
    model_config = ConfigDict(from_attributes=True)

class ArticleQuery(BaseModel):
    category_id: Optional[str] = None
    author: Optional[str] = None
    status: Optional[str] = None
    search: Optional[str] = None
    offset: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)

# Category schemas
class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)

class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    description: Optional[str] = Field(None, max_length=500)

class CategoryResponse(BaseModel):
    id: str
    name: str
    description: str
    article_count: int
    
    model_config = ConfigDict(from_attributes=True)

# Comment schemas
class CommentCreate(BaseModel):
    article_id: str
    author_name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    content: str = Field(..., min_length=1, max_length=1000)

class CommentUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|approved|rejected)$")

class CommentResponse(BaseModel):
    id: str
    article_id: str
    author_name: str
    email: str
    content: str
    created_at: datetime
    status: str
    
    model_config = ConfigDict(from_attributes=True)

class CommentQuery(BaseModel):
    article_id: Optional[str] = None
    status: Optional[str] = None
    offset: int = Field(0, ge=0)
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
    APPROVED = "approved"
    REJECTED = "rejected"

# 业务常量
MAX_TITLE_LENGTH = 200
MAX_SUMMARY_LENGTH = 500
MAX_CONTENT_LENGTH = 10000
MAX_COMMENT_LENGTH = 1000
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100
```

## 2. Service Layer（服务层）

### Business Services（业务服务）

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

class ArticleService:
    """文章业务服务"""
    
    def __init__(self, repository: ArticleRepository):
        self.repository = repository
    
    def create_article(self, article_data: ArticleCreate) -> ArticleResponse:
        """创建文章（保存为草稿）"""
        article = ArticleDB(**article_data.model_dump())
        return self.repository.create(article)
    
    def publish_article(self, article_id: str) -> ArticleResponse:
        """发布文章"""
        article = self.repository.get_by_id(article_id)
        if not article:
            raise ValueError("文章不存在")
        
        article.status = ArticleStatus.PUBLISHED.value
        article.updated_at = datetime.now()
        return self.repository.update(article)
    
    def update_article(self, article_id: str, update_data: ArticleUpdate) -> ArticleResponse:
        """更新文章"""
        article = self.repository.get_by_id(article_id)
        if not article:
            raise ValueError("文章不存在")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(article, field, value)
        
        article.updated_at = datetime.now()
        return self.repository.update(article)
    
    def delete_article(self, article_id: str) -> bool:
        """删除文章"""
        return self.repository.delete(article_id)
    
    def get_articles_by_category(self, category_id: str, offset: int = 0, limit: int = 10) -> List[ArticleResponse]:
        """按分类查询文章"""
        return self.repository.get_by_category(category_id, offset, limit)
    
    def search_articles(self, query: str, offset: int = 0, limit: int = 10) -> List[ArticleResponse]:
        """搜索文章（按标题或内容）"""
        return self.repository.search(query, offset, limit)
    
    def increment_view_count(self, article_id: str) -> ArticleResponse:
        """增加浏览量"""
        article = self.repository.get_by_id(article_id)
        if not article:
            raise ValueError("文章不存在")
        
        article.view_count += 1
        return self.repository.update(article)

class CategoryService:
    """分类业务服务"""
    
    def __init__(self, repository: CategoryRepository):
        self.repository = repository
    
    def create_category(self, category_data: CategoryCreate) -> CategoryResponse:
        """创建分类"""
        # 检查名称唯一性
        if self.repository.exists_by_name(category_data.name):
            raise ValueError("分类名称已存在")
        
        category = CategoryDB(**category_data.model_dump())
        return self.repository.create(category)
    
    def update_category(self, category_id: str, update_data: CategoryUpdate) -> CategoryResponse:
        """更新分类"""
        category = self.repository.get_by_id(category_id)
        if not category:
            raise ValueError("分类不存在")
        
        if update_data.name and update_data.name != category.name:
            if self.repository.exists_by_name(update_data.name):
                raise ValueError("分类名称已存在")
        
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(category, field, value)
        
        return self.repository.update(category)
    
    def delete_category(self, category_id: str) -> bool:
        """删除分类"""
        # 检查是否有文章使用该分类
        article_count = self.repository.get_article_count(category_id)
        if article_count > 0:
            raise ValueError("该分类下有文章，无法删除")
        
        return self.repository.delete(category_id)
    
    def get_all_categories(self) -> List[CategoryResponse]:
        """获取所有分类"""
        return self.repository.get_all()

class CommentService:
    """评论业务服务"""
    
    def __init__(self, repository: CommentRepository, article_repository: ArticleRepository):
        self.repository = repository
        self.article_repository = article_repository
    
    def create_comment(self, comment_data: CommentCreate) -> CommentResponse:
        """发表评论"""
        # 验证文章存在
        article = self.article_repository.get_by_id(comment_data.article_id)
        if not article:
            raise ValueError("文章不存在")
        
        comment = CommentDB(**comment_data.model_dump())
        return self.repository.create(comment)
    
    def approve_comment(self, comment_id: str) -> CommentResponse:
        """审核通过评论"""
        comment = self.repository.get_by_id(comment_id)
        if not comment:
            raise ValueError("评论不存在")
        
        comment.status = CommentStatus.APPROVED.value
        return self.repository.update(comment)
    
    def reject_comment(self, comment_id: str) -> CommentResponse:
        """拒绝评论"""
        comment = self.repository.get_by_id(comment_id)
        if not comment:
            raise ValueError("评论不存在")
        
        comment.status = CommentStatus.REJECTED.value
        return self.repository.update(comment)
    
    def delete_comment(self, comment_id: str) -> bool:
        """删除评论"""
        return self.repository.delete(comment_id)
    
    def get_comments_by_article(self, article_id: str, offset: int = 0, limit: int = 10) -> List[CommentResponse]:
        """获取文章的评论列表"""
        return self.repository.get_by_article(article_id, offset, limit)
```

### Repository Pattern（仓储模式）

```python
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_, func

class ArticleRepository:
    """文章数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, article: ArticleDB) -> ArticleResponse:
        """创建文章"""
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return ArticleResponse.model_validate(article)
    
    def get_by_id(self, article_id: str) -> Optional[ArticleDB]:
        """根据ID获取文章"""
        return self.db.query(ArticleDB).filter(ArticleDB.id == article_id).first()
    
    def update(self, article: ArticleDB) -> ArticleResponse:
        """更新文章"""
        self.db.commit()
        self.db.refresh(article)
        return ArticleResponse.model_validate(article)
    
    def delete(self, article_id: str) -> bool:
        """删除文章"""
        article = self.get_by_id(article_id)
        if article:
            self.db.delete(article)
            self.db.commit()
            return True
        return False
    
    def get_by_category(self, category_id: str, offset: int, limit: int) -> List[ArticleResponse]:
        """按分类获取文章"""
        articles = self.db.query(ArticleDB)\
            .filter(ArticleDB.category_id == category_id)\
            .order_by(ArticleDB.created_at.desc())\
            .offset(offset).limit(limit).all()
        return [ArticleResponse.model_validate(article) for article in articles]
    
    def search(self, query: str, offset: int, limit: int) -> List[ArticleResponse]:
        """搜索文章"""
        search_filter = or_(
            ArticleDB.title.contains(query),
            ArticleDB.content.contains(query)
        )
        articles = self.db.query(ArticleDB)\
            .filter(search_filter)\
            .order_by(ArticleDB.created_at.desc())\
            .offset(offset).limit(limit).all()
        return [ArticleResponse.model_validate(article) for article in articles]

class CategoryRepository:
    """分类数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, category: CategoryDB) -> CategoryResponse:
        """创建分类"""
        self.db.add(category)
        self.db.commit()
        self.db.refresh(category)
        return CategoryResponse.model_validate(category)
    
    def get_by_id(self, category_id: str) -> Optional[CategoryDB]:
        """根据ID获取分类"""
        return self.db.query(CategoryDB).filter(CategoryDB.id == category_id).first()
    
    def update(self, category: CategoryDB) -> CategoryResponse:
        """更新分类"""
        self.db.commit()
        self.db.refresh(category)
        return CategoryResponse.model_validate(category)
    
    def delete(self, category_id: str) -> bool:
        """删除分类"""
        category = self.get_by_id(category_id)
        if category:
            self.db.delete(category)
            self.db.commit()
            return True
        return False
    
    def exists_by_name(self, name: str) -> bool:
        """检查分类名称是否存在"""
        return self.db.query(CategoryDB).filter(CategoryDB.name == name).first() is not None
    
    def get_all(self) -> List[CategoryResponse]:
        """获取所有分类"""
        categories = self.db.query(CategoryDB).all()
        return [CategoryResponse.model_validate(category) for category in categories]
    
    def get_article_count(self, category_id: str) -> int:
        """获取分类下的文章数量"""
        return self.db.query(func.count(ArticleDB.id))\
            .filter(ArticleDB.category_id == category_id).scalar()

class CommentRepository:
    """评论数据访问层"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, comment: CommentDB) -> CommentResponse:
        """创建评论"""
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return CommentResponse.model_validate(comment)
    
    def get_by_id(self, comment_id: str) -> Optional[CommentDB]:
        """根据ID获取评论"""
        return self.db.query(CommentDB).filter(CommentDB.id == comment_id).first()
    
    def update(self, comment: CommentDB) -> CommentResponse:
        """更新评论"""
        self.db.commit()
        self.db.refresh(comment)
        return CommentResponse.model_validate(comment)
    
    def delete(self, comment_id: str) -> bool:
        """删除评论"""
        comment = self.get_by_id(comment_id)
        if comment:
            self.db.delete(comment)
            self.db.commit()
            return True
        return False
    
    def get_by_article(self, article_id: str, offset: int, limit: int) -> List[CommentResponse]:
        """获取文章的评论列表"""
        comments = self.db.query(CommentDB)\
            .filter(CommentDB.article_id == article_id)\
            .order_by(CommentDB.created_at.desc())\
            .offset(offset).limit(limit).all()
        return [CommentResponse.model_validate(comment) for comment in comments]
```

### Transaction Management（事务管理）

```python
from contextlib import contextmanager
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

@contextmanager
def transaction_context(db: Session):
    """事务上下文管理器"""
    try:
        yield db
        db.commit()
    except SQLAlchemyError as e:
        db.rollback()
        raise e
    except Exception as e:
        db.rollback()
        raise e

class TransactionManager:
    """事务管理器"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def execute_in_transaction(self, operation):
        """在事务中执行操作"""
        with transaction_context(self.db):
            return operation()
```

## 3. REST API Design（API设计）

### API Endpoints（端点定义）

#### 文章相关接口

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional

router = APIRouter(prefix="/api/articles", tags=["articles"])

@router.post("/", response_model=ArticleResponse, status_code=201)
def create_article(
    article_data: ArticleCreate,
    service: ArticleService = Depends(get_article_service)
):
    """创建文章"""
    try:
        return service.create_article(article_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: str,
    service: ArticleService = Depends(get_article_service)
):
    """获取文章详情"""
    article = service.repository.get_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")
    
    # 增加浏览量
    service.increment_view_count(article_id)
    return ArticleResponse.model_validate(article)

@router.put("/{article_id}", response_model=ArticleResponse)
def update_article(
    article_id: str,
    article_data: ArticleUpdate,
    service: ArticleService = Depends(get_article_service)
):
    """更新文章"""
    try:
        return service.update_article(article_id, article_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        return service.publish_article(article_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[ArticleResponse])
def list_articles(
    category_id: Optional[str] = Query(None, description="分类ID"),
    author: Optional[str] = Query(None, description="作者"),
    status: Optional[str] = Query(None, description="状态"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: ArticleService = Depends(get_article_service)
):
    """获取文章列表"""
    if search:
        return service.search_articles(search, offset, limit)
    elif category_id:
        return service.get_articles_by_category(category_id, offset, limit)
    else:
        # 获取所有已发布的文章
        return service.repository.get_published_articles(offset, limit)
```

#### 分类相关接口

```python
router = APIRouter(prefix="/api/categories", tags=["categories"])

@router.post("/", response_model=CategoryResponse, status_code=201)
def create_category(
    category_data: CategoryCreate,
    service: CategoryService = Depends(get_category_service)
):
    """创建分类"""
    try:
        return service.create_category(category_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service)
):
    """获取分类详情"""
    category = service.repository.get_by_id(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="分类不存在")
    return CategoryResponse.model_validate(category)

@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    category_data: CategoryUpdate,
    service: CategoryService = Depends(get_category_service)
):
    """更新分类"""
    try:
        return service.update_category(category_id, category_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{category_id}", status_code=204)
def delete_category(
    category_id: str,
    service: CategoryService = Depends(get_category_service)
):
    """删除分类"""
    try:
        if not service.delete_category(category_id):
            raise HTTPException(status_code=404, detail="分类不存在")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/", response_model=List[CategoryResponse])
def list_categories(
    service: CategoryService = Depends(get_category_service)
):
    """获取所有分类"""
    return service.get_all_categories()

@router.get("/{category_id}/articles", response_model=List[ArticleResponse])
def get_articles_by_category(
    category_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: ArticleService = Depends(get_article_service)
):
    """获取分类下的文章"""
    return service.get_articles_by_category(category_id, offset, limit)
```

#### 评论相关接口

```python
router = APIRouter(prefix="/api/comments", tags=["comments"])

@router.post("/", response_model=CommentResponse, status_code=201)
def create_comment(
    comment_data: CommentCreate,
    service: CommentService = Depends(get_comment_service)
):
    """发表评论"""
    try:
        return service.create_comment(comment_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """获取评论详情"""
    comment = service.repository.get_by_id(comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return CommentResponse.model_validate(comment)

@router.put("/{comment_id}/approve", response_model=CommentResponse)
def approve_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """审核通过评论"""
    try:
        return service.approve_comment(comment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{comment_id}/reject", response_model=CommentResponse)
def reject_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """拒绝评论"""
    try:
        return service.reject_comment(comment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{comment_id}", status_code=204)
def delete_comment(
    comment_id: str,
    service: CommentService = Depends(get_comment_service)
):
    """删除评论"""
    if not service.delete_comment(comment_id):
        raise HTTPException(status_code=404, detail="评论不存在")

@router.get("/", response_model=List[CommentResponse])
def list_comments(
    article_id: Optional[str] = Query(None, description="文章ID"),
    status: Optional[str] = Query(None, description="评论状态"),
    offset: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: CommentService = Depends(get_comment_service)
):
    """获取评论列表"""
    if article_id:
        return service.get_comments_by_article(article_id, offset, limit)
    else:
        # 获取所有评论
        return service.repository.get_all(offset, limit)
```

### Request/Response Models（请求响应模型）

```python
# 统一响应格式
class ApiResponse(BaseModel):
    code: int = 200
    message: str = "success"
    data: Optional[dict] = None

class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None

# 分页响应
class PaginatedResponse(BaseModel):
    items: List[dict]
    total: int
    offset: int
    limit: int
```

### API Routing（路由配置）

```python
from fastapi import FastAPI
from api.v1 import articles, categories, comments

def register_routes(app: FastAPI):
    """注册所有路由"""
    # v1版本路由
    app.include_router(articles.router)
    app.include_router(categories.router)
    app.include_router(comments.router)
    
    # 健康检查
    @app.get("/health")
    def health_check():
        return {"status": "healthy"}
    
    # API文档
    @app.get("/")
    def root():
        return {
            "message": "博客系统API",
            "version": "1.0.0",
            "docs": "/docs"
        }
```

### Middleware（中间件）

```python
from fastapi import Request
from fastapi.responses import JSONResponse
import time
import logging

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 错误处理中间件
@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)}
    )

@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "资源不存在"}
    )

@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "服务器内部错误"}
    )

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    logger.info(
        f"{request.method} {request.url.path} - "
        f"{response.status_code} - {process_time:.4f}s"
    )
    
    return response

# CORS中间件
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

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from db.session import engine, Base
from api.v1.routes import register_routes

# 创建FastAPI应用
app = FastAPI(
    title="博客系统API",
    description="一个简单的博客发布系统，支持文章发布、分类和评论功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# 注册路由
register_routes(app)

# 启动事件
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    
    # 初始化默认分类
    from services.category_service import CategoryService
    from repositories.category_repository import CategoryRepository
    from db.session import SessionLocal
    
    db = SessionLocal()
    try:
        category_service = CategoryService(CategoryRepository(db))
        # 检查是否已有分类
        if not category_service.get_all_categories():
            # 创建默认分类
            from schemas.category import CategoryCreate
            default_category = CategoryCreate(
                name="未分类",
                description="默认分类"
            )
            category_service.create_category(default_category)
    finally:
        db.close()

# 关闭事件
@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时的清理"""
    pass

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

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from core.config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite特定配置
    echo=settings.DEBUG  # 调试模式下打印SQL
)

# 创建会话工厂
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# 创建基类
Base = declarative_base()

# 依赖注入函数
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### Dependency Injection（依赖注入）

```python
from fastapi import Depends
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
    repository: CommentRepository = Depends(get_comment_repository),
    article_repository: ArticleRepository = Depends(get_article_repository)
) -> CommentService:
    """获取评论服务"""
    return CommentService(repository, article_repository)
```

### Environment Settings（环境配置）

```python
from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    """应用配置"""
    
    # 应用配置
    APP_NAME: str = "博客系统API"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./blog.db"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
    ]
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# 创建配置实例
settings = Settings()
```

### 环境变量文件 (.env)

```bash
# 应用配置
APP_NAME=博客系统API
VERSION=1.0.0
DEBUG=True
HOST=0.0.0.0
PORT=8000

# 数据库配置
DATABASE_URL=sqlite:///./blog.db

# CORS配置
ALLOWED_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# 安全配置
SECRET_KEY=your-secret-key-change-in-production
```

### 项目结构

```
blog-system/
├── src/
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── articles.py
│   │       ├── categories.py
│   │       ├── comments.py
│   │       └── deps.py
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py
│   ├── db/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── session.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── article.py
│   │   ├── category.py
│   │   └── comment.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── article.py
│   │   ├── category.py
│   │   └── comment.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── article_service.py
│   │   ├── category_service.py
│   │   └── comment_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── article_repository.py
│   │   ├── category_repository.py
│   │   └── comment_repository.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── test_articles.py
│   ├── test_categories.py
│   └── test_comments.py
├── requirements.txt
├── .env
└── README.md
```

### 启动脚本

```bash
#!/bin/bash
# start.sh

echo "启动博客系统..."

# 安装依赖
pip install -r requirements.txt

# 运行应用
python -m src.main
```

### requirements.txt

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
pydantic-settings==2.1.0
python-multipart==0.0.6
email-validator==2.1.0
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.2
```

## 5. Testing Specifications（测试规范）

### Unit Tests（单元测试）

#### 文章服务单元测试

```python
import unittest
from unittest.mock import Mock
from services.article_service import ArticleService
from schemas.article import ArticleCreate

class TestArticleService(unittest.TestCase):
    
    def setUp(self):
        self.mock_repository = Mock()
        self.service = ArticleService(self.mock_repository)
    
    def test_create_article(self):
        """测试创建文章"""
        article_data = ArticleCreate(
            title="测试文章",
            content="测试内容",
            author="测试作者"
        )
        
        result = self.service.create_article(article_data)
        self.assertEqual(result.title, "测试文章")
        self.mock_repository.create.assert_called_once()

class TestCategoryService(unittest.TestCase):
    
    def setUp(self):
        self.mock_repository = Mock()
        self.service = CategoryService(self.mock_repository)
    
    def test_create_category(self):
        """测试创建分类"""
        from schemas.category import CategoryCreate
        category_data = CategoryCreate(name="技术", description="技术相关")
        
        self.mock_repository.exists_by_name.return_value = False
        result = self.service.create_category(category_data)
        
        self.assertEqual(result.name, "技术")
        self.mock_repository.create.assert_called_once()
```

### Integration Tests（集成测试）

#### API集成测试

```python
import unittest
from fastapi.testclient import TestClient
from main import app
from db.session import engine, Base

class TestArticleAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        Base.metadata.create_all(bind=engine)
    
    def tearDown(self):
        Base.metadata.drop_all(bind=engine)
    
    def test_create_and_get_article(self):
        """测试创建和获取文章"""
        article_data = {
            "title": "测试文章",
            "content": "这是测试内容",
            "author": "测试作者"
        }
        
        response = self.client.post("/api/articles/", json=article_data)
        self.assertEqual(response.status_code, 201)
        
        article_id = response.json()["id"]
        response = self.client.get(f"/api/articles/{article_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "测试文章")
    
    def test_update_article(self):
        """测试更新文章"""
        article_data = {
            "title": "原始标题",
            "content": "原始内容",
            "author": "测试作者"
        }
        
        response = self.client.post("/api/articles/", json=article_data)
        article_id = response.json()["id"]
        
        update_data = {"title": "更新后的标题"}
        response = self.client.put(f"/api/articles/{article_id}", json=update_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["title"], "更新后的标题")

class TestCategoryAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        Base.metadata.create_all(bind=engine)
    
    def tearDown(self):
        Base.metadata.drop_all(bind=engine)
    
    def test_create_category(self):
        """测试创建分类"""
        category_data = {
            "name": "技术",
            "description": "技术相关文章"
        }
        
        response = self.client.post("/api/categories/", json=category_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["name"], "技术")
    
    def test_list_categories(self):
        """测试获取分类列表"""
        categories = [
            {"name": "技术", "description": "技术文章"},
            {"name": "生活", "description": "生活随笔"}
        ]
        
        for category in categories:
            self.client.post("/api/categories/", json=category)
        
        response = self.client.get("/api/categories/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 2)

class TestCommentAPI(unittest.TestCase):
    
    def setUp(self):
        self.client = TestClient(app)
        Base.metadata.create_all(bind=engine)
    
    def tearDown(self):
        Base.metadata.drop_all(bind=engine)
    
    def test_create_comment(self):
        """测试创建评论"""
        # 先创建文章
        article_data = {
            "title": "测试文章",
            "content": "内容",
            "author": "作者"
        }
        
        response = self.client.post("/api/articles/", json=article_data)
        article_id = response.json()["id"]
        
        # 创建评论
        comment_data = {
            "article_id": article_id,
            "author_name": "评论者",
            "email": "test@example.com",
            "content": "这是一条测试评论"
        }
        
        response = self.client.post("/api/comments/", json=comment_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["content"], "这是一条测试评论")
    
    def test_approve_comment(self):
        """测试审核评论"""
        # 创建文章和评论
        article_data = {
            "title": "测试文章",
            "content": "内容",
            "author": "作者"
        }
        
        response = self.client.post("/api/articles/", json=article_data)
        article_id = response.json()["id"]
        
        comment_data = {
            "article_id": article_id,
            "author_name": "评论者",
            "email": "test@example.com",
            "content": "评论内容"
        }
        
        response = self.client.post("/api/comments/", json=comment_data)
        comment_id = response.json()["id"]
        
        # 审核通过评论
        response = self.client.put(f"/api/comments/{comment_id}/approve")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "approved")
```

### Test Fixtures（测试夹具）

```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.session import Base

# 测试数据库配置
TEST_DATABASE_URL = "sqlite:///./test_blog.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """创建测试数据库会话"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_category():
    """创建测试分类"""
    return {
        "name": "测试分类",
        "description": "这是一个测试分类"
    }

@pytest.fixture
def sample_article():
    """创建测试文章"""
    return {
        "title": "测试文章",
        "content": "这是测试文章内容，包含一些示例文本。",
        "author": "测试作者",
        "summary": "测试摘要"
    }

@pytest.fixture
def sample_comment():
    """创建测试评论"""
    return {
        "author_name": "测试评论者",
        "email": "test@example.com",
        "content": "这是一条测试评论"
    }
```

### Test Configuration（测试配置）

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short

# 测试运行命令
# python -m pytest tests/
# python -m pytest tests/test_articles.py -v
# python -m pytest tests/ -k "test_create_article"
```

### 测试覆盖率报告

```bash
# 安装覆盖率工具
pip install pytest-cov

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html --cov-report=term

# 覆盖率报告将生成在 htmlcov/ 目录
# 打开 htmlcov/index.html 查看详细报告
```

### 测试总结

- **单元测试覆盖率**: 目标 > 80%
- **集成测试覆盖率**: 目标 > 70%
- **API测试**: 覆盖所有主要端点
- **边界条件测试**: 验证错误处理和异常情况
- **性能测试**: 基础负载测试确保系统稳定性

通过完整的测试套件，确保博客系统的功能正确性和稳定性。
