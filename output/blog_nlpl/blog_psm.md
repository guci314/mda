# 博客系统 PSM (Platform Specific Model)

基于 FastAPI + PostgreSQL + SQLAlchemy 2.0 的博客发布系统

生成时间: 2023-11-01
基于PIM: /home/guci/aiProjects/mda/pim-compiler/examples/blog.md## 1. Domain Models（领域模型）

### 1.1 Entity Definitions（实体定义）
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Article(Base):
    __tablename__ = 'articles'
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    summary = Column(String(300))
    author = Column(String(100), nullable=False)
    publish_time = Column(DateTime)
    update_time = Column(DateTime)
    status = Column(String(20), default='draft')
    views = Column(Integer, default=0)
    category_id = Column(Integer, ForeignKey('categories.id'))
    category = relationship('Category', back_populates='articles')
    comments = relationship('Comment', back_populates='article')

class Category(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(300))
    article_count = Column(Integer, default=0)
    articles = relationship('Article', back_populates='category')

class Comment(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True)
    article_id = Column(Integer, ForeignKey('articles.id'))
    author_name = Column(String(100), nullable=False)
    email = Column(String(100))
    content = Column(String, nullable=False)
    publish_time = Column(DateTime)
    status = Column(String(20), default='pending')
    article = relationship('Article', back_populates='comments')
```

### 1.2 Schema Definitions（模式定义）
```python
from pydantic import BaseModel
from datetime import datetime

class ArticleSchema(BaseModel):
    title: str
    content: str
    summary: str
    author: str
    status: str = 'draft'

class CategorySchema(BaseModel):
    name: str
    description: str

class CommentSchema(BaseModel):
    author_name: str
    email: str
    content: str
```

### 1.3 Relationships（关系映射）
- `Article` 与 `Category` 是多对一关系（一个分类可以有多篇文章）。
- `Article` 与 `Comment` 是一对多关系（一篇文章可以有多条评论）。

### 1.4 Constraints（约束条件）
- `Article` 的 `title` 和 `content` 不能为空。
- `Category` 的 `name` 必须唯一且不能为空。
- `Comment` 的 `author_name` 和 `content` 不能为空。## 2. Service Layer（服务层）

### 2.1 Service Interfaces（服务接口）
```python
from sqlalchemy.orm import Session

class ArticleService:
    def __init__(self, db: Session):
        self.db = db

    def create_article(self, article_data: ArticleSchema) -> Article:
        article = Article(**article_data.dict())
        self.db.add(article)
        self.db.commit()
        self.db.refresh(article)
        return article

    def publish_article(self, article_id: int) -> Article:
        article = self.db.query(Article).filter(Article.id == article_id).first()
        if article:
            article.status = 'published'
            self.db.commit()
            self.db.refresh(article)
        return article

class CommentService:
    def __init__(self, db: Session):
        self.db = db

    def add_comment(self, comment_data: CommentSchema, article_id: int) -> Comment:
        comment = Comment(**comment_data.dict(), article_id=article_id)
        self.db.add(comment)
        self.db.commit()
        self.db.refresh(comment)
        return comment
```

### 2.2 Business Logic（业务逻辑）
- 文章发布时自动更新分类的文章数量。
- 评论审核通过后才能显示。

### 2.3 Transaction Management（事务管理）
- 使用 SQLAlchemy 的 `Session` 管理事务。
- 每个服务方法中使用 `commit` 确保数据一致性。

### 2.4 Service Dependencies（服务依赖）
- `ArticleService` 和 `CommentService` 依赖于 SQLAlchemy 的 `Session`。## 3. REST API Design（API设计）

### 3.1 Endpoints（端点）
```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/articles/")
def create_article(article: ArticleSchema, db: Session = Depends(get_db)):
    return ArticleService(db).create_article(article)

@app.put("/articles/{article_id}/publish")
def publish_article(article_id: int, db: Session = Depends(get_db)):
    return ArticleService(db).publish_article(article_id)

@app.post("/articles/{article_id}/comments")
def add_comment(article_id: int, comment: CommentSchema, db: Session = Depends(get_db)):
    return CommentService(db).add_comment(comment, article_id)
```

### 3.2 Request/Response Models（请求响应模型）
- 使用 `ArticleSchema` 和 `CommentSchema` 定义请求和响应格式。

### 3.3 Authentication & Authorization（认证授权）
- 使用 FastAPI 的 `OAuth2PasswordBearer` 实现 JWT 认证。

### 3.4 API Documentation（API文档）
- FastAPI 自动生成 OpenAPI/Swagger 文档，通过 `/docs` 访问。

### 3.5 Error Handling（错误处理）
```python
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
```## 4. Application Configuration（应用配置）

### 4.1 Database Configuration（数据库配置）
```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/blog_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4.2 Main Application（主应用）
```python
from fastapi import FastAPI

app = FastAPI()

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
```

### 4.3 Environment Variables（环境变量）
- 使用 `.env` 文件配置数据库连接信息。

### 4.4 Dependencies（依赖项）
```text
fastapi
uvicorn
sqlalchemy
psycopg2-binary
python-dotenv
```

### 4.5 Middleware Configuration（中间件配置）
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)## 5. Testing Specifications（测试规范）

### 5.1 Unit Tests（单元测试）
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Article, Base

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_create_article(db_session):
    article = Article(title="Test", content="Test content", author="Tester")
    db_session.add(article)
    db_session.commit()
    assert article.id is not None
```

### 5.2 Integration Tests（集成测试）
```python
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_publish_article():
    response = client.put("/articles/1/publish")
    assert response.status_code == 200
```

### 5.3 Test Fixtures（测试链接器）
- 使用 `pytest` 的 `fixture` 管理数据库连接和会话。
- 使用 SQLite 内存数据库进行测试。