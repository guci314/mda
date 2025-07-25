"""
Agent CLI v2.0 - 支持动态执行架构

核心设计：
1. 动作决策器（Action Decider）：单步决策，决定具体执行什么工具
2. 步骤决策器（Step Decider）：动态决策，判断步骤是否完成，是否需要调整计划
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from .core import LLMConfig, ActionType
from .executors import LangChainToolExecutor

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr

# 导入上下文压缩器
try:
    from .context_compressor import ThreeLayerContextCompressor
    COMPRESSION_AVAILABLE = True
except ImportError:
    COMPRESSION_AVAILABLE = False

# 导入诊断日志器
try:
    from .enhanced_logging import init_diagnostic_logger, get_diagnostic_logger
    DIAGNOSTIC_LOGGING_AVAILABLE = True
except ImportError:
    DIAGNOSTIC_LOGGING_AVAILABLE = False

logger = logging.getLogger(__name__)

# 定义提示词
PLANNER_SYSTEM_PROMPT = """你是一个任务规划专家。根据用户的任务描述，制定详细的执行计划。

计划要求：
1. 将任务分解为清晰的步骤
2. 每个步骤应该有明确的目标和期望输出
3. 步骤之间应该有逻辑顺序

返回格式（JSON）：
{
    "steps": [
        {
            "name": "步骤名称",
            "description": "步骤详细描述",
            "expected_output": "期望的输出结果"
        }
    ]
}"""

PLANNER_HUMAN_PROMPT = "任务：{task}\n\n请制定执行计划。"


class StepStatus(Enum):
    """步骤状态"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"  
    COMPLETED = "completed"
    FAILED = "failed"
    

@dataclass
class Action:
    """动作记录"""
    tool_name: str
    description: str
    params: Dict[str, Any]
    result: Optional[str] = None
    success: bool = False
    

@dataclass
class Step:
    """步骤定义"""
    name: str
    description: str
    expected_output: str
    status: StepStatus = StepStatus.NOT_STARTED
    actions: List[Action] = field(default_factory=list)
    result: Optional[str] = None
    

class AgentCLI_V2:
    """支持动态执行的 Agent CLI
    
    两个核心决策器：
    1. 动作决策器：决定使用什么工具，如何使用
    2. 步骤决策器：决定步骤是否完成，是否需要调整计划
    """
    
    def __init__(
        self,
        llm_config: LLMConfig,
        use_langchain_tools: bool = True,
        enable_dynamic_planning: bool = True,
        max_actions_per_step: int = 10,  # 防止无限循环
        enable_context_compression: bool = True,  # 启用上下文压缩
        context_size_limit: int = 30 * 1024,  # 30KB 触发压缩
        recent_file_window: int = 3,  # 保护最近的3个文件
        enable_diagnostic_logging: bool = True,  # 启用诊断日志
        diagnostic_log_file: str = "agent_cli_diagnostics.log"  # 诊断日志文件
    ):
        self.llm_config = llm_config
        self.use_langchain_tools = use_langchain_tools
        self.enable_dynamic_planning = enable_dynamic_planning
        self.max_actions_per_step = max_actions_per_step
        self.enable_context_compression = enable_context_compression and COMPRESSION_AVAILABLE
        self.context_size_limit = context_size_limit
        self.recent_file_window = recent_file_window
        
        # 初始化 LLM 客户端
        if llm_config.provider == "openrouter":
            self.llm_client = ChatOpenAI(
                api_key=SecretStr(llm_config.api_key) if llm_config.api_key else None,
                base_url=llm_config.base_url,
                model=llm_config.model,
                temperature=llm_config.temperature,
                default_headers={
                    "HTTP-Referer": "https://github.com/pim-compiler",
                    "X-Title": "PIM Compiler Agent CLI"
                },
                max_tokens=1000
            )
        else:
            self.llm_client = ChatOpenAI(
                api_key=SecretStr(llm_config.api_key) if llm_config.api_key else None,
                base_url=llm_config.base_url,
                model=llm_config.model,
                temperature=llm_config.temperature,
                max_tokens=1000
            )
        self.output_parser = StrOutputParser()
        
        # 初始化执行器
        self.executor = LangChainToolExecutor()
        
        # 初始化压缩器（如果启用）
        self.context_compressor = None
        if self.enable_context_compression:
            self.context_compressor = ThreeLayerContextCompressor(
                llm_client=self.llm_client,
                context_size_limit=context_size_limit,
                recent_file_window=recent_file_window
            )
            logger.info(f"Context compression enabled (limit: {context_size_limit} bytes)")
            
        # 上下文
        self.context: Dict[str, Any] = {
            "file_contents": {}  # 改进的文件存储策略
        }
        
        # 初始化诊断日志器
        self.diagnostic_logger = None
        if enable_diagnostic_logging and DIAGNOSTIC_LOGGING_AVAILABLE:
            self.diagnostic_logger = init_diagnostic_logger(diagnostic_log_file)
            logger.info(f"Diagnostic logging enabled: {diagnostic_log_file}")
        self.steps: List[Step] = []
        self.current_step_index: int = 0
        
    def execute_task(self, task: str) -> Tuple[bool, str]:
        """执行任务"""
        logger.info(f"Starting task: {task}")
        self.context["task"] = task
        
        # 记录诊断日志
        if self.diagnostic_logger:
            self.diagnostic_logger.log_task(task)
        
        try:
            # 1. 创建初始计划
            self._create_plan(task)
            
            # 2. 执行步骤
            while self.current_step_index < len(self.steps):
                step = self.steps[self.current_step_index]
                
                # 执行单个步骤（支持多动作）
                success = self._execute_step(step)
                
                if not success:
                    return False, f"Step failed: {step.name}"
                    
                # 动态调整计划（如果启用）
                if self.enable_dynamic_planning and self.current_step_index < len(self.steps) - 1:
                    self._adjust_plan_if_needed()
                    
                self.current_step_index += 1
                
            # 诊断日志 - 生成总结
            if self.diagnostic_logger:
                self.diagnostic_logger.log_summary()
                
            return True, "Task completed successfully"
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            
            # 诊断日志 - 错误
            if self.diagnostic_logger:
                self.diagnostic_logger.log_error("Task execution failed", e)
                self.diagnostic_logger.log_summary()
                
            return False, str(e)
            
    def _execute_step(self, step: Step) -> bool:
        """执行单个步骤 - 支持多个动作"""
        logger.info(f"\n{'='*60}")
        logger.info(f"Executing step: {step.name}")
        logger.info(f"Description: {step.description}")
        logger.info(f"Expected output: {step.expected_output}")
        logger.info(f"{'='*60}")
        
        # 诊断日志 - 步骤开始
        if self.diagnostic_logger:
            self.diagnostic_logger.log_step_start(
                step.name, step.description, step.expected_output
            )
        
        step.status = StepStatus.IN_PROGRESS
        action_count = 0
        
        while action_count < self.max_actions_per_step:
            # 1. 使用动作决策器决定下一个动作
            action_decision = self._action_decider(step)
            
            if not action_decision:
                logger.info("No more actions needed for this step")
                break
                
            # 2. 执行动作
            action = Action(
                tool_name=action_decision["tool_name"],
                description=action_decision["description"],
                params=action_decision["params"]
            )
            
            logger.info(f"\nAction {action_count + 1}: {action.tool_name} - {action.description}")
            
            # 诊断日志 - 动作
            if self.diagnostic_logger:
                self.diagnostic_logger.log_action(
                    action_count + 1, action.tool_name, 
                    action.description, action.params
                )
            
            try:
                if self.use_langchain_tools:
                    # LangChain 执行器使用工具名称
                    result = self.executor.execute(
                        tool_name=action.tool_name,
                        parameters=action.params
                    )
                    if hasattr(result, 'output'):
                        action.result = result.output
                    else:
                        action.result = str(result)
                else:
                    # 传统执行器使用动作类型
                    result = self.executor.execute(
                        action_type=self._get_action_type(action.tool_name),
                        params=action.params
                    )
                    action.result = str(result)
                action.success = True
                logger.info(f"✓ Action completed successfully")
                
                # 诊断日志 - 动作结果
                if self.diagnostic_logger:
                    self.diagnostic_logger.log_action_result(
                        True, action.result
                    )
                
                # 更新上下文
                self._update_context_from_action(action)
                
                # 检查并压缩上下文（如果需要）
                if self.enable_context_compression and self.context_compressor:
                    if self.context_compressor.should_compress(self.context):
                        logger.info("Context size exceeded limit, compressing...")
                        original_context = self.context.copy()
                        self.context = self.context_compressor.compress_with_attention(
                            self.context,
                            task=self.context.get("task", ""),
                            step_plan=self.steps,
                            current_step=step,
                            current_action=action.description
                        )
                        # 保存压缩统计
                        stats = self.context_compressor.get_compression_stats(
                            original_context, self.context
                        )
                        self.context["_compression_stats"] = stats
                        logger.info(f"Compression completed: {stats['space_saved_percentage']:.1f}% saved")
                        
                        # 诊断日志 - 压缩
                        if self.diagnostic_logger:
                            self.diagnostic_logger.log_context_compression(
                                stats['original_size'],
                                stats['compressed_size'],
                                stats['space_saved_percentage']
                            )
                
            except Exception as e:
                logger.error(f"✗ Action failed: {e}")
                action.result = str(e)
                action.success = False
                
                # 诊断日志 - 动作失败
                if self.diagnostic_logger:
                    self.diagnostic_logger.log_action_result(
                        False, None, str(e)
                    )
                
                step.status = StepStatus.FAILED
                return False
                
            # 3. 记录动作
            step.actions.append(action)
            action_count += 1
            
            # 4. 使用步骤决策器判断步骤是否完成
            if self._step_decider(step):
                logger.info(f"\n✓ Step completed: {step.name}")
                break
                
        # 检查是否因为达到最大动作数而退出
        if action_count >= self.max_actions_per_step:
            logger.warning(f"Reached maximum actions ({self.max_actions_per_step}) for step")
            if self.diagnostic_logger:
                self.diagnostic_logger.log_warning(
                    f"Step '{step.name}' reached maximum actions limit ({self.max_actions_per_step})"
                )
            
        step.status = StepStatus.COMPLETED
        
        # 诊断日志 - 步骤结束
        if self.diagnostic_logger:
            self.diagnostic_logger.log_step_end(step.name, step.status.value)
            
        return True
        
    def _action_decider(self, step: Step) -> Optional[Dict]:
        """动作决策器 - 决定下一个动作"""
        # 构建动作决策提示词
        system_prompt = """你是一个动作决策专家。根据当前步骤和已执行的动作，决定下一个需要执行的动作。

可用工具：
- read_file: 读取文件内容
- write_file: 写入文件内容
- list_files: 列出目录文件
- python_repl: 执行Python代码
- bash: 执行系统命令

决策原则：
1. 分析步骤目标和已完成的动作
2. 如果步骤目标已达成，返回 null
3. 否则返回下一个必要的动作

返回格式：
{
    "tool_name": "工具名称",
    "description": "这个动作要做什么",
    "params": {"参数名": "参数值"}
}

或者如果不需要更多动作：
null"""

        # 构建已执行动作的摘要
        actions_summary = ""
        if step.actions:
            actions_summary = "\n已执行的动作：\n"
            for i, action in enumerate(step.actions, 1):
                actions_summary += f"{i}. {action.tool_name}: {action.description}"
                if action.success:
                    actions_summary += " ✓"
                else:
                    actions_summary += " ✗"
                actions_summary += "\n"
                
        human_prompt = f"""当前步骤：{step.name}
步骤描述：{step.description}
期望输出：{step.expected_output}

{actions_summary}

任务上下文：{self.context.get('task', '未知')}

请决定下一个动作，如果步骤已完成则返回 null。"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            response = self.llm_client.invoke(messages)
            response = response.content if hasattr(response, 'content') else str(response)
            
            content = response.strip()
            if content.lower() == "null" or content == "None":
                return None
                
            # 解析 JSON
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            decision = json.loads(content)
            
            # 验证必需字段
            required = ["tool_name", "description", "params"]
            for field in required:
                if field not in decision:
                    raise ValueError(f"Missing required field: {field}")
                    
            return decision
            
        except Exception as e:
            logger.error(f"Action decision failed: {e}")
            return None
            
    def _step_decider(self, step: Step) -> bool:
        """步骤决策器 - 判断步骤是否完成"""
        if not step.actions:
            return False
            
        # 构建步骤决策提示词
        system_prompt = """你是一个步骤完成度评估专家。根据步骤目标和已执行的动作，判断步骤是否已经完成。

评估标准：
1. 检查期望输出是否已经实现
2. 检查所有必要的子任务是否完成
3. 考虑动作的执行结果

返回格式：
{
    "completed": true/false,
    "reason": "判断理由",
    "missing": "如果未完成，还缺少什么"
}"""

        # 构建动作执行详情
        actions_detail = "已执行的动作及结果：\n"
        for i, action in enumerate(step.actions, 1):
            actions_detail += f"\n{i}. {action.tool_name}: {action.description}\n"
            actions_detail += f"   参数: {json.dumps(action.params, ensure_ascii=False)}\n"
            actions_detail += f"   结果: {'成功' if action.success else '失败'}\n"
            if action.result:
                # 限制结果长度
                result_preview = action.result[:200] + "..." if len(action.result) > 200 else action.result
                actions_detail += f"   输出: {result_preview}\n"

        human_prompt = f"""步骤名称：{step.name}
步骤描述：{step.description}
期望输出：{step.expected_output}

{actions_detail}

请判断这个步骤是否已经完成。"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            response = self.llm_client.invoke(messages)
            response = response.content if hasattr(response, 'content') else str(response)
            
            # 解析 JSON
            content = response.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            decision = json.loads(content)
            
            logger.info(f"Step completion decision: {decision}")
            
            # 诊断日志 - 步骤决策
            if self.diagnostic_logger:
                self.diagnostic_logger.log_step_decision(
                    decision.get("completed", False),
                    decision.get("reason", ""),
                    decision.get("missing")
                )
            
            return decision.get("completed", False)
            
        except Exception as e:
            logger.error(f"Step decision failed: {e}")
            # 默认认为未完成，继续执行
            return False
            
    def _create_plan(self, task: str):
        """创建执行计划"""
        logger.info("Creating execution plan...")
        
        try:
            messages = [
                SystemMessage(content=PLANNER_SYSTEM_PROMPT),
                HumanMessage(content=PLANNER_HUMAN_PROMPT.format(task=task))
            ]
            response = self.llm_client.invoke(messages)
            response = response.content if hasattr(response, 'content') else str(response)
            
            # 解析计划
            plan_text = response.strip()
            if plan_text.startswith("```json"):
                plan_text = plan_text[7:]
            if plan_text.endswith("```"):
                plan_text = plan_text[:-3]
                
            plan_data = json.loads(plan_text)
            
            # 创建步骤对象
            self.steps = []
            for step_data in plan_data.get("steps", []):
                step = Step(
                    name=step_data["name"],
                    description=step_data.get("description", ""),
                    expected_output=step_data.get("expected_output", "")
                )
                self.steps.append(step)
                
            logger.info(f"Created plan with {len(self.steps)} steps:")
            for i, step in enumerate(self.steps, 1):
                logger.info(f"  Step {i}: {step.name}")
                
        except Exception as e:
            logger.error(f"Failed to create plan: {e}")
            raise
            
    def _adjust_plan_if_needed(self):
        """动态调整计划（如果需要）"""
        # 构建计划调整提示词
        system_prompt = """你是一个计划调整专家。根据已完成的步骤和当前进展，判断是否需要调整后续计划。

调整原则：
1. 如果当前进展顺利，保持原计划
2. 如果发现新的依赖或问题，调整计划
3. 如果某些步骤变得不必要，可以删除

返回格式：
{
    "need_adjustment": true/false,
    "reason": "调整理由",
    "new_steps": [调整后的步骤列表，如果需要]
}"""

        # 构建当前进展摘要
        completed_steps = [s for s in self.steps[:self.current_step_index+1] if s.status == StepStatus.COMPLETED]
        remaining_steps = self.steps[self.current_step_index+1:]
        
        progress_summary = "已完成的步骤：\n"
        for step in completed_steps:
            progress_summary += f"- {step.name}: {step.description}\n"
            
        progress_summary += "\n剩余步骤：\n"
        for step in remaining_steps:
            progress_summary += f"- {step.name}: {step.description}\n"

        human_prompt = f"""任务：{self.context.get('task', '未知')}

{progress_summary}

请判断是否需要调整剩余的执行计划。"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=human_prompt)
            ]
            response = self.llm_client.invoke(messages)
            response = response.content if hasattr(response, 'content') else str(response)
            
            # 解析决策
            content = response.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
                
            decision = json.loads(content)
            
            if decision.get("need_adjustment", False):
                logger.info(f"Plan adjustment needed: {decision.get('reason')}")
                # TODO: 实现计划调整逻辑
                
        except Exception as e:
            logger.error(f"Plan adjustment decision failed: {e}")
            # 继续执行原计划
            
    def _get_action_type(self, tool_name: str) -> ActionType:
        """将工具名称转换为动作类型"""
        mapping = {
            "read_file": ActionType.READ_FILE,
            "write_file": ActionType.WRITE_FILE,
            "list_files": ActionType.LIST_FILES,
            "python_repl": ActionType.PYTHON,
            "bash": ActionType.BASH
        }
        return mapping.get(tool_name, ActionType.READ_FILE)
        
    def _update_context_from_action(self, action: Action):
        """根据动作结果更新上下文"""
        import time
        
        # 如果是读取文件，保存内容到文件字典
        if action.tool_name == "read_file" and action.success:
            file_path = action.params.get("path", action.params.get("file_path", ""))
            if file_path:
                # 使用改进的存储策略
                if "file_contents" not in self.context:
                    self.context["file_contents"] = {}
                    
                self.context["file_contents"][file_path] = {
                    "content": action.result,
                    "timestamp": time.time(),
                    "size": len(action.result) if action.result else 0
                }
                
                # 仍然保留最后文件信息以保持兼容性
                self.context["last_file_content"] = action.result
                self.context["last_file_path"] = file_path
                
                logger.debug(f"Stored file content: {file_path} ({len(action.result)} bytes)")
            
        # 如果是写入文件，记录已创建的文件
        elif action.tool_name == "write_file" and action.success:
            if "created_files" not in self.context:
                self.context["created_files"] = []
            file_path = action.params.get("path", action.params.get("file_path", ""))
            if file_path:
                self.context["created_files"].append(file_path)
                
    def get_context_size(self) -> int:
        """获取当前上下文大小"""
        if self.context_compressor:
            return self.context_compressor._calculate_context_size(self.context)
        return 0
        
    def get_compression_stats(self) -> Optional[Dict[str, Any]]:
        """获取压缩统计信息"""
        if self.context.get("_compressed") and self.context.get("_compression_stats"):
            return self.context["_compression_stats"]
        return None