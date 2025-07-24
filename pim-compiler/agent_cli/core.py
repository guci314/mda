#!/usr/bin/env python3
"""
通用 Agent CLI 核心实现
使用 LangChain 支持多种 LLM 提供商
"""
import os
import json
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr

# 导入工具执行器
try:
    from .executors import LangChainToolExecutor, ToolExecutionResult  # type: ignore
    from .tools import get_all_tools, get_tools_description  # type: ignore
    USE_LANGCHAIN_TOOLS = True
except ImportError:
    USE_LANGCHAIN_TOOLS = False

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
# 设置调试级别以查看详细信息
logger.setLevel(logging.DEBUG)


@dataclass
class LLMConfig:
    """LLM 配置"""
    api_key: str
    base_url: str
    model: str
    provider: str = "openai"  # openai, deepseek, qwen, glm, moonshot, openrouter
    temperature: float = 0.3
    max_tokens: Optional[int] = None
    
    @classmethod
    def from_env(cls, provider: Optional[str] = None) -> 'LLMConfig':
        """从环境变量加载配置"""
        provider = provider or os.getenv("LLM_PROVIDER", "openai")
        
        # 不同提供商的默认配置
        provider_configs = {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": "https://api.openai.com/v1",
                "model": os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
            },
            "deepseek": {
                "api_key": os.getenv("DEEPSEEK_API_KEY"),
                "base_url": "https://api.deepseek.com/v1",
                "model": os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
            },
            "qwen": {
                "api_key": os.getenv("DASHSCOPE_API_KEY"),
                "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
                "model": os.getenv("QWEN_MODEL", "qwen-turbo"),
            },
            "glm": {
                "api_key": os.getenv("ZHIPU_API_KEY"),
                "base_url": "https://open.bigmodel.cn/api/paas/v4",
                "model": os.getenv("GLM_MODEL", "glm-4"),
            },
            "moonshot": {
                "api_key": os.getenv("MOONSHOT_API_KEY"),
                "base_url": "https://api.moonshot.cn/v1",
                "model": os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k"),
            },
            "openrouter": {
                "api_key": os.getenv("OPENROUTER_API_KEY"),
                "base_url": "https://openrouter.ai/api/v1",
                "model": os.getenv("OPENROUTER_MODEL", "google/gemini-2.5-flash"),
            }
        }
        
        config = provider_configs.get(provider, provider_configs["openai"])
        if not config["api_key"]:
            raise ValueError(f"API key not found for provider '{provider}'. Please set the appropriate environment variable.")
        
        return cls(
            api_key=config["api_key"],
            base_url=config["base_url"],
            model=config["model"],
            provider=provider
        )


class ActionType(Enum):
    """动作类型"""
    THINK = "think"
    PLAN = "plan"
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    LIST_FILES = "list_files"
    ANALYZE = "analyze"
    GENERATE = "generate"
    VALIDATE = "validate"
    EXECUTE = "execute"
    COMPLETE = "complete"


class StepStatus(Enum):
    """步骤状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class TaskStatus(Enum):
    """任务状态"""
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Action:
    """动作定义 - 执行的最小单元"""
    type: ActionType
    description: str
    params: Optional[Dict[str, Any]] = None
    result: Any = None
    error: Optional[str] = None
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    @property
    def duration(self) -> Optional[float]:
        """执行时长"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def is_successful(self) -> bool:
        """是否成功"""
        return self.result is not None and self.error is None


@dataclass
class Step:
    """步骤定义 - 任务的逻辑单元"""
    name: str
    description: str
    status: StepStatus = StepStatus.PENDING
    actions: List[Action] = field(default_factory=list)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    iteration_count: int = 0
    max_iterations: int = 5
    
    
    def add_action(self, action: Action) -> None:
        """添加动作"""
        self.actions.append(action)
    
    def start(self) -> None:
        """开始执行"""
        self.status = StepStatus.IN_PROGRESS
        self.start_time = time.time()
        self.iteration_count += 1
    
    def complete(self) -> None:
        """完成步骤"""
        self.status = StepStatus.COMPLETED
        self.end_time = time.time()
    
    def fail(self, error: Optional[str] = None) -> None:
        """标记失败"""
        self.status = StepStatus.FAILED
        self.end_time = time.time()
        if error and self.actions:
            self.actions[-1].error = error
    
    @property
    def duration(self) -> Optional[float]:
        """执行时长"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def is_completed(self) -> bool:
        """是否完成"""
        return self.status == StepStatus.COMPLETED
    
    @property
    def should_skip(self) -> bool:
        """是否应该跳过（超过最大迭代次数）"""
        return self.iteration_count >= self.max_iterations


@dataclass
class Task:
    """任务定义 - 顶层执行单元"""
    description: str
    goal: str
    status: TaskStatus = TaskStatus.PENDING
    steps: List[Step] = field(default_factory=list)
    current_step_index: int = 0
    context: Dict[str, Any] = field(default_factory=dict)
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    
    
    def add_step(self, step: Step) -> None:
        """添加步骤"""
        self.steps.append(step)
    
    def start(self) -> None:
        """开始任务"""
        self.status = TaskStatus.EXECUTING
        self.start_time = time.time()
    
    def complete(self) -> None:
        """完成任务"""
        self.status = TaskStatus.COMPLETED
        self.end_time = time.time()
    
    def fail(self, error: Optional[str] = None) -> None:
        """任务失败"""
        self.status = TaskStatus.FAILED
        self.end_time = time.time()
    
    @property
    def current_step(self) -> Optional[Step]:
        """当前步骤"""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def advance_step(self) -> bool:
        """前进到下一步"""
        if self.current_step_index < len(self.steps) - 1:
            self.current_step_index += 1
            return True
        return False
    
    @property
    def is_completed(self) -> bool:
        """是否完成"""
        return all(step.is_completed for step in self.steps)
    
    @property
    def duration(self) -> Optional[float]:
        """执行时长"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None
    
    def get_summary(self) -> Dict[str, Any]:
        """获取任务摘要"""
        total_actions = sum(len(step.actions) for step in self.steps)
        completed_steps = sum(1 for step in self.steps if step.is_completed)
        
        return {
            "description": self.description,
            "status": self.status.value,
            "duration": self.duration,
            "total_steps": len(self.steps),
            "completed_steps": completed_steps,
            "total_actions": total_actions,
            "steps_summary": [
                {
                    "name": step.name,
                    "status": step.status.value,
                    "actions": len(step.actions),
                    "duration": step.duration
                }
                for step in self.steps
            ]
        }


# ExecutionPlan 已被 Task/Step/Action 架构替代


class Tool(ABC):
    """工具基类"""
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        pass


class FileReader(Tool):
    """文件读取工具"""
    def execute(self, params: Dict[str, Any]) -> str:
        file_path = params.get("file_path")
        if not file_path:
            raise ValueError("file_path is required")
        logger.info(f"Reading file: {file_path}")
        
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        logger.info(f"Read {len(content)} characters from {file_path}")
        return content


class FileWriter(Tool):
    """文件写入工具"""
    def execute(self, params: Dict[str, Any]) -> str:
        file_path = params.get("file_path")
        content = params.get("content")
        
        if not file_path:
            raise ValueError("file_path is required")
        if content is None:
            raise ValueError("content is required")
        
        logger.info(f"Writing file: {file_path}")
        
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Wrote {len(content)} characters to {file_path}")
        return f"File written: {file_path}"


class FileLister(Tool):
    """文件列表工具"""
    def execute(self, params: Dict[str, Any]) -> List[str]:
        directory = params.get("directory", ".")
        pattern = params.get("pattern", "*")
        
        logger.info(f"Listing files in {directory} with pattern {pattern}")
        
        path = Path(directory)
        if not path.exists():
            return []
        
        files = list(path.glob(pattern))
        file_list = [str(f) for f in files]
        
        logger.info(f"Found {len(file_list)} files")
        return file_list


class AgentCLI:
    """通用 Agent CLI 实现"""
    
    def __init__(self, llm_config: Optional[LLMConfig] = None, working_dir: str = ".", 
                 enable_symbolic_fallback: bool = True, use_langchain_tools: bool = True):
        self.working_dir = Path(working_dir)
        self.enable_symbolic_fallback = enable_symbolic_fallback  # 是否启用符号主义回退
        self.use_langchain_tools = use_langchain_tools and USE_LANGCHAIN_TOOLS  # 是否使用 LangChain 工具
        
        # 初始化 LLM
        if not llm_config:
            llm_config = LLMConfig.from_env()
        
        self.llm_config = llm_config
        # OpenRouter 需要特殊的 headers
        if llm_config.provider == "openrouter":
            self.llm = ChatOpenAI(
                api_key=SecretStr(llm_config.api_key) if llm_config.api_key else None,
                base_url=llm_config.base_url,
                model=llm_config.model,
                temperature=llm_config.temperature,
                default_headers={
                    "HTTP-Referer": "https://github.com/pim-compiler",
                    "X-Title": "PIM Compiler Agent CLI"
                }
            )
        else:
            self.llm = ChatOpenAI(
                api_key=SecretStr(llm_config.api_key) if llm_config.api_key else None,
                base_url=llm_config.base_url,
                model=llm_config.model,
                temperature=llm_config.temperature
            )
        # 设置 max_tokens（如果提供）
        if llm_config.max_tokens is not None:
            self.llm.max_tokens = llm_config.max_tokens
        else:
            # 默认限制响应长度，避免生成过长内容
            self.llm.max_tokens = 1000
        self.output_parser = StrOutputParser()
        
        # 初始化工具
        if self.use_langchain_tools:
            # 使用 LangChain 工具执行器
            self.tool_executor = LangChainToolExecutor()
            logger.info("Using LangChain tools for execution")
        else:
            # 使用传统工具
            self.tools = {
                "read_file": FileReader(),
                "write_file": FileWriter(),
                "list_files": FileLister()
            }
            self.tool_executor = None
            logger.info("Using legacy tools for execution")
        
        # 执行上下文
        self.context: Dict[str, Any] = {}
        self.current_task: Optional[Task] = None
        self.max_iterations = 50
    
    def _call_llm(self, messages: List[Any]) -> str:
        """调用 LLM"""
        try:
            response = self.llm.invoke(messages)
            return self.output_parser.invoke(response)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def _call_llm_json(self, messages: List[Any]) -> dict:
        """调用 LLM 并强制返回 JSON 格式"""
        try:
            # 修改系统消息，强调返回JSON
            if messages and isinstance(messages[0], SystemMessage):
                messages[0].content += "\n\n重要：必须返回纯JSON格式，不要包含markdown标记或其他文本。"
            
            response = self.llm.invoke(messages)
            response_text = self.output_parser.invoke(response)
            
            # 清理响应文本
            response_text = response_text.strip()
            
            # 移除可能的 markdown 代码块标记
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            # 尝试解析 JSON
            try:
                return json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {e}")
                logger.debug(f"Response text: {response_text[:200]}...")
                
                # 尝试提取 JSON 部分
                import re
                # 更精确的 JSON 提取模式
                json_patterns = [
                    r'\{[^{}]*\{[^{}]*\}[^{}]*\}',  # 嵌套的 JSON
                    r'\{[^}]+\}',  # 简单的 JSON
                    r'\{[\s\S]*\}'  # 任意 JSON
                ]
                
                for pattern in json_patterns:
                    json_match = re.search(pattern, response_text)
                    if json_match:
                        try:
                            return json.loads(json_match.group())
                        except:
                            continue
                
                # 如果还是失败，返回错误信息
                return {"error": "Failed to parse JSON", "raw_response": response_text}
                
        except Exception as e:
            logger.error(f"LLM JSON call failed: {e}")
            # 回退到普通调用
            try:
                response = self._call_llm(messages)
                response = response.strip()
                # 尝试清理和解析
                if response.startswith("```"):
                    response = response.split("```")[1]
                return json.loads(response)
            except:
                return {"error": str(e), "raw_response": response if 'response' in locals() else ""}
    
    def think(self, context: str, current_step: str) -> str:
        """思考当前任务"""
        messages = [
            SystemMessage(content="你是一个高效的任务执行助手。请用1-2句话说明下一步行动。不要分析，直接说要做什么。"),
            HumanMessage(content=f"""任务：{self.context.get('task', '未知')}
当前步骤：{current_step}

直接说明下一步行动（20字以内）：""")
        ]
        
        return self._call_llm(messages)
    
    def plan(self, task_description: str) -> Task:
        """制定任务执行计划 - 使用LLM进行智能规划"""
        system_prompt = """你是一个任务规划专家。请生成最简洁、高效的执行计划。

重要原则：
1. 只包含必要的步骤，避免冗余
2. 简单任务（如打招呼、简单计算）只需1个步骤
3. 每个步骤必须有明确的输出
4. 不要生成"分析"、"理解"、"准备"等无实际产出的步骤

任务复杂度判断：
- 简单任务（1步）：打招呼、简单计算、单一操作
- 中等任务（2-3步）：读取文件并处理、简单的代码生成
- 复杂任务（3-5步）：系统设计、多文件操作、完整功能实现

返回 JSON 格式：
{
    "goal": "任务的最终目标",
    "steps": [
        {
            "name": "步骤名称（动词+名词）",
            "description": "具体要做什么",
            "expected_output": "产出什么"
        }
    ],
    "estimated_complexity": "low|medium|high"
}"""
        
        human_prompt = f"""请为以下任务制定最简洁的执行计划：
{task_description}

记住：如果是简单任务，只生成1个步骤即可。"""
        
        # 输出计划提示词到日志
        logger.debug("=== Planning Prompt ===")
        logger.debug(f"System: {system_prompt}")
        logger.debug(f"Human: {human_prompt}")
        logger.debug("======================")
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=human_prompt)
        ]
        
        # 使用 JSON 格式调用
        plan_data = self._call_llm_json(messages)
        
        # 输出计划结果到日志
        logger.info("=== Planning Result ===")
        logger.info(f"Plan data: {json.dumps(plan_data, indent=2, ensure_ascii=False)}")
        logger.info("======================")
        
        # 提取步骤
        if "steps" in plan_data:
            steps = plan_data["steps"]
        else:
            # 如果没有步骤，尝试从 raw_response 中提取
            steps = []
            if "raw_response" in plan_data:
                logger.warning("Failed to get structured steps, extracting from text")
                response = plan_data["raw_response"]
                for line in response.split('\n'):
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        # 移除数字和符号前缀
                        step = line.lstrip('0123456789.- \t')
                        if step:
                            steps.append(step)
        
        if not steps:
            if self.enable_symbolic_fallback:
                # 使用默认步骤
                steps = self._get_default_steps(task_description)
            else:
                # 纯连接主义模式：创建一个通用步骤
                logger.warning("No steps from LLM and symbolic fallback is disabled, using generic step")
                steps = ["执行任务"]
        
        # 创建任务对象
        goal = plan_data.get("goal", task_description) if isinstance(plan_data, dict) else task_description
        new_task = Task(
            description=task_description,
            goal=goal
        )
        
        # 将步骤添加到任务
        for step_info in steps:
            if isinstance(step_info, dict):
                # 如果是字典格式，提取详细信息
                step_name = step_info.get("name", "未命名步骤")
                step_desc = step_info.get("description", step_name)
            else:
                # 如果是字符串格式
                step_name = str(step_info)
                step_desc = step_name
                
            step = Step(
                name=step_name,
                description=step_desc
            )
            new_task.add_step(step)
        
        return new_task
    
    def _get_default_steps(self, task: str) -> List[str]:
        """获取默认步骤"""
        task_lower = task.lower()
        
        if "psm" in task_lower and "pim" in task_lower:
            return [
                "读取 PIM 文件内容",
                "分析 PIM 中的实体和属性",
                "生成数据模型定义",
                "生成 API Schema 定义",
                "生成 CRUD 操作接口",
                "生成 REST API 端点",
                "组合所有代码为 PSM 文档",
                "写入 PSM 文件"
            ]
        elif "代码" in task or "code" in task_lower:
            return [
                "分析需求",
                "设计架构",
                "生成代码",
                "验证代码",
                "写入文件"
            ]
        elif "设计" in task_lower or "方案" in task_lower:
            return [
                "分析需求和目标",
                "设计系统架构",
                "定义数据模型",
                "设计核心功能",
                "生成设计文档"
            ]
        else:
            return [
                "理解任务需求",
                "制定解决方案",
                "实施方案",
                "验证结果"
            ]
    
    def analyze_content(self, content: str, instruction: str) -> Dict[str, Any]:
        """分析内容"""
        messages = [
            SystemMessage(content="你是一个代码分析专家，擅长分析和理解各种格式的技术文档。请始终以JSON格式返回分析结果。"),
            HumanMessage(content=f"""{instruction}

内容：
{content}

请以 JSON 格式返回分析结果。""")
        ]
        
        # 使用 JSON 格式调用
        return self._call_llm_json(messages)
    
    def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """生成代码"""
        system_prompt = """你是一个专业的代码生成专家。请生成简洁、高质量的代码。
要求：遵循 PEP 8，包含类型注解，适当注释，处理错误。
重要：保持代码简洁，避免过度设计。每个函数不超过20行。"""
        
        user_prompt = prompt
        if context:
            user_prompt = f"""基于以下上下文生成代码：
{json.dumps(context, indent=2, ensure_ascii=False)}

任务：{prompt}"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ]
        
        return self._call_llm(messages)
    
    def execute_task(self, task: str) -> Tuple[bool, str]:
        """执行任务的主入口"""
        logger.info(f"Starting task: {task}")
        logger.info(f"Using LLM provider: {self.llm_config.provider}")
        logger.info(f"Model: {self.llm_config.model}")
        
        # 1. 创建任务并制定执行计划
        logger.info("Creating execution plan...")
        self.current_task = self.plan(task)
        self.current_task.context = {
            "task": task,
            "task_description": task
        }
        self.context = self.current_task.context
        
        logger.info(f"Execution plan created with {len(self.current_task.steps)} steps:")
        for i, step in enumerate(self.current_task.steps):
            logger.info(f"  Step {i+1}: {step.name}")
        
        # 2. 开始执行任务
        self.current_task.start()
        iteration = 0
        
        while not self.current_task.is_completed and iteration < self.max_iterations:
            iteration += 1
            current_step = self.current_task.current_step
            if not current_step:
                break
                
            # 检查当前步骤的迭代次数
            if current_step.should_skip:
                logger.warning(f"Step '{current_step.name}' exceeded max iterations, advancing to next step")
                current_step.status = StepStatus.SKIPPED
                self.current_task.advance_step()
                continue
                
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration}: {current_step.name}")
            logger.info(f"{'='*60}")
            
            try:
                # 开始执行步骤
                current_step.start()
                
                # 思考当前步骤
                thought = self._think(current_step.name)
                
                # 决定动作
                action = self._decide_action(thought, current_step.name)
                
                # 执行动作
                result = self._execute_action(action)
                action.result = result
                
                # 更新上下文
                self._update_context(action)
                self.current_task.context.update(self.context)
                
                # 记录动作到步骤
                current_step.add_action(action)
                
                # 判断是否可以进入下一步
                if self._should_advance(action, current_step.name):
                    current_step.complete()
                    logger.info(f"✓ Step completed: {current_step.name}")
                    self.current_task.advance_step()
                    
            except Exception as e:
                logger.error(f"Action failed: {e}")
                if 'action' in locals():
                    action.error = str(e)
                    current_step.add_action(action)
                
                # 尝试恢复或跳过
                if self._can_recover(e):
                    logger.info("Attempting to recover...")
                    continue
                else:
                    current_step.fail(str(e))
                    self.current_task.fail(f"Step '{current_step.name}' failed: {str(e)}")
                    return False, f"Task failed: {str(e)}"
        
        # 3. 检查是否完成
        if self.current_task.is_completed:
            self.current_task.complete()
            logger.info("\n✅ Task completed successfully!")
            return True, "Task completed"
        else:
            self.current_task.fail("Max iterations reached")
            logger.warning("\n⚠️ Task did not complete within iteration limit")
            return False, "Max iterations reached"
    
    def _think(self, step: str) -> str:
        """思考当前步骤"""
        context_str = json.dumps(self.context, indent=2, ensure_ascii=False)
        thought = self.think(context_str, step)
        logger.info(f"Thought: {thought[:200]}...")
        return thought
    
    def _decide_action(self, thought: str, step: str) -> Action:
        """基于LLM推理决定动作 - 连接主义方法"""
        # 获取可用工具描述（如果使用 LangChain）
        tools_desc = ""
        if self.use_langchain_tools and self.tool_executor is not None:
            tools_desc = "\n\n" + self.tool_executor.format_tools_for_prompt()
        
        # 使用LLM来决定应该执行什么动作
        if self.use_langchain_tools and tools_desc:
            # 使用 LangChain 工具的提示
            prompt_content = f"""根据当前步骤选择合适的工具。

{tools_desc}

重要提示：
1. 仔细阅读步骤描述，从中提取所需的参数值
2. 对于 write_file 工具，必须从步骤描述中提取文件内容作为 content 参数
3. 确保所有必需参数都有具体的值，不要留空

根据上述工具，决定使用哪个工具和参数。

返回JSON格式：
{{
    "tool_name": "工具名称",
    "description": "要做什么",
    "params": {{"参数名": "参数值"}}
}}"""
        else:
            # 传统动作的提示
            prompt_content = f"""快速决定下一个动作。

动作类型：
- GENERATE: 生成内容（最常用）
- READ_FILE: 读取文件
- WRITE_FILE: 保存结果
- ANALYZE: 分析已有内容

返回JSON：
{{
    "action_type": "动作类型",
    "description": "做什么",
    "params": {{}}
}}"""
        
        human_content = f"""步骤：{step}
任务：{self.context.get('task', '未知')}

决定动作（大多数情况使用GENERATE）："""
        
        messages = [
            SystemMessage(content=prompt_content),
            HumanMessage(content=human_content)
        ]
        
        # 输出决策提示词到日志
        logger.debug("=== Decision Prompt ===")
        logger.debug(f"System: {prompt_content}")
        logger.debug(f"Human: {human_content}")
        logger.debug("=======================")
        
        # 使用 JSON 格式调用
        decision = self._call_llm_json(messages)
        
        # 输出决策结果到日志
        logger.info(f"Decision result: {json.dumps(decision, indent=2, ensure_ascii=False)}")
        
        try:
            # 检查是否有错误
            if "error" in decision:
                raise ValueError(f"LLM returned error: {decision.get('error')}")
                
            # 根据LLM的决策创建动作
            if self.use_langchain_tools and "tool_name" in decision:
                # LangChain 工具模式
                tool_name = decision.get("tool_name", "")
                # 映射工具名到动作类型
                tool_to_action = {
                    "read_file": ActionType.READ_FILE,
                    "write_file": ActionType.WRITE_FILE,
                    "list_files": ActionType.LIST_FILES,
                    "analyze": ActionType.ANALYZE,
                    "generate": ActionType.GENERATE,
                    "python_repl": ActionType.EXECUTE,
                    "bash": ActionType.EXECUTE,
                }
                action_type = tool_to_action.get(tool_name, ActionType.GENERATE)
            else:
                # 传统动作模式
                action_type_map = {
                    "READ_FILE": ActionType.READ_FILE,
                    "WRITE_FILE": ActionType.WRITE_FILE,
                    "ANALYZE": ActionType.ANALYZE,
                    "GENERATE": ActionType.GENERATE,
                    "VALIDATE": ActionType.VALIDATE,
                    "LIST_FILES": ActionType.LIST_FILES,
                    "THINK": ActionType.THINK
                }
                
                action_type_str = decision.get("action_type", "GENERATE")
                action_type = action_type_map.get(action_type_str, ActionType.GENERATE)
            
            # 如果需要文件路径但未提供，使用启发式方法
            params = decision.get("params", {})
            if action_type == ActionType.READ_FILE and "file_path" not in params:
                if "params" not in decision:
                    decision["params"] = {}
                decision["params"]["file_path"] = self._extract_file_path(thought, step)
            elif action_type == ActionType.WRITE_FILE:
                # 对于 write_file，不要覆盖 LLM 已经生成的参数
                # 只在 content 为空时才尝试从上下文获取
                if "content" not in params or not params["content"]:
                    params["content"] = self.context.get("generated_content", "")
                    logger.debug(f"Content was empty, using context: {params['content'][:100]}...")
            
            return Action(
                type=action_type,
                description=decision.get("description", step),
                params=decision.get("params", {})
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            if self.enable_symbolic_fallback:
                logger.warning(f"Failed to parse LLM decision, falling back to symbolic approach: {e}")
                # 混合策略：LLM推理失败时使用符号推理作为后备
                return self._decide_action_symbolic(thought, step)
            else:
                logger.error(f"Failed to parse LLM decision and symbolic fallback is disabled: {e}")
                # 返回一个默认的生成动作
                return Action(
                    type=ActionType.GENERATE,
                    description=f"执行步骤：{step}（LLM决策失败）",
                    params={
                        "prompt": f"由于LLM决策失败，请基于当前步骤执行：{step}",
                        "context": self.context
                    }
                )
    
    def _decide_action_symbolic(self, thought: str, step: str) -> Action:
        """符号主义决策方法 - 作为后备策略"""
        step_lower = step.lower()
        
        # 基于关键词的简单规则
        if any(word in step_lower for word in ["读取", "加载", "获取"]) and any(word in step_lower for word in ["文件", "pim", "psm"]):
            file_path = self._extract_file_path(thought, step)
            return Action(
                type=ActionType.READ_FILE,
                description=f"读取文件: {file_path}",
                params={"file_path": file_path}
            )
        
        elif any(word in step_lower for word in ["分析", "解析", "理解", "提取"]):
            content = self.context.get("file_content", self.context.get("task", ""))
            return Action(
                type=ActionType.ANALYZE,
                description="分析内容",
                params={
                    "content": content,
                    "instruction": step
                }
            )
        
        elif any(word in step_lower for word in ["写入", "保存", "输出", "导出"]):
            file_path = self._extract_output_path(step)
            return Action(
                type=ActionType.WRITE_FILE,
                description=f"写入文件: {file_path}",
                params={
                    "file_path": file_path,
                    "content": self.context.get("generated_content", "")
                }
            )
        
        else:
            # 默认使用生成动作
            return Action(
                type=ActionType.GENERATE,
                description=step,
                params={
                    "prompt": f"执行步骤：{step}。任务：{self.context.get('task', '')}",
                    "context": self.context
                }
            )
    
    def _create_generate_action(self, step: str) -> Action:
        """创建生成动作 - 使用LLM决定生成策略"""
        # 使用LLM来理解需要生成什么
        messages = [
            SystemMessage(content="""你是一个代码生成专家。基于当前步骤和上下文，决定具体的生成策略。

请返回JSON格式的生成策略：
{
    "prompt": "详细的生成提示词",
    "focus": "生成的重点内容",
    "constraints": ["约束条件1", "约束条件2"],
    "expected_output": "期望的输出格式或内容"
}"""),
            HumanMessage(content=f"""当前步骤：{step}

当前上下文：
- 任务：{self.context.get('task', '未知')}
- 已分析内容：{'有' if self.context.get('analysis') else '无'}
- 已有文件内容：{'有' if self.context.get('file_content') else '无'}
- 已生成内容长度：{len(self.context.get('generated_content', ''))} 字符

请决定生成策略。""")
        ]
        
        # 使用 JSON 格式调用
        strategy = self._call_llm_json(messages)
        
        try:
            # 检查是否有错误
            if "error" in strategy:
                raise ValueError(f"LLM returned error: {strategy.get('error')}")
                
            # 构建完整的生成提示
            prompt = strategy.get("prompt", f"基于当前上下文，{step}")
            if strategy.get("constraints"):
                prompt += "\n\n约束条件：\n" + "\n".join(f"- {c}" for c in strategy["constraints"])
            if strategy.get("expected_output"):
                prompt += f"\n\n期望输出：{strategy['expected_output']}"
            
            return Action(
                type=ActionType.GENERATE,
                description=f"生成: {step}",
                params={
                    "prompt": prompt,
                    "context": self.context,
                    "focus": strategy.get("focus", "")
                }
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            if self.enable_symbolic_fallback:
                logger.warning(f"Failed to parse generation strategy, using simple approach: {e}")
                # 后备方案：使用简单的生成策略
                return Action(
                    type=ActionType.GENERATE,
                    description=f"生成: {step}",
                    params={
                        "prompt": f"基于当前上下文，{step}。任务背景：{self.context.get('task', '')}",
                        "context": self.context
                    }
                )
            else:
                logger.error(f"Failed to parse generation strategy and symbolic fallback is disabled: {e}")
                # 返回基本的生成动作
                return Action(
                    type=ActionType.GENERATE,
                    description=f"生成: {step}（策略生成失败）",
                    params={
                        "prompt": f"请执行步骤：{step}",
                        "context": self.context
                    }
                )
    
    def _execute_action(self, action: Action) -> Any:
        """执行动作"""
        logger.info(f"Executing: {action.type.value} - {action.description}")
        
        action.start_time = time.time()
        
        try:
            if self.use_langchain_tools and self.tool_executor:
                # 使用 LangChain 工具执行
                result = self._execute_with_langchain(action)
            else:
                # 使用传统方式执行
                result = self._execute_legacy(action)
            
            action.end_time = time.time()
            return result
            
        except Exception as e:
            action.end_time = time.time()
            action.error = str(e)
            raise
    
    def _execute_with_langchain(self, action: Action) -> Any:
        """使用 LangChain 工具执行动作"""
        # 映射动作类型到工具名称
        tool_mapping = {
            ActionType.READ_FILE: "read_file",
            ActionType.WRITE_FILE: "write_file",
            ActionType.LIST_FILES: "list_files",
            ActionType.ANALYZE: "analyze",
            ActionType.GENERATE: "generate",
            ActionType.EXECUTE: "python_repl",
        }
        
        tool_name = tool_mapping.get(action.type)
        
        if tool_name:
            # 使用 LangChain 工具执行
            if self.tool_executor is not None:
                result = self.tool_executor.execute(tool_name, action.params or {})
                if result.success:
                    return result.output
                else:
                    raise Exception(result.error or "Tool execution failed")
            else:
                raise Exception("Tool executor not initialized")
        
        elif action.type == ActionType.THINK:
            return "Continuing analysis..."
        
        else:
            return None
    
    def _execute_legacy(self, action: Action) -> Any:
        """使用传统方式执行动作"""
        if action.type == ActionType.READ_FILE:
            tool = self.tools["read_file"]
            return tool.execute(action.params or {})
        
        elif action.type == ActionType.WRITE_FILE:
            tool = self.tools["write_file"]
            return tool.execute(action.params or {})
        
        elif action.type == ActionType.LIST_FILES:
            tool = self.tools["list_files"]
            return tool.execute(action.params or {})
        
        elif action.type == ActionType.ANALYZE:
            params = action.params or {}
            content = params.get("content", "")
            instruction = params.get("instruction", "")
            return self.analyze_content(content, instruction)
        
        elif action.type == ActionType.GENERATE:
            params = action.params or {}
            prompt = params.get("prompt", "")
            context = params.get("context", {})
            return self.generate_code(prompt, context)
        
        elif action.type == ActionType.THINK:
            return "Continuing analysis..."
        
        else:
            return None
    
    def _update_context(self, action: Action):
        """更新执行上下文"""
        if action.type == ActionType.READ_FILE and action.result:
            self.context["file_content"] = action.result
            if action.params:
                self.context["input_file"] = action.params.get("file_path")
        
        elif action.type == ActionType.ANALYZE and action.result:
            self.context["analysis"] = action.result
        
        elif action.type == ActionType.GENERATE and action.result:
            # 累积生成的内容
            if "generated_content" not in self.context:
                self.context["generated_content"] = ""
            
            # 添加适当的分隔
            if self.context["generated_content"]:
                self.context["generated_content"] += "\n\n"
            
            self.context["generated_content"] += action.result
    
    def _should_advance(self, action: Action, current_step: str) -> bool:
        """判断是否应该进入下一步"""
        # 如果动作成功完成且有结果，通常可以进入下一步
        if action.result and not action.error:
            # 特定动作类型的判断
            if action.type in [ActionType.READ_FILE, ActionType.ANALYZE, 
                             ActionType.GENERATE, ActionType.WRITE_FILE,
                             ActionType.EXECUTE, ActionType.LIST_FILES]:
                return True
        
        # 思考动作通常不推进步骤
        if action.type == ActionType.THINK:
            return False
        
        return False
    
    def _can_recover(self, error: Exception) -> bool:
        """判断是否可以从错误中恢复"""
        # 文件不存在错误通常可以通过创建文件或使用默认值恢复
        if isinstance(error, FileNotFoundError):
            return True
        
        # 其他错误暂时不尝试恢复
        return False
    
    def _extract_file_path(self, thought: str, step: str) -> str:
        """从思考或步骤中提取文件路径"""
        # 简单实现：查找常见的文件扩展名
        import re
        
        # 尝试从步骤中找到文件名
        patterns = [
            r'([a-zA-Z0-9_\-]+\.(?:md|py|txt|json|yaml|yml))',
            r'"([^"]+)"',
            r"'([^']+)'"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, step + " " + thought)
            for match in matches:
                if '.' in match:  # 可能是文件名
                    return match
        
        # 默认返回
        return "input.md"
    
    def _extract_output_path(self, step: str) -> str:
        """从步骤中提取输出文件路径"""
        if "psm" in step.lower():
            return "output_psm.md"
        
        return "output.md"
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        if self.current_task:
            # 使用任务的摘要
            task_summary = self.current_task.get_summary()
            
            # 添加动作类型统计
            action_types = {}
            for action_type in ActionType:
                action_types[action_type.value] = 0
            
            total_actions = 0
            successful_actions = 0
            failed_actions = 0
            
            for step in self.current_task.steps:
                for action in step.actions:
                    total_actions += 1
                    if action.is_successful:
                        successful_actions += 1
                    else:
                        failed_actions += 1
                    action_types[action.type.value] += 1
            
            task_summary["action_types"] = action_types
            task_summary["successful_actions"] = successful_actions
            task_summary["failed_actions"] = failed_actions
            task_summary["context_keys"] = list(self.current_task.context.keys())
            
            return task_summary
        else:
            # 没有任务时返回空摘要
            return {
                "total_actions": 0,
                "successful_actions": 0,
                "failed_actions": 0,
                "action_types": {action_type.value: 0 for action_type in ActionType},
                "context_keys": list(self.context.keys())
            }