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

# 自动加载.env文件
def load_env_file():
    """自动查找并加载.env文件"""
    # 尝试多个可能的.env文件位置（优先级从高到低）
    possible_paths = [
        Path(__file__).parent.parent.parent / ".env",  # pim-compiler/.env（优先）
        Path(__file__).parent.parent / ".env",  # react_is_all_you_need/.env
        Path.cwd() / ".env",  # 当前工作目录
    ]
    
    for env_path in possible_paths:
        if env_path.exists():
            loaded_count = 0
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        # 移除可能的引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        # 只设置尚未存在的环境变量
                        if key not in os.environ:
                            os.environ[key] = value
                            loaded_count += 1
            if loaded_count > 0:
                print(f"  ✅ 已加载{loaded_count}个环境变量: {env_path}")
            return  # 只加载第一个找到的.env文件
    print("  ⚠️ 未找到.env文件，使用系统环境变量")

# 使用标记避免重复加载
_ENV_LOADED = False
def ensure_env_loaded():
    """确保环境变量只加载一次"""
    global _ENV_LOADED
    if not _ENV_LOADED:
        load_env_file()
        _ENV_LOADED = True

# 模块加载时即确保环境变量已加载
ensure_env_loaded()

# 不再需要外部记忆系统 - Agent自己做笔记
try:
    from .tool_base import Function, ReadFileTool, WriteFileTool, ExecuteCommandTool
except ImportError:
    # 支持直接运行此文件
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.tool_base import Function, ReadFileTool, WriteFileTool, ExecuteCommandTool


class ReactAgentMinimal(Function):
    """
    极简React Agent
    
    核心理念：
    1. 只用一个记忆系统 - MemoryWithNaturalDecay
    2. 压缩就是认知
    3. 简单就是美
    """
    
    # 默认参数定义
    DEFAULT_PARAMETERS = {
        "task": {
            "type": "string",
            "description": "要执行的任务描述"
        }
    }
    
    def __init__(self, 
                 work_dir: str,
                 name: str = "react_agent",
                 description: str = "React Agent - 能够思考和使用工具的智能代理",
                 parameters: Optional[Dict[str, Dict]] = None,
                 return_type: str = "string",
                 model: str = "deepseek-chat",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 window_size: int = 50,
                 max_rounds: int = 100,
                 knowledge_files: Optional[List[str]] = None):
        """
        初始化极简Agent
        
        Args:
            work_dir: 工作目录
            name: Agent名称
            description: Agent描述
            parameters: 参数定义，默认为{"task": {"type": "string", "description": "任务描述"}}
            return_type: 返回值类型，默认为"string"
            model: 模型名称
            api_key: API密钥
            base_url: API基础URL
            window_size: 滑动窗口大小，默认50条消息（约10-15k tokens）
                        简单任务可设为20-30，复杂任务可设为100或更高
            max_rounds: 最大执行轮数
            knowledge_files: 知识文件列表（自然语言程序）
        """
        # 使用类变量作为默认值
        if parameters is None:
            parameters = self.DEFAULT_PARAMETERS.copy()
        
        # 初始化Function基类
        super().__init__(
            name=name,
            description=description,
            parameters=parameters,
            return_type=return_type
        )
        
        # 保存字段（方便直接访问）
        self.name = name
        self.description = description
        self.parameters = parameters
        self.return_type = return_type
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = model
        self.max_rounds = max_rounds
        
        # API配置
        self.api_key = api_key or self._detect_api_key()
        self.base_url = base_url or self._detect_base_url_for_key(self.api_key)
        
        # 知识文件（自然语言程序）- 提前加载
        self.knowledge_files = knowledge_files or []
        
        # 自动添加结构化笔记系统的知识文件
        knowledge_dir = Path(__file__).parent.parent / "knowledge"
        structured_notes_path = knowledge_dir / "structured_notes.md"
        if structured_notes_path.exists() and str(structured_notes_path) not in self.knowledge_files:
            self.knowledge_files.append(str(structured_notes_path))
        self.knowledge_content = self._load_knowledge()
        
        # 🌟 笔记系统 - Agent自己就是智能压缩器！
        self.window_size = window_size
        # 不再需要 message_count，直接使用 len(messages) 计算压力
        self.notes_dir = self.work_dir / ".notes"
        self.notes_dir.mkdir(exist_ok=True)
        # 三层笔记架构文件
        self.experience_file = self.notes_dir / "experience.md"
        self.task_state_file = self.notes_dir / "task_state.md"
        self.environment_file = self.notes_dir / "environment.md"
        # 保留旧的notes_file以兼容（但不再使用）
        self.notes_file = self.notes_dir / "session_notes.md"
        
        # 创建工具实例
        self.tool_instances = self._create_tool_instances()
        # 生成工具定义（用于API调用）
        self.tools = [tool.to_openai_function() for tool in self.tool_instances]
        
        # 显示初始化信息
        print(f"🚀 极简Agent已初始化")
        print(f"  📍 API: {self._detect_service()}")
        print(f"  🤖 模型: {self.model}")
        print(f"  📝 滑动窗口大小: {window_size}条消息")
        print(f"  📓 笔记目录: {self.notes_dir}")
        print(f"     - experience.md (经验库)")
        print(f"     - task_state.md (任务状态)")
        print(f"     - environment.md (环境知识)")
        if self.knowledge_files:
            print(f"  📚 知识文件: {len(self.knowledge_files)}个")
        print(f"  ✨ Agent自己就是智能压缩器")
    
    def execute(self, **kwargs) -> str:
        """
        执行任务 - 实现Function接口
        
        Args:
            **kwargs: 包含task参数
            
        Returns:
            任务结果
        """
        # 从kwargs中提取task参数
        task = kwargs.get("task", "")
        if not task:
            return "错误：未提供任务描述"
        print(f"\n[极简Agent] 执行任务...")
        print(f"📝 任务: {task[:100]}...")
        
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
            
            # 滑动窗口管理（FIFO）- 保持固定大小的工作记忆
            if self.window_size > 0 and len(messages) > self.window_size:
                # 识别关键消息
                system_messages = [m for m in messages if m["role"] == "system"]
                
                # 找到最后一条用户消息（当前任务）
                last_user_msg = None
                last_user_idx = -1
                for i in range(len(messages) - 1, -1, -1):
                    if messages[i]["role"] == "user":
                        last_user_msg = messages[i]
                        last_user_idx = i
                        break
                
                # 计算可用窗口大小（减去系统消息和最后的用户消息）
                reserved_count = len(system_messages) + (1 if last_user_msg else 0)
                available_window = self.window_size - reserved_count
                
                if available_window > 0:
                    # 将消息分组为原子单元（保持tool消息与其tool_calls配对）
                    message_units = []
                    i = 0
                    while i < len(messages):
                        msg = messages[i]
                        
                        # 跳过系统消息和最后的用户消息（它们会被特殊处理）
                        if msg["role"] == "system" or i == last_user_idx:
                            i += 1
                            continue
                        
                        # 如果是带有tool_calls的assistant消息，收集所有相关的tool响应
                        if msg["role"] == "assistant" and msg.get("tool_calls"):
                            unit = [msg]
                            i += 1
                            # 收集所有紧跟的tool消息
                            while i < len(messages) and messages[i]["role"] == "tool":
                                unit.append(messages[i])
                                i += 1
                            message_units.append(unit)
                        else:
                            # 单独的消息作为一个单元
                            message_units.append([msg])
                            i += 1
                    
                    # 计算每个单元的消息数
                    unit_sizes = [len(unit) for unit in message_units]
                    
                    # 从后向前选择单元，直到达到窗口限制
                    selected_units = []
                    current_size = 0
                    for i in range(len(message_units) - 1, -1, -1):
                        unit_size = unit_sizes[i]
                        if current_size + unit_size <= available_window:
                            selected_units.insert(0, message_units[i])
                            current_size += unit_size
                        else:
                            break
                    
                    # 展开选中的单元为消息列表
                    recent_other = []
                    for unit in selected_units:
                        recent_other.extend(unit)
                    
                    # 重组消息：系统 + 最后用户消息 + 最近的其他消息
                    messages = system_messages
                    if last_user_msg:
                        messages.append(last_user_msg)
                    messages.extend(recent_other)
                    
                    print(f"  🔄 工作记忆滑动窗口：保持系统提示、当前任务和最近 {current_size} 条消息（{len(selected_units)} 个单元）")
                else:
                    # 窗口太小，只保留系统消息和最后的用户消息
                    messages = system_messages
                    if last_user_msg:
                        messages.append(last_user_msg)
                    print(f"  🔄 工作记忆滑动窗口：仅保持系统提示和当前任务")
            
            # 显示LLM的思考内容（如果有）
            if message.get("content"):
                content_preview = message["content"][:200]
                if len(content_preview) > 0:
                    print(f"💭 思考: {content_preview}...")
            
            # 滑动窗口自动管理，无需压力提示
            
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
                        
                        # 检测是否写了笔记（三层架构）
                        if tool_name == "write_file":
                            file_path = str(arguments.get("file_path", ""))
                            if "experience.md" in file_path:
                                print(f"\n   📝 经验库已更新（长期知识）")
                            elif "task_state.md" in file_path:
                                print(f"\n   📋 任务状态已更新（TODO管理）")
                            elif "environment.md" in file_path:
                                print(f"\n   🏗️ 环境知识已更新（系统架构）")
                            elif str(self.notes_dir) in file_path:
                                print(f"\n   📝 笔记已保存（外部持久化）")
                            
                            if str(self.notes_dir) in file_path:
                                print(f"   💭 工作记忆继续保持滑动窗口")
                        
                        # 添加工具结果到消息（正确的格式）
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": tool_result
                        }
                        messages.append(tool_message)
                        
                        # 消息会被添加到messages列表，自动影响窗口大小
                        
                    except Exception as e:
                        tool_error = f"工具执行错误: {e}"
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": tool_error
                        }
                        messages.append(tool_message)
                        # 错误消息也会被添加到messages列表
            
            # 检查是否完成
            if response["choices"][0].get("finish_reason") == "stop" and not message.get("tool_calls"):
                print(f"\n✅ 任务完成（第{round_num + 1}轮）")
                
                # 显示统计
                print(f"\n📊 任务完成统计：")
                notes_created = []
                if self.experience_file.exists():
                    notes_created.append("experience.md")
                if self.task_state_file.exists():
                    notes_created.append("task_state.md")
                if self.environment_file.exists():
                    notes_created.append("environment.md")
                
                if notes_created:
                    print(f"  ✅ 已创建/更新笔记: {', '.join(notes_created)}")
                else:
                    print(f"  ℹ️ 未创建笔记（任务简单或无需记录）")
                
                return message.get("content", "任务完成")
        
        print(f"\n⚠️ 达到最大轮数")
        return "达到最大执行轮数"
    
    def _build_minimal_prompt(self) -> str:
        """构建极简系统提示"""
        # 尝试加载外部系统提示词模板
        prompt_template_path = Path(__file__).parent.parent / "knowledge" / "system_prompt.md"
        
        if prompt_template_path.exists():
            # 使用外部模板
            template = prompt_template_path.read_text(encoding='utf-8')
            
            # 检查是否有现存笔记（元记忆）
            meta_memory = ""
            existing_notes = []
            if self.experience_file.exists():
                existing_notes.append("experience.md")
            if self.task_state_file.exists():
                existing_notes.append("task_state.md")
            if self.environment_file.exists():
                existing_notes.append("environment.md")
            
            if existing_notes:
                meta_memory = f"\n[元记忆] 发现之前的笔记文件：{', '.join(existing_notes)}\n首次需要时使用read_file查看。"
            
            # 准备知识内容部分
            knowledge_section = ""
            if self.knowledge_content:
                knowledge_section = f"\n## 知识库（可参考的自然语言程序）\n{self.knowledge_content}"
            
            # 替换模板中的占位符
            prompt = template.format(
                work_dir=self.work_dir,
                notes_dir=self.notes_dir,
                notes_file=self.notes_file,
                meta_memory=meta_memory,
                window_size=self.window_size,
                knowledge_content=knowledge_section
            )
        else:
            # 降级到内置提示词（保持向后兼容）
            meta_memory = ""
            if self.notes_file.exists():
                meta_memory = f"\n[元记忆] 发现之前的笔记: {self.notes_file}\n首次需要时，使用read_file查看。\n"
            
            prompt = f"""你是一个编程助手，像数学家一样使用笔记扩展认知。

工作目录：{self.work_dir}
笔记目录：{self.notes_dir}
{meta_memory}
认知模型（滑动窗口）：
- 工作记忆是固定大小的滑动窗口（{self.window_size}条消息）
- 新信息进入，旧信息自然滑出（FIFO）

这就是图灵完备：你 + 文件系统 = 数学家 + 纸笔
"""
            
            if self.knowledge_content:
                prompt += f"\n知识库：\n{self.knowledge_content}"
            
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
    
    def _create_tool_instances(self) -> List[Function]:
        """创建工具实例"""
        # 使用从tool_base导入的工具类
        return [
            ReadFileTool(self.work_dir),
            WriteFileTool(self.work_dir),
            ExecuteCommandTool(self.work_dir)
        ]
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """执行工具 - 使用Tool实例"""
        try:
            # 查找对应的工具实例
            for tool in self.tool_instances:
                if tool.name == tool_name:
                    return tool.execute(**arguments)
            
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
                # 准备请求数据
                request_data = {
                    "model": self.model,
                    "messages": messages,
                    "tools": self.tools,
                    "tool_choice": "auto",
                    "temperature": 0.3,
                    "max_tokens": 4096
                }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data,
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
            api_key = os.getenv(key)
            if api_key:
                return api_key
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
    
    # 记忆功能已简化 - Agent自己做笔记
    
    def to_openai_function(self) -> Dict:
        """
        转换为OpenAI function calling格式
        使Agent可以作为工具被其他Agent调用
        
        Returns:
            OpenAI格式的函数定义
        """
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {
                    "type": "object",
                    "properties": self.parameters,
                    "required": [
                        key for key, param in self.parameters.items() 
                        if (param.get("required", True) if isinstance(param, dict) else True)
                    ]
                }
            }
        }
    
    def cleanup(self) -> None:
        """清理资源"""
        print(f"🧹 清理完成，笔记已保存在: {self.notes_file}")




if __name__ == "__main__":
    # 演示极简系统
    print("🌟 极简React Agent演示")
    print("=" * 60)
    
    # 创建极简Agent
    agent = ReactAgentMinimal(
        work_dir="test_minimal",
        window_size=100,  # 滑动窗口大小
        max_rounds=30
    )
    
    # 执行任务
    task = """
    创建一个简单的Python函数，返回"Hello, Minimal World!"
    """
    
    result = agent.execute(task=task)
    print(f"\n结果：{result}")
    
    # 清理
    import shutil
    if Path("test_minimal").exists():
        shutil.rmtree("test_minimal")
        print("\n✅ 测试文件已清理")