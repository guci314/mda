"""LLM Providers for intelligent code generation"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import subprocess
import json
import os


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def generate_code(
        self, 
        context: str, 
        prompt: str,
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate code based on context and prompt"""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if the provider is available"""
        pass


# Import the enhanced Gemini provider
from .gemini_provider import GeminiCLIProvider


class AnthropicAPIProvider(LLMProvider):
    """Anthropic API provider for code generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get('ANTHROPIC_API_KEY')
        
    async def is_available(self) -> bool:
        """Check if API key is configured"""
        return bool(self.api_key)
    
    async def generate_code(
        self,
        context: str,
        prompt: str,
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate code using Anthropic API"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Build the message
            message_content = self._build_prompt(context, prompt, constraints, examples)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4000,
                temperature=0.2,  # Lower temperature for more consistent code
                messages=[{
                    "role": "user",
                    "content": message_content
                }],
                timeout=1200.0  # 20 分钟超时
            )
            
            return self._extract_code(response.content[0].text)
            
        except ImportError:
            raise Exception("anthropic package not installed. Run: pip install anthropic")
        except Exception as e:
            raise Exception(f"Anthropic API error: {str(e)}")
    
    def _build_prompt(
        self,
        context: str,
        prompt: str,
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build prompt for Claude"""
        # Similar to Gemini but adapted for Claude's preferences
        return GeminiCLIProvider._build_prompt(self, context, prompt, constraints, examples)
    
    def _extract_code(self, response: str) -> str:
        """Extract code from Claude response"""
        return GeminiCLIProvider._extract_code(self, response)


class LocalLLMProvider(LLMProvider):
    """Local LLM provider using Ollama or similar"""
    
    def __init__(self, model_name: str = "codellama:13b"):
        self.model_name = model_name
        self.base_url = "http://localhost:11434"  # Default Ollama URL
        
    async def is_available(self) -> bool:
        """Check if local LLM server is running"""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.base_url}/api/tags") as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        models = [m['name'] for m in data.get('models', [])]
                        return self.model_name in models
            return False
        except:
            return False
    
    async def generate_code(
        self,
        context: str,
        prompt: str,
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate code using local LLM"""
        import aiohttp
        
        full_prompt = GeminiCLIProvider._build_prompt(
            self, context, prompt, constraints, examples
        )
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,
                        "top_p": 0.9,
                    }
                }
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return GeminiCLIProvider._extract_code(self, data['response'])
                else:
                    raise Exception(f"Local LLM error: {await resp.text()}")


def get_llm_provider(provider_type: str = "auto") -> LLMProvider:
    """Get the appropriate LLM provider"""
    
    if provider_type == "auto":
        # Try providers in order of preference
        providers = [
            GeminiCLIProvider(),
            AnthropicAPIProvider(),
            LocalLLMProvider()
        ]
        
        for provider in providers:
            import asyncio
            if asyncio.run(provider.is_available()):
                return provider
                
        raise Exception("No LLM provider available")
        
    elif provider_type == "gemini":
        return GeminiCLIProvider()
    elif provider_type == "anthropic":
        return AnthropicAPIProvider()
    elif provider_type == "local":
        return LocalLLMProvider()
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")