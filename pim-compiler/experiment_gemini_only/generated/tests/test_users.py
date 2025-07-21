import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.config import settings
from tests.utils import random_email, random_lower_string

pytestmark = pytest.mark.asyncio


async def test_register_user(client: AsyncClient, db_session: AsyncSession) -> None:
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    data = {"username": username, "email": email, "password": password}
    r = await client.post(f"{settings.API_V1_STR}/users/register", json=data)
    assert r.status_code == 200
    created_user = r.json()
    assert created_user["email"] == email
    assert created_user["username"] == username
    assert "id" in created_user


async def test_login(client: AsyncClient, db_session: AsyncSession) -> None:
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    # Create user first
    user_data = {"username": username, "email": email, "password": password}
    await client.post(f"{settings.API_V1_STR}/users/register", json=user_data)

    # Test login
    login_data = {"username": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/users/login/access-token", data=login_data
    )
    assert r.status_code == status.HTTP_200_OK
    token = r.json()
    assert "access_token" in token
    assert token["token_type"] == "bearer"


async def test_get_current_user(client: AsyncClient, db_session: AsyncSession) -> None:
    username = random_lower_string()
    email = random_email()
    password = random_lower_string()
    user_data = {"username": username, "email": email, "password": password}
    r = await client.post(f"{settings.API_V1_STR}/users/register", json=user_data)
    user_id = r.json()["id"]

    login_data = {"username": username, "password": password}
    r = await client.post(
        f"{settings.API_V1_STR}/users/login/access-token", data=login_data
    )
    token = r.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = await client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r.status_code == status.HTTP_200_OK
    user = r.json()
    assert user["id"] == user_id
    assert user["username"] == username
    assert user["email"] == email
