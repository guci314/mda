"""
Unit tests for the Todo API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker, Session

from src.main import app
from src.core.database import Base, get_db
from src.schemas.todo import Todo

# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# Override the get_db dependency to use the test database
def override_get_db():
    """Dependency override for test database session."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db_session():
    """Fixture to create and teardown the database for each test function."""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session: Session):
    """Fixture to provide a TestClient instance."""
    yield TestClient(app)


def test_health_check(client: TestClient):
    """Test the health check endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_todo(client: TestClient):
    """Test creating a new todo item."""
    response = client.post(
        "/todos/",
        json={"title": "Test Todo", "description": "A test description"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Todo"
    assert data["description"] == "A test description"
    assert data["status"] == "pending"
    assert "id" in data


def test_get_all_todos(client: TestClient, db_session: Session):
    """Test retrieving all todo items."""
    # Create a todo to ensure the list is not empty
    client.post("/todos/", json={"title": "Todo 1"})
    
    response = client.get("/todos/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == "Todo 1"


def test_get_todo_by_id(client: TestClient):
    """Test retrieving a single todo by its ID."""
    create_response = client.post("/todos/", json={"title": "Specific Todo"})
    todo_id = create_response.json()["id"]

    response = client.get(f"/todos/{todo_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == todo_id
    assert data["title"] == "Specific Todo"


def test_get_todo_not_found(client: TestClient):
    """Test retrieving a non-existent todo."""
    response = client.get("/todos/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


def test_update_todo_status(client: TestClient):
    """Test updating a todo's status."""
    create_response = client.post("/todos/", json={"title": "Update Me"})
    todo_id = create_response.json()["id"]

    update_response = client.patch(
        f"/todos/{todo_id}",
        json={"status": "completed"},
    )
    assert update_response.status_code == 200
    data = update_response.json()
    assert data["status"] == "completed"
    assert data["completed_at"] is not None


def test_delete_todo(client: TestClient):
    """Test deleting a todo."""
    create_response = client.post("/todos/", json={"title": "Delete Me"})
    todo_id = create_response.json()["id"]

    delete_response = client.delete(f"/todos/{todo_id}")
    assert delete_response.status_code == 204

    # Verify it's gone
    get_response = client.get(f"/todos/{todo_id}")
    assert get_response.status_code == 404
