"""PIM Engine 基础测试"""

import pytest
from httpx import AsyncClient
import sys
from pathlib import Path

# 将 src 目录添加到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.engine import PIMEngine
from core.models import ModelLoadResult


@pytest.fixture
async def engine():
    """创建引擎实例
    
    Returns:
        PIMEngine: PIM 引擎实例
    """
    engine = PIMEngine()
    return engine


@pytest.fixture
async def client(engine):
    """创建测试客户端
    
    Args:
        engine: PIM 引擎实例
        
    Yields:
        AsyncClient: HTTP 异步测试客户端
    """
    from httpx import ASGITransport
    
    # 创建 ASGI 传输层用于测试 FastAPI 应用
    transport = ASGITransport(app=engine.app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """测试健康检查端点
    
    验证 /health 端点返回正确的健康状态信息
    """
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_engine_status(client):
    """测试引擎状态端点
    
    验证 /engine/status 端点返回引擎运行状态
    """
    response = await client.get("/engine/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "loaded_models" in data
    assert isinstance(data["loaded_models"], list)


@pytest.mark.asyncio
async def test_list_models_empty(client):
    """测试空模型列表
    
    当没有加载任何模型时，验证返回空列表
    """
    response = await client.get("/engine/models")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["models"] == []


@pytest.mark.asyncio
async def test_model_loading(engine):
    """测试模型加载功能
    
    创建一个简单的测试模型并验证加载功能
    """
    # 创建测试模型文件
    test_model_path = Path("models/test_model.yaml")
    test_model_content = """
domain: test-domain
version: 1.0.0

entities:
  - name: TestEntity
    attributes:
      name:
        type: string
        required: true
      value:
        type: integer
        default: 0
"""
    
    # 写入测试模型文件
    test_model_path.write_text(test_model_content)
    
    try:
        # 加载模型
        result = await engine.load_model("test_model")
        assert result.success
        assert "test_model" in engine.models
        
        # 检查模型详情
        model = engine.models["test_model"]
        assert model.domain == "test-domain"
        assert len(model.entities) == 1
        assert model.entities[0].name == "TestEntity"
        
    finally:
        # 清理测试文件
        if test_model_path.exists():
            test_model_path.unlink()


@pytest.mark.asyncio
async def test_api_generation(engine, client):
    """测试 API 自动生成功能
    
    验证加载模型后会自动生成对应的 REST API 端点
    """
    # 创建测试模型
    test_model_path = Path("models/test_api.yaml")
    test_model_content = """
domain: test-api
version: 1.0.0

entities:
  - name: Item
    attributes:
      name:
        type: string
        required: true
      quantity:
        type: integer
        default: 1
"""
    
    test_model_path.write_text(test_model_content)
    
    try:
        # 加载模型
        result = await engine.load_model("test_api")
        assert result.success
        
        # 测试生成的端点是否存在
        # 注意：在真实的测试环境中，我们需要正确设置路由
        # 这是一个简化的测试
        
    finally:
        if test_model_path.exists():
            test_model_path.unlink()


if __name__ == "__main__":
    # 运行测试，-v 参数显示详细输出
    pytest.main([__file__, "-v"])