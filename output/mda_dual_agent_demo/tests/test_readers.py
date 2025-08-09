import pytest
from fastapi.testclient import TestClient
from main import app
from app.models.pydantic import ReaderCreate

client = TestClient(app)

@pytest.mark.asyncio
async def test_register_reader():
    reader_data = ReaderCreate(
        name="Test Reader",
        id_card="123456789012345678",
        phone="12345678901",
        reader_type="student"
    )
    response = client.post("/readers/", json=reader_data.dict())
    assert response.status_code == 200
    assert response.json()["name"] == "Test Reader"

@pytest.mark.asyncio
async def test_get_reader():
    response = client.get("/readers/1")
    assert response.status_code == 200
    assert response.json()["reader_id"] == "1"

@pytest.mark.asyncio
async def test_update_reader():
    reader_data = ReaderCreate(
        name="Updated Reader",
        id_card="123456789012345678",
        phone="12345678901",
        reader_type="student"
    )
    response = client.put("/readers/1", json=reader_data.dict())
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Reader"

@pytest.mark.asyncio
async def test_freeze_reader():
    response = client.delete("/readers/1")
    assert response.status_code == 200
    assert response.json()["message"] == "Reader frozen successfully"