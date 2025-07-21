"""
Tests for the Authentication API Endpoints.

This module contains tests for the /auth/register and /auth/login endpoints.
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config import settings
from src.models.user import User

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_register_user_success(test_client: AsyncClient, db_session: AsyncSession):
    """
    Test successful user registration.
    """
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "newuser@example.com",
            "username": "newuser",
            "password": "ValidPassword123!",
        },
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser"
    assert "id" in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_user_duplicate_username(test_client: AsyncClient, test_user: User):
    """
    Test registration with a username that already exists.
    """
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "another@example.com",
            "username": test_user.username,  # Existing username
            "password": "ValidPassword123!",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "username is already taken" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_user_duplicate_email(test_client: AsyncClient, test_user: User):
    """
    Test registration with an email that already exists.
    """
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": test_user.email,  # Existing email
            "username": "anotheruser",
            "password": "ValidPassword123!",
        },
    )
    assert response.status_code == status.HTTP_409_CONFLICT
    assert "email already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_user_invalid_password(test_client: AsyncClient):
    """
    Test registration with a password that does not meet complexity requirements.
    """
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/register",
        json={
            "email": "invalidpass@example.com",
            "username": "invalidpass",
            "password": "weak",  # Too short
        },
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.asyncio
async def test_login_success(test_client: AsyncClient, test_user: User):
    """
    Test successful login with correct credentials.
    """
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": test_user.username, "password": "Str0ngPassword!"},
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(test_client: AsyncClient, test_user: User):
    """
    Test login with an incorrect password.
    """
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": test_user.username, "password": "WrongPassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Incorrect username or password" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login_wrong_username(test_client: AsyncClient):
    """
    Test login with a non-existent username.
    """
    response = await test_client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": "nonexistentuser", "password": "anypassword"},
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
