"""
简单测试用例，验证基本功能
"""
import pytest
from httpx import AsyncClient


class TestSimpleAPI:
    """简单API测试"""
    
    async def test_root_endpoint(self, client: AsyncClient):
        """测试根端点"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "图书借阅系统" in data["message"]
    
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查端点"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    async def test_create_book(self, client: AsyncClient, sample_book_data):
        """测试创建图书"""
        response = await client.post("/books/", json=sample_book_data)
        assert response.status_code == 201
        data = response.json()
        assert data["isbn"] == sample_book_data["isbn"]
        assert data["title"] == sample_book_data["title"]
    
    async def test_create_reader(self, client: AsyncClient, sample_reader_data):
        """测试创建读者"""
        response = await client.post("/readers/", json=sample_reader_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_reader_data["name"]
        assert data["id_card"] == sample_reader_data["id_card"]
    
    async def test_get_books_list(self, client: AsyncClient, created_book):
        """测试获取图书列表"""
        response = await client.get("/books/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["isbn"] == created_book["isbn"]
    
    async def test_get_readers_list(self, client: AsyncClient, created_reader):
        """测试获取读者列表"""
        response = await client.get("/readers/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["reader_id"] == created_reader["reader_id"]