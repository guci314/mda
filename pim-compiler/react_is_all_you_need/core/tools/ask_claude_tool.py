#!/usr/bin/env python3
"""
Ask Claude Tool - 通过OpenRouter API直接调用Claude
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from tool_base import Function
import json
import requests


class AskClaude(Function):
    """直接调用Claude获取高质量回答"""

    def __init__(self, work_dir):
        super().__init__(
            name="ask_claude",
            description="调用Claude获取高质量回答（通过OpenRouter API）",
            parameters={
                "question": {
                    "type": "string",
                    "description": "要问Claude的问题"
                },
                "model": {
                    "type": "string",
                    "description": "使用的模型，默认claude-sonnet-4",
                    "default": "anthropic/claude-sonnet-4"
                }
            }
        )
        self.work_dir = Path(work_dir)

    def execute(self, **kwargs) -> str:
        question = kwargs["question"]
        model = kwargs.get("model", "anthropic/claude-sonnet-4")

        # 尝试从环境变量获取API密钥
        api_key = os.getenv("OPENROUTER_API_KEY")

        # 如果环境变量没有，尝试从.env文件读取
        if not api_key:
            env_file = self.work_dir / ".env"
            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith("OPENROUTER_API_KEY="):
                            api_key = line.split("=", 1)[1].strip()
                            break

        if not api_key:
            return "❌ 未找到OPENROUTER_API_KEY（检查环境变量或.env文件）"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Agent System"
        }

        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": question}
            ],
            "temperature": 0,
            "max_tokens": 4000
        }

        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
            else:
                # 返回错误信息但不中断
                error_msg = f"API错误({response.status_code})"
                try:
                    error_detail = response.json()
                    if "error" in error_detail:
                        error_msg += f": {error_detail['error'].get('message', '')}"
                except:
                    pass
                return f"❌ {error_msg}"

        except requests.exceptions.Timeout:
            return "❌ 请求超时（30秒）- Claude可能正忙"
        except Exception as e:
            return f"❌ 请求失败: {str(e)}"