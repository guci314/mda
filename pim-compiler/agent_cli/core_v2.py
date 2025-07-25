"""
Agent CLI 核心模块 V2 - 支持动态执行架构
"""
import json
import time
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import SystemMessage, HumanMessage

# 为了避免循环导入，直接定义需要的类
from .core import (
    ActionType, StepStatus, TaskStatus, 
    Action, Step, Task, LLMConfig
)

# 导入基础 AgentCLI
from . import core
BaseAgentCLI = core.AgentCLI

logger = logging.getLogger(__name__)


@dataclass
class StepDecision:
    """步骤完成决策"""
    is_complete: bool
    reason: str
    add_steps: Optional[List[Dict[str, str]]] = None
    remove_steps: Optional[List[str]] = None


class AgentCLIV2(BaseAgentCLI):
    """增强版 Agent CLI - 支持动态执行"""
    
    def __init__(self, llm_config: LLMConfig, **kwargs):
        # 提取自定义参数
        self.max_actions_per_step = kwargs.pop('max_actions_per_step', 10)
        self.enable_dynamic_planning = kwargs.pop('enable_dynamic_planning', True)
        
        # 调用父类构造函数
        super().__init__(llm_config, **kwargs)
    
    def execute_task(self, task: str) -> Tuple[bool, str]:
        """执行任务 - 增强版"""
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
        
        while not self.current_task.is_completed:
            current_step = self.current_task.current_step
            if not current_step:
                break
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Executing Step: {current_step.name}")
            logger.info(f"{'='*60}")
            
            # 执行当前步骤（支持多动作）
            success, message = self._execute_step_with_loop(current_step)
            
            if not success:
                self.current_task.fail(message)
                return False, f"Task failed: {message}"
            
            # 动态调整计划（如果需要）
            if self.enable_dynamic_planning:
                self._check_and_adjust_plan(current_step)
            
            # 前进到下一步
            self.current_task.advance_step()
        
        # 3. 任务完成
        self.current_task.complete()
        logger.info("\n✅ Task completed successfully!")
        return True, "Task completed"
    
    def _execute_step_with_loop(self, current_step: Step) -> Tuple[bool, Optional[str]]:
        """执行单个步骤 - 支持多动作循环"""
        current_step.start()
        action_count = 0
        
        while action_count < self.max_actions_per_step:
            # 1. 思考当前进展
            thought = self._think_about_progress(current_step)
            
            # 2. 决定步骤是否完成
            step_decision = self._decide_step_completion(current_step, thought)
            
            if step_decision.is_complete:
                current_step.complete()
                logger.info(f"✓ Step completed: {current_step.name}")
                logger.info(f"  Reason: {step_decision.reason}")
                return True, None
            
            # 3. 决定下一个动作
            action = self._decide_next_action(thought, current_step)
            
            # 4. 执行动作
            try:
                result = self._execute_action(action)
                action.result = result
                
                # 5. 更新上下文
                self._update_context(action)
                self.current_task.context.update(self.context)
                
                # 6. 记录动作
                current_step.add_action(action)
                action_count += 1
                
            except Exception as e:
                logger.error(f"Action failed: {e}")
                action.error = str(e)
                current_step.add_action(action)
                
                # 尝试恢复
                if self._can_recover(e):
                    logger.info("Attempting to recover...")
                    continue
                else:
                    current_step.fail(str(e))
                    return False, str(e)
        
        # 达到最大动作数
        logger.warning(f"Step '{current_step.name}' reached max actions limit")
        return False, "Max actions per step reached"
    
    def _think_about_progress(self, step: Step) -> str:
        """思考当前步骤的进展"""
        # 构建进展摘要
        progress_summary = {
            "step_name": step.name,
            "step_goal": step.expected_output,
            "actions_taken": len(step.actions),
            "last_action": step.actions[-1].description if step.actions else "None",
            "last_result": step.actions[-1].result[:200] if step.actions and step.actions[-1].result else "None",
            "available_context": list(self.context.keys())
        }
        
        thought_prompt = f"""
分析当前步骤的进展情况。

步骤：{progress_summary['step_name']}
目标：{progress_summary['step_goal']}
已执行动作数：{progress_summary['actions_taken']}
最后动作：{progress_summary['last_action']}
最后结果：{progress_summary['last_result']}
可用数据：{progress_summary['available_context']}

请分析：
1. 目标是否已达成？
2. 还需要做什么？
3. 遇到了什么问题？
"""
        
        messages = [
            SystemMessage(content="你是一个任务执行分析专家。"),
            HumanMessage(content=thought_prompt)
        ]
        
        thought = self._call_llm(messages)
        logger.info(f"Progress thought: {thought[:200]}...")
        return thought
    
    def _decide_step_completion(self, step: Step, thought: str) -> StepDecision:
        """决定步骤是否完成"""
        decision_prompt = f"""
基于当前进展分析，决定步骤是否完成。

步骤名称：{step.name}
期望输出：{step.expected_output}
已执行动作：
{json.dumps([{"action": a.description, "result": bool(a.result and not a.error)} for a in step.actions], indent=2, ensure_ascii=False)}

当前分析：{thought}

请决定：
1. 步骤是否已完成？（考虑期望输出是否达成）
2. 如果未完成，还需要什么动作？

返回 JSON 格式：
{{
    "is_complete": true/false,
    "reason": "判断理由",
    "next_action_hint": "如果未完成，下一步应该做什么"
}}
"""
        
        messages = [
            SystemMessage(content="你是一个任务完成度评估专家。严格基于期望输出判断任务是否完成。"),
            HumanMessage(content=decision_prompt)
        ]
        
        try:
            response = self._call_llm_json(messages)
            
            return StepDecision(
                is_complete=response.get("is_complete", False),
                reason=response.get("reason", "Unknown")
            )
        except Exception as e:
            logger.error(f"Failed to parse step decision: {e}")
            # 默认继续执行
            return StepDecision(is_complete=False, reason="Decision parsing failed")
    
    def _decide_next_action(self, thought: str, step: Step) -> Action:
        """基于当前状态决定下一个动作"""
        # 构建动作历史
        action_history = []
        for a in step.actions:
            action_history.append({
                "action": a.description,
                "success": bool(a.result and not a.error),
                "result_preview": (a.result[:100] + "...") if a.result and len(a.result) > 100 else a.result
            })
        
        # 增强的决策提示
        if self.use_langchain_tools and self.tool_executor is not None:
            tools_desc = "\n\n" + self.tool_executor.format_tools_for_prompt()
            
            prompt_content = f"""基于当前进展选择下一个工具。

当前步骤：{step.name}
目标：{step.expected_output}

已执行动作：
{json.dumps(action_history, indent=2, ensure_ascii=False)}

当前思考：{thought}

{tools_desc}

重要提示：
1. 基于已完成的动作和当前思考，选择最合适的下一个工具
2. 如果需要生成文件，确保 content 参数包含完整内容
3. 避免重复已成功的动作

返回JSON格式：
{{
    "tool_name": "工具名称",
    "description": "要做什么",
    "params": {{"参数名": "参数值"}}
}}
"""
        else:
            # 传统动作决策（保持兼容）
            prompt_content = "..."  # 省略
        
        human_content = f"基于以上信息，决定下一个动作："
        
        messages = [
            SystemMessage(content=prompt_content),
            HumanMessage(content=human_content)
        ]
        
        # 记录决策日志
        logger.debug("=== Next Action Decision ===")
        logger.debug(f"Step: {step.name}")
        logger.debug(f"Actions taken: {len(step.actions)}")
        logger.debug("============================")
        
        try:
            decision = self._call_llm_json(messages)
            logger.info(f"Next action decision: {json.dumps(decision, indent=2, ensure_ascii=False)}")
            
            # 解析为 Action 对象
            if self.use_langchain_tools:
                tool_name = decision.get("tool_name")
                params = decision.get("params", {})
                
                # 映射到 ActionType
                tool_to_action = {
                    "read_file": ActionType.READ_FILE,
                    "write_file": ActionType.WRITE_FILE,
                    "list_files": ActionType.LIST_FILES,
                    "python_repl": ActionType.EXECUTE,
                    "bash": ActionType.EXECUTE,
                }
                action_type = tool_to_action.get(tool_name, ActionType.EXECUTE)
                
                action = Action(
                    type=action_type,
                    description=decision.get("description", f"Execute {tool_name}"),
                    params=params
                )
                # 添加 tool_name 作为额外属性
                action.tool_name = tool_name
                return action
            else:
                # 传统方式
                return self._parse_traditional_action(decision)
                
        except Exception as e:
            logger.error(f"Failed to decide action: {e}")
            # 返回思考动作作为后备
            return Action(
                type=ActionType.THINK,
                description="Thinking about next step",
                params={"thought": thought}
            )
    
    def _check_and_adjust_plan(self, completed_step: Step):
        """检查并调整执行计划"""
        # 这里可以实现动态计划调整逻辑
        # 例如：基于步骤执行结果，决定是否需要添加新步骤
        pass
    
    def _parse_traditional_action(self, decision: Dict[str, Any]) -> Action:
        """解析传统格式的动作决策"""
        action_type_map = {
            "READ_FILE": ActionType.READ_FILE,
            "WRITE_FILE": ActionType.WRITE_FILE,
            "ANALYZE": ActionType.ANALYZE,
            "GENERATE": ActionType.GENERATE,
            "VALIDATE": ActionType.VALIDATE,
            "LIST_FILES": ActionType.LIST_FILES,
            "THINK": ActionType.THINK
        }
        
        action_type_str = decision.get("action_type", "THINK")
        action_type = action_type_map.get(action_type_str, ActionType.THINK)
        
        return Action(
            type=action_type,
            description=decision.get("description", ""),
            params=decision.get("params", {})
        )


# 扩展 Task 类以支持动态步骤管理
def extend_task_class():
    """为 Task 类添加动态管理方法"""
    
    def insert_step_after_current(self, new_step: Step):
        """在当前步骤后插入新步骤"""
        if self.current_step_index < len(self.steps) - 1:
            self.steps.insert(self.current_step_index + 1, new_step)
        else:
            self.steps.append(new_step)
    
    def remove_step(self, step_name: str):
        """删除指定名称的步骤"""
        self.steps = [s for s in self.steps if s.name != step_name]
        # 调整当前步骤索引
        if self.current_step_index >= len(self.steps):
            self.current_step_index = len(self.steps) - 1
    
    # 动态添加方法到 Task 类
    Task.insert_step_after_current = insert_step_after_current
    Task.remove_step = remove_step

# 执行扩展
extend_task_class()