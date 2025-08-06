"""
LLM模板匹配器

使用LLM进行语义理解和模板匹配。
"""

import json
import os
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from .template_manager import MatchResult, TaskTemplate


class LLMTemplateMatcher:
    """基于LLM的模板匹配器"""
    
    def __init__(self,
                 llm_model: str = "gemini-2.0-flash-exp",
                 llm_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/",
                 llm_api_key_env: str = "GEMINI_API_KEY",
                 temperature: float = 0,
                 use_proxy: bool = True):
        """初始化LLM匹配器"""
        # 配置httpx客户端
        http_client = None
        if use_proxy:
            try:
                import httpx
                http_client = httpx.Client(
                    proxy='socks5://127.0.0.1:7890',
                    timeout=30,
                    verify=False
                )
            except ImportError:
                print("警告: httpx未安装，无法使用代理")
        
        self.llm = ChatOpenAI(
            model=llm_model,
            base_url=llm_base_url,
            api_key=os.getenv(llm_api_key_env),
            temperature=temperature,
            http_client=http_client
        )
    
    def match(self, task: str, templates_summary: List[Dict[str, Any]]) -> MatchResult:
        """匹配任务与模板"""
        
        if not templates_summary:
            return MatchResult(
                can_reuse=False,
                reasoning="没有可用的模板"
            )
        
        # 构建prompt
        prompt = self._build_match_prompt(task, templates_summary)
        
        try:
            response = self.llm.invoke([
                SystemMessage(content=prompt['system']),
                HumanMessage(content=prompt['user'])
            ])
            
            # 解析响应
            result = self._parse_response(response.content)
            return result
            
        except Exception as e:
            print(f"LLM匹配错误: {e}")
            return MatchResult(
                can_reuse=False,
                reasoning=f"匹配过程出错: {str(e)}"
            )
    
    def _build_match_prompt(self, task: str, templates: List[Dict[str, Any]]) -> Dict[str, str]:
        """构建匹配提示词"""
        
        # 格式化模板列表
        templates_text = self._format_templates(templates)
        
        system_prompt = """你是一个智能模板匹配器。

你的任务是判断新任务是否可以使用已有的参数化模板。

判断原则：
1. 语义相似性：理解任务的本质，不要被表面表达迷惑
2. 参数可提取性：能否从新任务中提取出模板所需的参数
3. 功能等价性：使用模板能否完全实现新任务的需求

特别注意：
- 支持同义词和近义词（如"显示"="列出"="查看"）
- 支持单位转换（如50m = 50MB = 50兆）
- 支持语序变化（如"大于50m的镜像"="镜像大于50m"）

只输出JSON，不要有其他内容。"""
        
        user_prompt = f"""新任务：{task}

已有模板：
{templates_text}

请分析这个新任务是否可以使用某个已有模板。

输出JSON格式：
{{
    "can_reuse": true/false,
    "template_id": "模板ID（如果可以重用）",
    "extracted_parameters": {{"参数名": "参数值"}},
    "confidence": 0.0-1.0,
    "reasoning": "判断理由"
}}"""
        
        return {
            'system': system_prompt,
            'user': user_prompt
        }
    
    def _format_templates(self, templates: List[Dict[str, Any]]) -> str:
        """格式化模板列表"""
        lines = []
        for i, template in enumerate(templates, 1):
            lines.append(f"{i}. 模板ID: {template['id']}")
            lines.append(f"   模式: {template['pattern']}")
            lines.append(f"   参数: {template['parameters']}")
            if template.get('examples'):
                lines.append(f"   示例: {', '.join(template['examples'][:2])}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _parse_response(self, content: str) -> MatchResult:
        """解析LLM响应"""
        try:
            # 提取JSON部分
            content = content.strip()
            if '```json' in content:
                content = content.split('```json')[1].split('```')[0].strip()
            elif '```' in content:
                content = content.split('```')[1].split('```')[0].strip()
            
            # 解析JSON
            data = json.loads(content)
            
            return MatchResult(
                can_reuse=data.get('can_reuse', False),
                template_id=data.get('template_id'),
                extracted_parameters=data.get('extracted_parameters', {}),
                confidence=float(data.get('confidence', 0.0)),
                reasoning=data.get('reasoning', '')
            )
            
        except Exception as e:
            print(f"解析LLM响应失败: {e}")
            print(f"原始响应: {content}")
            
            return MatchResult(
                can_reuse=False,
                reasoning=f"无法解析匹配结果: {str(e)}"
            )