"""
Agent CLI v3.0 - 增强版，集成任务分类和自适应规划
"""

import json
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum

from .core import LLMConfig, ActionType
from .executors import LangChainToolExecutor
from .task_classifier import TaskClassifier, TaskType
from .query_handler import QueryHandler
from .improved_planner_v2 import AdaptivePlanner

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from pydantic import SecretStr

# 导入优化组件
from .file_cache_optimizer import FileCacheOptimizer
from .path_validator import PathValidator
from .dependency_analyzer import DependencyAnalyzer
from .decision_optimizer import DecisionOptimizer, DecisionContext, DecisionStrategy
from .file_content_manager import FileContentManager, MergeStrategy

# 导入诊断日志
try:
    from .enhanced_logging import init_diagnostic_logger, get_diagnostic_logger
    DIAGNOSTIC_LOGGING_AVAILABLE = True
except ImportError:
    DIAGNOSTIC_LOGGING_AVAILABLE = False

logger = logging.getLogger(__name__)

# 复用原有的数据结构
from .core_v2_new import (
    StepStatus,
    Action,
    Step
)


class AgentCLI_V3_Enhanced:
    """增强版 Agent CLI v3 - 集成任务分类和自适应规划"""
    
    def __init__(
        self,
        llm_config: LLMConfig,
        use_langchain_tools: bool = True,
        enable_dynamic_planning: bool = True,
        max_actions_per_step: int = 10,
        enable_task_classification: bool = True,  # 新增：任务分类
        enable_adaptive_planning: bool = True,    # 新增：自适应规划
        enable_query_optimization: bool = True,   # 新增：查询优化
        enable_file_cache: bool = True,
        file_cache_ttl: int = 3600,
        enable_path_validation: bool = True,
        project_root: Optional[str] = None,
        enable_diagnostic_logging: bool = True,
        diagnostic_log_file: str = "agent_cli_v3_diagnostics.log"
    ):
        # 基本配置
        self.llm_config = llm_config
        self.use_langchain_tools = use_langchain_tools
        self.enable_dynamic_planning = enable_dynamic_planning
        self.max_actions_per_step = max_actions_per_step
        
        # 新增配置
        self.enable_task_classification = enable_task_classification
        self.enable_adaptive_planning = enable_adaptive_planning
        self.enable_query_optimization = enable_query_optimization
        
        # 初始化 LLM 客户端
        self._init_llm_client()
        
        # 初始化工具执行器
        self.tool_executor = LangChainToolExecutor() if use_langchain_tools else None
        
        # 初始化任务分类器和处理器
        if enable_task_classification:
            self.task_classifier = TaskClassifier()
            # 只在工具执行器存在时创建查询处理器
            self.query_handler = QueryHandler(self.tool_executor) if enable_query_optimization and self.tool_executor else None
            
        # 初始化自适应规划器
        if enable_adaptive_planning:
            self.adaptive_planner = AdaptivePlanner()
            
        # 初始化优化组件
        self.file_cache = FileCacheOptimizer(cache_ttl=file_cache_ttl) if enable_file_cache else None
        self.path_validator = PathValidator(project_root) if enable_path_validation else None
        self.dependency_analyzer = DependencyAnalyzer() if enable_path_validation else None
        
        # 初始化诊断日志
        if enable_diagnostic_logging and DIAGNOSTIC_LOGGING_AVAILABLE:
            self.diagnostic_logger = init_diagnostic_logger(diagnostic_log_file)
        else:
            self.diagnostic_logger = None
            
        # 执行上下文
        self.steps: List[Step] = []
        self.current_step_index: int = 0
        self.execution_history: List[Dict[str, Any]] = []
        self.context: Dict[str, Any] = {
            "created_files": [],
            "modified_files": [],
            "read_files": []
        }
        
    def _init_llm_client(self):
        """初始化 LLM 客户端"""
        if self.llm_config.provider == "openrouter":
            self.llm_client = ChatOpenAI(
                api_key=SecretStr(self.llm_config.api_key) if self.llm_config.api_key else None,
                base_url=self.llm_config.base_url,
                model=self.llm_config.model,
                temperature=self.llm_config.temperature,
                default_headers={
                    "HTTP-Referer": "https://github.com/pim-compiler",
                    "X-Title": "PIM Compiler Agent CLI v3"
                }
            )
        else:
            self.llm_client = ChatOpenAI(
                api_key=SecretStr(self.llm_config.api_key) if self.llm_config.api_key else None,
                base_url=self.llm_config.base_url,
                model=self.llm_config.model,
                temperature=self.llm_config.temperature
            )
    
    def execute_task(self, task: str) -> Tuple[bool, str]:
        """执行任务 - 带任务分类和自适应规划"""
        logger.info(f"Starting task (v3): {task}")
        
        # 记录诊断日志
        if self.diagnostic_logger:
            self.diagnostic_logger.log_task(task)
        
        try:
            # 1. 任务分类
            task_type = TaskType.CREATE  # 默认类型
            confidence = 0.5
            
            if self.enable_task_classification:
                task_type, confidence = self.task_classifier.classify(task)
                logger.info(f"Task classified as: {task_type.value} (confidence: {confidence:.2f})")
                
                # 如果是高置信度的查询任务，使用查询处理器
                if task_type == TaskType.QUERY and confidence > 0.7 and self.query_handler:
                    logger.info("Using optimized query handler")
                    return self._handle_query_task(task)
            
            # 2. 获取执行策略
            strategy = self.task_classifier.get_execution_strategy(task_type) if self.enable_task_classification else {}
            
            # 3. 创建自适应计划
            if self.enable_adaptive_planning:
                plan = self._create_adaptive_plan(task, task_type, strategy)
            else:
                plan = self._create_standard_plan(task)
            
            # 4. 执行计划
            success = self._execute_plan(plan, strategy)
            
            # 5. 记录执行历史
            self.execution_history.append({
                "task": task,
                "task_type": task_type.value if task_type else "unknown",
                "success": success,
                "steps_executed": self.current_step_index
            })
            
            # 6. 生成总结
            if self.diagnostic_logger:
                self.diagnostic_logger.log_summary()
            
            return success, "Task completed successfully" if success else "Task failed"
            
        except Exception as e:
            logger.error(f"Task execution failed: {e}", exc_info=True)
            
            if self.diagnostic_logger:
                self.diagnostic_logger.log_error("Task execution failed", e)
                
            return False, str(e)
    
    def _handle_query_task(self, task: str) -> Tuple[bool, str]:
        """处理查询类任务"""
        # 识别查询类型
        if "执行流程" in task or "流程是什么" in task:
            # 提取项目信息
            import re
            path_match = re.search(r'([/\w\-_]+)', task)
            if path_match:
                project_path = path_match.group(1)
                project_name = project_path.split('/')[-1]
                if self.query_handler:
                    return self.query_handler.handle_execution_flow_query(project_name, project_path)
                else:
                    return self._execute_simple_query(task)
        
        elif "项目结构" in task or "目录结构" in task:
            import re
            path_match = re.search(r'([/\w\-_]+)', task)
            if path_match:
                project_path = path_match.group(1)
                if self.query_handler:
                    return self.query_handler.handle_project_structure_query(project_path)
                else:
                    return self._execute_simple_query(task)
        
        # 默认查询处理
        return self._execute_simple_query(task)
    
    def _execute_simple_query(self, task: str) -> Tuple[bool, str]:
        """执行简单查询"""
        # 使用 LLM 直接回答
        messages = [
            SystemMessage(content="你是一个代码分析助手。请简洁地回答用户的查询。"),
            HumanMessage(content=task)
        ]
        
        response = self.llm_client.invoke(messages)
        # 处理响应内容
        if hasattr(response, 'content'):
            content = response.content
        else:
            content = str(response)
        return True, str(content)
    
    def _create_adaptive_plan(self, task: str, task_type: TaskType, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """创建自适应计划"""
        # 使用自适应规划器
        plan = self.adaptive_planner.create_plan(task, task_type, self.context)
        
        # 基于执行历史优化计划
        if self.execution_history:
            plan = self.adaptive_planner.optimize_plan(plan, self.execution_history)
        
        # 应用策略限制
        if strategy:
            # 限制步骤数
            if "max_steps" in strategy and len(plan.get("steps", [])) > strategy["max_steps"]:
                plan["steps"] = plan["steps"][:strategy["max_steps"]]
            
            # 过滤不允许的动作
            if "avoid_actions" in strategy:
                for step in plan.get("steps", []):
                    if "actions" in step:
                        step["actions"] = [
                            action for action in step["actions"]
                            if not any(avoid in action for avoid in strategy["avoid_actions"])
                        ]
        
        return plan
    
    def _create_standard_plan(self, task: str) -> Dict[str, Any]:
        """创建标准计划（后备方案）"""
        # 使用 LLM 创建计划
        system_prompt = """你是一个任务规划专家。请将任务分解为可执行的步骤。

返回 JSON 格式：
{
    "steps": [
        {
            "name": "步骤名称",
            "actions": ["action1", "action2"],
            "expected_outcome": "预期结果"
        }
    ]
}"""
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"任务：{task}")
        ]
        
        response = self.llm_client.invoke(messages)
        
        try:
            # 处理响应内容
            if hasattr(response, 'content'):
                content = response.content
            else:
                content = str(response)
            return json.loads(str(content))
        except:
            # 如果解析失败，返回简单计划
            return {
                "steps": [
                    {
                        "name": "执行任务",
                        "actions": ["think", "execute"],
                        "expected_outcome": "完成任务"
                    }
                ]
            }
    
    def _execute_plan(self, plan: Dict[str, Any], strategy: Optional[Dict[str, Any]] = None) -> bool:
        """执行计划"""
        steps_data = plan.get("steps", [])
        
        # 转换为 Step 对象
        self.steps = []
        for i, step_data in enumerate(steps_data):
            step = Step(
                name=step_data.get("name", f"Step {i+1}"),
                description=step_data.get("description", ""),
                expected_output=step_data.get("expected_outcome", step_data.get("expected_output", "")),
                status=StepStatus.NOT_STARTED
            )
            
            # 添加动作
            if "actions" in step_data:
                for action_str in step_data["actions"]:
                    # 解析动作字符串
                    if ":" in action_str:
                        action_type, params = action_str.split(":", 1)
                        action = Action(
                            tool_name=action_type,
                            description=f"Execute {action_type}",
                            params={"target": params}
                        )
                        step.actions.append(action)
            
            self.steps.append(step)
        
        # 执行步骤
        for step in self.steps:
            success = self._execute_step(step, strategy)
            if not success:
                return False
            self.current_step_index += 1
        
        return True
    
    def _execute_step(self, step: Step, strategy: Optional[Dict[str, Any]] = None) -> bool:
        """执行单个步骤"""
        logger.info(f"Executing step: {step.name}")
        step.status = StepStatus.IN_PROGRESS
        
        try:
            # 执行所有动作
            for action in step.actions:
                if strategy and "tools_priority" in strategy:
                    # 检查工具优先级
                    if action.tool_name not in strategy["tools_priority"]:
                        logger.warning(f"Skipping low-priority action: {action.tool_name}")
                        continue
                
                # 执行动作
                result = self._execute_action(action)
                if not result.success:
                    step.status = StepStatus.FAILED
                    return False
            
            step.status = StepStatus.COMPLETED
            return True
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            step.status = StepStatus.FAILED
            return False
    
    def _execute_action(self, action: Action) -> Any:
        """执行单个动作"""
        if self.tool_executor:
            # 构建参数
            params = action.params or {}
            
            # 执行工具
            return self.tool_executor.execute(action.tool_name, params)
        else:
            # 模拟执行
            class MockResult:
                def __init__(self):
                    self.success = True
                    self.output = "Mock execution successful"
            
            return MockResult()
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """获取执行总结"""
        return {
            "total_steps": len(self.steps),
            "completed_steps": sum(1 for s in self.steps if s.status == StepStatus.COMPLETED),
            "failed_steps": sum(1 for s in self.steps if s.status == StepStatus.FAILED),
            "created_files": self.context.get("created_files", []),
            "modified_files": self.context.get("modified_files", []),
            "execution_history": self.execution_history[-5:]  # 最近5次执行
        }