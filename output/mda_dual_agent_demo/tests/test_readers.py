
import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

def test_register_reader(client):
    response = client.post("/readers/", json={
        "name": "张三",
        "id_card": "440106199901011234",
        "phone": "13800138000",
        "reader_type": "学生"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "张三"
