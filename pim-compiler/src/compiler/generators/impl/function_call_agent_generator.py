"""
Function Call Agent 代码生成器实现
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


class FunctionCallAgentGenerator(BaseGenerator):
    """Function Call Agent 代码生成器
    
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
                    "name": "create_directory",
                    "description": "创建目录",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "要创建的目录路径"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_file",
                    "description": "写入文件内容（覆盖现有内容）",
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
            },
            {
                "type": "function",
                "function": {
                    "name": "append_file",
                    "description": "追加内容到文件末尾",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "要追加的内容"
                            }
                        },
                        "required": ["path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "读取文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "文件路径"
                            }
                        },
                        "required": ["path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "list_directory",
                    "description": "列出目录内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "目录路径",
                                "default": "."
                            }
                        }
                    }
                }
            }
        ]
        
        self.logger.info(f"Initialized Function Call Agent with model: {model}")
    
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

你需要分章节生成 PSM 文档。每次只生成一个章节，按以下顺序：

1. 先生成文档标题和概述
2. 然后生成数据模型定义章节
3. 接着生成 API 端点设计章节
4. 然后生成服务层方法定义章节
5. 最后生成业务规则说明章节

每个章节都应该详细完整。使用 write_file 函数将内容追加到 psm.md 文件。"""

        # 用户消息
        user_message = f"""请根据以下 PIM 生成对应的 PSM。先生成文档标题和概述部分：

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
            
            # 执行函数调用循环
            psm_content = ""
            max_rounds = 15
            chapters = [
                "文档标题和概述",
                "数据模型定义",
                "API 端点设计", 
                "服务层方法定义",
                "业务规则说明"
            ]
            current_chapter = 0
            
            for round in range(max_rounds):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=self.temperature
                )
                
                message = response.choices[0].message
                
                # 添加助手消息到历史
                messages.append(message.model_dump())
                
                # 如果有工具调用，执行它
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        self.logger.info(f"Round {round + 1}: {function_name}({function_args.get('path', '')})")
                        
                        # 执行函数
                        function_result = self._execute_function(
                            function_name, 
                            function_args, 
                            output_dir
                        )
                        
                        # 添加工具调用结果到消息历史
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(function_result)
                        })
                        
                        # 如果写入了 PSM 文件，累积内容
                        if (function_name in ["write_file", "append_file"]) and function_args.get("path", "").endswith("psm.md") and function_result.get("success"):
                            psm_content += function_args.get("content", "") + "\n\n"
                            if current_chapter == 0 and function_name == "write_file":
                                # 第一章使用 write_file 创建文件
                                current_chapter += 1
                            elif current_chapter > 0 and function_name == "append_file":
                                # 后续章节使用 append_file 追加
                                current_chapter += 1
                            
                            # 如果还有更多章节，提示生成下一章
                            if current_chapter < len(chapters):
                                messages.append({
                                    "role": "user",
                                    "content": f"很好！现在请生成 '{chapters[current_chapter]}' 章节的内容。使用 append_file 函数追加到 psm.md 文件中。"
                                })
                            else:
                                # 所有章节都生成完毕
                                self.logger.info("All PSM chapters generated successfully")
                                break
                
                # 如果没有函数调用，提示开始生成
                else:
                    if current_chapter == 0:
                        messages.append({
                            "role": "user",
                            "content": "请开始生成 PSM 文档。先使用 write_file 函数创建 psm.md 文件，写入文档标题和概述。"
                        })
                    else:
                        messages.append({
                            "role": "user",
                            "content": f"请继续生成 '{chapters[current_chapter]}' 章节的内容。"
                        })
            
            if psm_content:
                return GenerationResult(
                    success=True,
                    output_path=output_dir,
                    psm_content=psm_content,
                    generation_time=time.time() - start_time,
                    logs=f"PSM generated successfully in {round + 1} rounds"
                )
            else:
                return GenerationResult(
                    success=False,
                    output_path=output_dir,
                    error_message="Failed to generate PSM content",
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
        
        # 构建系统提示
        system_prompt = f"""你是一个专业的 {platform} 开发专家，负责根据 PSM（Platform Specific Model）生成完整的应用代码。

要求：
1. 生成完整的、可直接运行的应用
2. 包含所有必要的文件和目录结构
3. 使用类型注解和适当的错误处理
4. 每个 Python 包都必须包含 __init__.py 文件
5. 生成 requirements.txt 和 README.md

请按以下顺序生成代码：
1. 创建项目目录结构
2. 生成配置文件
3. 生成数据模型
4. 生成数据库配置
5. 生成 Schema/DTO
6. 生成 Repository/DAO
7. 生成 Service 层
8. 生成 API 路由
9. 生成主应用文件
10. 生成依赖文件

使用 create_directory 和 write_file 函数来创建完整的项目结构。"""

        # 用户消息
        user_message = f"""请根据以下 PSM 生成完整的 {platform} 应用代码：

```markdown
{psm_content}
```"""

        try:
            # 调用 LLM 生成代码
            self.logger.info("Calling LLM to generate code...")
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # 收集生成的文件
            code_files = {}
            max_rounds = 50  # 生成代码需要更多轮次
            
            for round in range(max_rounds):
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.tools,
                    tool_choice="auto",
                    temperature=self.temperature
                )
                
                message = response.choices[0].message
                
                # 添加助手消息到历史
                messages.append(message.model_dump())
                
                # 如果有工具调用，执行它
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    for tool_call in message.tool_calls:
                        function_name = tool_call.function.name
                        function_args = json.loads(tool_call.function.arguments)
                        
                        self.logger.info(f"Round {round + 1}: {function_name}({function_args.get('path', '')})")
                        
                        # 执行函数
                        function_result = self._execute_function(
                            function_name, 
                            function_args, 
                            output_dir
                        )
                        
                        # 添加工具调用结果到消息历史
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(function_result)
                        })
                        
                        # 如果是写入文件，记录到 code_files
                        if function_name == "write_file" and function_result.get("success"):
                            file_path = function_args.get("path", "")
                            code_files[file_path] = function_args.get("content", "")
                
                # 如果没有函数调用，可能已经完成
                else:
                    # 检查是否已经生成了基本文件
                    if len(code_files) > 10:  # 至少生成了10个文件
                        self.logger.info(f"Code generation completed after {round + 1} rounds")
                        break
                    else:
                        # 提示继续生成
                        messages.append({
                            "role": "user",
                            "content": "请继续生成剩余的代码文件。确保包含所有必要的模块、服务、API路由和配置文件。"
                        })
            
            if code_files:
                return GenerationResult(
                    success=True,
                    output_path=output_dir,
                    code_files=code_files,
                    generation_time=time.time() - start_time,
                    logs=f"Generated {len(code_files)} files in {round + 1} rounds"
                )
            else:
                return GenerationResult(
                    success=False,
                    output_path=output_dir,
                    error_message="No code files generated",
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
    
    def _execute_function(self, function_name: str, args: Dict[str, Any], base_dir: Path) -> Dict[str, Any]:
        """执行函数调用"""
        try:
            if function_name == "create_directory":
                path = base_dir / args["path"]
                path.mkdir(parents=True, exist_ok=True)
                return {"success": True, "message": f"Directory created: {args['path']}"}
            
            elif function_name == "write_file":
                path = base_dir / args["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(args["content"], encoding='utf-8')
                return {"success": True, "message": f"File written: {args['path']}"}
            
            elif function_name == "append_file":
                path = base_dir / args["path"]
                path.parent.mkdir(parents=True, exist_ok=True)
                if path.exists():
                    current_content = path.read_text(encoding='utf-8')
                    path.write_text(current_content + "\n\n" + args["content"], encoding='utf-8')
                else:
                    path.write_text(args["content"], encoding='utf-8')
                return {"success": True, "message": f"Content appended to: {args['path']}"}
            
            elif function_name == "read_file":
                path = base_dir / args["path"]
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    return {"success": True, "content": content}
                else:
                    return {"success": False, "error": f"File not found: {args['path']}"}
            
            elif function_name == "list_directory":
                path = base_dir / args.get("path", ".")
                if path.exists():
                    items = []
                    for item in sorted(path.iterdir()):
                        if item.is_file():
                            items.append(f"📄 {item.name}")
                        else:
                            items.append(f"📁 {item.name}/")
                    return {"success": True, "items": items}
                else:
                    return {"success": False, "error": f"Directory not found: {args.get('path', '.')}"}
            
            else:
                return {"success": False, "error": f"Unknown function: {function_name}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
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