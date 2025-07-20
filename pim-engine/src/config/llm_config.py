"""LLM Configuration Settings"""

import os
from typing import Optional

# LLM Timeout Settings
LLM_TIMEOUT_SECONDS = int(os.environ.get('LLM_TIMEOUT_SECONDS', '1200'))  # 默认 20 分钟
LLM_GENERATION_TIMEOUT = LLM_TIMEOUT_SECONDS

# API Request Timeout
API_REQUEST_TIMEOUT = LLM_TIMEOUT_SECONDS + 60  # API 超时比 LLM 超时多 1 分钟

# LLM Provider Settings
DEFAULT_LLM_PROVIDER = os.environ.get('LLM_PROVIDER', 'auto')
USE_LLM_FOR_ALL = os.environ.get('USE_LLM_FOR_ALL', 'false').lower() == 'true'

# Gemini Settings
GEMINI_API_KEY = os.environ.get('GOOGLE_AI_STUDIO_KEY') or os.environ.get('GEMINI_API_KEY')
GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-pro')

# Anthropic Settings
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY')
ANTHROPIC_MODEL = os.environ.get('ANTHROPIC_MODEL', 'claude-3-sonnet-20240229')

# Local LLM Settings
LOCAL_LLM_URL = os.environ.get('LOCAL_LLM_URL', 'http://localhost:11434')
LOCAL_LLM_MODEL = os.environ.get('LOCAL_LLM_MODEL', 'codellama:13b')

# Proxy Settings
PROXY_HOST = os.environ.get('PROXY_HOST', 'host.docker.internal')
PROXY_PORT = os.environ.get('PROXY_PORT', '7890')
PROXY_URL = f"http://{PROXY_HOST}:{PROXY_PORT}"

# LLM Generation Parameters
LLM_TEMPERATURE = float(os.environ.get('LLM_TEMPERATURE', '0.2'))
LLM_MAX_TOKENS = int(os.environ.get('LLM_MAX_TOKENS', '4000'))


def get_llm_config() -> dict:
    """Get complete LLM configuration"""
    return {
        'timeout': LLM_TIMEOUT_SECONDS,
        'provider': DEFAULT_LLM_PROVIDER,
        'use_llm_for_all': USE_LLM_FOR_ALL,
        'temperature': LLM_TEMPERATURE,
        'max_tokens': LLM_MAX_TOKENS,
        'proxy': {
            'host': PROXY_HOST,
            'port': PROXY_PORT,
            'url': PROXY_URL
        },
        'providers': {
            'gemini': {
                'api_key': GEMINI_API_KEY,
                'model': GEMINI_MODEL
            },
            'anthropic': {
                'api_key': ANTHROPIC_API_KEY,
                'model': ANTHROPIC_MODEL
            },
            'local': {
                'url': LOCAL_LLM_URL,
                'model': LOCAL_LLM_MODEL
            }
        }
    }