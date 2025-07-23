from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings
from datetime import date, timedelta

# Helper to create a book and a reader for tests
def setup_borrow_return(client: TestClient):
    # Create a book
    client.post(
        f"{settings.API_V1_STR}/books/",
        json={
            "isbn": "978-1491904244",
            "title": "Fluent Python",
            "author": "Luciano Ramalho",
            "publisher": "O'Reilly Media",
            "publish_year": 2015,
            "category": "Programming",
            "total_stock": 1,
            "available_count": 1,
            "location": "A1-02",
        },
    )
    # Create a reader
    valid_until = (date.today() + timedelta(days=365)).isoformat()
    client.post(
        f"{settings.API_V1_STR}/readers/",
        json={
            "reader_id": "BORROW_TEST001",
            "name": "Jane Doe",
            "id_card_number": "876543210987654321",
            "phone_number": "0987654321",
            "email": "jane.doe@example.com",
            "reader_type": "教师",
            "valid_until": valid_until
        },
    )

def test_borrow_book(client: TestClient, db: Session):
    setup_borrow_return(client)
    response = client.post(
        f"{settings.API_V1_STR}/borrowing/borrow",
        json={"reader_id": "BORROW_TEST001", "isbn": "978-1491904244"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reader_id"] == "BORROW_TEST001"
    assert data["isbn"] == "978-1491904244"
    assert data["status"] == "借阅中"
    
    # Check if book count decreased
    book_resp = client.get(f"{settings.API_V1_STR}/books/978-1491904244")
    assert book_resp.json()["available_count"] == 0

def test_return_book(client: TestClient, db: Session):
    # Create a reader
    valid_until = (date.today() + timedelta(days=365)).isoformat()
    reader_data = {
        "reader_id": "RETURN_TEST001",
        "name": "John Doe",
        "id_card_number": "123456789012345678",
        "phone_number": "1234567890",
        "email": "john.doe@example.com",
        "reader_type": "学生",
        "valid_until": valid_until
    }
    client.post(f"{settings.API_V1_STR}/readers/", json=reader_data)

    # Create a book
    book_data = {
        "isbn": "new_book_for_return", 
        "title": "t", "author":"a", "publisher":"p", 
        "publish_year":2022, "category":"c", 
        "total_stock":1, "available_count":1, "location":"l"
    }
    client.post(f"{settings.API_V1_STR}/books/", json=book_data)

    # Borrow the book
    borrow_resp = client.post(
        f"{settings.API_V1_STR}/borrowing/borrow",
        json={"reader_id": "RETURN_TEST001", "isbn": "new_book_for_return"},
    )
    assert borrow_resp.status_code == 201
    borrow_id = borrow_resp.json()["borrow_id"]

    # Now, return it
    response = client.post(
        f"{settings.API_V1_STR}/borrowing/return",
        json={"borrow_id": borrow_id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["已归还", "已逾期"]
    
    # Check if book count increased
    book_resp = client.get(f"{settings.API_V1_STR}/books/new_book_for_return")
    assert book_resp.json()["available_count"] == 1
