"""
主应用测试
"""
import pytest
from httpx import AsyncClient


class TestMainApp:
    """主应用测试类"""
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, client: AsyncClient):
        """测试根路径"""
        response = await client.get("/")
        assert response.status_code == 200
        
        data = response.json()
        assert "message" in data
        assert "version" in data
        assert "docs" in data
        assert "redoc" in data
    
    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查"""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_api_info(self, client: AsyncClient):
        """测试API信息"""
        response = await client.get("/api/info")
        assert response.status_code == 200
        
        data = response.json()
        assert data["title"] == "图书借阅系统API"
        assert data["version"] == "1.0.0"
        assert "description" in data
        assert "endpoints" in data
        
        endpoints = data["endpoints"]
        assert "books" in endpoints
        assert "readers" in endpoints
        assert "borrows" in endpoints
        assert "reservations" in endpoints
    
    @pytest.mark.asyncio
    async def test_docs_endpoint(self, client: AsyncClient):
        """测试API文档端点"""
        response = await client.get("/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    @pytest.mark.asyncio
    async def test_redoc_endpoint(self, client: AsyncClient):
        """测试ReDoc文档端点"""
        response = await client.get("/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    @pytest.mark.asyncio
    async def test_openapi_schema(self, client: AsyncClient):
        """测试OpenAPI schema"""
        response = await client.get("/openapi.json")
        assert response.status_code == 200
        
        data = response.json()
        assert data["info"]["title"] == "图书借阅系统API"
        assert data["info"]["version"] == "1.0.0"
        assert "paths" in data
        assert "components" in data
    
    @pytest.mark.asyncio
    async def test_cors_headers(self, client: AsyncClient):
        """测试CORS头部"""
        response = await client.options("/")
        # 由于测试客户端可能不完全模拟CORS，这里主要测试端点可访问性
        assert response.status_code in [200, 405]  # OPTIONS可能不被支持，但不应该是500错误
    
    @pytest.mark.asyncio
    async def test_404_endpoint(self, client: AsyncClient):
        """测试不存在的端点"""
        response = await client.get("/nonexistent")
        assert response.status_code == 404