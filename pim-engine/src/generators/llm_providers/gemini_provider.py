"""Gemini CLI provider with proxy support"""

import subprocess
import os
import logging
from typing import List, Dict, Any, Optional

from . import LLMProvider
from config.llm_config import LLM_TIMEOUT_SECONDS, PROXY_HOST, PROXY_PORT

logger = logging.getLogger(__name__)


class GeminiCLIProvider(LLMProvider):
    """Gemini CLI provider for code generation with proxy support"""
    
    def __init__(self):
        self.cli_path = "gemini"
        # 设置代理环境变量
        self._setup_proxy()
        
    def _setup_proxy(self):
        """Setup proxy for Gemini CLI"""
        # Docker 容器访问主机的几种方式：
        # 1. host.docker.internal (Docker Desktop)
        # 2. 172.17.0.1 (Linux Docker 默认网桥)
        # 3. 通过环境变量传入的主机 IP
        
        proxy_host = PROXY_HOST
        proxy_port = PROXY_PORT
        
        # 构建代理 URL
        proxy_url = f"http://{proxy_host}:{proxy_port}"
        
        # 设置代理环境变量
        os.environ['HTTP_PROXY'] = proxy_url
        os.environ['HTTPS_PROXY'] = proxy_url
        os.environ['http_proxy'] = proxy_url
        os.environ['https_proxy'] = proxy_url
        
        # 不代理本地地址
        os.environ['NO_PROXY'] = 'localhost,127.0.0.1,*.local'
        os.environ['no_proxy'] = 'localhost,127.0.0.1,*.local'
        
    async def is_available(self) -> bool:
        """Check if Gemini CLI is installed and API key is set"""
        # 检查 API key
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_STUDIO_KEY')
        if not api_key:
            return False
            
        # 检查 CLI 是否安装
        try:
            result = subprocess.run(
                [self.cli_path, "--version"],
                capture_output=True,
                text=True,
                env=os.environ.copy()  # 包含代理设置
            )
            return result.returncode == 0
        except:
            return False
    
    async def generate_code(
        self,
        context: str,
        prompt: str,
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Generate code using Gemini CLI"""
        
        # 确保 API key 设置
        api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_AI_STUDIO_KEY')
        if not api_key:
            raise Exception("GEMINI_API_KEY not set")
        
        # Build the full prompt
        full_prompt = self._build_prompt(context, prompt, constraints, examples)
        
        # 准备环境变量
        env = os.environ.copy()
        env['GEMINI_API_KEY'] = api_key
        # 确保代理设置被传递（同时支持大写和小写）
        for proxy_var in ['http_proxy', 'HTTP_PROXY', 'https_proxy', 'HTTPS_PROXY', 'no_proxy', 'NO_PROXY']:
            if proxy_var in os.environ:
                env[proxy_var] = os.environ[proxy_var]
                # 确保小写版本也设置
                env[proxy_var.lower()] = os.environ[proxy_var]
        
        # Call Gemini CLI with prompt flag
        # Gemini CLI 使用环境变量而不是命令行参数
        cmd = [
            self.cli_path,
            '-p', full_prompt  # 使用 -p 参数直接传递 prompt
        ]
        
        # Debug: 打印环境变量
        print(f"[DEBUG] Calling Gemini CLI with proxy settings:")
        for key in ['https_proxy', 'HTTPS_PROXY', 'http_proxy', 'HTTP_PROXY']:
            if key in env:
                print(f"[DEBUG]   {key}={env[key]}")
            else:
                print(f"[DEBUG]   {key}=NOT SET")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=LLM_TIMEOUT_SECONDS,  # 从配置读取超时时间
            env=env
        )
        
        if result.returncode == 0:
            return self._extract_code(result.stdout)
        else:
            raise Exception(f"Gemini CLI error: {result.stderr}")
    
    def _build_prompt(
        self,
        context: str,
        prompt: str,
        constraints: Optional[List[str]] = None,
        examples: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build a structured prompt for Gemini"""
        
        parts = [
            "You are an expert software engineer. Generate production-ready code based on the following requirements.\n",
            "# Code Generation Request\n",
            "## Context\n",
            context,
            "\n## Task\n",
            prompt,
        ]
        
        if constraints:
            parts.extend([
                "\n## Constraints\n",
                "\n".join(f"- {c}" for c in constraints)
            ])
            
        if examples:
            parts.append("\n## Examples\n")
            for example in examples:
                parts.extend([
                    f"\n### {example.get('title', 'Example')}\n",
                    f"Input:\n```\n{example.get('input', '')}\n```\n",
                    f"Output:\n```python\n{example.get('output', '')}\n```\n"
                ])
        
        parts.extend([
            "\n## Instructions\n",
            "1. Generate complete, working code - no placeholders or TODOs",
            "2. Include all necessary imports",
            "3. Add proper error handling and validation",
            "4. Follow best practices for the target framework",
            "5. Include docstrings and type hints",
            "6. Return only the code without any explanation"
        ])
        
        return "\n".join(parts)
    
    def _extract_code(self, response: str) -> str:
        """Extract code from Gemini response"""
        # Gemini might return code in markdown blocks
        lines = response.split('\n')
        in_code_block = False
        code_lines = []
        
        for line in lines:
            if line.strip().startswith('```'):
                if in_code_block:
                    # End of code block
                    break
                else:
                    # Start of code block
                    in_code_block = True
                continue
            if in_code_block:
                code_lines.append(line)
        
        # If no code blocks found, assume entire response is code
        if not code_lines:
            # Filter out obvious non-code lines
            for line in lines:
                if not line.strip().startswith(('#', '//', '/*', 'Here', 'This', 'The')):
                    code_lines.append(line)
        
        return '\n'.join(code_lines).strip()