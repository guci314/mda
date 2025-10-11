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
            with open(env_path,encoding="utf-8") as f:
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
    from .tool_base import Function, ReadFileTool, WriteFileTool, AppendFileTool
    from .tools.search_tool import SearchTool, NewsSearchTool
except ImportError:
    # 支持直接运行此文件
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from core.tool_base import Function, ReadFileTool, WriteFileTool, AppendFileTool
    from core.tools.search_tool import SearchTool, NewsSearchTool


class ReactAgentMinimal(Function):
    """
    极简React Agent
    
    核心理念：
    1. Agent即Function - 可以作为工具被调用
    2. 三层记忆架构 - 工作记忆/情景记忆/状态记忆
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
                 max_rounds: int = 300,
                 knowledge_files: Optional[List[str]] = None,
                 stateful: bool = True,  # 新增：是否保持状态
                 _from_load: bool = False,  # 内部参数：是否从load方法创建
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
        self.stateful = stateful  # 保存状态标志
        self.interceptor = None  # 拦截器钩子，可选功能
        self.children = []  # 子Agent列表（金字塔结构）

        # API配置 - 必须通过参数传入或从.env读取
        self.api_key = api_key or self._detect_api_key()
        self.base_url = base_url or "https://api.deepseek.com/v1"  # 默认DeepSeek

        # Compact记忆配置 - 使用当前Agent的模型配置
        self.compress_config = {
            "model": self.model,  # 使用当前Agent的模型
            "base_url": self.base_url,  # 使用当前Agent的base_url
            "api_key": self.api_key,  # 使用当前Agent的api_key
            "threshold": 70000,  # 触发压缩的token数
            "temperature": 0     # 确定性压缩
        }
        # 添加阈值属性方便访问
        self.compact_threshold = 70000
        self.compact_memory = None  # 存储压缩后的记忆
        
        # 设置agent_name（必须在加载知识文件之前，因为知识文件需要替换模板变量）
        self.agent_name = name  # 保留agent_name字段以兼容

        # 知识文件（自然语言程序）- 支持包和单独文件
        self.knowledge_files = self._resolve_knowledge_files(knowledge_files or [])

        # 加载极简system包和默认验证知识（大道至简版）
        knowledge_dir = Path(__file__).parent.parent / "knowledge"
        self._load_knowledge_package(knowledge_dir / "minimal" / "system")

        # 默认加载自适应验证知识（客观+主观，根据任务类型选择）
        validation_adaptive = knowledge_dir / "minimal" / "validation" / "validation_adaptive.md"
        if validation_adaptive.exists() and str(validation_adaptive) not in self.knowledge_files:
            self.knowledge_files.append(str(validation_adaptive))

        # 默认加载learning_functions知识，让每个Agent都能学习和记忆
        learning_functions = knowledge_dir / "learning_functions.md"
        if learning_functions.exists() and str(learning_functions) not in self.knowledge_files:
            self.knowledge_files.append(str(learning_functions))

        # 默认加载agent_essence知识，让每个Agent理解自己的本质
        agent_essence = knowledge_dir / "minimal" / "agent_essence.md"
        if agent_essence.exists() and str(agent_essence) not in self.knowledge_files:
            self.knowledge_files.append(str(agent_essence))

        # 默认加载model_mappings知识，让Agent知道正确的模型名称映射
        model_mappings = knowledge_dir / "model_mappings.md"
        if model_mappings.exists() and str(model_mappings) not in self.knowledge_files:
            self.knowledge_files.append(str(model_mappings))

        # 默认加载诚实执行机制，防止Agent虚报成功和找借口
        honesty_enforcement = knowledge_dir / "honesty_enforcement.md"
        if honesty_enforcement.exists() and str(honesty_enforcement) not in self.knowledge_files:
            self.knowledge_files.append(str(honesty_enforcement))

        # Home目录: ~/.agent/[agent名]/
        agent_home = Path.home() / ".agent" / self.name
        agent_home.mkdir(parents=True, exist_ok=True)  # 确保home目录存在

        # 个体知识文件
        knowledge = agent_home / "knowledge.md"
        if knowledge.exists() and str(knowledge) not in self.knowledge_files:
            self.knowledge_files.append(str(knowledge))
            # 不在这里打印，统一在_load_all_knowledge_files中打印
        else:
            # 创建新的知识文件
            if not knowledge.exists():
                knowledge.write_text(
                    f"# {self.name} 知识\n\n创建时间: {datetime.now().isoformat()}\n\n"
                    f"## 核心能力\n\n## 决策逻辑\n\n## 经验总结\n\n",
                    encoding='utf-8'
                )
                print(f"  📚 创建统一知识文件: {knowledge}")

        # compact.md不作为知识文件加载，只作为压缩记忆使用

        # 🎯 初始化拦截器系统
        # 1. 系统拦截器（最高优先级）
        from core.interceptors.system_interceptor import SystemInterceptor
        self.system_interceptor = SystemInterceptor(self)

        # 2. 斜杠命令拦截器（次优先级）
        from core.interceptors.minimal_slash_interceptor import MinimalSlashInterceptor
        self.slash_interceptor = MinimalSlashInterceptor(self.name)

        self.knowledge_content = self._load_knowledge()

        # 🌟 Compact记忆系统 - Agent自己就是智能压缩器！
        # 不再需要滑动窗口，使用智能压缩
        # 使用name创建独立的笔记目录
        
        # Agent的大脑放在用户home目录，而不是工作目录
        # 这样清空工作目录不会影响Agent的记忆
        home_dir = Path.home()
        self.agent_home = home_dir / ".agent" / name
        self.notes_dir = self.agent_home  # 兼容旧代码
        
        # 总是创建agent_home目录（即使在minimal模式下也需要）
        # 创建Agent的home目录
        self.agent_home.mkdir(parents=True, exist_ok=True)
            
        # 知识文件路径
        self.knowledge_file = self.agent_home / "knowledge.md"  # 统一的知识文件
        # task_process_file 已废弃，ExecutionContext 现在只存在于内存中
        self.world_state_file = self.agent_home / "world_state.md"
        self.notes_file = self.notes_dir / "session_notes.md"  # 兼容性
        
        # 创建Function实例（包括工具和Agent）
        self.function_instances = self._create_function_instances()

        # 将Agent自己添加到functions列表（元认知：自己调用自己）
        # 注意：只暴露特定的自我管理方法，避免递归调用execute
        self._add_self_management_functions()

        # 生成函数定义（用于API调用）
        self.functions = [func.to_openai_function() for func in self.function_instances]

        # sessions_dir已废弃，不再需要
        
        # 初始化状态跟踪属性
        self._previous_message_count = 0  # 用于检测消息增长

        # 自动加载记忆文件（基础设施保证）
        self._auto_load_memory()

        # 初始化消息列表（在Agent初始化时，而不是任务执行时）
        self.messages = [
            {"role": "system", "content": self._build_minimal_prompt()}
        ]
        
        # 尝试加载compact.md（如果存在）
        if self._load_compact_memory():
            # 将compact记忆作为assistant消息添加到消息列表
            # 这样它会在对话中累积和演化
            if self.compact_memory:
                self.messages.append({
                    "role": "assistant",
                    "content": f"[已加载历史压缩记忆]\n{self.compact_memory}"
                })
                print(f"  ✨ 已加载Compact记忆到消息列表")

        # 尝试加载project_notes.md（如果存在）
        self._load_project_notes()
        
        # 显示初始化信息（延迟到load方法，避免混淆）
        if not _from_load:  # 只在非load创建时显示
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

        特殊处理：如果是self_management调用，执行相应的自我管理方法。

        Args:
            **kwargs: 包含task参数或method/args参数

        Returns:
            任务结果
        """
        # 检查是否是self_management调用
        if "method" in kwargs:
            method_name = kwargs["method"]
            method_args = kwargs.get("args", {})

            # 调用相应的方法
            if method_name == "update_api_config":
                return self.update_api_config(
                    model_name=method_args.get("model_name"),
                    base_url=method_args.get("base_url"),
                    api_key=method_args.get("api_key")
                )
            elif method_name == "update_description":
                return self.update_description(method_args.get("new_description", ""))
            elif method_name == "get_status":
                return self.get_status()
            elif method_name == "update_knowledge":
                return self.update_knowledge(method_args.get("content", ""))
            elif method_name == "update_agent_knowledge":
                return self.update_agent_knowledge()
            elif method_name == "change_work_dir":
                new_work_dir = method_args.get("new_work_dir", "")
                if not new_work_dir:
                    return "错误：change_work_dir方法需要new_work_dir参数"
                return self.change_work_dir(new_work_dir)
            elif method_name == "get_work_dir":
                return self.get_work_dir()
            elif method_name == "execute":
                # 支持子Agent的execute调用，但在_execute_tool中会阻止自己调用自己
                task = method_args.get("task", "")
                if not task:
                    return "错误：execute方法需要task参数"
                # 这里会执行任务，但如果是自己调用自己，会在_execute_tool中被阻止
                return self.execute(task=task)
            else:
                return f"错误：未知的方法 {method_name}"

        # 普通任务执行
        task = kwargs.get("task", "")
        if not task:
            return "错误：未提供任务描述"

        # ===== 纯粹的拦截钩子 =====
        if hasattr(self, 'interceptor') and self.interceptor:
            result = self.interceptor(task)
            if result is not None:
                return result
        # ===== 钩子结束 =====

        # 如果是无状态模式，清空消息历史（保留系统提示）
        if not self.stateful:
            # 重新初始化消息列表，只保留系统提示
            self.messages = [
                {"role": "system", "content": self._build_minimal_prompt()}
            ]
            # 如果有compact记忆，重新加载
            if hasattr(self, 'compact_memory') and self.compact_memory:
                self.messages.append({
                    "role": "assistant", 
                    "content": f"[已加载历史压缩记忆]\n{self.compact_memory}"
                })
        
        # personal_knowledge.md现在在init时作为知识文件加载，不需要在这里重复注入
        # 重定向标准输出到output.log
        import sys
        import os

        # 检查是否禁用stdout重定向
        no_redirect = os.getenv('AGENT_NO_REDIRECT') == '1'

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
        
        # 如果禁用重定向，跳过日志文件处理
        log_file = None
        if not no_redirect:
            # 备份旧的output.log到output_logs目录
            if output_log_path.exists():
                # 创建output_logs目录
                output_logs_dir = self.notes_dir / "output_logs"
                output_logs_dir.mkdir(parents=True, exist_ok=True)

                # 生成带时间戳的备份文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = output_logs_dir / f"output_{timestamp}.log"

                # 移动旧日志到备份目录
                import shutil
                shutil.move(str(output_log_path), str(backup_path))
                print(f"  📦 备份output.log -> {backup_path.name}")

                # 保留最近10个，删除多余的
                log_files = sorted(output_logs_dir.glob("output_*.log"))
                if len(log_files) > 10:
                    # 删除最老的文件
                    for old_log in log_files[:-10]:
                        old_log.unlink()
                        print(f"  🗑️ 删除旧日志: {old_log.name}")

            # 打开新的日志文件（写入模式）
            log_file = open(output_log_path, 'w', encoding='utf-8')

            # 设置stdout同时输出到控制台和文件
            sys.stdout = Tee(original_stdout, log_file)
        else:
            print(f"  ⚠️  stdout重定向已禁用（AGENT_NO_REDIRECT=1）")
        
        try:
            print(f"\n[{self.name}] 执行任务...")
            print(f"[{self.name}] 📝 任务: {task[:100]}...")
            print(f"[{self.name}] ⏰ 时间: {datetime.now()}")
            print(f"[{self.name}] " + "="*60)
            
            # 记录任务开始时间
            self.task_start_time = datetime.now()
            self.current_task = task
            
            # 执行任务的主逻辑将在try块中
            result = self._execute_task_impl(task, original_stdout, log_file)

            # 🔄 自动保存状态（实现"活在文件系统"）
            self._auto_save_state()

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

        # 🎯 拦截器链处理（优先级从高到低）
        if task.strip().startswith("/"):
            # 1. 系统拦截器（最高优先级）
            result = self.system_interceptor.intercept(task.strip())
            if result is not None:
                print(f"[{self.name}] ⚡ 系统命令执行")
                return result

            # 2. 斜杠命令拦截器（工具命令）
            result = self.slash_interceptor.intercept(task.strip())
            if result is not None:
                print(f"[{self.name}] ⚡ 工具命令执行")
                return result

            # 3. 未知斜杠命令
            return f"❓ 未知命令: {task.strip()}\n使用 /help 查看可用命令"
        
        # 添加用户任务到消息列表（消息列表已在__init__中初始化）
        self.messages.append({"role": "user", "content": task})
        
        # 执行循环
        for round_num in range(self.max_rounds):
            print(f"\n[{self.name}] 🤔 思考第{round_num + 1}轮...")
            
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
                    print(f"[{self.name}] 💭 思考: {content_preview}...")
            
            # 处理工具调用
            if "tool_calls" in message and message["tool_calls"]:
                for tool_call in message["tool_calls"]:
                    tool_name = tool_call["function"]["name"]
                    tool_call_id = tool_call["id"]
                    
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                        print(f"\n[{self.name}] 🔧 调用工具: {tool_name}")
                        # 显示工具参数
                        for key, value in arguments.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"   [{self.name}] 📝 {key}: {value[:100]}...")
                            else:
                                print(f"   [{self.name}] 📝 {key}: {value}")
                        
                        tool_result = self._execute_tool(tool_name, arguments)
                        
                        # 显示工具执行结果
                        result_preview = tool_result[:150] if len(tool_result) > 150 else tool_result
                        print(f"   [{self.name}] ✅ 结果: {result_preview}")
                        
                        
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
                print(f"\n[{self.name}] ✅ 任务完成（第{round_num + 1}轮）")
                return message.get("content", "任务完成")
        
        print(f"\n[{self.name}] ⚠️ 达到最大轮数")
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
            
            # 准备知识内容部分
            knowledge_section = ""
            if self.knowledge_content:
                knowledge_section = f"\n## 知识库（可参考的自然语言程序）\n**说明**：以下是已加载的知识文件内容，直接参考使用，无需再去文件系统查找。\n\n{self.knowledge_content}"
            
            # 不在系统提示词中包含Compact记忆
            # Compact记忆应该在消息列表中，这样才能累积和演化
            
            # 替换模板中的占位符
            # 注意：system_prompt.md中的{{agent_name}}是转义的，会变成{agent_name}
            # 而{agent_name}需要被替换
            # 准备知识文件列表字符串
            knowledge_files_str = "\n".join([f"  - {kf}" for kf in self.knowledge_files])

            prompt = template.format(
                work_dir=self.work_dir,
                notes_dir=self.notes_dir,
                notes_file=self.notes_file,
                knowledge_content=knowledge_section,
                agent_name=self.agent_name,
                description=self.description,
                knowledge_files_list=knowledge_files_str
            )
        else:
            # 降级到内置提示词（保持向后兼容）
            prompt = f"""你是一个编程助手，像数学家一样使用笔记扩展认知。
你只能写工作目录和笔记目录下的文件，别的地方可以读，但不能写。

工作目录：{self.work_dir}
笔记目录：{self.notes_dir}
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
                    # 替换知识文件中的模板变量
                    content = content.replace('{agent_name}', self.agent_name)
                    content = content.replace('{work_dir}', str(self.work_dir))
                    content = content.replace('{home_dir}', f'~/.agent/{self.agent_name}')
                    knowledge_content.append(f"=== {path.name} ===\n{content}")
                    print(f"  ✅ 加载知识文件: {path.name}")
                else:
                    print(f"  ⚠️ 知识文件不存在: {file_path}")
            except Exception as e:
                print(f"  ❌ 加载知识文件失败 {file_path}: {e}")
        
        return "\n\n".join(knowledge_content) if knowledge_content else ""
    
    def add_function(self, function):
        """
        添加Function到Agent的function列表
        项目经理Agent可以通过此方法添加子Agent作为工具

        Args:
            function: Function实例（可以是工具或另一个Agent）
        """
        # 检查是否有必要的方法（鸭子类型）
        if not hasattr(function, 'execute') or not hasattr(function, 'to_openai_function'):
            raise TypeError(f"Function必须有execute和to_openai_function方法")

        self.function_instances.append(function)
        self.functions = [f.to_openai_function() for f in self.function_instances]

        # 显示添加的工具信息
        function_name = function.name if hasattr(function, 'name') else str(function)
        print(f"  ➕ 已添加函数: {function_name}")

    def append_tool(self, tool):
        """
        添加工具的兼容性方法（已废弃，请使用add_function）
        保留此方法以保持向后兼容性

        Args:
            tool: Function实例（工具或另一个Agent）
        """
        return self.add_function(tool)
    
    def _create_function_instances(self) -> List[Function]:
        """创建Function实例（包括工具和Agent）"""
        # 导入ExecutionContext（任务管理，只在内存中）
        from tools.execution_context import ExecutionContext
        
        # 基础工具集
        tools = [
            ExecutionContext(),  # 内存中的任务记录本
            ReadFileTool(self.work_dir),
            WriteFileTool(self.work_dir),
            AppendFileTool(self.work_dir),  # 追加文件工具
            SearchTool()  # 搜索工具作为默认工具
        ]

        # 添加ExecuteCommandExtended工具（唯一的命令执行工具）
        try:
            from tools.execute_command_extended import ExecuteCommandExtended
            tools.append(ExecuteCommandExtended(self.work_dir))
        except ImportError:
            # ExecuteCommandExtended是必需的
            raise ImportError("ExecuteCommandExtended工具未找到，请确保execute_command_extended.py存在")
        
        # 添加EditFile工具（安全的文件编辑）
        try:
            from tools.edit_file_tool import EditFileTool, InsertLineTool, DeleteLinesTool
            tools.append(EditFileTool(self.work_dir))
            tools.append(InsertLineTool(self.work_dir))
            tools.append(DeleteLinesTool(self.work_dir))
        except ImportError:
            # 如果导入失败，继续运行
            pass
        
        
        # Claude Code工具已移除 - 使用知识文件方式更灵活
        # 如需Claude Code功能，请加载knowledge/tools/claude_code_cli.md

        # AskClaude工具已移除 - 没有全局视角，不如直接换模型
        # 如需高智力任务，直接使用Claude作为主模型
        # 添加新闻搜索工具（如果API密钥存在）
        try:
            if os.getenv("SERPER_API_KEY"):
                tools.append(NewsSearchTool())
        except Exception as e:
            # 如果新闻搜索工具初始化失败，继续运行但不添加新闻搜索功能
            pass

        # 分形同构：每个Agent默认都有CreateAgentTool能力
        # 让每个Agent都能创建子Agent，实现无限递归
        try:
            from .tools.create_agent_tool import CreateAgentTool
            tools.append(CreateAgentTool(work_dir=str(self.work_dir), parent_agent=self))
        except ImportError:
            # 如果导入失败（比如循环依赖），继续运行
            pass

        return tools
    
    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        """执行工具 - 使用Tool实例"""
        try:
            # 查找对应的工具实例
            for tool in self.function_instances:  # 查找对应的function实例
                if tool.name == tool_name:
                    # 防止agent递归调用自己的execute方法
                    # 但允许调用其他agent的execute方法
                    if tool is self and arguments.get("method") == "execute":
                        return "❌ 错误：Agent不允许递归调用自己的execute方法。请直接执行任务，而不是调用execute。"
                    return tool.execute(**arguments)

            return f"未知工具: {tool_name}"

        except Exception as e:
            return f"工具执行错误: {str(e)}"
    
    def _call_api(self, messages: List[Dict]) -> Optional[Dict]:
        """调用API - 极简版本（带重试）"""
        import time
        import os

        # 保持单一模型，不做切换

        max_retries = 6  # 增加到6次，应对网络不稳定
        retry_delay = 2  # 秒

        # 调试模式
        debug = os.getenv('AGENT_DEBUG') == '1'

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

                if debug:
                    import json
                    msg_size = len(json.dumps(messages))
                    tools_size = len(json.dumps(self.functions))
                    print(f"[DEBUG] Messages大小: {msg_size/1024:.1f}KB, Tools大小: {tools_size/1024:.1f}KB")
                    print(f"[DEBUG] 发送API请求到: {self.base_url}")
                    print(f"[DEBUG] 准备调用requests.post...")

                # 使用环境代理设置（不强制禁用）
                # 如果环境没有代理，requests会自动直连
                # 如果环境有代理，requests会使用代理
                if debug:
                    print(f"[DEBUG] 序列化request_data...")
                    import json
                    payload = json.dumps(request_data)
                    print(f"[DEBUG] Payload大小: {len(payload)/1024:.1f}KB")
                    print(f"[DEBUG] 调用requests.post (timeout=10)...")

                response = requests.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data,
                    timeout=10  # 临时改为10秒以便快速诊断
                )

                if debug:
                    print(f"[DEBUG] requests.post返回，状态码: {response.status_code}")
            
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

        特殊处理：如果是Agent自己，只暴露安全的自我管理方法，
        避免危险的递归调用（如execute）。

        Returns:
            OpenAI格式的函数定义
        """
        # ReactAgentMinimal实例返回特殊格式，暴露所有方法
        if isinstance(self, ReactAgentMinimal):
            # 这是Agent自己，暴露所有主要方法
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": f"{self.description} - 可调用管理方法进行自我管理",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "method": {
                                "type": "string",
                                "enum": [
                                    "execute",
                                    "update_api_config",
                                    "update_description",
                                    "get_status",
                                    "update_knowledge",
                                    "update_agent_knowledge",
                                    "change_work_dir",
                                    "get_work_dir"
                                ],
                                "description": "要调用的方法名"
                            },
                            "args": {
                                "type": "object",
                                "description": "方法参数。execute需要task参数；update_api_config需要model_name/base_url/api_key参数；update_description需要new_description参数；update_knowledge需要content参数；change_work_dir需要new_work_dir参数；update_agent_knowledge和get_work_dir不需要参数",
                                "properties": {
                                    "task": {
                                        "type": "string",
                                        "description": "要执行的任务（仅用于execute方法）"
                                    },
                                    "model_name": {
                                        "type": "string",
                                        "description": "新的模型名称（仅用于update_api_config方法）"
                                    },
                                    "base_url": {
                                        "type": "string",
                                        "description": "新的API基础URL（仅用于update_api_config方法）"
                                    },
                                    "api_key": {
                                        "type": "string",
                                        "description": "新的API密钥（仅用于update_api_config方法）"
                                    },
                                    "new_description": {
                                        "type": "string",
                                        "description": "新的description（仅用于update_description方法）"
                                    },
                                    "new_work_dir": {
                                        "type": "string",
                                        "description": "新的工作目录路径（仅用于change_work_dir方法）"
                                    },
                                    "content": {
                                        "type": "string",
                                        "description": "要添加的知识内容（仅用于update_knowledge方法）"
                                    },
                                    "operation": {
                                        "type": "string",
                                        "enum": ["append", "replace"],
                                        "description": "知识操作类型（仅用于update_knowledge方法）"
                                    }
                                }
                            }
                        },
                        "required": ["method"]
                    }
                }
            }
        else:
            # 普通Function或其他Agent，使用原有逻辑
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
        """保存压缩后的记忆到compact.md（不包含系统提示词）"""
        # 使用Agent的home目录
        agent_home = Path.home() / ".agent" / self.name
        agent_home.mkdir(parents=True, exist_ok=True)
        compact_file = agent_home / "compact.md"
        
        # 确保目录存在
        self.notes_dir.mkdir(parents=True, exist_ok=True)
        
        # 过滤掉系统消息，只保存对话消息
        dialogue_msgs = [m for m in self.messages if m.get("role") != "system"]
        
        # 准备内容
        content = [f"""# Compact Memory - {self.name}

生成时间: {datetime.now().isoformat()}
消息数量: {len(dialogue_msgs)}
预估tokens: {self._count_tokens(dialogue_msgs)}

## 压缩的对话历史

"""]
        
        # 添加消息内容（不包含系统消息）
        msg_counter = 1
        for msg in dialogue_msgs:
            role = msg.get("role", "unknown")
            content_text = msg.get("content", "")
            
            if role == "user":
                content.append(f"### 用户消息 {msg_counter}\n{content_text}\n\n")
            elif role == "assistant":
                # 不截断Assistant消息，保留完整内容
                content.append(f"### Assistant消息 {msg_counter}\n{content_text}\n\n")
            elif role == "tool":
                # 工具响应可能很长，适度截断
                if len(content_text) > 2000:
                    content.append(f"### 工具响应 {msg_counter}\n{content_text[:2000]}...\n\n")
                else:
                    content.append(f"### 工具响应 {msg_counter}\n{content_text}\n\n")
            
            msg_counter += 1
        
        # 写入文件
        compact_file.write_text(''.join(content), encoding='utf-8')
    
    def _load_compact_memory(self):
        """从compact.md加载压缩的记忆"""
        # 使用Agent的home目录
        agent_home = Path.home() / ".agent" / self.name
        compact_file = agent_home / "compact.md"

        if not compact_file.exists():
            return False

        print(f"  📚 加载Compact记忆: compact.md")

        # 读取compact.md的内容
        compact_content = compact_file.read_text(encoding='utf-8')

        # 从compact.md中提取实际的压缩内容
        # 查找 "### Assistant消息" 后的内容
        import re
        match = re.search(r'### Assistant消息 \d+\n(.*)', compact_content, re.DOTALL)
        if match:
            compressed_history = match.group(1).strip()
        else:
            # 如果格式不对，使用整个内容
            compressed_history = compact_content

        # 创建user/assistant消息对，这样压缩时能看到历史
        compact_messages = [
            {"role": "user", "content": "[请基于以下压缩的历史记忆继续对话]"},
            {"role": "assistant", "content": compressed_history}
        ]
        
        # 在系统消息后插入压缩记忆（作为对话消息，不是系统消息）
        if len(self.messages) > 0 and self.messages[0]["role"] == "system":
            # 在系统消息后插入
            self.messages[1:1] = compact_messages
        else:
            # 在开头插入
            self.messages[0:0] = compact_messages
        
        self.compact_memory = compressed_history  # 保存以便后续使用
        
        return True

    def _load_project_notes(self) -> bool:
        """从project_notes.md加载项目上下文（如果存在）"""
        # 检查工作目录下的.notes/project_notes.md
        project_notes_path = self.work_dir / ".notes" / "project_notes.md"

        if not project_notes_path.exists():
            return False

        try:
            # 读取项目笔记内容
            project_notes = project_notes_path.read_text(encoding='utf-8')

            # 将项目笔记作为系统消息的一部分添加
            # 这样Agent会知道项目上下文，但不会占用对话历史
            if self.messages and self.messages[0]["role"] == "system":
                # 在系统消息后追加项目上下文
                self.messages[0]["content"] += f"\n\n## 项目上下文\n{project_notes}"
                print(f"  📋 加载项目笔记: .notes/project_notes.md")
                return True
        except Exception as e:
            print(f"  ⚠️ 加载项目笔记失败: {e}")
            return False

        return False

    def _find_project_root(self, start_path: Path) -> Optional[Path]:
        """查找项目根目录
        
        判断标准（按优先级）：
        1. 包含 .git 目录
        2. 包含 pyproject.toml 或 setup.py
        3. 包含 package.json
        4. 包含 README.md 或 README.rst
        5. 包含 requirements.txt 或 Pipfile
        
        Args:
            start_path: 开始查找的路径
            
        Returns:
            项目根目录Path，如果找不到返回None
        """
        current = start_path.resolve()
        
        # 项目根目录标志文件（按优先级排序）
        root_markers = [
            '.git',                    # Git仓库
            'pyproject.toml',          # Python项目
            'setup.py',                # Python项目
            'package.json',            # Node.js项目
            'Cargo.toml',              # Rust项目
            'go.mod',                  # Go项目
            'pom.xml',                 # Java Maven项目
            'build.gradle',            # Java Gradle项目
            'README.md',               # 通用项目
            'README.rst',              # 通用项目
            'requirements.txt',        # Python项目
            'Pipfile',                 # Python Pipenv项目
            'Makefile',                # 有Makefile的项目
        ]
        
        # 向上查找，最多到根目录
        while current != current.parent:
            # 检查是否包含任何根目录标志
            for marker in root_markers:
                if (current / marker).exists():
                    return current
            current = current.parent
        
        # 如果找不到，返回None
        return None
    
    
    def _auto_save_state(self) -> None:
        """
        自动保存Agent状态到home目录
        实现"活在文件系统"的理念 - 每次执行后自动持久化

        新策略：
        1. 先执行compact压缩对话历史到compact.md
        2. state.json只保存配置，不保存messages
        """
        try:
            # 1. 先保存compact记忆（压缩对话历史）
            if hasattr(self, 'messages') and len(self.messages) > 1:  # 至少有系统消息+其他消息
                self._save_compact_memory()

            # 2. 构建状态（不含messages）
            state = {
                "name": self.name,
                "description": self.description,  # 保存Agent描述
                "model": self.model,  # 保存使用的LLM模型
                "base_url": self.base_url,  # 保存API基础URL
                "api_key": self.api_key,  # 保存API密钥（注意安全性）
                "work_dir": str(self.work_dir),  # 保存工作目录
                # "messages": self.messages,  # ← 不再保存messages！
                "has_compact": True,  # 标记有compact.md存在
                "message_count": len(self.messages) if hasattr(self, 'messages') else 0,  # 只记录数量
                "timestamp": datetime.now().isoformat(),
                "task_count": getattr(self, '_task_count', 0) + 1,
                "children": self.children  # 保存子Agent列表（金字塔结构）
            }

            # 3. 保存到home目录
            agent_home = Path.home() / ".agent" / self.name
            agent_home.mkdir(parents=True, exist_ok=True)
            state_file = agent_home / "state.json"

            # 原子写入（先写临时文件，再重命名）
            import json
            temp_file = state_file.with_suffix('.tmp')
            temp_file.write_text(json.dumps(state, ensure_ascii=False, indent=2))
            temp_file.replace(state_file)  # 原子操作

            # 更新任务计数
            self._task_count = state["task_count"]

        except Exception as e:
            # 自动保存失败不应该影响正常执行
            # 只是记录错误（不打印，避免干扰输出）
            pass

    def _get_execution_context_info(self) -> str:
        """获取ExecutionContext的完整信息（包括当前上下文和调用栈）

        Returns:
            ExecutionContext的格式化信息，如果为空返回None
        """
        try:
            # 查找ExecutionContext工具实例
            for tool in self.function_instances:
                if hasattr(tool, 'name') and tool.name == 'context':
                    # 获取当前上下文（栈顶）
                    context_info = tool.execute(action='get_context')

                    # 获取调用栈
                    call_stack_info = tool.execute(action='get_call_stack')

                    # 组合信息
                    combined_info = []
                    has_content = False

                    # 解析当前上下文
                    if context_info and context_info != "{}":
                        try:
                            context_data = json.loads(context_info)
                            # 检查是否有实质内容
                            if (context_data.get('目标') != '未设置' or
                                context_data.get('任务详情') or
                                context_data.get('当前状态') != '未设置' or
                                context_data.get('数据存储')):
                                combined_info.append("=== 当前执行上下文 ===")
                                combined_info.append(context_info)
                                has_content = True
                        except:
                            # 如果不是JSON格式，仍然保留
                            if context_info.strip():
                                combined_info.append("=== 当前执行上下文 ===")
                                combined_info.append(context_info)
                                has_content = True

                    # 添加调用栈信息（如果不为空）
                    if call_stack_info and "调用栈为空" not in call_stack_info:
                        combined_info.append("\n=== 调用栈 ===")
                        combined_info.append(call_stack_info)
                        has_content = True

                    # 返回组合的信息
                    if has_content:
                        return "\n".join(combined_info)

                    break
        except Exception as e:
            print(f"  ⚠️ 获取ExecutionContext失败: {e}")

        return None

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
1. 如果遇到"[已加载压缩的历史记忆]"，适度压缩为关键要点（保留200-500字）
2. 保留最新对话的关键事实和重要细节（包括关键过程）
3. 旧记忆简洁总结，新记忆充分保留（可以包含重要代码片段）
4. 去除所有重复和冗余
5. 确保时间顺序：旧记忆→新记忆

输出要求：
- 旧记忆：简洁总结（500-1000字）
- 新记忆：详细要点（10-20点）
- 总长度不超过10000字
- 不要嵌套结构"""
        else:
            # 无description时使用通用压缩
            compress_prompt = """你是一个对话历史压缩专家。请将冗长的对话历史压缩成精炼的摘要。

压缩原则：
1. 如果遇到"[已加载压缩的历史记忆]"，适度压缩为关键要点（保留200-500字）
2. 保留最新对话的关键事实和重要细节（包括关键过程）
3. 旧记忆简洁总结，新记忆充分保留（可以包含重要代码片段）
4. 去除所有重复和冗余
5. 确保时间顺序：旧记忆→新记忆

输出要求：
- 旧记忆：简洁总结（500-1000字）
- 新记忆：详细要点（10-20点）
- 总长度不超过10000字
- 不要嵌套结构"""
        
        # 分离系统消息和对话消息
        # 只保留第一个系统消息（原始系统提示词），忽略后续可能添加的系统消息
        original_system_msg = None
        for m in messages:
            if m["role"] == "system":
                original_system_msg = m
                break
        
        # 对话消息不包含任何系统消息
        dialogue_msgs = [m for m in messages if m["role"] != "system"]
        
        # 统计Compact记忆的压缩次数，避免过度嵌套
        compact_count = 0
        for m in dialogue_msgs:
            if m.get("role") == "assistant" and "[已加载压缩的历史记忆]" in m.get("content", ""):
                compact_count += 1
        
        # 如果压缩次数过多，提取核心记忆进行深度压缩
        if compact_count >= 3:
            print(f"  🔄 深度压缩模式（已压缩{compact_count}次）")
        
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
                
                print(f"  ✅ 压缩完成，保留关键信息")
                
                # 创建压缩后的消息对
                # 直接使用新的压缩内容（已包含旧记忆的精简版）
                self.compact_memory = compressed_content
                
                # 使用user/assistant对来保持消息交替格式
                compressed_messages = [
                    {"role": "user", "content": "[请基于以下压缩的历史记忆继续对话]"},
                    {"role": "assistant", "content": f"[已加载压缩的历史记忆]\n{self.compact_memory}"}
                ]
                
                # 检查是否有未完成的tool调用
                # 找到最后一个assistant消息看是否有tool_calls
                pending_tool_messages = []
                for i in range(len(messages) - 1, -1, -1):
                    msg = messages[i]
                    if msg["role"] == "tool":
                        # 继续向前查找对应的tool_calls
                        pending_tool_messages.insert(0, msg)
                    elif msg["role"] == "assistant" and msg.get("tool_calls"):
                        # 找到了tool_calls，添加到pending列表
                        pending_tool_messages.insert(0, msg)
                        break
                    elif msg["role"] in ["user", "assistant"] and not msg.get("tool_calls"):
                        # 遇到普通消息，停止查找
                        pending_tool_messages = []
                        break
                
                # 获取ExecutionContext信息
                execution_context_info = self._get_execution_context_info()

                # 返回新的消息列表：系统提示词 + 压缩的消息对 + ExecutionContext信息 + 未完成的tool调用
                result_messages = []
                if original_system_msg:
                    result_messages.append(original_system_msg)
                result_messages.extend(compressed_messages)

                # 如果ExecutionContext不为空，添加到消息中
                if execution_context_info:
                    result_messages.append({
                        "role": "user",
                        "content": f"[当前ExecutionContext状态]\n{execution_context_info}"
                    })
                    result_messages.append({
                        "role": "assistant",
                        "content": "OK"
                    })

                result_messages.extend(pending_tool_messages)
                return result_messages
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
                
                # 只返回原始系统提示词 + 保留的对话消息
                result_messages = []
                if original_system_msg:
                    result_messages.append(original_system_msg)
                result_messages.extend(kept_msgs)
                return result_messages
                
        except Exception as e:
            print(f"  ⚠️ 压缩出错: {e}，保留最近消息")
            # 出错时的降级策略（与压缩失败时相同）
            keep_count = max(2, len(dialogue_msgs) // 3)
            kept_msgs = dialogue_msgs[-keep_count:]
            if kept_msgs and kept_msgs[0]["role"] == "assistant":
                kept_msgs = kept_msgs[1:]
            if len(kept_msgs) % 2 != 0:
                kept_msgs = kept_msgs[1:]
            
            # 只返回原始系统提示词 + 保留的对话消息
            result_messages = []
            if original_system_msg:
                result_messages.append(original_system_msg)
            result_messages.extend(kept_msgs)
            return result_messages

    @classmethod
    def load(cls, name: str, **kwargs):
        """
        根据名字加载Agent - 最简单的方法

        Args:
            name: Agent名字
            **kwargs: 其他参数（可选）

        Returns:
            Agent实例

        使用方式:
            alice = ReactAgentMinimal.load("alice")

        行为:
            - 如果~/.agent/{name}存在，自动加载其中的知识和状态
            - 如果不存在，创建新的Agent
        """
        # 默认工作目录为当前目录
        work_dir = kwargs.pop("work_dir", ".")

        # 检查是否有保存的配置
        home = Path.home() / ".agent" / name
        config_file = home / "config.json"

        # 如果有保存的配置，加载它
        if config_file.exists():
            try:
                import json
                saved_config = json.loads(config_file.read_text())
                # 合并保存的配置和传入的参数（传入参数优先）
                for key, value in saved_config.items():
                    if key not in kwargs and key not in ["name", "work_dir"]:
                        kwargs[key] = value
            except:
                pass  # 如果配置文件损坏，忽略

        # 设置标记，避免在__init__中显示信息
        kwargs['_from_load'] = True

        # 创建Agent（__init__会自动加载home目录中的文件）
        agent = cls(
            work_dir=work_dir,
            name=name,
            **kwargs
        )

        # 尝试恢复状态
        state_file = home / "state.json"
        state_restored = False
        if state_file.exists():
            try:
                import json
                state = json.loads(state_file.read_text())
                # 恢复工作目录（如果保存了的话）
                if "work_dir" in state and work_dir == ".":
                    # 只有在没有显式指定work_dir时才使用保存的值
                    agent.work_dir = Path(state["work_dir"])
                # 恢复API配置（如果保存了的话）
                if "base_url" in state:
                    agent.base_url = state["base_url"]
                if "api_key" in state:
                    agent.api_key = state["api_key"]
                # 恢复模型设置（如果保存了的话）
                if "model" in state:
                    agent.model = state["model"]  # 直接恢复，不需要switch_model

                # 新策略：不从state.json恢复messages
                # compact.md已经在__init__中通过_load_compact_memory()加载
                # 这里不需要额外处理messages

                # 只记录消息数量信息（用于调试）
                if "message_count" in state:
                    agent._previous_message_count = state["message_count"]
                # 恢复description（接口定义）
                if "description" in state:
                    agent.description = state["description"]
                # 恢复子Agent列表（金字塔结构）
                if "children" in state:
                    agent.children = state["children"]
                state_restored = True
            except:
                pass  # 状态文件损坏，使用新状态

        # 显示实际的初始化信息
        print(f"🚀 极简Agent已加载 [{agent.name}]")
        print(f"  📍 API: {agent._detect_service()}")
        print(f"  🤖 模型: {agent.model}")  # 显示实际使用的模型
        print(f"  🧠 Compact记忆: 70k tokens触发压缩")
        print(f"  ⚡ Compact记忆替代文件系统")
        if agent.knowledge_files:
            print(f"  📚 知识文件: {len(agent.knowledge_files)}个")
        print(f"  ✨ Compact即注意力机制")
        if state_restored:
            print(f"  📂 已从home目录恢复状态")

        # 级联加载子Agent（金字塔结构）
        if agent.children:
            print(f"  👶 子Agent: {len(agent.children)}个")
            print(f"     级联加载中...")
            for child_name in agent.children:
                try:
                    # 递归加载子Agent
                    child_agent = cls.load(child_name)
                    # 将子Agent添加到父Agent的工具列表
                    agent.add_function(child_agent)
                    print(f"     ✅ {child_name} 已加载并添加为工具")
                except Exception as e:
                    print(f"     ⚠️ {child_name} 加载失败: {e}")

        return agent

    def _add_self_management_functions(self) -> None:
        """添加自我管理函数（元认知能力）

        将Agent自己注册为工具，让Agent可以调用自己的管理方法。
        注意：execute方法中会阻止递归调用自己的execute。
        """
        # 将自己作为Function添加，但execute方法会检查防止递归
        self.function_instances.append(self)

    # ========== 自我管理方法（暴露给Agent自己调用） ==========

    def update_api_config(self, model_name: str = None, base_url: str = None, api_key: str = None) -> str:
        """更新API配置（模型、base_url、api_key）

        Args:
            model_name: 新的模型名称
            base_url: 新的API基础URL
            api_key: 新的API密钥

        Returns:
            更新结果的描述
        """
        updates = []

        if model_name:
            old_model = self.model
            self.model = model_name
            updates.append(f"模型: {old_model} → {model_name}")

        if base_url:
            old_url = self.base_url
            self.base_url = base_url
            updates.append(f"Base URL: {old_url} → {base_url}")

        if api_key:
            self.api_key = api_key
            updates.append(f"API Key: 已更新")

        if updates:
            self._auto_save_state()
            return f"✅ API配置已更新:\n" + "\n".join(updates)
        else:
            return "⚠️ 没有提供任何更新参数"

    def update_description(self, new_description: str) -> str:
        """更新Agent的description（接口定义）"""
        old = self.description
        self.description = new_description
        self._auto_save_state()
        return f"✅ Description已更新\n从: {old}\n到: {new_description}"

    def get_status(self) -> str:
        """获取Agent当前状态"""
        return f"""Agent状态:
- 名称: {self.name}
- 描述: {self.description}
- 模型: {self.model}
- 消息数: {len(self.messages)}
- 工具数: {len(self.function_instances)}
- Home目录: {self.agent_home}"""

    def save_state(self) -> str:
        """手动保存当前状态（内部使用，不暴露给Agent）"""
        self._auto_save_state()
        return "✅ 状态已保存到state.json"

    def update_knowledge(self, content: str) -> str:
        """更新knowledge.md（统一知识文件）"""
        knowledge_file = self.agent_home / "knowledge.md"

        # 读取现有内容
        existing = ""
        if knowledge_file.exists():
            existing = knowledge_file.read_text()

        # 追加新内容
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_section = f"\n\n## {timestamp}\n{content}\n"

        knowledge_file.write_text(existing + new_section)
        return f"✅ 已更新knowledge.md，添加了{len(content)}字符"

    def update_agent_knowledge(self) -> str:
        """读取knowledge.md并重构系统提示词

        工作流程：
        1. 用户和Agent多轮讨论，直接编辑~/.agent/[name]/knowledge.md
        2. 用户满意后，告诉Agent更新
        3. Agent调用此方法读取文件，重构系统提示词

        Returns:
            更新结果描述
        """
        knowledge_file = self.agent_home / "knowledge.md"

        # 检查文件是否存在
        if not knowledge_file.exists():
            return f"❌ 文件不存在: {knowledge_file}"

        # 读取文件内容
        try:
            content = knowledge_file.read_text(encoding='utf-8')
            file_size = len(content)
        except Exception as e:
            return f"❌ 读取文件失败: {e}"

        # 重新加载知识到系统消息
        self._reload_system_prompt()

        # 记录更新
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return f"""✅ 已重新加载agent_knowledge.md并重构系统提示词
时间: {timestamp}
文件: {knowledge_file}
大小: {file_size}字符
状态: 系统提示词已更新，新知识已生效"""

    def change_work_dir(self, new_work_dir: str) -> str:
        """更改Agent的工作目录

        Args:
            new_work_dir: 新的工作目录路径

        Returns:
            更改结果描述
        """
        # 验证新目录
        new_path = Path(new_work_dir).expanduser().resolve()

        # 检查目录是否存在
        if not new_path.exists():
            try:
                new_path.mkdir(parents=True, exist_ok=True)
                created = True
            except Exception as e:
                return f"❌ 无法创建目录 {new_path}: {e}"
        else:
            created = False
            if not new_path.is_dir():
                return f"❌ 路径存在但不是目录: {new_path}"

        # 保存旧目录
        old_work_dir = self.work_dir

        # 更新工作目录
        self.work_dir = new_path

        # 保存状态
        self._auto_save_state()

        # 返回结果
        status = "✅ 工作目录已更改"
        if created:
            status += "（已创建新目录）"

        return f"""{status}
从: {old_work_dir}
到: {new_path}
当前位置: {new_path}"""

    def get_work_dir(self) -> str:
        """获取当前工作目录

        Returns:
            当前工作目录的完整路径
        """
        return f"""📂 当前工作目录
路径: {self.work_dir}
绝对路径: {Path(self.work_dir).resolve()}
存在: {'✅ 是' if Path(self.work_dir).exists() else '❌ 否'}"""

    def _reload_system_prompt(self) -> None:
        """重新加载系统提示词，包括更新后的knowledge.md"""
        # 重新读取所有知识文件
        knowledge_content = []

        # 1. 加载统一的知识文件（knowledge.md）
        knowledge_file = self.agent_home / "knowledge.md"
        if knowledge_file.exists():
            content = knowledge_file.read_text()
            if content.strip():
                knowledge_content.append(f"## 你的知识\n{content}")

        # 3. 加载知识文件（如果有）
        if self.knowledge_files:
            for kf in self.knowledge_files:
                try:
                    kf_path = Path(kf)
                    if not kf_path.exists():
                        # 尝试在knowledge目录查找
                        kf_path = Path(__file__).parent.parent / "knowledge" / kf

                    if kf_path.exists():
                        content = kf_path.read_text()
                        knowledge_content.append(f"## 知识文件: {kf_path.name}\n{content}")
                except Exception as e:
                    print(f"  ⚠️ 无法加载知识文件 {kf}: {e}")

        # 更新系统消息
        if knowledge_content:
            # 找到系统消息并更新
            for i, msg in enumerate(self.messages):
                if msg.get("role") == "system":
                    # 保留基础系统提示，追加知识内容
                    base_prompt = f"""你是{self.name}，一个基于React模式的智能Agent。
你的描述：{self.description}

工作目录：{self.work_dir}"""

                    # 组合完整的系统提示
                    full_prompt = base_prompt + "\n\n" + "\n\n".join(knowledge_content)
                    self.messages[i]["content"] = full_prompt
                    break

        # 自动保存状态
        self._auto_save_state()


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