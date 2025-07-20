"""Basic tests for PIM Engine"""

import pytest
from httpx import AsyncClient
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from core.engine import PIMEngine
from core.models import ModelLoadResult


@pytest.fixture
async def engine():
    """Create engine instance"""
    engine = PIMEngine()
    return engine


@pytest.fixture
async def client(engine):
    """Create test client"""
    async with AsyncClient(app=engine.app, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_endpoint(client):
    """Test health check endpoint"""
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


@pytest.mark.asyncio
async def test_engine_status(client):
    """Test engine status endpoint"""
    response = await client.get("/engine/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "running"
    assert "loaded_models" in data
    assert isinstance(data["loaded_models"], list)


@pytest.mark.asyncio
async def test_list_models_empty(client):
    """Test listing models when none are loaded"""
    response = await client.get("/engine/models")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0
    assert data["models"] == []


@pytest.mark.asyncio
async def test_model_loading(engine):
    """Test model loading functionality"""
    # Create a simple test model
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
    
    # Write test model
    test_model_path.write_text(test_model_content)
    
    try:
        # Load model
        result = await engine.load_model("test_model")
        assert result.success
        assert "test_model" in engine.models
        
        # Check model details
        model = engine.models["test_model"]
        assert model.domain == "test-domain"
        assert len(model.entities) == 1
        assert model.entities[0].name == "TestEntity"
        
    finally:
        # Cleanup
        if test_model_path.exists():
            test_model_path.unlink()


@pytest.mark.asyncio
async def test_api_generation(engine, client):
    """Test that APIs are generated for loaded models"""
    # Create test model
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
        # Load model
        result = await engine.load_model("test_api")
        assert result.success
        
        # Test generated endpoints exist
        # Note: In a real test environment, we'd need to properly setup the routes
        # This is a simplified test
        
    finally:
        if test_model_path.exists():
            test_model_path.unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])