"""PSM to Code generator using Gemini CLI"""
# pyright: reportUndefinedVariable=false, reportAttributeAccessIssue=false

import os
import yaml
import asyncio
from pathlib import Path
from typing import Dict, Any, List
import logging
from dotenv import load_dotenv

from utils.gemini_cli import call_gemini_cli

logger = logging.getLogger(__name__)


class PSMtoCodeGeminiGenerator:
    """使用 Gemini CLI 将 PSM 转换为可执行代码"""
    
    def __init__(self):
        # 加载项目的 .env 文件
        project_root = Path(__file__).parent.parent.parent.parent
        env_file = project_root / ".env"
        if env_file.exists():
            load_dotenv(env_file)
            logger.info(f"Loaded .env from: {env_file}")
    
    async def generate(self, psm_file: Path, output_dir: Path) -> Dict[str, Path]:
        """从 PSM 生成完整的代码"""
        
        # 读取 PSM 内容
        with open(psm_file, 'r', encoding='utf-8') as f:
            psm_data = yaml.safe_load(f)
        
        platform = psm_data.get('platform', 'fastapi')
        
        # 确保输出目录存在
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 根据平台生成代码
        if platform == 'fastapi':
            return await self._generate_fastapi_code(psm_data, output_dir)
        elif platform == 'spring':
            raise NotImplementedError("Spring code generation is not yet implemented")
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    async def _generate_fastapi_code(self, psm_data: Dict[str, Any], output_dir: Path) -> Dict[str, Path]:
        """生成 FastAPI 代码"""
        
        generated_files = {}
        
        # 生成各个组件
        components = [
            ("models.py", self._generate_models_prompt),
            ("schemas.py", self._generate_schemas_prompt),
            ("database.py", self._generate_database_prompt),
            ("services.py", self._generate_services_prompt),
            ("api.py", self._generate_api_prompt),
            ("main.py", self._generate_main_prompt),
            ("requirements.txt", self._generate_requirements_prompt),
        ]
        
        for filename, prompt_generator in components:
            logger.info(f"Generating {filename}...")
            
            # 生成提示
            prompt = prompt_generator(psm_data)
            
            # 调用 Gemini CLI
            response = await call_gemini_cli(prompt)
            code = self._extract_code(response, filename)
            
            # 保存文件
            file_path = output_dir / filename
            file_path.write_text(code, encoding='utf-8')
            generated_files[filename] = file_path
            
            logger.info(f"Generated: {file_path}")
        
        # 生成配置文件
        await self._generate_config_files(psm_data, output_dir)
        
        return generated_files
    
    def _generate_models_prompt(self, psm_data: Dict[str, Any]) -> str:
        """生成 SQLAlchemy 模型的提示"""
        psm_yaml = yaml.dump(psm_data, allow_unicode=True)
        
        return f"""根据以下 PSM（平台特定模型）生成 SQLAlchemy 2.0 数据模型代码。

PSM 内容：
{psm_yaml}

要求：
1. 使用 SQLAlchemy 2.0 声明式风格
2. 包含所有实体的完整定义
3. 正确设置主键、外键、索引和约束
4. 添加 created_at 和 updated_at 时间戳
5. 使用类型注解
6. 添加必要的导入语句

示例格式：
```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False, comment="图书标题")
    isbn = Column(String(20), unique=True, nullable=False, index=True)
    author = Column(String(100), nullable=False)
    stock = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 关系
    borrow_records = relationship("BorrowRecord", back_populates="book")
    
    def __repr__(self):
        return f"<Book(id={{self.id}}, title='{{self.title}}', isbn='{{self.isbn}}')">"
```

只输出 Python 代码，不要解释。确保代码可以直接运行。"""
    
    def _generate_schemas_prompt(self, psm_data: Dict[str, Any]) -> str:
        """生成 Pydantic schemas 的提示"""
        psm_yaml = yaml.dump(psm_data, allow_unicode=True)
        
        return f"""根据以下 PSM 生成 Pydantic v2 schemas（请求/响应模型）。

PSM 内容：
{psm_yaml}

要求：
1. 使用 Pydantic v2 语法
2. 为每个实体生成 Create、Update、Response schemas
3. 添加字段验证（如 EmailStr、HttpUrl）
4. 使用 ConfigDict 配置
5. 添加示例数据
6. 处理可选字段和默认值

示例格式：
```python
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime
from typing import Optional, List

class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="图书标题")
    isbn: str = Field(..., pattern=r"^\\d{{13}}$", description="ISBN号")
    author: str = Field(..., min_length=1, max_length=100)
    stock: int = Field(0, ge=0, description="库存数量")

class BookCreate(BookBase):
    pass

class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    author: Optional[str] = Field(None, min_length=1, max_length=100)
    stock: Optional[int] = Field(None, ge=0)

class BookResponse(BookBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
```

只输出 Python 代码。"""
    
    def _generate_services_prompt(self, psm_data: Dict[str, Any]) -> str:
        """生成业务逻辑服务的提示"""
        psm_yaml = yaml.dump(psm_data, allow_unicode=True)
        
        # 使用普通字符串拼接，避免 f-string 解析问题
        prompt = f"""根据以下 PSM 生成业务逻辑服务层代码。

PSM 内容：
{psm_yaml}

要求：
1. 实现所有业务方法
2. 包含完整的业务规则验证
3. 使用依赖注入（数据库会话）
4. 正确的错误处理
5. 实现 PSM 中定义的所有业务流程
6. 添加日志记录

示例格式：
```python
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from models import Book, Borrower, BorrowRecord
from schemas import BookCreate, BookUpdate, BorrowRequest

logger = logging.getLogger(__name__)

class BookService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_book(self, book_data: BookCreate) -> Book:
        \"\"\"创建新图书\"\"\"
        db_book = Book(**book_data.model_dump())
        
        try:
            self.db.add(db_book)
            self.db.commit()
            self.db.refresh(db_book)
            logger.info(f"Created book: {{db_book.title}}")
            return db_book
        except IntegrityError as e:
            self.db.rollback()
            if 'isbn' in str(e):
                raise ValueError(f"ISBN {{book_data.isbn}} 已存在")
            raise
    
    def borrow_book(self, borrow_request: BorrowRequest) -> BorrowRecord:
        \"\"\"借书流程实现\"\"\"
        # 1. 检查借阅者状态
        borrower = self.db.query(Borrower).filter(
            Borrower.id == borrow_request.borrower_id
        ).first()
        
        if not borrower:
            raise ValueError("借阅者不存在")
        
        if borrower.status == "blacklist":
            raise ValueError("借阅者在黑名单中")
        
        # 2. 检查借阅数量限制
        active_borrows = self.db.query(BorrowRecord).filter(
            BorrowRecord.borrower_id == borrower.id,
            BorrowRecord.status == "borrowed"
        ).count()
        
        if active_borrows >= 5:
            raise ValueError("已达到最大借阅数量限制")
        
        # 3. 检查图书库存
        book = self.db.query(Book).filter(
            Book.id == borrow_request.book_id
        ).with_for_update().first()
        
        if not book:
            raise ValueError("图书不存在")
        
        if book.stock <= 0:
            raise ValueError("图书库存不足")
        
        # 4. 创建借阅记录
        borrow_record = BorrowRecord(
            borrower_id=borrower.id,
            book_id=book.id,
            borrow_date=datetime.utcnow(),
            due_date=datetime.utcnow() + timedelta(days=30),
            status="borrowed"
        )
        
        # 5. 更新库存
        book.stock -= 1
        borrower.borrowed_count += 1
        
        self.db.add(borrow_record)
        self.db.commit()
        self.db.refresh(borrow_record)
        
        logger.info(f"Book borrowed: {{book.title}} by {{borrower.name}}")
        return borrow_record
```

只输出完整的 Python 代码。"""
        
        return prompt
    
    def _generate_api_prompt(self, psm_data: Dict[str, Any]) -> str:
        """生成 API 路由的提示"""
        psm_yaml = yaml.dump(psm_data, allow_unicode=True)
        
        return f"""根据以下 PSM 生成 FastAPI 路由代码。

PSM 内容：
{psm_yaml}

要求：
1. 实现所有定义的 API 端点
2. 使用依赖注入获取数据库会话和服务
3. 正确的 HTTP 状态码
4. 完整的错误处理
5. 添加 API 文档（描述、响应示例）
6. 实现分页、过滤等功能

示例格式：
```python
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from schemas import BookCreate, BookUpdate, BookResponse, BorrowRequest, BorrowResponse
from services import BookService, BorrowService

router = APIRouter(prefix="/api", tags=["Library Management"])

# 依赖注入
def get_book_service(db: Session = Depends(get_db)) -> BookService:
    return BookService(db)

@router.post("/books", response_model=BookResponse, status_code=status.HTTP_201_CREATED)
async def create_book(
    book: BookCreate,
    service: BookService = Depends(get_book_service)
) -> BookResponse:
    \"\"\"创建新图书\"\"\"
    try:
        db_book = service.create_book(book)
        return BookResponse.model_validate(db_book)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/books", response_model=List[BookResponse])
async def list_books(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    search: Optional[str] = None,
    service: BookService = Depends(get_book_service)
) -> List[BookResponse]:
    \"\"\"获取图书列表\"\"\"
    books = service.list_books(skip=skip, limit=limit, search=search)
    return [BookResponse.model_validate(book) for book in books]

@router.post("/borrow", response_model=BorrowResponse)
async def borrow_book(
    request: BorrowRequest,
    service: BorrowService = Depends(get_borrow_service)
) -> BorrowResponse:
    \"\"\"借书\"\"\"
    try:
        record = service.borrow_book(request)
        return BorrowResponse.model_validate(record)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

只输出完整的 Python 代码。"""
    
    def _generate_main_prompt(self, psm_data: Dict[str, Any]) -> str:
        """生成主程序入口的提示"""
        return f"""生成 FastAPI 应用程序的主入口文件 main.py。

要求：
1. 创建 FastAPI 应用实例
2. 配置 CORS
3. 包含所有路由
4. 添加健康检查端点
5. 配置日志
6. 数据库初始化
7. 添加中间件（请求日志、错误处理）

```python
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import time

from database import engine, Base
from api import router

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 生命周期管理
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    logger.info("Starting application...")
    # 创建数据库表
    Base.metadata.create_all(bind=engine)
    yield
    # 关闭时
    logger.info("Shutting down...")

# 创建应用
app = FastAPI(
    title="{{psm_data.get('description', 'API Service')}}",
    version="1.0.0",
    lifespan=lifespan
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 请求日志中间件
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"{{request.method}} {{request.url.path}} - "
        f"{{response.status_code}} - {{process_time:.3f}}s"
    )
    return response

# 健康检查
@app.get("/health")
async def health_check():
    return {{"status": "healthy", "service": "{{psm_data.get('description', 'API Service')}}"}}

# 包含路由
app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
```

只输出 Python 代码。"""
    
    def _generate_database_prompt(self, psm_data: Dict[str, Any]) -> str:
        """生成数据库配置的提示"""
        return """生成 FastAPI 的数据库配置文件 database.py。

要求：
1. SQLAlchemy 2.0 配置
2. 数据库连接池
3. 会话管理
4. 支持环境变量配置

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import os
from typing import Generator

# 数据库 URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/library_db"
)

# 创建引擎
engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # 检查连接健康
    echo=False  # 生产环境设置为 False
)

# 会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 依赖注入
def get_db() -> Generator[Session, None, None]:
    \"\"\"获取数据库会话\"\"\"
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

只输出 Python 代码。"""
    
    def _generate_requirements_prompt(self, psm_data: Dict[str, Any]) -> str:
        """生成 requirements.txt 的提示"""
        return """生成 FastAPI 项目的 requirements.txt 文件。

包含：
- FastAPI 及相关依赖
- SQLAlchemy 2.0+
- PostgreSQL 驱动
- 其他必要的库

格式：
```
fastapi==0.109.0
uvicorn[standard]==0.27.0
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
pydantic==2.5.3
pydantic[email]==2.5.3
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
alembic==1.13.1
```

只输出依赖列表，每行一个。"""
    
    
    def _extract_code(self, response: str, filename: str) -> str:
        """从 Gemini 响应中提取代码"""
        import re
        
        # 查找代码块
        if filename.endswith('.py'):
            pattern = r'```python\n(.*?)\n```'
        else:
            pattern = r'```\n(.*?)\n```'
        
        match = re.search(pattern, response, re.DOTALL)
        if match:
            return match.group(1)
        
        # 如果没有代码块，返回整个响应（可能是 requirements.txt）
        return response.strip()
    
    async def _generate_config_files(self, psm_data: Dict[str, Any], output_dir: Path):
        """生成配置文件"""
        # .env 文件
        env_content = """# 数据库配置
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/library_db

# 应用配置
APP_NAME=Library Management System
APP_VERSION=1.0.0
DEBUG=True

# 安全配置
SECRET_KEY=your-secret-key-here
"""
        (output_dir / '.env').write_text(env_content)
        
        # docker-compose.yml
        docker_compose = """version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/library_db
    depends_on:
      - db
    volumes:
      - .:/app
    command: uvicorn main:app --host 0.0.0.0 --port 8000 --reload

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=library_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
"""
        (output_dir / 'docker-compose.yml').write_text(docker_compose)
        
        # Dockerfile
        dockerfile = """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
        (output_dir / 'Dockerfile').write_text(dockerfile)


# 测试函数
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python psm_to_code_gemini.py <psm_file> <output_dir>")
        sys.exit(1)
    
    async def main():
        psm_file = Path(sys.argv[1])
        output_dir = Path(sys.argv[2])
        
        generator = PSMtoCodeGeminiGenerator()
        try:
            files = await generator.generate(psm_file, output_dir)
            print(f"✅ Generated {len(files)} files in {output_dir}")
            for name, path in files.items():
                print(f"  - {name}")
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    asyncio.run(main())