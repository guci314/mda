import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.pydantic import BookCreate

client = TestClient(app)

@pytest.mark.asyncio
async def test_add_book():
    book_data = BookCreate(
        isbn="1234567890",
        title="Test Book",
        author="Test Author",
        publisher="Test Publisher",
        publish_year=2023,
        category="Test",
        total_quantity=5,
        available_quantity=5,
        location="A1"
    )
    response = client.post("/books/", json=book_data.dict())
    assert response.status_code == 200
    assert response.json()["title"] == "Test Book"

@pytest.mark.asyncio
async def test_get_book():
    response = client.get("/books/1234567890")
    assert response.status_code == 200
    assert response.json()["isbn"] == "1234567890"

@pytest.mark.asyncio
async def test_update_book():
    book_data = BookCreate(
        isbn="1234567890",
        title="Updated Book",
        author="Test Author",
        publisher="Test Publisher",
        publish_year=2023,
        category="Test",
        total_quantity=5,
        available_quantity=5,
        location="A1"
    )
    response = client.put("/books/1234567890", json=book_data.dict())
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Book"

@pytest.mark.asyncio
async def test_remove_book():
    response = client.delete("/books/1234567890")
    assert response.status_code == 200
    assert response.json()["message"] == "Book removed successfully"