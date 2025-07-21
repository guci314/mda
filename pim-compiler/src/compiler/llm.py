"""
LLM 客户端接口和实现
"""
import os
import json
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import requests

from utils.logger import get_logger

logger = get_logger(__name__)


class LLMClient(ABC):
    """LLM 客户端基类"""
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> Optional[str]:
        """生成文本补全"""
        pass


class DeepSeekClient(LLMClient):
    """DeepSeek 客户端实现"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        if not self.api_key:
            raise ValueError("DeepSeek API key is required")
        
        self.base_url = "https://api.deepseek.com/v1"
        self.model = "deepseek-chat"
        
        # 检查是否使用代理
        self.proxies = None
        proxy_host = os.getenv("PROXY_HOST")
        proxy_port = os.getenv("PROXY_PORT")
        if proxy_host and proxy_port:
            proxy_url = f"http://{proxy_host}:{proxy_port}"
            self.proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            logger.info(f"Using proxy: {proxy_url}")
    
    def complete(self, prompt: str, **kwargs) -> Optional[str]:
        """生成文本补全"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                proxies=self.proxies,
                timeout=120  # 增加到2分钟超时
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"DeepSeek API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"DeepSeek client error: {e}")
            return None


class OpenAIClient(LLMClient):
    """OpenAI 客户端实现"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.base_url = "https://api.openai.com/v1"
        self.model = "gpt-4"
        
        # 检查是否使用代理
        self.proxies = None
        proxy_host = os.getenv("PROXY_HOST")
        proxy_port = os.getenv("PROXY_PORT")
        if proxy_host and proxy_port:
            proxy_url = f"http://{proxy_host}:{proxy_port}"
            self.proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
    
    def complete(self, prompt: str, **kwargs) -> Optional[str]:
        """生成文本补全"""
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 4000)
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                proxies=self.proxies,
                timeout=120  # 增加到2分钟超时
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI client error: {e}")
            return None