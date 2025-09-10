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

def setup_module():
    """在每个测试模块运行前清理并设置测试数据"""
    db = TestingSessionLocal()
    try:
        # 清理所有数据
        db.execute('DELETE FROM comments')
        db.execute('DELETE FROM articles')
        db.execute('DELETE FROM categories')
        db.commit()
        
        # 创建测试category
        db.execute('INSERT INTO categories (name, description) VALUES (?, ?)', 
                   ('Test Category', 'Test Description'))
        db.commit()
    finally:
        db.close()

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
    # 先创建article
    create_response = client.post(
        "/api/articles/",
        json={"title": "Test Read Article", "content": "Test Content", "author": "Test Author", "category_id": 1},
    )
    article_id = create_response.json()["id"]
    
    # 然后读取
    response = client.get(f"/api/articles/{article_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Read Article"

def test_update_article():
    # 先创建article
    create_response = client.post(
        "/api/articles/",
        json={"title": "Test Update Article", "content": "Test Content", "author": "Test Author", "category_id": 1},
    )
    article_id = create_response.json()["id"]
    
    # 然后更新
    response = client.put(
        f"/api/articles/{article_id}",
        json={"title": "Updated Test Article"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Test Article"

def test_delete_article():
    # 先创建article
    create_response = client.post(
        "/api/articles/",
        json={"title": "Test Delete Article", "content": "Test Content", "author": "Test Author", "category_id": 1},
    )
    article_id = create_response.json()["id"]
    
    # 然后删除
    response = client.delete(f"/api/articles/{article_id}")
    assert response.status_code == 204
    
    # 验证已删除
    response = client.get(f"/api/articles/{article_id}")
    assert response.status_code == 404