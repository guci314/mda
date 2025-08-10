from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
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

def test_create_category():
    response = client.post(
        "/api/categories/",
        json={"name": "Test Category", "description": "Test Description"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Category"
    assert response.json()["description"] == "Test Description"

def test_read_category():
    response = client.get("/api/categories/1")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Category"

def test_update_category():
    response = client.put(
        "/api/categories/1",
        json={"name": "Updated Test Category"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Category"

def test_delete_category():
    response = client.delete("/api/categories/1")
    assert response.status_code == 204
    response = client.get("/api/categories/1")
    assert response.status_code == 404