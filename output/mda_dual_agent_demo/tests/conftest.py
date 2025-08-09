import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.database import Base, get_async_db
from app.main import app
from app.models.domain import BookDB, ReaderDB, BorrowRecordDB, ReservationRecordDB
from fastapi.testclient import TestClient

# 使用内存数据库进行测试
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
AsyncTestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def init_test_db():
    """初始化测试数据库，创建所有表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_test_db():
    """清理测试数据库"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """会话级别的数据库初始化"""
    await init_test_db()
    yield
    await drop_test_db()


@pytest.fixture(scope="function")
async def db_session():
    """创建测试数据库会话"""
    async with AsyncTestingSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
def client():
    """创建测试客户端"""
    def override_get_async_db():
        async def _get_db():
            async with AsyncTestingSessionLocal() as session:
                yield session
        return _get_db()
    
    app.dependency_overrides[get_async_db] = override_get_async_db()
    yield TestClient(app)
    app.dependency_overrides.clear()