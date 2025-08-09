import pytest
from fastapi.testclient import TestClient


def test_add_book(client):
    """测试添加图书"""
    response = client.post("/books/", json={
        "isbn": "9787532767406",
        "title": "解忧杂货店",
        "author": "[日] 东野圭吾",
        "publisher": "南海出版公司",
        "publish_year": 2014,
        "category": "小说",
        "total_quantity": 10,
        "available_quantity": 10,
        "location": "A-1-1"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "解忧杂货店"


def test_add_duplicate_book(client):
    """测试添加重复图书"""
    # 第一次添加
    response = client.post("/books/", json={
        "isbn": "9787532767407",
        "title": "白夜行",
        "author": "[日] 东野圭吾",
        "publisher": "南海出版公司",
        "publish_year": 2013,
        "category": "小说",
        "total_quantity": 5,
        "available_quantity": 5,
        "location": "A-1-2"
    })
    assert response.status_code == 200
    
    # 尝试添加相同ISBN的书
    response = client.post("/books/", json={
        "isbn": "9787532767407",
        "title": "白夜行",
        "author": "[日] 东野圭吾",
        "publisher": "南海出版公司",
        "publish_year": 2013,
        "category": "小说",
        "total_quantity": 5,
        "available_quantity": 5,
        "location": "A-1-2"
    })
    assert response.status_code == 400