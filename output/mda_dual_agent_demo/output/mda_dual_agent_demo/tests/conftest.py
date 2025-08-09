"""
pytest配置文件
"""
import pytest
import asyncio
from typing import AsyncGenerator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from main import app
from app.models.database import Base
from app.database import get_async_db

# 测试数据库URL（使用SQLite内存数据库）
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# 创建测试引擎
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False  # 关闭SQL日志以减少测试输出
)

# 创建测试会话工厂
TestSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """创建测试数据库会话"""
    # 创建表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 创建会话
    async with TestSessionLocal() as session:
        yield session
    
    # 清理表
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def client(db_session: AsyncSession):
    """创建测试客户端"""
    # 覆盖依赖
    def override_get_db():
        return db_session
    
    app.dependency_overrides[get_async_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # 清理依赖覆盖
    app.dependency_overrides.clear()


@pytest.fixture
def sample_book_data():
    """示例图书数据"""
    return {
        "isbn": "9787111213826",
        "title": "深入理解计算机系统",
        "author": "Randal E. Bryant",
        "publisher": "机械工业出版社",
        "publish_year": 2011,
        "category": "计算机科学",
        "total_quantity": 10,
        "available_quantity": 8,
        "location": "A区1层",
        "description": "计算机系统经典教材"
    }


@pytest.fixture
def sample_reader_data():
    """示例读者数据"""
    return {
        "name": "张三",
        "id_card": "110101199001011234",
        "phone": "13800138000",
        "email": "zhangsan@example.com",
        "reader_type": "学生"
    }


@pytest.fixture
async def created_book(client: AsyncClient, sample_book_data):
    """创建测试图书"""
    response = await client.post("/books/", json=sample_book_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def created_reader(client: AsyncClient, sample_reader_data):
    """创建测试读者"""
    response = await client.post("/readers/", json=sample_reader_data)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
async def borrowed_book_setup(client: AsyncClient, created_book, created_reader):
    """创建借阅设置（图书和读者）"""
    # 先借阅图书，使其不可用
    borrow_data = {
        "isbn": created_book["isbn"],
        "reader_id": created_reader["reader_id"]
    }
    borrow_response = await client.post("/borrows/", json=borrow_data)
    assert borrow_response.status_code == 201
    
    return {
        "isbn": created_book["isbn"],
        "reader_id": created_reader["reader_id"],
        "borrow_id": borrow_response.json()["borrow_id"]
    }