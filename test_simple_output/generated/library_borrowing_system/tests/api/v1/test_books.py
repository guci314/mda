from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings

def test_add_book(client: TestClient, db: Session):
    response = client.post(
        f"{settings.API_V1_STR}/books/",
        json={
            "isbn": "978-0321765723",
            "title": "The C++ Programming Language",
            "author": "Bjarne Stroustrup",
            "publisher": "Addison-Wesley",
            "publish_year": 2013,
            "category": "Programming",
            "total_stock": 10,
            "available_count": 10,
            "location": "A1-01",
            "summary": "The definitive guide to C++."
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["isbn"] == "978-0321765723"
    assert data["title"] == "The C++ Programming Language"
    assert data["status"] == "在架"

def test_get_book(client: TestClient, db: Session):
    # First, add a book
    add_response = client.post(
        f"{settings.API_V1_STR}/books/",
        json={
            "isbn": "978-0321765723",
            "title": "The C++ Programming Language",
            "author": "Bjarne Stroustrup",
            "publisher": "Addison-Wesley",
            "publish_year": 2013,
            "category": "Programming",
            "total_stock": 10,
            "available_count": 10,
            "location": "A1-01",
        },
    )
    assert add_response.status_code == 201
    isbn = add_response.json()["isbn"]

    response = client.get(f"{settings.API_V1_STR}/books/{isbn}")
    assert response.status_code == 200
    data = response.json()
    assert data["isbn"] == isbn

def test_search_book(client: TestClient, db: Session):
    # First, add a book
    add_response = client.post(
        f"{settings.API_V1_STR}/books/",
        json={
            "isbn": "978-0321765723",
            "title": "The C++ Programming Language",
            "author": "Bjarne Stroustrup",
            "publisher": "Addison-Wesley",
            "publish_year": 2013,
            "category": "Programming",
            "total_stock": 10,
            "available_count": 10,
            "location": "A1-01",
        },
    )
    assert add_response.status_code == 201

    response = client.get(f"{settings.API_V1_STR}/books/search/?query=C%2B%2B")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "C++" in data[0]["title"]
