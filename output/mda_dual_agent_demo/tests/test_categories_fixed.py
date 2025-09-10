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
    from sqlalchemy import text
    db = TestingSessionLocal()
    try:
        # 清理所有数据
        db.execute(text('DELETE FROM comments'))
        db.execute(text('DELETE FROM articles'))
        db.execute(text('DELETE FROM categories'))
        db.commit()
    finally:
        db.close()

def test_create_category():
    response = client.post(
        "/api/categories/",
        json={"name": "Unique Test Category", "description": "Test Description"},
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Unique Test Category"

def test_read_category():
    # 先创建category
    create_response = client.post(
        "/api/categories/",
        json={"name": "Test Read Category", "description": "Test Description"},
    )
    category_id = create_response.json()["id"]
    
    # 然后读取
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Test Read Category"

def test_update_category():
    # 先创建category
    create_response = client.post(
        "/api/categories/",
        json={"name": "Test Update Category", "description": "Test Description"},
    )
    category_id = create_response.json()["id"]
    
    # 然后更新
    response = client.put(
        f"/api/categories/{category_id}",
        json={"name": "Updated Test Category"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Test Category"

def test_delete_category():
    # 先创建category
    create_response = client.post(
        "/api/categories/",
        json={"name": "Test Delete Category", "description": "Test Description"},
    )
    category_id = create_response.json()["id"]
    
    # 然后删除
    response = client.delete(f"/api/categories/{category_id}")
    assert response.status_code == 204
    
    # 验证已删除
    response = client.get(f"/api/categories/{category_id}")
    assert response.status_code == 404