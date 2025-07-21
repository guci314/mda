"""
Pytest Configuration and Fixtures.

This file contains shared fixtures used across the test suite.
It sets up a test database, a test client, and provides
helper fixtures for authentication and data creation.
"""
import asyncio
import pytest_asyncio
from typing import AsyncGenerator, Generator

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from src.main import app
from src.core.database import Base, get_db
from src.models.user import User
from src.core.security import create_access_token
from src.services.user_service import user_service
from src.schemas.user import UserCreate

# --- Test Database Setup ---
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency override for getting a test database session.
    """
    async with TestingSessionLocal() as session:
        yield session


# Apply the override for the entire application
app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """

    Creates an instance of the default event loop for each test session.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    """
    Fixture to set up and tear down the test database.
    It creates all tables before tests run and drops them after.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Provides a clean database session for each test function.
    """
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Provides an AsyncClient for making requests to the test app.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# --- Authentication and Data Fixtures ---
@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """
    Creates a test user in the database and returns the user object.
    """
    user_in = UserCreate(
        email="test@example.com",
        username="testuser",
        password="Str0ngPassword!",
    )
    return await user_service.create_user(db_session, user_in)


@pytest_asyncio.fixture(scope="function")
def auth_token(test_user: User) -> str:
    """
    Generates an authentication token for the test user.
    """
    return create_access_token(data={"sub": test_user.username})


@pytest_asyncio.fixture(scope="function")
def auth_headers(auth_token: str) -> dict[str, str]:
    """
    Returns authorization headers for authenticated requests.
    """
    return {"Authorization": f"Bearer {auth_token}"}
