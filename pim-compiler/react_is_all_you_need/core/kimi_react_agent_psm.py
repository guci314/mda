#!/usr/bin/env python3
"""
Kimi React Agent - PSM生成优化版
专门用于处理大型PSM文件生成，解决了原版的append问题和改进版的文件大小限制问题
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
import re

class KimiReactAgentPSM:
    """Kimi React Agent PSM生成优化版"""
    
    def __init__(self, 
                 work_dir: str,
                 model: str = "kimi-k2-turbo-preview",
                 api_key: Optional[str] = None,
                 knowledge_files: Optional[List[str]] = None,
                 interface: str = "",
                 max_rounds: int = 300):
        """
        初始化Kimi Agent PSM版
        
        Args:
            work_dir: 工作目录
            model: 模型名称
            api_key: API密钥
            knowledge_files: 知识文件列表
            interface: Agent接口描述
            max_rounds: 最大执行轮数，默认300（复杂任务需要多次调用）
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = model
        self.api_key = api_key or os.getenv("MOONSHOT_API_KEY")
        if not self.api_key:
            raise ValueError("MOONSHOT_API_KEY not set")
            
        self.base_url = "https://api.moonshot.cn/v1"
        self.knowledge_files = knowledge_files or []
        self.interface = interface
        self.max_rounds = max_rounds
        
        # 加载知识文件
        self.knowledge = self._load_knowledge()
        
        # 定义工具
        self.tools = self._define_tools()
        
        # 用于跟踪大文件写入
        self.large_file_buffer = {}
        
    def _load_knowledge(self) -> str:
        """加载知识文件"""
        knowledge_content = []
        
        for file_path in self.knowledge_files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    knowledge_content.append(f"# 知识文件: {file_path}\n{content}\n")
        
        return "\n".join(knowledge_content)
    
    def _define_tools(self) -> List[Dict]:
        """定义工具列表（OpenAI格式）"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "读取文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            }
                        },
                        "required": ["file_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "write_large_file",
                    "description": """写入大型文件（如PSM文档）。专门用于一次性写入完整的大文件。
                    
特点：
- 支持超大文件（无大小限制）
- 一次性写入，避免分片问题
- 适合PSM、代码文件等结构化文档""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "完整的文件内容"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "create_file_section",
                    "description": """创建文件的一个章节。用于逐步构建大型文档。
                    
使用方法：
1. 第一次调用时设置mode='create'创建新文件
2. 后续调用设置mode='append'追加章节
3. 最后调用设置mode='complete'完成文件""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "section_title": {
                                "type": "string",
                                "description": "章节标题"
                            },
                            "section_content": {
                                "type": "string",
                                "description": "章节内容"
                            },
                            "mode": {
                                "type": "string",
                                "description": "操作模式：create(创建新文件), append(追加章节), complete(完成文件)",
                                "enum": ["create", "append", "complete"]
                            }
                        },
                        "required": ["file_path", "section_content", "mode"]
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
                            "directory_path": {
                                "type": "string",
                                "description": "目录路径（默认为工作目录）"
                            }
                        },
                        "required": []
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "执行Python计算或处理",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "要执行的Python代码"
                            }
                        },
                        "required": ["command"]
                    }
                }
            }
        ]
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """执行工具调用"""
        try:
            if tool_name == "read_file":
                file_path = arguments["file_path"]
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.work_dir, file_path)
                    
                if not os.path.exists(file_path):
                    return f"文件不存在: {file_path}"
                    
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return content
                
            elif tool_name == "write_large_file":
                file_path = arguments["file_path"]
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.work_dir, file_path)
                    
                # 创建目录
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 一次性写入完整文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(arguments["content"])
                
                file_size = len(arguments["content"])
                return f"成功写入大文件: {file_path} ({file_size} 字符)"
                
            elif tool_name == "create_file_section":
                file_path = arguments["file_path"]
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.work_dir, file_path)
                
                mode = arguments["mode"]
                section_content = arguments["section_content"]
                section_title = arguments.get("section_title", "")
                
                # 创建目录
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                if mode == "create":
                    # 创建新文件并写入第一部分
                    self.large_file_buffer[file_path] = []
                    if section_title:
                        self.large_file_buffer[file_path].append(f"# {section_title}\n\n")
                    self.large_file_buffer[file_path].append(section_content)
                    
                    # 立即写入文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("".join(self.large_file_buffer[file_path]))
                    
                    return f"创建文件并写入第一个章节: {file_path}"
                    
                elif mode == "append":
                    # 追加章节
                    if file_path not in self.large_file_buffer:
                        # 如果缓冲区没有，读取现有文件
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                self.large_file_buffer[file_path] = [f.read()]
                        else:
                            self.large_file_buffer[file_path] = []
                    
                    if section_title:
                        self.large_file_buffer[file_path].append(f"\n\n## {section_title}\n\n")
                    self.large_file_buffer[file_path].append(section_content)
                    
                    # 立即更新文件
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write("".join(self.large_file_buffer[file_path]))
                    
                    return f"追加章节到: {file_path}"
                    
                elif mode == "complete":
                    # 完成文件写入
                    if file_path in self.large_file_buffer:
                        # 最终写入
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write("".join(self.large_file_buffer[file_path]))
                        
                        file_size = os.path.getsize(file_path)
                        del self.large_file_buffer[file_path]
                        return f"文件完成: {file_path} ({file_size} 字节)"
                    else:
                        return f"文件已经完成或不存在缓冲: {file_path}"
                
            elif tool_name == "list_directory":
                directory_path = arguments.get("directory_path", ".")
                if not os.path.isabs(directory_path):
                    directory_path = os.path.join(self.work_dir, directory_path)
                    
                if not os.path.exists(directory_path):
                    return f"目录不存在: {directory_path}"
                    
                items = []
                for item in os.listdir(directory_path):
                    item_path = os.path.join(directory_path, item)
                    if os.path.isdir(item_path):
                        items.append(f"[DIR] {item}/")
                    else:
                        size = os.path.getsize(item_path)
                        items.append(f"[FILE] {item} ({size} bytes)")
                
                return "\n".join(items) if items else "目录为空"
                
            elif tool_name == "execute_command":
                command = arguments["command"]
                
                # 创建安全的执行环境
                import math
                import statistics
                
                safe_globals = {
                    "math": math,
                    "statistics": statistics,
                    "sum": sum,
                    "len": len,
                    "max": max,
                    "min": min,
                    "sorted": sorted,
                }
                
                # 执行命令
                result = eval(command, safe_globals)
                return str(result)
                
            else:
                return f"未知工具: {tool_name}"
                
        except Exception as e:
            return f"工具执行失败: {str(e)}"
    
    def execute_task(self, task: str) -> str:
        """执行任务"""
        # 构建系统提示
        system_prompt = f"""你是一个专门用于生成PSM和大型文档的Kimi React Agent。

工作目录：{self.work_dir}

{self.interface}

可用工具：
1. read_file: 读取文件
2. write_large_file: 一次性写入大型文件（推荐用于PSM）
3. create_file_section: 分章节构建大型文档
4. list_directory: 列出目录
5. execute_command: 执行Python计算

{self.knowledge}

重要提示：
1. 对于PSM文件生成，优先使用write_large_file一次性写入完整内容
2. 如果内容特别大，可以使用create_file_section分章节构建
3. 确保生成的文件包含所有必需的章节
4. 生成后必须验证文件是否创建成功

PSM生成策略：
- 方案1（推荐）：构建完整的PSM内容，然后使用write_large_file一次性写入
- 方案2：使用create_file_section逐章节构建（适合超大文件）
"""
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        # 执行多轮对话
        for round_num in range(self.max_rounds):
            # 调用API
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "tools": self.tools,
                    "tool_choice": "auto",
                    "temperature": 0
                }
            )
            
            if response.status_code != 200:
                print(f"API调用失败: {response.status_code}")
                print(response.text)
                return "API调用失败"
            
            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                print("无效的API响应")
                return "无效响应"
            
            message = result["choices"][0]["message"]
            messages.append(message)
            
            # 检查是否有工具调用
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    
                    # 解析参数
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError as e:
                        # 尝试修复常见的JSON错误
                        raw_args = tool_call["function"]["arguments"]
                        print(f"JSON解析错误: {e}")
                        print(f"原始参数: {raw_args[:200]}...")
                        
                        # 尝试基本修复
                        try:
                            # 移除可能的控制字符
                            cleaned_args = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', raw_args)
                            arguments = json.loads(cleaned_args)
                        except:
                            arguments = {"error": f"JSON解析失败: {str(e)}"}
                    
                    # 执行工具
                    print(f"  [工具调用] {tool_name}")
                    tool_result = self._execute_tool(tool_name, arguments)
                    
                    # 添加工具结果到消息
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": tool_result
                    })
            else:
                # 没有工具调用，任务完成
                return message.get("content", "")
        
        return "达到最大轮数限制"