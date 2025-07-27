#!/usr/bin/env python3
"""
使用 ChatOpenAI 直接生成 PSM，并行执行四个部分
"""

import os
import asyncio
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
import logging
from datetime import datetime
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 规范系统提示词
FASTAPI_SYSTEM_PROMPT = """你是一个专业的软件架构师，负责根据 PIM（Platform Independent Model）生成 PSM（Platform Specific Model）。

## 技术栈规范
- Web框架: FastAPI
- ORM: SQLAlchemy 2.0
- 数据验证: Pydantic v2
- 数据库: PostgreSQL
- 异步: asyncio
- Python版本: 3.11+

## 代码规范
1. 使用类型注解
2. 异步函数使用 async/await
3. 使用中文注释
4. 遵循 PEP 8
5. 使用依赖注入
6. 实现完整的错误处理

## 项目结构
```
project/
├── app/
│   ├── models/       # SQLAlchemy 模型
│   ├── schemas/      # Pydantic 模型
│   ├── services/     # 业务逻辑
│   ├── api/          # API 端点
│   ├── core/         # 核心配置
│   └── tests/        # 测试代码
├── main.py           # 应用入口
└── requirements.txt  # 依赖
```

生成的代码必须：
1. 可以直接运行
2. 包含完整的类型注解
3. 有适当的错误处理
4. 包含中文业务注释
"""

def get_domain_prompt():
    """Domain 章节生成提示词"""
    return """请生成 Domain Models 章节，包含：

1. SQLAlchemy 模型定义
   - 使用 SQLAlchemy 2.0 语法
   - 包含所有字段和约束
   - 使用 mapped_column
   - 添加索引和关系

2. Pydantic 模型定义
   - BaseModel：基础字段
   - CreateModel：创建时使用
   - UpdateModel：更新时使用（所有字段可选）
   - ResponseModel：API 响应使用
   - 使用 ConfigDict

3. 枚举定义
   - 使用 Enum 类
   - 提供中文注释

示例格式：
```python
# models/user.py
from sqlalchemy import String, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base
import uuid
from datetime import datetime

class UserDB(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment="用户姓名")
    # ... 其他字段

# schemas/user.py
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional
from datetime import datetime
from enum import Enum

class UserStatus(str, Enum):
    active = "active"
    inactive = "inactive"

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="用户姓名")
    email: EmailStr = Field(..., description="用户邮箱")
    # ... 其他字段

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    # ... 其他字段

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)
```
"""

def get_service_prompt():
    """Service 章节生成提示词"""
    return """请生成 Service Layer 章节，包含：

1. 服务类定义
   - 使用依赖注入
   - 异步方法
   - 完整的业务逻辑实现
   - 错误处理

2. 仓储模式
   - 抽象仓储接口
   - SQLAlchemy 实现
   - 支持事务

3. 业务规则实现
   - 验证逻辑
   - 业务约束
   - 异常处理

示例格式：
```python
# services/user_service.py
from typing import Optional, List
from uuid import UUID
from app.models.user import UserDB
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.repositories.user_repository import UserRepository
from app.core.exceptions import BusinessException
from sqlalchemy.ext.asyncio import AsyncSession

class UserService:
    def __init__(self, session: AsyncSession):
        self.repository = UserRepository(session)
        self.session = session
    
    async def register_user(self, user_data: UserCreate) -> UserResponse:
        \"\"\"注册新用户\"\"\"
        # 检查邮箱唯一性
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            raise BusinessException("邮箱已被注册")
        
        # 创建用户
        user = await self.repository.create(user_data)
        return UserResponse.model_validate(user)
    
    async def get_user(self, user_id: UUID) -> UserResponse:
        \"\"\"获取用户信息\"\"\"
        user = await self.repository.get(user_id)
        if not user:
            raise BusinessException("用户不存在")
        return UserResponse.model_validate(user)
    
    # ... 其他方法

# repositories/user_repository.py
from typing import Optional, List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserDB
from app.schemas.user import UserCreate, UserUpdate

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, user_data: UserCreate) -> UserDB:
        \"\"\"创建用户\"\"\"
        user = UserDB(**user_data.model_dump())
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get(self, user_id: UUID) -> Optional[UserDB]:
        \"\"\"根据ID获取用户\"\"\"
        result = await self.session.execute(
            select(UserDB).where(UserDB.id == user_id)
        )
        return result.scalar_one_or_none()
    
    # ... 其他方法
```
"""

def get_test_prompt():
    """Test 章节生成提示词"""
    return """请生成 Test 章节，包含：

1. 单元测试
   - 测试服务层逻辑
   - Mock 仓储层
   - 覆盖所有业务场景

2. 集成测试
   - 测试 API 端点
   - 使用测试数据库
   - 测试完整流程

3. 测试工具
   - Fixtures
   - 测试数据工厂
   - 测试客户端配置

示例格式：
```python
# tests/conftest.py
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.main import app
from app.core.database import Base

@pytest.fixture
async def test_session():
    \"\"\"创建测试数据库会话\"\"\"
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with AsyncSession(engine) as session:
        yield session

@pytest.fixture
async def client(test_session):
    \"\"\"创建测试客户端\"\"\"
    app.dependency_overrides[get_session] = lambda: test_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

# tests/test_user_service.py
import pytest
from uuid import uuid4
from app.services.user_service import UserService
from app.schemas.user import UserCreate

@pytest.mark.asyncio
async def test_register_user(test_session):
    \"\"\"测试用户注册\"\"\"
    service = UserService(test_session)
    
    user_data = UserCreate(
        name="张三",
        email="zhangsan@example.com",
        phone="13800138000"
    )
    
    user = await service.register_user(user_data)
    
    assert user.name == "张三"
    assert user.email == "zhangsan@example.com"
    assert user.id is not None

# tests/test_user_api.py
@pytest.mark.asyncio
async def test_create_user_endpoint(client):
    \"\"\"测试创建用户API\"\"\"
    response = await client.post(
        "/api/users",
        json={
            "name": "李四",
            "email": "lisi@example.com",
            "phone": "13900139000"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "李四"
    assert "id" in data
```
"""

def get_app_prompt():
    """App 章节生成提示词"""
    return """请生成 Application Configuration 章节，包含：

1. FastAPI 应用配置
   - 主应用文件
   - 中间件配置
   - 异常处理器
   - 启动/关闭事件

2. 数据库配置
   - 连接池设置
   - 会话管理
   - 迁移配置

3. API 路由
   - RESTful 端点
   - 请求/响应模型
   - 认证授权

4. 配置管理
   - 环境变量
   - Settings 类
   - 日志配置

示例格式：
```python
# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.api import user_router
from app.core.config import settings
from app.core.database import engine, Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    \"\"\"应用生命周期管理\"\"\"
    # 启动时
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # 关闭时
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)

# 注册路由
app.include_router(user_router, prefix="/api")

# api/user.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.services.user_service import UserService
from app.schemas.user import UserCreate, UserUpdate, UserResponse

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    session: AsyncSession = Depends(get_session)
):
    \"\"\"创建新用户\"\"\"
    service = UserService(session)
    try:
        return await service.register_user(user_data)
    except BusinessException as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    session: AsyncSession = Depends(get_session)
):
    \"\"\"获取用户信息\"\"\"
    service = UserService(session)
    try:
        return await service.get_user(user_id)
    except BusinessException as e:
        raise HTTPException(status_code=404, detail=str(e))

# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "用户管理系统"
    VERSION: str = "1.0.0"
    DATABASE_URL: str = "postgresql+asyncpg://user:pass@localhost/db"
    
    class Config:
        env_file = ".env"

settings = Settings()
```
"""

async def generate_chapter(llm: ChatOpenAI, pim_content: str, chapter_type: str, prompt_getter):
    """生成单个章节"""
    logger.info(f"开始生成 {chapter_type} 章节")
    
    messages = [
        SystemMessage(content=FASTAPI_SYSTEM_PROMPT),
        HumanMessage(content=f"{prompt_getter()}\n\nPIM内容：\n{pim_content}")
    ]
    
    try:
        response = await llm.ainvoke(messages)
        content = response.content
        logger.info(f"{chapter_type} 章节生成完成，长度: {len(content)} 字符")
        return chapter_type, content
    except Exception as e:
        logger.error(f"生成 {chapter_type} 章节失败: {str(e)}")
        return chapter_type, None

async def generate_psm_parallel(pim_path: str, output_dir: str):
    """并行生成 PSM 的四个部分"""
    # 读取 PIM 内容
    pim_content = Path(pim_path).read_text(encoding='utf-8')
    logger.info(f"加载 PIM 文件: {pim_path}, 长度: {len(pim_content)} 字符")
    
    # 获取 API 配置
    api_key = os.getenv('DEEPSEEK_API_KEY')
    if not api_key:
        try:
            with open('/home/guci/aiProjects/mda/.env', 'r') as f:
                for line in f:
                    if line.startswith('DEEPSEEK_API_KEY='):
                        api_key = line.split('=', 1)[1].strip()
                        break
        except:
            pass
    
    if not api_key:
        raise ValueError("No DEEPSEEK_API_KEY found")
    
    # 创建 LLM
    llm = ChatOpenAI(
        model="deepseek-chat",
        api_key=api_key,
        base_url="https://api.deepseek.com",
        temperature=0.7
    )
    
    # 并行生成四个章节
    tasks = [
        generate_chapter(llm, pim_content, "domain", get_domain_prompt),
        generate_chapter(llm, pim_content, "service", get_service_prompt),
        generate_chapter(llm, pim_content, "test", get_test_prompt),
        generate_chapter(llm, pim_content, "app", get_app_prompt)
    ]
    
    logger.info("开始并行生成四个章节...")
    start_time = datetime.now()
    
    results = await asyncio.gather(*tasks)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    logger.info(f"所有章节生成完成，总耗时: {duration:.2f} 秒")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存结果
    psm_content = "# Platform Specific Model (PSM)\n\n"
    psm_content += f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    psm_content += f"技术栈: FastAPI + SQLAlchemy 2.0 + Pydantic v2\n\n"
    
    chapter_files = {}
    for chapter_type, content in results:
        if content:
            # 保存单独的章节文件
            chapter_file = output_path / f"{chapter_type}.md"
            chapter_file.write_text(content, encoding='utf-8')
            chapter_files[chapter_type] = str(chapter_file)
            
            # 添加到完整 PSM
            psm_content += f"## {chapter_type.upper()} 章节\n\n"
            psm_content += content
            psm_content += "\n\n---\n\n"
        else:
            logger.error(f"{chapter_type} 章节生成失败")
    
    # 保存完整 PSM
    psm_file = output_path / "complete_psm.md"
    psm_file.write_text(psm_content, encoding='utf-8')
    
    # 保存生成报告
    report = {
        "generation_time": datetime.now().isoformat(),
        "duration_seconds": duration,
        "pim_file": pim_path,
        "output_dir": str(output_path),
        "chapters": chapter_files,
        "complete_psm": str(psm_file)
    }
    
    report_file = output_path / "generation_report.json"
    report_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    
    logger.info(f"PSM 生成完成，输出目录: {output_path}")
    return report

def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="并行生成 PSM")
    parser.add_argument("pim_file", help="PIM 文件路径")
    parser.add_argument("-o", "--output", default="./psm_output", help="输出目录")
    
    args = parser.parse_args()
    
    # 运行异步生成
    asyncio.run(generate_psm_parallel(args.pim_file, args.output))

if __name__ == "__main__":
    main()