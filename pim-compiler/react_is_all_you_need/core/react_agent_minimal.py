#!/usr/bin/env python3
"""
ReactAgent Minimal - 极简版本
使用MemoryWithNaturalDecay作为唯一的记忆系统
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .memory_with_natural_decay import MemoryWithNaturalDecay


class ReactAgentMinimal:
    """
    极简React Agent
    
    核心理念：
    1. 只用一个记忆系统 - MemoryWithNaturalDecay
    2. 压缩就是认知
    3. 简单就是美
    """
    
    def __init__(self, 
                 work_dir: str,
                 model: str = "deepseek-chat",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 pressure_threshold: int = 50,
                 max_rounds: int = 100,
                 knowledge_files: Optional[List[str]] = None):
        """
        初始化极简Agent
        
        Args:
            work_dir: 工作目录
            model: 模型名称
            api_key: API密钥
            base_url: API基础URL
            pressure_threshold: 记忆压缩阈值（唯一的记忆参数！）
            max_rounds: 最大执行轮数
            knowledge_files: 知识文件列表（自然语言程序）
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = model
        self.max_rounds = max_rounds
        
        # API配置
        self.api_key = api_key or self._detect_api_key()
        self.base_url = base_url or self._detect_base_url_for_key(self.api_key)
        
        # 🌟 唯一的记忆系统！
        self.memory = MemoryWithNaturalDecay(
            pressure_threshold=pressure_threshold,
            work_dir=str(self.work_dir / ".memory"),
            enable_persistence=True
        )
        
        # 知识文件（自然语言程序）
        self.knowledge_files = knowledge_files or []
        self.knowledge_content = self._load_knowledge()
        
        # 定义工具
        self.tools = self._define_minimal_tools()
        
        # 显示初始化信息
        print(f"🚀 极简Agent已初始化")
        print(f"  📍 API: {self._detect_service()}")
        print(f"  🤖 模型: {self.model}")
        print(f"  🧠 记忆压力阈值: {pressure_threshold}")
        if self.knowledge_files:
            print(f"  📚 知识文件: {len(self.knowledge_files)}个")
        print(f"  ✨ 极简即完美")
    
    def execute_task(self, task: str) -> str:
        """
        执行任务 - 极简版本
        
        Args:
            task: 要执行的任务
            
        Returns:
            任务结果
        """
        print(f"\n[极简Agent] 执行任务...")
        print(f"📝 任务: {task[:100]}...")
        
        # 添加任务到记忆
        self.memory.add_message("user", task)
        
        # 初始化消息列表
        messages = [
            {"role": "system", "content": self._build_minimal_prompt()},
            {"role": "user", "content": task}
        ]
        
        # 执行循环
        for round_num in range(self.max_rounds):
            print(f"\n🤔 思考第{round_num + 1}轮...")
            
            # 调用LLM
            response = self._call_api(messages)
            if response is None:
                return "API调用失败"
            
            # 处理响应
            message = response["choices"][0]["message"]
            messages.append(message)  # 添加assistant消息到对话历史
            
            # 显示LLM的思考内容（如果有）
            if message.get("content"):
                content_preview = message["content"][:200]
                if len(content_preview) > 0:
                    print(f"💭 思考: {content_preview}...")
            
            # 添加到记忆（可能触发自动压缩）
            self.memory.add_message("assistant", message.get("content", ""))
            
            # 处理工具调用
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_call_id = tool_call["id"]
                    
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                        print(f"\n🔧 调用工具: {tool_name}")
                        # 显示工具参数
                        for key, value in arguments.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"   📝 {key}: {value[:100]}...")
                            else:
                                print(f"   📝 {key}: {value}")
                        
                        tool_result = self._execute_tool(tool_name, arguments)
                        
                        # 显示工具执行结果
                        result_preview = tool_result[:150] if len(tool_result) > 150 else tool_result
                        print(f"   ✅ 结果: {result_preview}")
                        
                        # 添加工具结果到消息（正确的格式）
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": tool_result
                        }
                        messages.append(tool_message)
                        
                        # 添加到记忆系统
                        self.memory.add_message("tool", tool_result[:500])
                        
                    except Exception as e:
                        tool_error = f"工具执行错误: {e}"
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": tool_error
                        }
                        messages.append(tool_message)
                        self.memory.add_message("tool", tool_error)
            
            # 检查是否完成
            if response["choices"][0].get("finish_reason") == "stop" and not message.get("tool_calls"):
                print(f"\n✅ 任务完成（第{round_num + 1}轮）")
                
                # 显示记忆统计
                stats = self.memory.get_stats()
                print(f"\n📊 记忆统计：")
                print(f"  总消息: {stats['total_messages']}")
                print(f"  压缩次数: {stats['compressions']}")
                print(f"  当前压力: {stats['memory_pressure']}")
                
                return message.get("content", "任务完成")
        
        print(f"\n⚠️ 达到最大轮数")
        return "达到最大执行轮数"
    
    def _build_minimal_prompt(self) -> str:
        """构建极简系统提示"""
        prompt = f"""你是一个编程助手，使用自然记忆衰减系统。

工作目录：{self.work_dir}

记忆系统说明：
- 你的记忆会自动压缩和衰减
- 压缩的历史会保留关键信息
- 专注于当前任务，历史只作参考
"""
        
        # 注入知识文件（自然语言程序）
        if self.knowledge_content:
            prompt += f"""
知识库（可参考的自然语言程序）：
{self.knowledge_content}
"""
        
        prompt += "\n请高效完成任务。"
        return prompt
    
    def _load_knowledge(self) -> str:
        """加载知识文件（自然语言程序）"""
        knowledge_content = []
        
        for file_path in self.knowledge_files:
            try:
                path = Path(file_path)
                if not path.is_absolute():
                    # 首先尝试相对于当前工作目录（脚本运行位置）
                    if Path(file_path).exists():
                        path = Path(file_path)
                    # 然后尝试相对于agent工作目录
                    elif (self.work_dir / path).exists():
                        path = self.work_dir / path
                    # 最后尝试相对于项目根目录
                    else:
                        project_root = Path(__file__).parent.parent
                        if (project_root / path).exists():
                            path = project_root / path
                
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    knowledge_content.append(f"=== {path.name} ===\n{content}")
                    print(f"  ✅ 加载知识文件: {path.name}")
                else:
                    print(f"  ⚠️ 知识文件不存在: {file_path}")
            except Exception as e:
                print(f"  ❌ 加载知识文件失败 {file_path}: {e}")
        
        return "\n\n".join(knowledge_content) if knowledge_content else ""
    
    def _define_minimal_tools(self) -> List[Dict]:
        """定义最小工具集"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "read_file",
                    "description": "读取文件内容，支持分段读取大文件",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "要读取的文件路径"
                            },
                            "offset": {
                                "type": "integer",
                                "description": "起始字符位置，默认0"
                            },
                            "limit": {
                                "type": "integer",
                                "description": "读取字符数限制，默认2000"
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
                    "description": "创建或覆盖文件内容",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "要写入的文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "要写入的文件内容"
                            }
                        },
                        "required": ["file_path", "content"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_command",
                    "description": "执行shell命令",
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
            }
        ]
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """执行工具 - 极简实现"""
        try:
            if tool_name == "read_file":
                file_path = self.work_dir / arguments["file_path"]
                if file_path.exists():
                    offset = arguments.get("offset", 0)
                    limit = arguments.get("limit", 2000)
                    
                    with open(file_path, 'r', encoding='utf-8') as f:
                        file_size = file_path.stat().st_size
                        
                        # 处理负偏移（从文件末尾开始）
                        if offset < 0:
                            offset = max(0, file_size + offset)
                        
                        # 移动到指定位置
                        if offset > 0:
                            f.seek(offset)
                        
                        # 读取指定长度
                        content = f.read(limit)
                        
                        # 添加位置信息（仅在分段读取时）
                        if offset > 0 or (len(content) == limit and file_size > limit):
                            end_pos = offset + len(content)
                            return f"[读取范围: {offset}-{end_pos}/{file_size}字节]\n{content}"
                        
                        return content
                return f"文件不存在: {arguments['file_path']}"
            
            elif tool_name == "write_file":
                file_path = self.work_dir / arguments["file_path"]
                file_path.parent.mkdir(parents=True, exist_ok=True)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(arguments["content"])
                return f"文件已写入: {arguments['file_path']}"
            
            elif tool_name == "execute_command":
                import subprocess
                result = subprocess.run(
                    arguments["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    cwd=self.work_dir,
                    timeout=10
                )
                return result.stdout[:500] if result.stdout else "命令执行完成"
            
            else:
                return f"未知工具: {tool_name}"
                
        except Exception as e:
            return f"工具执行错误: {str(e)}"
    
    def _call_api(self, messages: List[Dict]) -> Optional[Dict]:
        """调用API - 极简版本（带重试）"""
        import time
        
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
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
                        "temperature": 0.3,
                        "max_tokens": 4096
                    },
                    timeout=60  # 增加到60秒
                )
            
                if response.status_code == 200:
                    return response.json()
                else:
                    print(f"❌ API错误: {response.status_code}")
                    print(f"错误详情: {response.text[:500]}")
                    if attempt < max_retries - 1:
                        print(f"⏳ 等待{retry_delay}秒后重试...（第{attempt+2}/{max_retries}次）")
                        time.sleep(retry_delay)
                        continue
                    return None
                    
            except requests.exceptions.Timeout as e:
                if attempt < max_retries - 1:
                    print(f"⏱️ 请求超时，等待{retry_delay}秒后重试...（第{attempt+2}/{max_retries}次）")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"❌ API调用超时（已重试{max_retries}次）: {e}")
                    return None
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"⚠️ API调用异常: {e}")
                    print(f"⏳ 等待{retry_delay}秒后重试...（第{attempt+2}/{max_retries}次）")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"❌ API调用失败（已重试{max_retries}次）: {e}")
                    return None
        
        return None  # 所有重试都失败
    
    def _detect_api_key(self) -> str:
        """检测API密钥"""
        for key in ["DEEPSEEK_API_KEY", "MOONSHOT_API_KEY", "OPENROUTER_API_KEY"]:
            if os.getenv(key):
                return os.getenv(key)
        raise ValueError("未找到API密钥")
    
    def _detect_base_url_for_key(self, api_key: str) -> str:
        """根据API密钥检测对应的API URL"""
        # 检查是否是特定服务的API密钥
        if api_key == os.getenv("DEEPSEEK_API_KEY"):
            return "https://api.deepseek.com/v1"
        elif api_key == os.getenv("MOONSHOT_API_KEY"):
            return "https://api.moonshot.cn/v1"
        elif api_key == os.getenv("OPENROUTER_API_KEY"):
            return "https://openrouter.ai/api/v1"
        
        # 如果无法确定，基于环境变量猜测
        if os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENROUTER_API_KEY"):
            return "https://api.deepseek.com/v1"
        elif os.getenv("MOONSHOT_API_KEY") and not os.getenv("OPENROUTER_API_KEY"):
            return "https://api.moonshot.cn/v1"
        else:
            return "https://openrouter.ai/api/v1"
    
    def _detect_service(self) -> str:
        """检测服务类型"""
        base_url_lower = self.base_url.lower()
        if "deepseek" in base_url_lower:
            return "DeepSeek"
        elif "moonshot" in base_url_lower:
            return "Moonshot"
        elif "openrouter" in base_url_lower:
            return "OpenRouter"
        else:
            return "Custom"
    
    def search_memory(self, query: str) -> List[str]:
        """搜索记忆"""
        results = self.memory.search(query, limit=5)
        return [f"{mem.summary}" for mem, score in results]
    
    def get_memory_timeline(self) -> List[Dict]:
        """获取记忆时间线"""
        return self.memory.get_memory_timeline()
    
    def cleanup(self) -> None:
        """清理资源"""
        self.memory.save_state()
        print("🧹 资源已保存")


# 对比：新旧系统
def compare_systems():
    """对比新旧系统的复杂度"""
    
    print("=" * 60)
    print("📊 系统复杂度对比")
    print("=" * 60)
    
    old_system = """
    旧系统（过度设计）：
    - SimpleMemoryManager (200行)
    - NLPLMemorySystem (500行)  
    - CognitiveMemoryIntegration (400行)
    - 4个认知Agent (各100行)
    - MemoryManagerAdapter (150行)
    总计：约1450行代码，6个类
    """
    
    new_system = """
    新系统（极简设计）：
    - MemoryWithNaturalDecay (350行)
    - ReactAgentMinimal (250行)
    总计：约600行代码，2个类
    
    减少了60%的代码！
    """
    
    print(old_system)
    print(new_system)
    
    print("\n✨ 极简设计的优势：")
    print("1. 代码量减少60%")
    print("2. 概念简化：压缩=记忆=认知")
    print("3. 零配置：只需一个pressure_threshold")
    print("4. 自然行为：模仿Claude Code本身")
    print("5. 性能更好：减少了层层抽象")


if __name__ == "__main__":
    # 演示极简系统
    print("🌟 极简React Agent演示")
    print("=" * 60)
    
    # 显示对比
    compare_systems()
    
    # 创建极简Agent
    agent = ReactAgentMinimal(
        work_dir="test_minimal",
        pressure_threshold=20,  # 唯一的记忆参数！
        max_rounds=30
    )
    
    # 执行任务
    task = """
    创建一个简单的Python函数，返回"Hello, Minimal World!"
    """
    
    result = agent.execute_task(task)
    print(f"\n结果：{result}")
    
    # 清理
    import shutil
    if Path("test_minimal").exists():
        shutil.rmtree("test_minimal")
        print("\n✅ 测试文件已清理")