import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_reserve_book():
    response = client.post("/api/reserve/", json={"reader_id": "1", "isbn": "1234567890"})
    assert response.status_code == 200
    assert response.json()["status"] == "PENDING"