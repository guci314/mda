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
from dataclasses import dataclass
from enum import Enum
from abc import ABC, abstractmethod

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class LLMConfig:
    """LLM 配置"""
    api_key: str
    base_url: str
    model: str
    provider: str = "openai"  # openai, deepseek, qwen, glm, moonshot
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
                "model": os.getenv("MOONSHOT_MODEL", "kimi-k2-0711-preview"),
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
    COMPLETE = "complete"


@dataclass
class Action:
    """动作定义"""
    type: ActionType
    description: str
    params: Optional[Dict[str, Any]] = None
    result: Any = None
    error: Optional[str] = None


@dataclass
class ExecutionPlan:
    """执行计划"""
    goal: str
    steps: List[str]
    current_step: int = 0
    
    def get_current_step(self) -> Optional[str]:
        if self.current_step < len(self.steps):
            return self.steps[self.current_step]
        return None
    
    def advance(self):
        self.current_step += 1
    
    def is_complete(self) -> bool:
        return self.current_step >= len(self.steps)


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
    
    def __init__(self, llm_config: Optional[LLMConfig] = None, working_dir: str = "."):
        self.working_dir = Path(working_dir)
        
        # 初始化 LLM
        if not llm_config:
            llm_config = LLMConfig.from_env()
        
        self.llm_config = llm_config
        self.llm = ChatOpenAI(
            api_key=SecretStr(llm_config.api_key) if llm_config.api_key else None,
            base_url=llm_config.base_url,
            model=llm_config.model,
            temperature=llm_config.temperature
        )
        # 设置 max_tokens（如果提供）
        if llm_config.max_tokens is not None:
            self.llm.max_tokens = llm_config.max_tokens
        self.output_parser = StrOutputParser()
        
        # 初始化工具
        self.tools = {
            "read_file": FileReader(),
            "write_file": FileWriter(),
            "list_files": FileLister()
        }
        
        # 执行上下文
        self.context: Dict[str, Any] = {}
        self.action_history: List[Action] = []
        self.max_iterations = 50
    
    def _call_llm(self, messages: List[Any]) -> str:
        """调用 LLM"""
        try:
            response = self.llm.invoke(messages)
            return self.output_parser.invoke(response)
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            raise
    
    def think(self, context: str, current_step: str) -> str:
        """思考当前任务"""
        messages = [
            SystemMessage(content="你是一个任务执行助手，需要分析当前状态并决定下一步行动。"),
            HumanMessage(content=f"""当前上下文：
{context}

当前执行步骤：{current_step}

请分析当前状态，并说明下一步应该做什么。注意查看上下文中的 'task' 字段了解整体任务目标。""")
        ]
        
        return self._call_llm(messages)
    
    def plan(self, task: str) -> ExecutionPlan:
        """制定任务执行计划"""
        messages = [
            SystemMessage(content="""你是一个任务规划专家。请将复杂任务分解为具体的执行步骤。
每个步骤应该是一个明确的、可执行的动作。
返回 JSON 格式的步骤列表。"""),
            HumanMessage(content=f"""请为以下任务制定执行计划：
{task}

返回格式：
{{
    "steps": ["步骤1", "步骤2", "步骤3", ...]
}}""")
        ]
        
        response = self._call_llm(messages)
        
        try:
            # 尝试解析 JSON
            plan_data = json.loads(response)
            steps = plan_data.get("steps", [])
        except json.JSONDecodeError:
            # 如果不是 JSON，尝试从文本中提取步骤
            logger.warning("Failed to parse JSON, extracting steps from text")
            steps = []
            for line in response.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # 移除数字和符号前缀
                    step = line.lstrip('0123456789.- \t')
                    if step:
                        steps.append(step)
        
        if not steps:
            # 使用默认步骤
            steps = self._get_default_steps(task)
        
        return ExecutionPlan(goal=task, steps=steps)
    
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
            SystemMessage(content="你是一个代码分析专家，擅长分析和理解各种格式的技术文档。"),
            HumanMessage(content=f"""{instruction}

内容：
{content}

请以 JSON 格式返回分析结果。""")
        ]
        
        response = self._call_llm(messages)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"raw_response": response}
    
    def generate_code(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> str:
        """生成代码"""
        system_prompt = """你是一个专业的代码生成专家，擅长生成高质量的 Python 代码。
生成的代码应该：
1. 遵循 PEP 8 规范
2. 包含适当的类型注解
3. 有清晰的注释
4. 处理错误情况
5. 使用现代 Python 特性（3.8+）"""
        
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
        
        # 初始化上下文，存储原始任务
        self.context = {
            "task": task,
            "task_description": task
        }
        
        # 1. 制定执行计划
        logger.info("Creating execution plan...")
        plan = self.plan(task)
        logger.info(f"Execution plan created with {len(plan.steps)} steps:")
        for i, step in enumerate(plan.steps):
            logger.info(f"  Step {i+1}: {step}")
        
        # 2. 执行计划
        iteration = 0
        while not plan.is_complete() and iteration < self.max_iterations:
            iteration += 1
            current_step = plan.get_current_step()
            if not current_step:
                break
                
            logger.info(f"\n{'='*60}")
            logger.info(f"Iteration {iteration}: {current_step}")
            logger.info(f"{'='*60}")
            
            try:
                # 思考当前步骤
                thought = self._think(current_step)
                
                # 决定动作
                action = self._decide_action(thought, current_step)
                
                # 执行动作
                result = self._execute_action(action)
                action.result = result
                
                # 更新上下文
                self._update_context(action)
                
                # 记录动作
                self.action_history.append(action)
                
                # 判断是否可以进入下一步
                if self._should_advance(action, current_step):
                    plan.advance()
                    logger.info(f"✓ Step completed: {current_step}")
                    
            except Exception as e:
                logger.error(f"Action failed: {e}")
                action.error = str(e)
                self.action_history.append(action)
                
                # 尝试恢复或跳过
                if self._can_recover(e):
                    logger.info("Attempting to recover...")
                    continue
                else:
                    return False, f"Task failed: {str(e)}"
        
        # 3. 检查是否完成
        if plan.is_complete():
            logger.info("\n✅ Task completed successfully!")
            return True, "Task completed"
        else:
            logger.warning("\n⚠️ Task did not complete within iteration limit")
            return False, "Max iterations reached"
    
    def _think(self, step: str) -> str:
        """思考当前步骤"""
        context_str = json.dumps(self.context, indent=2, ensure_ascii=False)
        thought = self.think(context_str, step)
        logger.info(f"Thought: {thought[:200]}...")
        return thought
    
    def _decide_action(self, thought: str, step: str) -> Action:
        """基于思考决定动作"""
        # 根据步骤内容决定动作类型
        step_lower = step.lower()
        
        if "读取" in step and ("文件" in step or "pim" in step):
            # 从思考中提取文件路径
            file_path = self._extract_file_path(thought, step)
            return Action(
                type=ActionType.READ_FILE,
                description=f"读取文件: {file_path}",
                params={"file_path": file_path}
            )
        
        elif "分析" in step or "解析" in step:
            # 如果是分析需求或设计相关的分析
            if "需求" in step or "目标" in step:
                return Action(
                    type=ActionType.ANALYZE,
                    description="分析任务需求",
                    params={
                        "content": self.context.get("task", ""),
                        "instruction": f"请分析任务需求：{self.context.get('task', '')}，并提取关键需求点和目标。"
                    }
                )
            else:
                return Action(
                    type=ActionType.ANALYZE,
                    description="分析内容结构",
                    params={
                        "content": self.context.get("file_content", ""),
                        "instruction": f"请分析以下内容并提取关键信息。{step}"
                    }
                )
        
        elif "设计" in step or "定义" in step:
            # 设计相关的步骤，使用生成动作
            if "架构" in step:
                prompt = "基于需求分析，设计系统架构，包括主要组件、层次结构和交互关系"
            elif "数据模型" in step:
                prompt = "基于需求分析，定义数据模型，包括实体、属性和关系"
            elif "功能" in step:
                prompt = "基于需求分析，设计核心功能模块和接口"
            else:
                prompt = f"执行设计任务：{step}"
            
            return Action(
                type=ActionType.GENERATE,
                description=step,
                params={
                    "prompt": prompt,
                    "context": self.context
                }
            )
        
        elif "生成" in step:
            return self._create_generate_action(step)
        
        elif "写入" in step or "保存" in step:
            file_path = self._extract_output_path(step)
            return Action(
                type=ActionType.WRITE_FILE,
                description=f"写入文件: {file_path}",
                params={
                    "file_path": file_path,
                    "content": self.context.get("generated_content", "")
                }
            )
        
        elif "理解" in step or "制定" in step or "实施" in step or "验证" in step:
            # 通用任务步骤，使用生成动作
            return Action(
                type=ActionType.GENERATE,
                description=step,
                params={
                    "prompt": f"基于任务：{self.context.get('task', '')}，执行步骤：{step}",
                    "context": self.context
                }
            )
        
        else:
            # 默认为思考动作
            return Action(
                type=ActionType.THINK,
                description="继续分析和思考",
                params={}
            )
    
    def _create_generate_action(self, step: str) -> Action:
        """创建生成动作"""
        step_lower = step.lower()
        
        # 根据步骤内容决定生成什么
        prompt_map = {
            ("sqlalchemy", "数据模型"): "基于分析结果生成 SQLAlchemy 数据模型",
            ("pydantic", "schema"): "基于分析结果生成 Pydantic Schema 定义",
            ("crud",): "基于数据模型生成 CRUD 操作接口",
            ("api", "endpoint", "rest"): "基于 CRUD 接口生成 REST API 端点",
            ("组合", "psm"): "将所有生成的代码组合成完整的 PSM 文档",
        }
        
        prompt = step  # 默认使用步骤作为提示
        for keywords, custom_prompt in prompt_map.items():
            if any(keyword in step_lower for keyword in keywords):
                prompt = custom_prompt
                break
        
        return Action(
            type=ActionType.GENERATE,
            description=f"生成: {step}",
            params={
                "prompt": prompt,
                "context": self.context.get("analysis", {})
            }
        )
    
    def _execute_action(self, action: Action) -> Any:
        """执行动作"""
        logger.info(f"Executing: {action.type.value} - {action.description}")
        
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
                             ActionType.GENERATE, ActionType.WRITE_FILE]:
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
        return {
            "total_actions": len(self.action_history),
            "successful_actions": sum(1 for a in self.action_history if not a.error),
            "failed_actions": sum(1 for a in self.action_history if a.error),
            "action_types": {
                action_type.value: sum(1 for a in self.action_history if a.type == action_type)
                for action_type in ActionType
            },
            "context_keys": list(self.context.keys()),
            "execution_log": [
                {
                    "type": action.type.value,
                    "description": action.description,
                    "success": action.error is None,
                    "error": action.error
                }
                for action in self.action_history
            ]
        }