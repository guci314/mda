#!/usr/bin/env python3
"""
Qwen专用的React Agent实现
使用OpenRouter API访问Qwen3-Coder模型
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

class QwenReactAgent:
    """Qwen专用的React Agent"""
    
    def __init__(self, 
                 work_dir: str,
                 model: str = "qwen/qwen3-coder",
                 api_key: Optional[str] = None,
                 knowledge_files: Optional[List[str]] = None,
                 interface: str = "",
                 max_rounds: int = 300):
        """
        初始化Qwen Agent
        
        Args:
            work_dir: 工作目录
            model: 模型名称，可选：
                - qwen/qwen3-coder (推荐 - Qwen3 Coder，优化用于agent编码任务)
                - qwen/qwen-2.5-coder-32b-instruct (Qwen2.5 Coder)
                - qwen/qwq-32b-preview (深度推理)
                - qwen/qwen-2-72b-instruct
            api_key: OpenRouter API密钥
            knowledge_files: 知识文件列表
            interface: Agent接口描述
            max_rounds: 最大执行轮数，默认300
        """
        self.work_dir = Path(work_dir)
        self.work_dir.mkdir(parents=True, exist_ok=True)
        
        self.model = model
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OPENROUTER_API_KEY not set")
            
        self.base_url = "https://openrouter.ai/api/v1"
        self.knowledge_files = knowledge_files or []
        self.interface = interface
        self.max_rounds = max_rounds
        
        # 加载知识文件
        self.knowledge = self._load_knowledge()
        
        # 定义工具
        self.tools = self._define_tools()
        
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
                    "description": """写入文件内容（覆盖原文件）。
                    
重要约束：
- content参数不能超过8000字符（Qwen支持更长内容）
- 超过8000字符会导致JSON解析失败
- 长内容必须使用append_file分多次追加""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "文件内容，必须少于8000字符",
                                "maxLength": 8000
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
                    "description": """追加内容到文件末尾（不覆盖）。
                    
重要约束：
- content参数必须少于6000字符（留有余量避免JSON错误）
- 超过6000字符会导致失败
- 大内容请分多次调用此工具
- 不要在content中使用未转义的特殊字符""",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "file_path": {
                                "type": "string",
                                "description": "文件路径"
                            },
                            "content": {
                                "type": "string",
                                "description": "要追加的内容，必须少于6000字符",
                                "maxLength": 6000
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
            },
            {
                "type": "function",
                "function": {
                    "name": "execute_python",
                    "description": "执行Python代码（Qwen特别擅长）",
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
            }
        ]
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """执行工具"""
        
        # 确保arguments是字典
        if not isinstance(arguments, dict):
            return f"参数格式错误: 期望字典，得到{type(arguments)}"
        
        try:
            if tool_name == "read_file":
                file_path = arguments["file_path"]
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.work_dir, file_path)
                
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        return f.read()
                else:
                    return f"文件不存在: {file_path}"
                    
            elif tool_name == "write_file":
                file_path = arguments["file_path"]
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.work_dir, file_path)
                    
                # 创建目录
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(arguments["content"])
                return f"成功写入文件: {file_path}"
                
            elif tool_name == "append_file":
                file_path = arguments["file_path"]
                if not os.path.isabs(file_path):
                    file_path = os.path.join(self.work_dir, file_path)
                    
                # 创建目录
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                
                # 追加模式写入
                with open(file_path, 'a', encoding='utf-8') as f:
                    f.write(arguments["content"])
                return f"成功追加内容到文件: {file_path}"
                
            elif tool_name == "list_directory":
                dir_path = arguments["directory_path"]
                if not os.path.isabs(dir_path):
                    dir_path = os.path.join(self.work_dir, dir_path)
                    
                if os.path.exists(dir_path):
                    items = os.listdir(dir_path)
                    return "\n".join(items) if items else "目录为空"
                else:
                    return f"目录不存在: {dir_path}"
                    
            elif tool_name == "execute_command":
                import subprocess
                result = subprocess.run(
                    arguments["command"],
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=self.work_dir  # 在工作目录中执行命令
                )
                output = result.stdout + result.stderr
                return f"退出码: {result.returncode}\n{output}"
                
            elif tool_name == "execute_python":
                # Qwen特有功能：执行Python代码
                import subprocess
                import tempfile
                
                # 创建临时Python文件
                with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, dir=self.work_dir) as f:
                    f.write(arguments["code"])
                    temp_file = f.name
                
                try:
                    result = subprocess.run(
                        ["python3", temp_file],
                        capture_output=True,
                        text=True,
                        timeout=30,
                        cwd=self.work_dir
                    )
                    output = result.stdout + result.stderr
                    return f"退出码: {result.returncode}\n{output}"
                finally:
                    # 清理临时文件
                    os.unlink(temp_file)
                
            else:
                return f"未知工具: {tool_name}"
                
        except Exception as e:
            return f"工具执行错误: {str(e)}"
    
    def execute_task(self, task: str) -> str:
        """
        执行任务
        
        Args:
            task: 任务描述
            
        Returns:
            执行结果
        """
        print(f"\n[{self.__class__.__name__}] > 执行任务...")
        
        # 构建系统提示词 - 针对Qwen优化
        system_prompt = f"""你是Qwen Coder，一个专业的编程助手，特别擅长代码生成、调试和优化。

{self.interface}

# 重要知识
{self.knowledge}

# 工作目录
{self.work_dir}

# 执行纪律【最高优先级】

## 你的核心优势
- 代码生成能力极强，支持多种编程语言
- 深度推理能力，可以解决复杂问题
- 数学和算法能力出色
- 支持更长的上下文窗口

## 自然语言图灵机 (NLTM) 模式
当任务包含以下特征时，使用NLTM模式：
- 需要多个步骤完成
- 包含条件判断或循环
- 需要维护执行状态
- 可能需要错误恢复
- 需要生成执行报告

NLTM执行流程：
1. 创建 task.nlpl 文件（YAML格式的自然语言程序）
2. 创建 execution.json 文件（执行状态）
3. 按程序步骤执行，每步更新状态
4. 根据执行结果动态调整策略
5. 生成最终报告

## 任务规划原则
复杂任务必须先规划：
1. 评估任务复杂度
2. 选择执行模式：NLTM（复杂）或 TODO（简单）
3. 创建执行计划
4. 逐步执行并验证

## 代码生成策略【Qwen特色】
- 优先使用execute_python工具进行快速原型验证
- 生成代码时注重性能和可读性
- 支持生成更长的代码片段（单次最多8000字符）
- 自动添加类型注解和文档字符串

## 防止精神错乱规则
- 如果连续3次相同操作失败，必须停下重新分析
- 如果连续修改同一文件超过5次，必须读取验证
- 禁止连续使用write_file覆盖同一文件
- 出现循环时，写一个分析报告

# 重要提醒
- 你必须使用工具来完成任务
- 完成任务后必须验证成功条件
- 如果条件不满足，继续执行直到满足

# 处理长内容的强制规则【必须遵守】
当需要生成长文件内容时（如PSM文件、代码文件等），你必须：

1. 严格遵守工具的maxLength约束：
   - write_file: content最多8000字符（Qwen支持更长）
   - append_file: content最多6000字符（更安全的限制）
   
2. 分段策略：
   - 第一次使用write_file创建文件（≤8000字符）
   - 后续使用append_file逐步追加（每次≤6000字符）
   
3. 违反长度限制会导致失败，没有例外

4. 可以并行调用多个append_file来提高效率
"""
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        # 最多执行max_rounds轮
        for round_num in range(self.max_rounds):
            print(f"\n🤔 思考第{round_num + 1}轮...")
            
            # 调用OpenRouter API
            request_body = {
                "model": self.model,
                "messages": messages,
                "temperature": 0.3,  # Qwen推荐更低的温度以保持准确性
                "max_tokens": 8192  # Qwen支持更长的输出
            }
            
            # 只有当有工具时才添加工具相关参数
            if self.tools:
                request_body["tools"] = self.tools
                request_body["tool_choice"] = "auto"
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://github.com/qwen-agent",  # OpenRouter要求
                    "X-Title": "Qwen React Agent"  # 可选，用于OpenRouter统计
                },
                json=request_body
            )
            
            if response.status_code != 200:
                print(f"❌ API错误: {response.text}")
                return f"API错误: {response.text}"
                
            result = response.json()
            
            # 检查是否有错误
            if "error" in result:
                print(f"❌ API返回错误: {result['error']}")
                return f"API错误: {result['error']}"
            
            choice = result["choices"][0]
            message = choice["message"]
            
            # 添加助手回复到消息历史
            messages.append(message)
            
            # 检查是否有工具调用
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    
                    # 解析JSON参数
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError as e:
                        print(f"⚠️ JSON解析错误: {e}")
                        arguments = None
                    
                    # 如果参数解析失败，提供错误响应
                    if arguments is None:
                        tool_result = f"参数解析失败: 无法从JSON中提取{tool_name}的参数"
                        print(f"❌ {tool_result}")
                    else:
                        print(f"🔧 调用工具: {tool_name}")
                        print(f"   参数: {list(arguments.keys()) if isinstance(arguments, dict) else arguments}")
                        
                        # 执行工具
                        try:
                            tool_result = self._execute_tool(tool_name, arguments)
                            # 限制输出长度
                            display_result = tool_result[:200] + "..." if len(tool_result) > 200 else tool_result
                            print(f"💬 工具结果: {display_result}")
                        except Exception as e:
                            tool_result = f"工具执行错误: {str(e)}"
                            print(f"❌ {tool_result}")
                    
                    # 添加工具结果到消息
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,
                        "content": tool_result if isinstance(tool_result, str) else json.dumps(tool_result, ensure_ascii=False)
                    })
            
            # 检查是否完成
            if choice.get("finish_reason") == "stop" and not message.get("tool_calls"):
                print(f"\n✅ 任务完成")
                return message["content"]
        
        print(f"\n⚠️ 达到最大执行轮数")
        return messages[-1]["content"] if messages else "达到最大执行轮数，任务未完成"


def create_qwen_agent(config, name="qwen_agent", max_rounds=300):
    """
    创建Qwen Agent的工厂函数
    
    Args:
        config: ReactAgentConfig配置对象
        name: Agent名称
        max_rounds: 最大执行轮数
        
    Returns:
        QwenReactAgent实例
    """
    return QwenReactAgent(
        work_dir=config.work_dir,
        model=getattr(config, 'llm_model', 'qwen/qwen3-coder'),
        api_key=os.getenv(config.llm_api_key_env),
        knowledge_files=config.knowledge_files,
        interface=getattr(config, 'interface', ''),
        max_rounds=max_rounds
    )