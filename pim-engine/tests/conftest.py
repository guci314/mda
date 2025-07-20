"""Pytest configuration for Gemini CLI tests"""

import pytest
import os


def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


@pytest.fixture(scope="session")
def gemini_api_key():
    """Fixture to provide Gemini API key"""
    api_key = os.environ.get('GOOGLE_AI_STUDIO_KEY') or os.environ.get('GEMINI_API_KEY')
    if not api_key:
        pytest.skip("No Gemini API key found in environment")
    return api_key


@pytest.fixture(scope="session")
def proxy_config():
    """Fixture to provide proxy configuration"""
    return {
        'host': os.environ.get('PROXY_HOST', 'host.docker.internal'),
        'port': os.environ.get('PROXY_PORT', '7890'),
        'url': f"http://{os.environ.get('PROXY_HOST', 'host.docker.internal')}:{os.environ.get('PROXY_PORT', '7890')}"
    }