#!/usr/bin/env python3
"""
ReactAgent Minimal - 极简版本
Agent自己就是智能压缩器，通过写笔记实现记忆
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional, Tuple
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
    from .tool_base import Function, ReadFileTool, WriteFileTool, AppendFileTool, ExecuteCommandTool
    from .tools.search_tool import SearchTool, NewsSearchTool
except ImportError:
    # 支持直接运行此文件
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.tool_base import Function, ReadFileTool, WriteFileTool, AppendFileTool, ExecuteCommandTool
    from core.tools.search_tool import SearchTool, NewsSearchTool


class ReactAgentMinimal(Function):
    """
    极简React Agent
    
    核心理念：
    1. Agent即Function - 可以作为工具被调用
    2. 三层记忆架构 - 工作记忆/情景记忆/语义记忆
    3. 压缩就是认知 - 通过写笔记实现显式压缩
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
                 max_rounds: int = 100,
                 knowledge_files: Optional[List[str]] = None,
):
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
        
        # 移除LLM策略，保持简洁
        
        # API配置 - 根据模型名称智能选择
        if "kimi" in model.lower() or "moonshot" in model.lower():
            # Kimi模型 - 使用Moonshot API
            self.api_key = api_key or os.getenv("MOONSHOT_API_KEY") or self._detect_api_key()
            self.base_url = base_url or "https://api.moonshot.cn/v1"
        elif "deepseek" in model.lower():
            # DeepSeek模型
            self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or self._detect_api_key()
            self.base_url = base_url or "https://api.deepseek.com/v1"
        elif "anthropic" in model.lower() or "claude" in model.lower():
            # Claude模型 - 通过OpenRouter
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or self._detect_api_key()
            self.base_url = base_url or "https://openrouter.ai/api/v1"
        elif "grok" in model.lower() or "claude" in model.lower():
            # grok模型 - 通过OpenRouter
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or self._detect_api_key()
            self.base_url = base_url or "https://openrouter.ai/api/v1"
        elif "gemini" in model.lower():
            # Gemini模型 - 通过OpenRouter（国内访问方便）
            self.api_key = api_key or os.getenv("OPENROUTER_API_KEY") or self._detect_api_key()
            self.base_url = base_url or "https://openrouter.ai/api/v1"
        else:
            # 默认配置
            self.api_key = api_key or self._detect_api_key()
            self.base_url = base_url or self._detect_base_url_for_key(self.api_key)
        
        # 保存极简模式开关（必须先设置，后面会用到）
        
        # Compact记忆配置
        self.compress_config = {
            "model": "x-ai/grok-code-fast-1",  # 聪明、快速、便宜的模型
            "base_url": "https://openrouter.ai/api/v1",
            "api_key": os.getenv("OPENROUTER_API_KEY"),
            "threshold": 70000,  # 触发压缩的token数
            "temperature": 0     # 确定性压缩
        }
        # 添加阈值属性方便访问
        self.compact_threshold = 70000
        self.compact_memory = None  # 存储压缩后的记忆
        
        # 知识文件（自然语言程序）- 支持包和单独文件
        self.knowledge_files = self._resolve_knowledge_files(knowledge_files or [])
        
        # 加载极简system包
        knowledge_dir = Path(__file__).parent.parent / "knowledge"
        self._load_knowledge_package(knowledge_dir / "minimal" / "system")
        
        self.knowledge_content = self._load_knowledge()
        
        # 🌟 Compact记忆系统 - Agent自己就是智能压缩器！
        # 不再需要滑动窗口，使用智能压缩
        # 使用name创建独立的笔记目录
        self.agent_name = name  # 保留agent_name字段以兼容
        
        # Agent的大脑放在用户home目录，而不是工作目录
        # 这样清空工作目录不会影响Agent的记忆
        home_dir = Path.home()
        self.agent_home = home_dir / ".agent" / name
        self.notes_dir = self.agent_home  # 兼容旧代码
        
        # 总是创建agent_home目录（即使在minimal模式下也需要）
        # 因为TodoTool需要在这里保存task_process文件
        self.agent_home.mkdir(parents=True, exist_ok=True)
            
        # Compact模式不使用这些记忆文件
        # 只保留变量名以保持兼容性
        self.agent_knowledge_file = self.agent_home / "agent_knowledge.md"
        self.task_process_file = self.agent_home / f"task_process_{self.work_dir.name}.md"
        self.world_state_file = self.agent_home / "world_state.md"
        self.notes_file = self.notes_dir / "session_notes.md"  # 兼容性
        
        # 创建Function实例（包括工具和Agent）
        self.function_instances = self._create_function_instances()
        # 生成函数定义（用于API调用）
        self.functions = [func.to_openai_function() for func in self.function_instances]
        
        # Session目录（也放在Agent home，不污染工作目录）
        self.sessions_dir = self.agent_home / "sessions"
        # 总是创建sessions目录（用于记录执行历史）
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # 自动加载记忆文件（基础设施保证）
        self._auto_load_memory()
        
        # 初始化消息列表（在Agent初始化时，而不是任务执行时）
        self.messages = [
            {"role": "system", "content": self._build_minimal_prompt()}
        ]
        
        # 尝试加载compact.md（如果存在）
        if self._load_compact_memory():
            print(f"  ✨ 已加载Compact记忆")
        
        # 显示初始化信息
        print(f"🚀 极简Agent已初始化 [{self.agent_name}]")
        print(f"  📍 API: {self._detect_service()}")
        print(f"  🤖 模型: {self.model}")
        print(f"  🧠 Compact记忆: 70k tokens触发压缩")
        print(f"  ⚡ Compact记忆替代文件系统")
        if self.knowledge_files:
            print(f"  📚 知识文件: {len(self.knowledge_files)}个")
        print(f"  ✨ Compact即注意力机制")
    
    def _auto_load_memory(self) -> None:
        """自动加载记忆文件"""
        # Compact哲学："遗忘即优化"、"当下即永恒"
        # 不加载任何历史记忆文件
        pass
    
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
        # 重定向标准输出到output.log
        import sys
        output_log_path = self.notes_dir / "output.log"
        
        # 确保目录存在（用于output.log）
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存原始stdout
        original_stdout = sys.stdout
        
        # 创建线程安全的Tee类，同时输出到控制台和文件
        import threading
        class Tee:
            def __init__(self, *files):
                self.files = files
                self.lock = threading.Lock()
            def write(self, obj):
                with self.lock:
                    for f in self.files:
                        try:
                            f.write(obj)
                            f.flush()
                        except ValueError:
                            # 忽略closed file错误
                            pass
            def flush(self):
                with self.lock:
                    for f in self.files:
                        try:
                            f.flush()
                        except ValueError:
                            pass
        
        # 打开日志文件（追加模式）- 两种模式都需要（用于debug）
        log_file = open(output_log_path, 'a', encoding='utf-8')
        
        # 设置stdout同时输出到控制台和文件
        sys.stdout = Tee(original_stdout, log_file)
        
        try:
            print(f"\n[极简Agent] 执行任务...")
            print(f"📝 任务: {task[:100]}...")
            print(f"⏰ 时间: {datetime.now()}")
            print("="*60)
            
            # 记录任务开始时间
            self.task_start_time = datetime.now()
            self.current_task = task
            
            # 执行任务的主逻辑将在try块中
            result = self._execute_task_impl(task, original_stdout, log_file)
            
            # Compact模式不保存session
            
            return result
        except Exception as e:
            print(f"\n❌ 任务执行出错: {e}")
            
            # Compact模式不保存session
            
            raise
        finally:
            # 始终恢复stdout并关闭日志文件（包括Jupyter中断的情况）
            try:
                sys.stdout = original_stdout
            except:
                pass
            try:
                if log_file and not log_file.closed:
                    log_file.close()
            except:
                pass
    
    def _execute_task_impl(self, task: str, original_stdout, log_file) -> str:
        """实际执行任务的实现"""
        import sys
        
        # 处理斜杠命令
        if task.strip().startswith("/"):
            return self._handle_slash_command(task.strip())
        
        # 添加用户任务到消息列表（消息列表已在__init__中初始化）
        self.messages.append({"role": "user", "content": task})
        
        # 执行循环
        for round_num in range(self.max_rounds):
            print(f"\n🤔 思考第{round_num + 1}轮...")
            
            # 调用LLM（使用实例的消息列表）
            response = self._call_api(self.messages)
            if response is None:
                return "API调用失败"
            
            # 处理响应
            message = response["choices"][0]["message"]
            self.messages.append(message)  # 添加assistant消息到对话历史
            
            # Compact记忆管理 - 智能压缩替代滑动窗口
            token_count = self._count_tokens(self.messages)
            if token_count > self.compress_config["threshold"]:
                self.messages = self._compact_messages(self.messages)
            
            # 显示LLM的思考内容（如果有）
            if message.get("content"):
                content_preview = message["content"][:200]
                if len(content_preview) > 0:
                    print(f"💭 思考: {content_preview}...")
            
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
                        self.messages.append(tool_message)
                        
                        # 消息会被添加到self.messages列表，自动影响窗口大小
                        
                    except Exception as e:
                        tool_error = f"工具执行错误: {e}"
                        tool_message = {
                            "role": "tool",
                            "tool_call_id": tool_call_id,
                            "content": tool_error
                        }
                        self.messages.append(tool_message)
                        # 错误消息也会被添加到self.messages列表
            
            # 检查是否完成
            if response["choices"][0].get("finish_reason") == "stop" and not message.get("tool_calls"):
                print(f"\n✅ 任务完成（第{round_num + 1}轮）")
                return message.get("content", "任务完成")
        
        print(f"\n⚠️ 达到最大轮数")
        return "达到最大执行轮数"
    
    def _resolve_knowledge_files(self, knowledge_files: List[str]) -> List[str]:
        """解析知识文件列表，支持包和单独文件
        
        支持的格式：
        - 单个文件：'knowledge/file.md'
        - 整个包：'knowledge/system' （加载包内所有.md文件）
        - 通配符：'knowledge/system/*.md'
        """
        resolved_files = []
        knowledge_dir = Path(__file__).parent.parent / "knowledge"
        
        for item in knowledge_files:
            path = Path(item)
            
            # 如果是相对路径，基于knowledge目录
            if not path.is_absolute():
                # 如果路径已经包含"knowledge/"前缀，去掉它
                if str(path).startswith("knowledge/"):
                    path = knowledge_dir / str(path).replace("knowledge/", "", 1)
                else:
                    path = knowledge_dir / path
            
            if path.is_dir():
                # 如果是目录，加载其中所有.md文件
                md_files = sorted(path.glob("*.md"))
                for md_file in md_files:
                    if str(md_file) not in resolved_files:
                        resolved_files.append(str(md_file))
            elif path.exists() and path.suffix == '.md':
                # 如果是单个.md文件
                if str(path) not in resolved_files:
                    resolved_files.append(str(path))
            elif '*' in str(path):
                # 如果包含通配符
                parent = path.parent
                pattern = path.name
                if parent.exists():
                    matching_files = sorted(parent.glob(pattern))
                    for match in matching_files:
                        if str(match) not in resolved_files:
                            resolved_files.append(str(match))
        
        return resolved_files
    
    def _load_knowledge_package(self, package_path: Path):
        """加载知识包
        
        优先级规则：
        1. __init__.md中export的文件（如果存在）
        2. 包内所有.md文件（如果没有__init__.md）
        """
        if not package_path.exists():
            return
        
        init_file = package_path / "__init__.md"
        
        if init_file.exists():
            # 读取__init__.md，解析导出模块
            init_content = init_file.read_text(encoding='utf-8')
            
            # 解析导出模块部分
            if "## 导出模块" in init_content or "## 导出模块（默认加载）" in init_content:
                # 提取导出模块列表
                lines = init_content.split('\n')
                in_export_section = False
                for line in lines:
                    if "## 导出模块" in line:
                        in_export_section = True
                        continue
                    elif in_export_section:
                        if line.startswith("## ") and "导出模块" not in line:
                            # 遇到下一个section，停止解析
                            break
                        elif line.strip().startswith("- `") and ".md`" in line.strip():
                            # 提取文件名，格式：- `filename.md` - 描述
                            # 注意：描述可能包含其他内容，所以不能用endswith
                            start = line.find("`") + 1
                            end = line.find(".md`") + 3
                            if end > start:
                                filename = line[start:end]
                                md_file = package_path / filename
                                if md_file.exists() and str(md_file) not in self.knowledge_files:
                                    # 系统包的文件优先级最高，插入到最前面
                                    if "system" in str(package_path):
                                        self.knowledge_files.insert(0, str(md_file))
                                    else:
                                        self.knowledge_files.append(str(md_file))
                return  # 如果有导出定义，只加载导出的文件
        
        # 如果没有__init__.md或没有导出定义，加载包内所有.md文件（除了__init__.md）
        for md_file in sorted(package_path.glob("*.md")):
            if md_file.name != "__init__.md":
                if str(md_file) not in self.knowledge_files:
                    # 系统包的文件优先级最高，插入到最前面
                    if "system" in str(package_path):
                        self.knowledge_files.insert(0, str(md_file))
                    else:
                        self.knowledge_files.append(str(md_file))
    
    def _build_minimal_prompt(self) -> str:
        """构建极简系统提示"""
        # 使用极简提示词模板
        prompt_template_path = Path(__file__).parent.parent / "knowledge" / "minimal" / "system" / "system_prompt_minimal.md"
        
        if prompt_template_path.exists():
            # 使用外部模板
            template = prompt_template_path.read_text(encoding='utf-8')
            
            # Compact模式不需要元记忆
            meta_memory = ""
            
            # 准备知识内容部分
            knowledge_section = ""
            if self.knowledge_content:
                knowledge_section = f"\n## 知识库（可参考的自然语言程序）\n**说明**：以下是已加载的知识文件内容，直接参考使用，无需再去文件系统查找。\n\n{self.knowledge_content}"
            
            # 注入Compact记忆
            if self.compact_memory:
                knowledge_section += f"\n\n## 压缩记忆\n{self.compact_memory}"
            
            # 替换模板中的占位符
            # 注意：system_prompt.md中的{{agent_name}}是转义的，会变成{agent_name}
            # 而{agent_name}需要被替换
            prompt = template.format(
                work_dir=self.work_dir,
                notes_dir=self.notes_dir,
                notes_file=self.notes_file,
                meta_memory=meta_memory,
                knowledge_content=knowledge_section,
                agent_name=self.agent_name
            )
        else:
            # 降级到内置提示词（保持向后兼容）
            meta_memory = ""
            if self.notes_file.exists():
                meta_memory = f"\n[元记忆] 发现之前的笔记: {self.notes_file}\n首次需要时，使用read_file查看。\n"
            
            prompt = f"""你是一个编程助手，像数学家一样使用笔记扩展认知。
你只能写工作目录和笔记目录下的文件，别的地方可以读，但不能写。
            
工作目录：{self.work_dir}
笔记目录：{self.notes_dir}
{meta_memory}
认知模型（Compact记忆）：
- 工作记忆通过智能压缩管理
- 超过70k tokens自动压缩保留关键信息

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
    
    def append_tool(self, tool):
        """
        添加Function到Agent的function列表（保留方法名以兼容）
        
        Args:
            tool: Function实例（工具或另一个Agent）
        """
        # 检查是否有必要的方法（鸭子类型）
        if not hasattr(tool, 'execute') or not hasattr(tool, 'to_openai_function'):
            raise TypeError(f"Function必须有execute和to_openai_function方法")
        
        self.function_instances.append(tool)
        self.functions = [f.to_openai_function() for f in self.function_instances]
        
        # 显示添加的工具信息
        tool_name = tool.name if hasattr(tool, 'name') else str(tool)
        print(f"  ➕ 已添加工具: {tool_name}")
    
    def add_function(self, function):
        """
        添加Function（工具或Agent）的别名方法
        项目经理Agent可以通过此方法添加子Agent作为工具
        
        Args:
            function: Function实例（可以是工具或另一个Agent）
        """
        return self.append_tool(function)
    
    def _create_function_instances(self) -> List[Function]:
        """创建Function实例（包括工具和Agent）"""
        # 导入ExecutionContext（原TodoTool）
        from tools.execution_context import ExecutionContext
        
        # 基础工具集
        tools = [
            ExecutionContext(),  # 内存中的任务记录本
            ReadFileTool(self.work_dir),
            WriteFileTool(self.work_dir),
            AppendFileTool(self.work_dir),  # 追加文件工具
            ExecuteCommandTool(self.work_dir),
            SearchTool()  # 搜索工具作为默认工具
        ]
        
        # 添加新闻搜索工具（如果API密钥存在）
        try:
            if os.getenv("SERPER_API_KEY"):
                tools.append(NewsSearchTool())
        except Exception as e:
            # 如果新闻搜索工具初始化失败，继续运行但不添加新闻搜索功能
            pass
        
        return tools
    
    def _switch_model(self, new_model: str) -> None:
        """切换模型并更新API配置"""
        self.model = new_model
        
        # 根据新模型更新API配置
        if "kimi" in new_model.lower() or "moonshot" in new_model.lower():
            self.api_key = os.getenv("MOONSHOT_API_KEY")
            self.base_url = "https://api.moonshot.cn/v1"
        elif "deepseek" in new_model.lower():
            self.api_key = os.getenv("DEEPSEEK_API_KEY")
            self.base_url = "https://api.deepseek.com/v1"
        elif "x-ai/grok" in new_model.lower():  # Grok模型通过OpenRouter
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.base_url = "https://openrouter.ai/api/v1"
        elif "/" in new_model:  # 其他OpenRouter模型格式
            self.api_key = os.getenv("OPENROUTER_API_KEY")
            self.base_url = "https://openrouter.ai/api/v1"
        else:
            # 保持现有配置
            pass
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """执行工具 - 使用Tool实例"""
        try:
            # 查找对应的工具实例
            for tool in self.function_instances:  # 查找对应的function实例
                if tool.name == tool_name:
                    return tool.execute(**arguments)
            
            return f"未知工具: {tool_name}"
                
        except Exception as e:
            return f"工具执行错误: {str(e)}"
    
    def _call_api(self, messages: List[Dict]) -> Optional[Dict]:
        """调用API - 极简版本（带重试）"""
        import time
        
        # 保持单一模型，不做切换
        
        max_retries = 3
        retry_delay = 2  # 秒
        
        for attempt in range(max_retries):
            try:
                # 准备请求数据
                request_data = {
                    "model": self.model,
                    "messages": messages,
                    "tools": self.functions,  # OpenAI API仍然使用"tools"参数名
                    "tool_choice": "auto",
                    "temperature": 0.3,
                    "max_tokens": 4096
                }
                
                # 对于中国的API服务，不使用代理
                proxies = None
                if 'moonshot.cn' in self.base_url or 'deepseek.com' in self.base_url:
                    # 禁用代理 - 使用空字符串覆盖环境变量
                    proxies = {
                        'http': '',
                        'https': '',
                        'all': ''
                    }
                
                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data,
                    timeout=180,  # 增加到180秒，处理大型任务
                    proxies=proxies
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
            return "Moonshot/Kimi"
        elif "openrouter" in base_url_lower:
            return "OpenRouter"
        elif "generativelanguage.googleapis.com" in base_url_lower:
            return "Gemini"
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
                    "required": []  # Grok可能对required字段敏感，先设为空数组
                }
            }
        }
    
    def _count_tokens(self, messages: List[Dict]) -> int:
        """估算消息列表的token数"""
        # 简单估算：平均每个字符约0.25个token（中文约0.5个token）
        total_chars = sum(len(str(msg)) for msg in messages)
        return int(total_chars * 0.3)  # 保守估计
    
    def _save_compact_memory(self):
        """保存压缩后的记忆到compact.md"""
        compact_file = self.notes_dir / "compact.md"
        
        # 确保目录存在
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        
        # 准备内容
        content = [f"""# Compact Memory - {self.name}

生成时间: {datetime.now().isoformat()}
消息数量: {len(self.messages)}
预估tokens: {self._count_tokens(self.messages)}

## 压缩的对话历史

"""]
        
        # 添加消息内容
        for i, msg in enumerate(self.messages, 1):
            role = msg.get("role", "unknown")
            content_text = msg.get("content", "")
            
            if role == "system":
                content.append(f"### 系统消息 {i}\n{content_text[:500]}...\n\n")
            elif role == "user":
                content.append(f"### 用户消息 {i}\n{content_text}\n\n")
            elif role == "assistant":
                content.append(f"### Assistant消息 {i}\n{content_text[:1000]}...\n\n")
            elif role == "tool":
                content.append(f"### 工具响应 {i}\n{content_text[:500]}...\n\n")
        
        # 写入文件
        compact_file.write_text(''.join(content), encoding='utf-8')
    
    def _load_compact_memory(self):
        """从compact.md加载压缩的记忆"""
        compact_file = self.notes_dir / "compact.md"
        
        if not compact_file.exists():
            return False
        
        print(f"  📚 加载Compact记忆: compact.md")
        
        # 读取文件但不直接解析成消息
        # 而是作为一个系统消息添加到对话开始
        compact_content = compact_file.read_text(encoding='utf-8')
        
        # 提取关键信息作为系统上下文
        compact_summary = f"""
[之前的Compact记忆已加载]
该记忆包含了之前对话的压缩版本。
请基于这些记忆继续对话。

{compact_content[:2000]}...
"""
        
        # 在系统消息后插入compact记忆
        if len(self.messages) > 0 and self.messages[0]["role"] == "system":
            self.messages.insert(1, {"role": "system", "content": compact_summary})
        else:
            self.messages.insert(0, {"role": "system", "content": compact_summary})
        
        return True
    
    def _handle_slash_command(self, command: str) -> str:
        """处理斜杠命令"""
        cmd = command.lower().strip()
        
        if cmd == "/compact":
            # 手动触发compact压缩（不检查阈值）
            print("\n🧠 手动触发Compact压缩...")
            
            if len(self.messages) <= 1:
                return "📝 当前对话历史为空，无需压缩"
            
            # 显示压缩前的信息
            original_count = len(self.messages)
            original_tokens = self._count_tokens(self.messages)
            print(f"  压缩前: {original_count} 条消息, 约 {original_tokens} tokens")
            
            # 执行压缩（传入manual=True参数表示手动触发）
            self.messages = self._compact_messages(self.messages, manual=True)
            
            # 显示压缩后的信息
            new_count = len(self.messages)
            new_tokens = self._count_tokens(self.messages)
            print(f"  压缩后: {new_count} 条消息, 约 {new_tokens} tokens")
            print(f"  压缩率: {(1 - new_tokens/original_tokens)*100:.1f}%")
            
            # 保存压缩结果到compact.md
            self._save_compact_memory()
            print(f"  💾 已保存到: {self.notes_dir}/compact.md")
            
            return f"✨ Compact压缩完成！{original_count}条消息 → {new_count}条消息"
        
        elif cmd == "/help":
            return """
📚 可用的斜杠命令：
  /compact - 手动触发Compact压缩
  /help    - 显示此帮助信息
"""
        
        else:
            return f"❌ 未知命令: {command}\n💡 输入 /help 查看可用命令"
    
    
    def _compact_messages(self, messages: List[Dict], manual: bool = False) -> List[Dict]:
        """智能压缩对话历史 - 使用description作为注意力先验
        
        Args:
            messages: 消息列表
            manual: 是否手动触发（手动触发时不显示阈值信息）
        """
        if not manual:
            print(f"\n🧠 触发Compact压缩（超过70k tokens）...")
        else:
            print(f"\n🧠 执行Compact压缩...")
        
        # 构建压缩提示词 - 将description作为注意力框架
        if self.description:
            compress_prompt = f"""你是一个对话历史压缩专家。

Agent描述（注意力框架）：
{self.description}

基于上述Agent的专业身份和职责，压缩对话历史时请重点关注与其相关的内容。

压缩原则：
1. 保留关键决策和重要结论
2. 保留错误和解决方案
3. 去除重复和冗余信息
4. 保持时间顺序和因果关系
5. 重点关注与Agent职责相关的核心内容

输出格式：
- 使用Markdown格式
- 按主题分组相关内容
- 突出重要的代码变更和设计决策"""
        else:
            # 无description时使用通用压缩
            compress_prompt = """你是一个对话历史压缩专家。请将冗长的对话历史压缩成精炼的摘要。

压缩原则：
1. 保留关键决策和重要结论
2. 保留错误和解决方案
3. 去除重复和冗余信息
4. 保持时间顺序和因果关系
5. 重点关注与任务相关的核心内容

输出格式：
- 使用Markdown格式
- 按主题分组相关内容
- 突出重要的代码变更和设计决策"""
        
        # 分离系统消息和对话消息
        system_msgs = [m for m in messages if m["role"] == "system"]
        dialogue_msgs = [m for m in messages if m["role"] != "system"]
        
        # 调用压缩模型
        try:
            compress_messages = [
                {"role": "system", "content": compress_prompt},
                {"role": "user", "content": f"请压缩以下对话历史：\n\n{json.dumps(dialogue_msgs, ensure_ascii=False, indent=2)}"}
            ]
            
            compress_response = requests.post(
                f"{self.compress_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.compress_config['api_key']}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.compress_config["model"],
                    "messages": compress_messages,
                    "temperature": self.compress_config["temperature"]
                }
            )
            
            if compress_response.status_code == 200:
                compressed_content = compress_response.json()["choices"][0]["message"]["content"]
                
                # 保存压缩记忆
                self.compact_memory = compressed_content
                
                print(f"  ✅ 压缩完成，保留关键信息")
                
                # 创建压缩后的消息对
                # 使用user/assistant对来保持消息交替格式
                compressed_messages = [
                    {"role": "user", "content": "[请基于以下压缩的历史记忆继续对话]"},
                    {"role": "assistant", "content": f"[已加载压缩的历史记忆]\n{compressed_content}"}
                ]
                
                # 返回新的消息列表：系统消息 + 压缩的消息对
                return system_msgs + compressed_messages
            else:
                print(f"  ⚠️ 压缩失败，保留最近消息")
                # 压缩失败时的降级策略：保留最近的1/3消息
                keep_count = max(2, len(dialogue_msgs) // 3)
                # 确保从user消息开始，保持交替格式
                kept_msgs = dialogue_msgs[-keep_count:]
                if kept_msgs and kept_msgs[0]["role"] == "assistant":
                    # 如果第一条是assistant消息，去掉它
                    kept_msgs = kept_msgs[1:]
                # 确保消息数量是偶数（user/assistant成对）
                if len(kept_msgs) % 2 != 0:
                    kept_msgs = kept_msgs[1:]
                return system_msgs + kept_msgs
                
        except Exception as e:
            print(f"  ⚠️ 压缩出错: {e}，保留最近消息")
            # 出错时的降级策略（与压缩失败时相同）
            keep_count = max(2, len(dialogue_msgs) // 3)
            kept_msgs = dialogue_msgs[-keep_count:]
            if kept_msgs and kept_msgs[0]["role"] == "assistant":
                kept_msgs = kept_msgs[1:]
            if len(kept_msgs) % 2 != 0:
                kept_msgs = kept_msgs[1:]
            return system_msgs + kept_msgs
    
    def save_template(self, filepath: str = "agent_template.json") -> str:
        """
        保存Agent模板 - 用于创建新Agent
        包含Function接口定义和配置，不包含运行时状态
        """
        template = {
            "type": "agent_template",
            "version": "1.0",
            "function_meta": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "return_type": self.return_type
            },
            "config": {
                "model": self.model,
                "base_url": self.base_url,
                "max_rounds": self.max_rounds,
                "knowledge_files": self.knowledge_files,
                "compress_config": self.compress_config
            }
        }
        
        file_path = Path(filepath)
        with open(str(file_path), 'w', encoding='utf-8') as f:
            json.dump(template, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Agent模板已保存: {file_path}")
        return str(file_path)
    
    @classmethod
    def create_from_template(cls, template_file: str, work_dir: str, **kwargs):
        """
        从模板创建新Agent实例
        
        Args:
            template_file: 模板文件路径
            work_dir: 新Agent的工作目录
            **kwargs: 覆盖模板中的配置
        """
        with open(template_file, 'r', encoding='utf-8') as f:
            template = json.load(f)
        
        if template.get("type") != "agent_template":
            raise ValueError(f"Invalid template type: {template.get('type')}")
        
        # 合并配置
        config = template["config"].copy()
        config.update(kwargs)
        
        # 分离compress_config（不是__init__参数）
        compress_config = config.pop("compress_config", None)
        
        # 创建Agent
        agent = cls(
            work_dir=work_dir,
            name=template["function_meta"]["name"],
            description=template["function_meta"]["description"],
            parameters=template["function_meta"]["parameters"],
            return_type=template["function_meta"]["return_type"],
            **config
        )
        
        # 恢复compress_config
        if compress_config:
            agent.compress_config = compress_config
        
        print(f"✨ 从模板创建Agent: {template['function_meta']['name']}")
        return agent
    
    def save_instance(self, messages: List[Dict], filepath: str = "agent_instance.json") -> str:
        """
        保存Agent实例 - 包含完整运行时状态
        可用于中断恢复、Agent迁移、调试回放
        
        Args:
            messages: 当前对话消息列表
            filepath: 保存路径
        """
        instance = {
            "type": "agent_instance",
            "version": "1.0",
            "timestamp": datetime.now().isoformat(),
            
            # Function接口（其他Agent调用时需要）
            "function_meta": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
                "return_type": self.return_type
            },
            
            # 核心运行时状态
            "state": {
                "messages": messages,  # 完整对话历史
                "compact_memory": self.compact_memory,  # 压缩记忆
                "round_count": len([m for m in messages if m["role"] == "assistant"])
            },
            
            # 运行环境
            "runtime": {
                "work_dir": str(self.work_dir),
                "agent_name": self.agent_name,
                "notes_dir": str(self.notes_dir)
            },
            
            # 配置
            "config": {
                "model": self.model,
                "base_url": self.base_url,
                "max_rounds": self.max_rounds,
                "compress_config": self.compress_config,
                "knowledge_files": self.knowledge_files
            }
        }
        
        file_path = Path(filepath)
        with open(str(file_path), 'w', encoding='utf-8') as f:
            json.dump(instance, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Agent实例已保存: {file_path} ({len(messages)}条消息)")
        return str(file_path)
    
    @classmethod
    def restore_instance(cls, instance_file: str, new_work_dir: Optional[str] = None):
        """
        恢复Agent实例
        
        Args:
            instance_file: 实例文件路径
            new_work_dir: 新的工作目录（可选，用于迁移）
        
        Returns:
            (agent, messages): 恢复的Agent和消息列表
        """
        with open(instance_file, 'r', encoding='utf-8') as f:
            instance = json.load(f)
        
        if instance.get("type") != "agent_instance":
            raise ValueError(f"Invalid instance type: {instance.get('type')}")
        
        # 决定工作目录
        work_dir = new_work_dir or instance["runtime"]["work_dir"]
        
        # 准备配置
        config = instance["config"].copy()
        compress_config = config.pop("compress_config", None)
        
        # 创建Agent
        agent = cls(
            work_dir=work_dir,
            name=instance["function_meta"]["name"],
            description=instance["function_meta"]["description"],
            parameters=instance["function_meta"]["parameters"],
            return_type=instance["function_meta"]["return_type"],
            **config
        )
        
        # 恢复compress_config
        if compress_config:
            agent.compress_config = compress_config
        
        # 恢复运行时状态
        agent.compact_memory = instance["state"]["compact_memory"]
        messages = instance["state"]["messages"]
        
        print(f"🔄 Agent实例已恢复: {instance['function_meta']['name']}")
        print(f"  📊 包含{len(messages)}条消息")
        if agent.compact_memory:
            print(f"  🧠 包含压缩记忆")
        
        return agent, messages
    
    def continue_from_messages(self, messages: List[Dict], additional_task: Optional[str] = None) -> str:
        """
        从保存的消息列表继续执行
        
        Args:
            messages: 恢复的消息列表
            additional_task: 附加任务（可选）
        """
        if additional_task:
            messages.append({"role": "user", "content": additional_task})
        
        # 继续执行
        print(f"\n🔄 继续执行任务...")
        
        # 使用恢复的消息继续React循环
        original_stdout = sys.stdout
        log_file = None
        
        try:
            # 继续执行循环
            for round_num in range(len(messages), self.max_rounds):
                # 调用API
                response = self._call_api(messages)
                if not response:
                    break
                
                # 处理响应
                message = response["choices"][0]["message"]
                messages.append(message)
                
                # Compact记忆管理
                token_count = self._count_tokens(messages)
                if token_count > self.compress_config["threshold"]:
                    messages = self._compact_messages(messages)
                
                # 检查完成
                if response["choices"][0].get("finish_reason") == "stop" and not message.get("tool_calls"):
                    result = message.get("content", "任务完成")
                    print(f"\n✅ 任务完成（第{round_num + 1}轮）")
                    return result
                
                # 处理工具调用
                if "tool_calls" in message and message["tool_calls"]:
                    for tool_call in message["tool_calls"]:
                        tool_result = self._execute_tool(
                            tool_call["function"]["name"],
                            json.loads(tool_call["function"]["arguments"])
                        )
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call["id"],
                            "content": tool_result
                        })
            
            return "达到最大轮数限制"
            
        except Exception as e:
            print(f"❌ 继续执行出错: {e}")
            return f"错误: {e}"
        finally:
            # 安全地恢复stdout和关闭文件
            try:
                sys.stdout = original_stdout
            except:
                pass
            try:
                if log_file and not log_file.closed:
                    log_file.close()
            except:
                pass
    
    def _save_session(self, task: str, result: str, status: str) -> None:
        """
        保存session记录（仅在完整模式下）
        
        注意：minimal模式下不保存session，符合Compact哲学：
        - "当下即永恒"：不需要历史记录
        - "遗忘即优化"：没有审计追踪
        
        Args:
            task: 执行的任务
            result: 任务结果
            status: 任务状态 (completed/failed)
        """
        try:
            # 生成带真实时间戳的文件名
            timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
            
            # 生成安全的任务简述（去除特殊字符）
            import re
            safe_summary = re.sub(r'[^\w\s-]', '', task[:50].replace('\n', ' '))
            safe_summary = safe_summary.strip().replace(' ', '_')
            
            # 生成session文件名
            session_filename = f"{timestamp}_{safe_summary}.md"
            session_path = self.sessions_dir / session_filename
            
            # 计算执行时长
            duration = datetime.now() - self.task_start_time
            
            # 构建session内容
            session_content = f"""# Session: {self.agent_name}

## 任务信息
- **开始时间**: {self.task_start_time.strftime('%Y-%m-%d %H:%M:%S')}
- **结束时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **执行时长**: {duration}
- **状态**: {status}
- **Agent**: {self.agent_name}
- **模型**: {self.model}

## 任务描述
```
{task}
```

## 执行结果
```
{result[:5000] if len(result) > 5000 else result}
```

## 记忆文件
- agent_knowledge.md
- world_state.md  
- task_process.md
"""
            
            # 写入session文件
            session_path.write_text(session_content, encoding='utf-8')
            print(f"\n💾 Session已保存: {session_filename}")
            
        except Exception as e:
            print(f"\n⚠️ Session保存失败: {e}")
    
    def query_sessions(self, pattern: Optional[str] = None, limit: int = 10) -> str:
        """
        查询历史session（按需查询工具）
        
        Args:
            pattern: 搜索模式（可选）
            limit: 返回数量限制
            
        Returns:
            匹配的session信息
        """
        if not self.sessions_dir.exists():
            return "没有找到session记录"
        
        # 获取所有session文件，按时间倒序
        session_files = sorted(self.sessions_dir.glob("*.md"), reverse=True)
        
        if pattern:
            # 如果提供了搜索模式，过滤文件
            import re
            regex = re.compile(pattern, re.IGNORECASE)
            session_files = [f for f in session_files if regex.search(f.read_text(encoding='utf-8'))]
        
        # 限制返回数量
        session_files = session_files[:limit]
        
        if not session_files:
            return "没有找到匹配的session"
        
        # 构建结果
        results = []
        for session_file in session_files:
            # 读取文件前几行获取摘要
            lines = session_file.read_text(encoding='utf-8').split('\n')[:10]
            summary = '\n'.join(lines)
            results.append(f"## {session_file.name}\n{summary}\n...")
        
        return '\n\n'.join(results)
    
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