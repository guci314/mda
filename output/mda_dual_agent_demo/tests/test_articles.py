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

def test_create_article():
    response = client.post(
        "/api/articles/",
        json={"title": "Test Article", "content": "Test Content", "author": "Test Author", "category_id": 1},
    )
    assert response.status_code == 201
    assert response.json()["title"] == "Test Article"
    assert response.json()["content"] == "Test Content"
    assert response.json()["author"] == "Test Author"

def test_read_article():
    response = client.get("/api/articles/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Article"

def test_update_article():
    response = client.put(
        "/api/articles/1",
        json={"title": "Updated Test Article"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Article"

def test_delete_article():
    response = client.delete("/api/articles/1")
    assert response.status_code == 204
    response = client.get("/api/articles/1")
    assert response.status_code == 404