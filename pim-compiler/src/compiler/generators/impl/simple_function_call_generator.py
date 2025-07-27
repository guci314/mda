"""
Simple Function Call 代码生成器实现
使用 LLM 的原生函数调用能力进行代码生成
"""

import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, List, Any
import logging
from datetime import datetime

from openai import OpenAI
from pydantic import BaseModel, Field

from ..base_generator import BaseGenerator, GeneratorConfig, GenerationResult


class SimpleFunctionCallGenerator(BaseGenerator):
    """Simple Function Call Agent 代码生成器
    
    使用 OpenAI 兼容的函数调用 API 进行智能代码生成
    """
    
    def setup(self):
        """初始化设置"""
        # 设置 LLM 配置
        api_key = self.config.api_key or os.getenv("DEEPSEEK_API_KEY")
        api_base = self.config.api_base or os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        model = self.config.model or "deepseek-chat"
        
        if not api_key:
            raise ValueError("API key not provided. Set DEEPSEEK_API_KEY or provide in config")
        
        # 创建 OpenAI 兼容客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )
        self.model = model
        self.temperature = self.config.temperature or 0.7
        
        # 定义可用的工具（使用 tools API）
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "写入文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "文件内容"
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            }
        ]
        
        self.logger.info(f"Initialized Simple Function Call Agent with model: {model}")
    
    def generate_psm(
        self, 
        pim_content: str, 
        platform: str = "fastapi",
        output_dir: Optional[Path] = None
    ) -> GenerationResult:
        """从 PIM 生成 PSM"""
        start_time = time.time()
        
        if output_dir is None:
            output_dir = Path.cwd()
        
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 构建系统提示
        system_prompt = f"""你是一个专业的软件架构师，负责将 PIM（Platform Independent Model）转换为 PSM（Platform Specific Model）。

目标平台: {platform}
框架: {self._get_framework_for_platform(platform)}
ORM: {self._get_orm_for_platform(platform)}
验证库: {self._get_validation_lib_for_platform(platform)}

请生成完整的 PSM 文档，包括：
1. 文档标题和概述
2. 数据模型定义（包含字段类型、约束等）
3. API 端点设计（RESTful）
4. 服务层方法定义
5. 业务规则说明

使用 write_file 函数将完整的 PSM 保存到 psm.md 文件。"""

        # 用户消息
        user_message = f"""请根据以下 PIM 生成对应的 PSM：

```markdown
{pim_content}
```"""

        try:
            # 调用 LLM 生成 PSM
            self.logger.info("Calling LLM to generate PSM...")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # 执行函数调用
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=self.temperature,
                max_tokens=8000
            )
            
            message = response.choices[0].message
            
            # 检查是否有工具调用
            if hasattr(message, 'tool_calls') and message.tool_calls:
                for tool_call in message.tool_calls:
                    if tool_call.function.name == "write_file":
                        function_args = json.loads(tool_call.function.arguments)
                        if function_args.get("path", "").endswith("psm.md"):
                            # 写入文件
                            psm_path = output_dir / function_args["path"]
                            psm_path.parent.mkdir(parents=True, exist_ok=True)
                            psm_path.write_text(function_args["content"], encoding='utf-8')
                            
                            return GenerationResult(
                                success=True,
                                output_path=output_dir,
                                psm_content=function_args["content"],
                                generation_time=time.time() - start_time,
                                logs="PSM generated successfully"
                            )
            
            # 如果没有工具调用，尝试从消息内容提取
            if message.content:
                # 保存为 PSM 文件
                psm_path = output_dir / "psm.md"
                psm_path.write_text(message.content, encoding='utf-8')
                
                return GenerationResult(
                    success=True,
                    output_path=output_dir,
                    psm_content=message.content,
                    generation_time=time.time() - start_time,
                    logs="PSM generated from message content"
                )
            
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message="No PSM content generated",
                generation_time=time.time() - start_time
            )
                
        except Exception as e:
            self.logger.error(f"Failed to generate PSM: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def generate_code(
        self, 
        psm_content: str, 
        output_dir: Path,
        platform: str = "fastapi"
    ) -> GenerationResult:
        """从 PSM 生成代码"""
        start_time = time.time()
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 简化方法：让 LLM 返回一个 JSON 格式的文件列表
        system_prompt = f"""你是一个专业的 {platform} 开发专家，负责根据 PSM（Platform Specific Model）生成完整的应用代码。

要求：
1. 生成完整的、可直接运行的应用
2. 包含所有必要的文件和目录结构
3. 使用类型注解和适当的错误处理
4. 每个 Python 包都必须包含 __init__.py 文件
5. 生成 requirements.txt 和 README.md

请生成一个包含所有文件的 JSON 列表，格式如下：
{{
  "files": [
    {{
      "path": "requirements.txt",
      "content": "文件内容..."
    }},
    {{
      "path": "src/__init__.py", 
      "content": ""
    }},
    ...
  ]
}}"""

        user_message = f"""请根据以下 PSM 生成完整的 {platform} 应用代码：

```markdown
{psm_content}
```

返回包含所有文件的 JSON 格式。"""

        try:
            # 调用 LLM 生成代码
            self.logger.info("Calling LLM to generate code...")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=self.temperature,
                max_tokens=16000,
                response_format={"type": "json_object"}
            )
            
            message = response.choices[0].message
            
            if message.content:
                try:
                    # 解析 JSON 响应
                    result = json.loads(message.content)
                    files = result.get("files", [])
                    
                    code_files = {}
                    for file_info in files:
                        file_path = file_info.get("path", "")
                        file_content = file_info.get("content", "")
                        
                        # 写入文件
                        full_path = output_dir / file_path
                        full_path.parent.mkdir(parents=True, exist_ok=True)
                        full_path.write_text(file_content, encoding='utf-8')
                        
                        code_files[file_path] = file_content
                    
                    if code_files:
                        return GenerationResult(
                            success=True,
                            output_path=output_dir,
                            code_files=code_files,
                            generation_time=time.time() - start_time,
                            logs=f"Generated {len(code_files)} files"
                        )
                    
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse JSON response")
            
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message="Failed to generate code files",
                generation_time=time.time() - start_time
            )
            
        except Exception as e:
            self.logger.error(f"Failed to generate code: {e}")
            return GenerationResult(
                success=False,
                output_path=output_dir,
                error_message=str(e),
                generation_time=time.time() - start_time
            )
    
    def _get_framework_for_platform(self, platform: str) -> str:
        """获取平台对应的框架"""
        frameworks = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "springboot": "Spring Boot",
            "express": "Express.js",
            "gin": "Gin"
        }
        return frameworks.get(platform, "FastAPI")
    
    def _get_orm_for_platform(self, platform: str) -> str:
        """获取平台对应的 ORM"""
        orms = {
            "fastapi": "SQLAlchemy",
            "flask": "SQLAlchemy",
            "django": "Django ORM",
            "springboot": "JPA/Hibernate",
            "express": "Sequelize",
            "gin": "GORM"
        }
        return orms.get(platform, "SQLAlchemy")
    
    def _get_validation_lib_for_platform(self, platform: str) -> str:
        """获取平台对应的验证库"""
        validators = {
            "fastapi": "Pydantic",
            "flask": "Marshmallow",
            "django": "Django Forms/Serializers",
            "springboot": "Bean Validation",
            "express": "Joi",
            "gin": "go-playground/validator"
        }
        return validators.get(platform, "Pydantic")