from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.config import settings
from datetime import date, timedelta

def test_register_reader(client: TestClient, db: Session):
    valid_until = (date.today() + timedelta(days=365)).isoformat()
    response = client.post(
        f"{settings.API_V1_STR}/readers/",
        json={
            "reader_id": "TEST001",
            "name": "John Doe",
            "id_card_number": "123456789012345678",
            "phone_number": "1234567890",
            "email": "john.doe@example.com",
            "reader_type": "学生",
            "valid_until": valid_until
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reader_id"] == "TEST001"
    assert data["name"] == "John Doe"
    assert data["status"] == "正常"

def test_get_reader(client: TestClient, db: Session):
    # First, register a reader
    valid_until = (date.today() + timedelta(days=365)).isoformat()
    reg_response = client.post(
        f"{settings.API_V1_STR}/readers/",
        json={
            "reader_id": "TEST_GET_001",
            "name": "John Doe",
            "id_card_number": "111111111111111111",
            "phone_number": "1234567890",
            "email": "john.doe.get@example.com",
            "reader_type": "学生",
            "valid_until": valid_until
        },
    )
    assert reg_response.status_code == 201
    reader_id = reg_response.json()["reader_id"]

    response = client.get(f"{settings.API_V1_STR}/readers/{reader_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["reader_id"] == reader_id

def test_freeze_reader(client: TestClient, db: Session):
    # First, register a reader
    valid_until = (date.today() + timedelta(days=365)).isoformat()
    reg_response = client.post(
        f"{settings.API_V1_STR}/readers/",
        json={
            "reader_id": "TEST_FREEZE_001",
            "name": "John Doe",
            "id_card_number": "222222222222222222",
            "phone_number": "1234567890",
            "email": "john.doe.freeze@example.com",
            "reader_type": "学生",
            "valid_until": valid_until
        },
    )
    assert reg_response.status_code == 201
    reader_id = reg_response.json()["reader_id"]

    response = client.post(f"{settings.API_V1_STR}/readers/{reader_id}/freeze")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "冻结"

def test_unfreeze_reader(client: TestClient, db: Session):
    # First, register a reader and freeze it
    valid_until = (date.today() + timedelta(days=365)).isoformat()
    reg_response = client.post(
        f"{settings.API_V1_STR}/readers/",
        json={
            "reader_id": "TEST_UNFREEZE_001",
            "name": "John Doe",
            "id_card_number": "333333333333333333",
            "phone_number": "1234567890",
            "email": "john.doe.unfreeze@example.com",
            "reader_type": "学生",
            "valid_until": valid_until
        },
    )
    assert reg_response.status_code == 201
    reader_id = reg_response.json()["reader_id"]
    
    freeze_response = client.post(f"{settings.API_V1_STR}/readers/{reader_id}/freeze")
    assert freeze_response.status_code == 200

    response = client.post(f"{settings.API_V1_STR}/readers/{reader_id}/unfreeze")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "正常"
