# MDA-GENERATED-START: test-users
"""
User API tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.core.database import Base, get_db
from app.models.user import UserStatus

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_user():
    """Test creating a new user"""
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "phone": "+1234567890"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test User"
    assert data["email"] == "test@example.com"
    assert data["status"] == UserStatus.ACTIVE
    assert "id" in data


def test_get_users():
    """Test getting user list"""
    response = client.get("/api/v1/users")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


def test_get_user():
    """Test getting a specific user"""
    # First create a user
    create_response = client.post(
        "/api/v1/users",
        json={
            "name": "Get Test User",
            "email": "gettest@example.com"
        }
    )
    user_id = create_response.json()["id"]
    
    # Then get the user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == "Get Test User"


def test_update_user():
    """Test updating user information"""
    # First create a user
    create_response = client.post(
        "/api/v1/users",
        json={
            "name": "Update Test User",
            "email": "updatetest@example.com"
        }
    )
    user_id = create_response.json()["id"]
    
    # Then update the user
    response = client.put(
        f"/api/v1/users/{user_id}",
        json={
            "name": "Updated Name",
            "phone": "+9876543210"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    assert data["phone"] == "+9876543210"
    assert data["email"] == "updatetest@example.com"  # Email unchanged


def test_delete_user():
    """Test soft deleting a user"""
    # First create a user
    create_response = client.post(
        "/api/v1/users",
        json={
            "name": "Delete Test User",
            "email": "deletetest@example.com"
        }
    )
    user_id = create_response.json()["id"]
    
    # Then delete the user
    response = client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204
    
    # Verify user status is now INACTIVE
    get_response = client.get(f"/api/v1/users/{user_id}")
    assert get_response.json()["status"] == UserStatus.INACTIVE


def test_create_user_duplicate_email():
    """Test creating a user with duplicate email"""
    # Create first user
    client.post(
        "/api/v1/users",
        json={
            "name": "First User",
            "email": "duplicate@example.com"
        }
    )
    
    # Try to create second user with same email
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Second User",
            "email": "duplicate@example.com"
        }
    )
    assert response.status_code == 409
    assert "already" in response.json()["detail"].lower()


def test_get_nonexistent_user():
    """Test getting a user that doesn't exist"""
    response = client.get("/api/v1/users/550e8400-e29b-41d4-a716-446655440000")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_invalid_email_format():
    """Test creating user with invalid email"""
    response = client.post(
        "/api/v1/users",
        json={
            "name": "Invalid Email User",
            "email": "not-an-email"
        }
    )
    assert response.status_code == 422  # Validation error


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data
    assert "version" in data
# MDA-GENERATED-END: test-users