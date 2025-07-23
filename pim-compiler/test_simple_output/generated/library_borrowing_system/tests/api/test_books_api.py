from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app import schemas
from app.core.config import settings

def test_create_book(client: TestClient, db: Session):
    data = {
        "isbn": "978-0321765723",
        "title": "The C++ Programming Language",
        "author": "Bjarne Stroustrup",
        "publisher": "Addison-Wesley",
        "publish_year": 2013,
        "category": "Programming",
        "total_stock": 10,
        "available_stock": 10,
        "location": "A-1-1",
    }
    response = client.post(f"{settings.API_V1_STR}/books/", json=data)
    assert response.status_code == 201
    content = response.json()
    assert content["isbn"] == data["isbn"]
    assert content["title"] == data["title"]
    assert "summary" in content

def test_get_book(client: TestClient, db: Session):
    # First create a book to get
    data = {
        "isbn": "978-1491904244",
        "title": "Grokking Algorithms",
        "author": "Aditya Bhargava",
        "publisher": "Manning",
        "publish_year": 2016,
        "category": "Algorithms",
        "total_stock": 5,
        "available_stock": 5,
        "location": "A-1-2",
    }
    client.post(f"{settings.API_V1_STR}/books/", json=data)

    response = client.get(f"{settings.API_V1_STR}/books/{data['isbn']}")
    assert response.status_code == 200
    content = response.json()
    assert content["isbn"] == data["isbn"]
    assert content["title"] == data["title"]

def test_search_books(client: TestClient, db: Session):
    response = client.get(f"{settings.API_V1_STR}/books/?q=Grokking")
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) > 0
    assert content[0]["title"] == "Grokking Algorithms"
