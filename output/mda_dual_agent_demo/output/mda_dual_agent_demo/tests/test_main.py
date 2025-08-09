from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_add_book():
    response = client.post("/books/", json={"isbn": "1234567890", "title": "Test Book", "author": "Test Author", "publisher": "Test Publisher", "publish_year": 2023, "category": "Test", "total_quantity": 10, "available_quantity": 10, "location": "Test Location", "status": "在架"})
    assert response.status_code == 200
    assert response.json()["isbn"] == "1234567890"

def test_get_book():
    response = client.get("/books/1234567890")
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"