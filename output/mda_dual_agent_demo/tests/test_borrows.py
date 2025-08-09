import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_borrow_book():
    response = client.post("/borrows/", json={"reader_id": "1", "isbn": "1234567890"})
    assert response.status_code == 200
    assert response.json()["status"] == "BORROWED"

@pytest.mark.asyncio
async def test_return_book():
    response = client.put("/borrows/1/return")
    assert response.status_code == 200
    assert response.json()["message"] == "Book returned successfully"

@pytest.mark.asyncio
async def test_renew_book():
    response = client.put("/borrows/1/renew")
    assert response.status_code == 200
    assert "due_date" in response.json()