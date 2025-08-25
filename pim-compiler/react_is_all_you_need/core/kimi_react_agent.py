#!/usr/bin/env python3
"""
Kimi专用的React Agent实现
使用Moonshot原生API而不是通过LangChain
"""

import os
import json
import requests
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

class KimiReactAgent:
    """Kimi专用的React Agent"""
    
    def __init__(self, 
                 work_dir: str,
                 model: str = "kimi-k2-turbo-preview",
                 api_key: Optional[str] = None,
                 knowledge_files: Optional[List[str]] = None,
                 interface: str = "",
                 max_rounds: int = 300):
        """
        初始化Kimi Agent
        
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
- content参数不能超过4000字符
- 超过4000字符会导致JSON解析失败
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
                                "description": "文件内容，必须少于4000字符",
                                "maxLength": 4000
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
- content参数必须少于3000字符（留有余量避免JSON错误）
- 超过3000字符会导致失败
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
                                "description": "要追加的内容，必须少于3000字符",
                                "maxLength": 3000
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
        
        # 构建系统提示词
        system_prompt = f"""你是一个专业的AI助手。

{self.interface}

# 重要知识
{self.knowledge}

# 工作目录
{self.work_dir}

# 执行纪律【最高优先级】

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
   - write_file: content最多4000字符
   - append_file: content最多3000字符（更安全的限制）
   
2. 分段策略：
   - 第一次使用write_file创建文件（≤4000字符）
   - 后续使用append_file逐步追加（每次≤3000字符）
   
3. 违反长度限制会导致失败，没有例外

4. 可以并行调用多个append_file来提高效率
"""
        
        # 构建消息
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": task}
        ]
        
        # 最多执行max_rounds轮（复杂任务需要多次工具调用）
        # 典型场景：
        # - 生成完整应用：约50-100轮
        # - 调试修复：约50-150轮  
        # - 复杂工作流：约100-300轮
        for round_num in range(self.max_rounds):
            print(f"\n🤔 思考第{round_num + 1}轮...")
            
            # 调用API
            request_body = {
                "model": self.model,
                "messages": messages,
                "tools": self.tools,
                "temperature": 0.6,  # Kimi推荐的温度设置
                "tool_choice": "auto",  # 明确指定工具选择模式
                "max_tokens": 4096  # 限制单次输出长度，避免截断
            }
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=request_body
            )
            
            if response.status_code != 200:
                print(f"❌ API错误: {response.text}")
                return f"API错误: {response.text}"
                
            result = response.json()
            choice = result["choices"][0]
            message = choice["message"]
            
            # 添加助手回复到消息历史（必须包含完整的tool_calls）
            messages.append(message)
            
            # 检查是否有工具调用
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    
                    # 安全解析JSON参数
                    try:
                        # 先检查参数长度，避免处理过大的数据
                        raw_args_len = len(tool_call["function"]["arguments"])
                        if raw_args_len > 100000:  # 100KB限制
                            print(f"⚠️ 参数过长 ({raw_args_len}字符)，可能需要分块处理")
                        
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError as e:
                        # JSON解析错误是预期的，因为Kimi有时会截断
                        # 不用警告符号，用信息符号
                        print(f"ℹ️ JSON需要修复: {e}")
                        
                        # 尝试多种修复策略
                        raw_args = tool_call["function"]["arguments"]
                        # 不需要显示原始参数，减少输出噪音
                        
                        # 策略1: 手动解析JSON结构（改进版）
                        import re
                        
                        # 尝试匹配常见的工具参数模式
                        if tool_name in ["write_file", "append_file"]:
                            # 匹配 file_path
                            match = re.search(r'"file_path"\s*:\s*"([^"]+)"', raw_args)
                            file_path = match.group(1) if match else None
                            
                            # 改进的content提取方法
                            content_start = raw_args.find('"content"')
                            if content_start != -1:
                                # 找到content字段后的冒号和引号
                                colon_pos = raw_args.find(':', content_start)
                                if colon_pos != -1:
                                    # 跳过空白字符找到开始引号
                                    quote_start = raw_args.find('"', colon_pos)
                                    if quote_start != -1:
                                        # 使用更智能的方法找到结束引号
                                        # 处理可能未完成的JSON（被截断的情况）
                                        quote_end = quote_start + 1
                                        in_escape = False
                                        
                                        while quote_end < len(raw_args):
                                            char = raw_args[quote_end]
                                            if in_escape:
                                                in_escape = False
                                            elif char == '\\':
                                                in_escape = True
                                            elif char == '"':
                                                # 检查后面是否有合理的JSON结构
                                                next_chars = raw_args[quote_end+1:quote_end+10].strip()
                                                if next_chars.startswith('}') or next_chars.startswith(',') or next_chars.startswith('\n}'):
                                                    break
                                            quote_end += 1
                                        
                                        # 如果没找到结束引号，肯定是被截断了
                                        if quote_end >= len(raw_args):
                                            # 使用整个剩余部分作为content
                                            content = raw_args[quote_start+1:]
                                            # 清理末尾可能的不完整转义
                                            if content.endswith('\\'):
                                                content = content[:-1]
                                            print(f"⚠️ JSON被截断，已恢复content (长度: {len(content)}字符)")
                                        else:
                                            content = raw_args[quote_start+1:quote_end]
                                        
                                        # 处理转义字符
                                        try:
                                            # 使用Python的字符串解码来处理转义
                                            content = content.encode().decode('unicode_escape')
                                        except:
                                            # 如果解码失败，手动处理基本转义
                                            content = content.replace('\\n', '\n')
                                            content = content.replace('\\t', '\t')
                                            content = content.replace('\\"', '"')
                                            content = content.replace('\\\\', '\\')
                                        
                                        if file_path and content:
                                            arguments = {"file_path": file_path, "content": content}
                                            print(f"✅ JSON修复成功")
                                        else:
                                            print(f"❌ 无法解析{tool_name}参数: file_path={file_path}, content长度={len(content) if content else 0}")
                                            arguments = None
                                    else:
                                        print(f"❌ 无法找到content的开始引号")
                                        arguments = None
                                else:
                                    print(f"❌ 无法找到content字段的冒号")
                                    arguments = None
                            else:
                                print(f"❌ 无法找到content字段")
                                arguments = None
                                
                        elif tool_name in ["read_file", "list_directory", "execute_command"]:
                            # 这些工具只有一个参数
                            param_name = {
                                "read_file": "file_path",
                                "list_directory": "directory_path",
                                "execute_command": "command"
                            }[tool_name]
                            
                            match = re.search(f'"{param_name}"\\s*:\\s*"([^"]+)"', raw_args)
                            if match:
                                arguments = {param_name: match.group(1)}
                                print(f"✅ JSON修复成功")
                            else:
                                print(f"❌ 无法解析{tool_name}参数")
                                arguments = None
                        else:
                            print(f"❌ 未知工具类型，无法手动解析")
                            arguments = None
                    
                    # 如果参数解析失败，提供错误响应
                    if arguments is None:
                        tool_result = f"参数解析失败: 无法从JSON中提取{tool_name}的参数"
                        print(f"❌ {tool_result}")
                    else:
                        print(f"🔧 调用工具: {tool_name}")
                        # 过滤掉不存在的参数（如content_truncated）
                        if isinstance(arguments, dict):
                            # 只保留工具定义中存在的参数
                            if tool_name in ["write_file", "append_file"]:
                                valid_params = {"file_path", "content"}
                                arguments = {k: v for k, v in arguments.items() if k in valid_params}
                            elif tool_name == "read_file":
                                valid_params = {"file_path"}
                                arguments = {k: v for k, v in arguments.items() if k in valid_params}
                            elif tool_name == "list_directory":
                                valid_params = {"directory_path"}
                                arguments = {k: v for k, v in arguments.items() if k in valid_params}
                            elif tool_name == "execute_command":
                                valid_params = {"command"}
                                arguments = {k: v for k, v in arguments.items() if k in valid_params}
                        print(f"   参数: {list(arguments.keys()) if isinstance(arguments, dict) else arguments}")
                        
                        # 执行工具
                        try:
                            tool_result = self._execute_tool(tool_name, arguments)
                            print(f"💬 工具结果: {tool_result[:200] if len(tool_result) > 200 else tool_result}")
                        except Exception as e:
                            tool_result = f"工具执行错误: {str(e)}"
                            print(f"❌ {tool_result}")
                    
                    # 添加工具结果到消息（必须包含tool_call_id和name）
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": tool_name,  # 官方文档要求包含name字段
                        "content": tool_result if isinstance(tool_result, str) else json.dumps(tool_result, ensure_ascii=False)
                    })
            
            # 检查是否完成
            if choice.get("finish_reason") == "stop" and not message.get("tool_calls"):
                print(f"\n✅ 任务完成")
                return message["content"]
        
        print(f"\n⚠️ 达到最大执行轮数")
        return messages[-1]["content"] if messages else "达到最大执行轮数，任务未完成"


def create_kimi_agent(config, name="kimi_agent", max_rounds=300):
    """
    创建Kimi Agent的工厂函数
    
    Args:
        config: ReactAgentConfig配置对象
        name: Agent名称
        max_rounds: 最大执行轮数
        
    Returns:
        KimiReactAgent实例
    """
    return KimiReactAgent(
        work_dir=config.work_dir,
        model=config.llm_model,
        api_key=os.getenv(config.llm_api_key_env),
        knowledge_files=config.knowledge_files,
        interface=getattr(config, 'interface', ''),
        max_rounds=max_rounds
    )