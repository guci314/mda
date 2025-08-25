#!/usr/bin/env python3
"""
React Agent - 完全集成记忆系统版本
通用的ReAct (Reasoning + Acting) Agent框架
支持任何OpenRouter兼容的LLM模型
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .simple_memory_manager import MemoryManagerAdapter

class ReactAgent:
    """带完整记忆系统的通用React Agent"""
    
    def __init__(self, 
                 work_dir: str,
                 model: str = "qwen/qwen3-coder",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 knowledge_files: Optional[List[str]] = None,
                 interface: str = "",
                 max_rounds: int = 300,
                 max_context_tokens: Optional[int] = None,
                 message_hooks: Optional[List] = None,
                 window_size: int = 50):
        """
        初始化React Agent with Cognitive Memory
        
        Args:
            work_dir: 工作目录
            model: 模型名称
            api_key: API密钥（支持OpenRouter、DeepSeek、Moonshot等）
            base_url: API基础URL（默认OpenRouter，可设置为DeepSeek等）
            knowledge_files: 知识文件列表
            interface: Agent接口描述
            max_rounds: 最大执行轮数
            max_context_tokens: 最大上下文tokens（None时自动检测）
            message_hooks: 消息钩子列表，用于拦截和处理消息流
            window_size: 消息窗口大小
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = model
        
        # API配置 - 支持多种服务
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("MOONSHOT_API_KEY")
        if not self.api_key:
            raise ValueError("No API key found. Please set OPENROUTER_API_KEY, DEEPSEEK_API_KEY, or MOONSHOT_API_KEY")
        
        # 基础URL - 支持自定义或默认
        if base_url:
            self.base_url = base_url
        elif os.getenv("DEEPSEEK_API_KEY") and not api_key:
            self.base_url = "https://api.deepseek.com/v1"  # DeepSeek 默认URL
        elif os.getenv("MOONSHOT_API_KEY") and not api_key:
            self.base_url = "https://api.moonshot.cn/v1"  # Moonshot 默认URL  
        else:
            self.base_url = "https://openrouter.ai/api/v1"  # OpenRouter 默认URL
        self.knowledge_files = knowledge_files or []
        self.interface = interface
        self.max_rounds = max_rounds
        
        # 自动检测模型的上下文大小
        if max_context_tokens is None:
            max_context_tokens = self._detect_context_size()
        
        # 初始化认知记忆架构
        self.memory = MemoryManagerAdapter(
            work_dir=str(self.work_dir),
            max_context_tokens=max_context_tokens
        )
        
        # 认知记忆集成（可选，在需要时初始化）
        self.cognitive_memory = None
        self.window_size = window_size
        
        # 显示配置信息
        service_name = self._detect_service()
        print(f"🚀 {service_name} Agent 已初始化")
        print(f"  📍 API: {self.base_url}")
        print(f"  🤖 模型: {self.model}")
        print(f"  🧠 认知记忆: 窗口大小 {window_size}")
        
        # 加载知识文件
        self.knowledge = self._load_knowledge()
        
        # 定义工具
        self.tools = self._define_tools()
        
        # 执行统计
        self.stats = {
            "total_rounds": 0,
            "tool_calls": {},
            "files_created": [],
            "files_read": []
        }
        
        # 消息钩子系统
        self.message_hooks = message_hooks or []
    
    def _detect_service(self) -> str:
        """检测使用的API服务"""
        if "deepseek" in self.base_url.lower():
            return "DeepSeek"
        elif "moonshot" in self.base_url.lower():
            return "Moonshot (Kimi)"
        elif "openrouter" in self.base_url.lower():
            return "OpenRouter"
        elif "generativelanguage.googleapis.com" in self.base_url.lower():
            return "Google Gemini"
        else:
            return "Custom API"
    
    def _detect_context_size(self) -> int:
        """根据模型自动检测上下文大小"""
        context_sizes = {
            "qwen/qwen3-coder": 262144,           # 262k
            "qwen/qwen-2.5-coder-32b-instruct": 131072,  # 131k
            "qwen/qwq-32b-preview": 32768,        # 32k
            "qwen/qwen-2-72b-instruct": 131072,   # 131k
            "deepseek-chat": 128000,               # 128k - DeepSeek
            "kimi-k2-0711-preview": 128000,        # 128k - Moonshot
            "kimi-k2-turbo-preview": 128000,       # 128k - Moonshot
            "gemini-2.5-flash": 1048576,           # 1M - Gemini
        }
        return context_sizes.get(self.model, 32768)  # 默认32k
    
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
                    "name": "write_file",
                    "description": "写入文件内容（覆盖原文件）。content不能超过8000字符",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "文件内容"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "append_file",
                    "description": "追加内容到文件末尾。content不能超过6000字符",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "要追加的内容"
                            }
                        },
                        "required": ["file_path", "content"]
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
                                "description": "目录路径"
                            }
                        },
                        "required": ["directory_path"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "执行Shell命令",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "command": {
                                "type": "string",
                                "description": "要执行的命令"
                            }
                        },
                        "required": ["command"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_python",
                    "description": "执行Python代码",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {
                                "type": "string",
                                "description": "要执行的Python代码"
                            }
                        },
                        "required": ["code"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_memory",
                    "description": "搜索记忆系统",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """执行工具并自动记录到记忆"""
        
        # 更新统计
        self.stats["tool_calls"][tool_name] = self.stats["tool_calls"].get(tool_name, 0) + 1
        
        try:
            if tool_name == "read_file":
                file_path = arguments["file_path"]
                abs_path = os.path.join(self.work_dir, file_path) if not os.path.isabs(file_path) else file_path
                
                if os.path.exists(abs_path):
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 自动记录到记忆
                    self.memory.open_file(file_path, content)
                    self.stats["files_read"].append(file_path)
                    
                    return content
                else:
                    return f"文件不存在: {file_path}"
            
            elif tool_name == "write_file":
                file_path = arguments["file_path"]
                content = arguments["content"]
                
                if len(content) > 8000:
                    return f"错误：内容超过8000字符限制（{len(content)}字符）"
                
                abs_path = os.path.join(self.work_dir, file_path) if not os.path.isabs(file_path) else file_path
                
                os.makedirs(os.path.dirname(abs_path), exist_ok=True)
                with open(abs_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                # 自动记录到记忆
                self.memory.open_file(file_path, content)
                self.stats["files_created"].append(file_path)
                
                return f"成功写入文件: {file_path}"
            
            elif tool_name == "append_file":
                file_path = arguments["file_path"]
                content = arguments["content"]
                
                if len(content) > 6000:
                    return f"错误：内容超过6000字符限制（{len(content)}字符）"
                
                abs_path = os.path.join(self.work_dir, file_path) if not os.path.isabs(file_path) else file_path
                
                # 读取现有内容
                existing_content = ""
                if os.path.exists(abs_path):
                    with open(abs_path, 'r', encoding='utf-8') as f:
                        existing_content = f.read()
                
                # 追加内容
                with open(abs_path, 'a', encoding='utf-8') as f:
                    f.write(content)
                
                # 更新记忆
                full_content = existing_content + content
                self.memory.open_file(file_path, full_content)
                
                return f"成功追加到文件: {file_path}"
            
            elif tool_name == "list_directory":
                directory_path = arguments["directory_path"]
                abs_path = os.path.join(self.work_dir, directory_path) if not os.path.isabs(directory_path) else directory_path
                
                if os.path.exists(abs_path) and os.path.isdir(abs_path):
                    items = os.listdir(abs_path)
                    return "\n".join(items) if items else "目录为空"
                else:
                    return f"目录不存在: {directory_path}"
            
            elif tool_name == "execute_command":
                import subprocess
                command = arguments["command"]
                
                result = subprocess.run(
                    command,
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.work_dir,
                    timeout=30
                )
                
                output = result.stdout
                if result.stderr:
                    output += f"\n错误输出:\n{result.stderr}"
                
                return output if output else "命令执行成功（无输出）"
            
            elif tool_name == "execute_python":
                import subprocess
                code = arguments["code"]
                
                result = subprocess.run(
                    ["python", "-c", code],
                    capture_output=True,
                    text=True,
                    cwd=self.work_dir,
                    timeout=30
                )
                
                output = result.stdout
                if result.stderr:
                    output += f"\n错误输出:\n{result.stderr}"
                
                return output if output else "代码执行成功（无输出）"
            
            elif tool_name == "search_memory":
                query = arguments["query"]
                results = self.memory.search(query)
                
                if results:
                    formatted = []
                    for r in results[:5]:  # 最多返回5个结果
                        formatted.append(f"- {r.get('type', 'unknown')}: {r.get('path', r.get('id', ''))}")
                    return "搜索结果:\n" + "\n".join(formatted)
                else:
                    return "未找到相关内容"
            
            else:
                return f"未知工具: {tool_name}"
                
        except Exception as e:
            return f"工具执行错误: {str(e)}"
        
        finally:
            # 记录工具调用事件
            self.memory.save_episode(
                event=f"tool_{tool_name}",
                data={
                    "tool": tool_name,
                    "arguments": arguments,
                    "round": self.stats["total_rounds"]
                }
            )
    
    def execute_task(self, task: str) -> str:
        """执行任务"""
        print(f"\n[ReactAgent] 执行任务...")
        print(f"📝 任务: {task[:100]}..." if len(task) > 100 else f"📝 任务: {task}")
        
        # 记录任务开始
        self.memory.save_episode(
            event="task_start",
            data={"task": task[:500], "timestamp": datetime.now().isoformat()}
        )
        
        # 构建初始消息
        messages = [
            {"role": "system", "content": self._build_system_prompt()},
            {"role": "user", "content": task}
        ]
        
        # 执行轮数循环
        for round_num in range(self.max_rounds):
            self.stats["total_rounds"] = round_num + 1
            
            print(f"\n🤔 思考第{round_num + 1}轮...")
            
            # 检查是否需要优化消息历史
            if self.memory.should_optimize(round_num, len(messages)):
                print(f"🔄 优化消息历史...")
                messages = self.memory.optimize_message_history(messages)
            
            # 添加消息到过程记忆
            if round_num > 0:
                for msg in messages[-2:]:  # 添加最新的消息
                    self.memory.add_message(msg)
            
            # 调用API
            response = self._call_api(messages)
            
            if response is None:
                return "API调用失败"
            
            # 处理响应
            message = response["choices"][0]["message"]
            messages.append(message)
            
            # 调用消息钩子
            self._call_hooks("assistant", message)
            
            # 处理工具调用
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = None
                    
                    if arguments is None:
                        tool_result = f"参数解析失败"
                    else:
                        print(f"🔧 调用工具: {tool_name}")
                        tool_result = self._execute_tool(tool_name, arguments)
                        
                        # 显示结果预览
                        preview = tool_result[:200] + "..." if len(tool_result) > 200 else tool_result
                        print(f"   → {preview}")
                    
                    # 添加工具结果
                    tool_message = {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": tool_result
                    }
                    messages.append(tool_message)
                    self.memory.add_message(tool_message)
                    
                    # 调用消息钩子
                    self._call_hooks("tool", tool_message)
            
            # 检查是否完成
            if response["choices"][0].get("finish_reason") == "stop" and not message.get("tool_calls"):
                print(f"\n✅ 任务完成（第{round_num + 1}轮）")
                
                # 记录任务完成
                self.memory.save_episode(
                    event="task_complete",
                    data={
                        "rounds": round_num + 1,
                        "result_preview": message["content"][:500] if message.get("content") else "",
                        "files_created": self.stats["files_created"],
                        "files_read": self.stats["files_read"]
                    }
                )
                
                # 保存最终状态
                self.memory.save_state(
                    state_name="task_completion",
                    state_data={
                        "task": task[:500],
                        "rounds": round_num + 1,
                        "stats": self.stats
                    }
                )
                
                return message.get("content", "任务完成")
        
        print(f"\n⚠️ 达到最大执行轮数 ({self.max_rounds}轮)")
        
        # 记录超时
        self.memory.save_episode(
            event="task_timeout",
            data={"rounds": self.max_rounds}
        )
        
        return messages[-1].get("content", "达到最大执行轮数") if messages else "任务未完成"
    
    def _build_system_prompt(self) -> str:
        """构建系统提示词（包含记忆状态）"""
        
        # 获取记忆上下文
        memory_context = self.memory.get_memory_context(extra_tokens=5000)
        
        prompt = f"""你是Qwen Coder，一个专业的编程助手，配备了高性能记忆系统。

{self.interface}

# 知识库
{self.knowledge}

# 工作目录
{self.work_dir}

# 当前记忆状态
{memory_context if memory_context else "（空）"}

# 执行纪律
1. 所有文件操作都会自动记录到记忆系统
2. 可以使用search_memory工具搜索历史
3. 复杂任务请分步骤执行
4. 遇到错误时记录并尝试修复

# 内容长度限制
- write_file: content最多8000字符
- append_file: content最多6000字符
- 长内容必须分段处理

# 核心优势
- 代码生成能力极强
- 深度推理能力
- 配备高性能记忆系统
- 支持超长上下文（{self.memory.max_context_tokens:,} tokens）
"""
        return prompt
    
    def _call_api(self, messages: List[Dict]) -> Optional[Dict]:
        """调用OpenRouter API"""
        try:
            request_body = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,
                "max_tokens": 8192
            }
            
            if self.tools:
                request_body["tools"] = self.tools
                request_body["tool_choice"] = "auto"
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/qwen-agent",
                    "X-Title": "React Agent with Integrated Memory"
                },
                json=request_body,
                timeout=60
            )
            
            if response.status_code != 200:
                print(f"❌ API错误: {response.text}")
                return None
            
            result = response.json()
            
            if "error" in result:
                print(f"❌ API返回错误: {result['error']}")
                return None
            
            return result
            
        except Exception as e:
            print(f"❌ API调用异常: {e}")
            return None
    
    def get_status(self) -> Dict:
        """获取Agent状态"""
        return {
            "stats": self.stats,
            "memory": self.memory.get_status()
        }
    
    def _call_hooks(self, message_type: str, message: Dict):
        """调用所有注册的消息钩子"""
        for hook in self.message_hooks:
            try:
                hook(self, message_type, message)
            except Exception as e:
                print(f"⚠️ 钩子执行错误: {e}")
    
    def add_hook(self, hook):
        """添加消息钩子"""
        if hook not in self.message_hooks:
            self.message_hooks.append(hook)
    
    def remove_hook(self, hook):
        """移除消息钩子"""
        if hook in self.message_hooks:
            self.message_hooks.remove(hook)
    
    def cleanup(self):
        """清理资源"""
        print("🧹 清理资源...")
        self.memory.cleanup()
    
    def init_cognitive_memory_integration(self, window_size: int = 50, memory_dir: str = ".memory"):
        """
        初始化认知记忆集成
        
        Args:
            window_size: 滑动窗口大小
            memory_dir: 记忆目录
            
        Returns:
            CognitiveMemoryIntegration实例
        """
        from .cognitive_memory_integration import CognitiveMemoryIntegration
        
        if not hasattr(self, 'cognitive_memory') or self.cognitive_memory is None:
            self.cognitive_memory = CognitiveMemoryIntegration(
                work_dir=str(self.work_dir),
                window_size=window_size,
                memory_dir=memory_dir
            )
            print(f"🧠 认知记忆集成已初始化（窗口：{window_size}，目录：{memory_dir}）")
        
        return self.cognitive_memory
    
    def enable_cognitive_memory(self):
        """
        启用认知记忆（简化接口）
        自动初始化并返回认知记忆集成实例
        """
        return self.init_cognitive_memory_integration()