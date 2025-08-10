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

def test_create_comment():
    response = client.post(
        "/api/comments/",
        json={"article_id": 1, "author_name": "Test Author", "email": "test@example.com", "content": "Test Content"},
    )
    assert response.status_code == 201
    assert response.json()["author_name"] == "Test Author"
    assert response.json()["content"] == "Test Content"

def test_read_comment():
    # 先创建评论
    create_response = client.post(
        "/api/comments/",
        json={"article_id": 1, "author_name": "Test Author", "email": "test@example.com", "content": "Test Content"},
    )
    comment_id = create_response.json()["id"]
    
    response = client.get(f"/api/comments/{comment_id}")
    assert response.status_code == 200
    assert response.json()["author_name"] == "Test Author"

def test_update_comment_status():
    # 先创建评论
    create_response = client.post(
        "/api/comments/",
        json={"article_id": 1, "author_name": "Test Author", "email": "test@example.com", "content": "Test Content"},
    )
    comment_id = create_response.json()["id"]
    
    response = client.put(
        f"/api/comments/{comment_id}/status",
        json={"status": "published"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "published"

def test_delete_comment():
    # 先创建评论
    create_response = client.post(
        "/api/comments/",
        json={"article_id": 1, "author_name": "Test Author", "email": "test@example.com", "content": "Test Content"},
    )
    comment_id = create_response.json()["id"]
    
    response = client.delete(f"/api/comments/{comment_id}")
    assert response.status_code == 204
    response = client.get(f"/api/comments/{comment_id}")
    assert response.status_code == 404

def test_read_comments_by_article():
    # 先创建文章
    article_response = client.post(
        "/api/articles/",
        json={"title": "Test Article", "content": "Test Content", "author": "Test Author", "category_id": 1},
    )
    article_id = article_response.json()["id"]
    
    # 创建评论
    client.post(
        "/api/comments/",
        json={"article_id": article_id, "author_name": "Comment Author", "email": "comment@example.com", "content": "Test Comment"},
    )
    
    # 获取文章评论
    response = client.get(f"/api/articles/{article_id}/comments")
    assert response.status_code == 200
    comments = response.json()
    assert len(comments) > 0