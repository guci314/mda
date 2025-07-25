"""
兼容层 - 让旧代码可以使用新架构

这个模块提供了从 v1 到 v2 的平滑过渡
"""

from typing import Tuple, Optional, Dict, Any
from .core_v2_new import AgentCLI_V2
from .core import Task, Step as LegacyStep, Action as LegacyAction, StepStatus, TaskStatus


class AgentCLI_Compat(AgentCLI_V2):
    """
    兼容版本的 AgentCLI
    保持 v1 的接口，但使用 v2 的实现
    """
    
    def __init__(self, *args, **kwargs):
        # 处理 v1 特有的参数
        if 'enable_symbolic_fallback' in kwargs:
            # v2 不需要这个参数
            kwargs.pop('enable_symbolic_fallback')
        
        # 处理 working_dir 参数
        if 'working_dir' in kwargs:
            # v2 暂时不使用这个参数
            kwargs.pop('working_dir')
            
        super().__init__(*args, **kwargs)
        
        # 为了兼容，保存一些 v1 的属性
        self.current_task = None
        
    def plan(self, task_description: str) -> Task:
        """
        v1 的 plan 方法
        在 v2 中，计划是在 execute_task 内部创建的
        """
        # 创建一个假的 Task 对象用于兼容
        task = Task(description=task_description)
        self.current_task = task
        return task
        
    def execute_task(self, task: str) -> Tuple[bool, str]:
        """
        重写 execute_task 以支持 v1 的用法
        """
        # 如果传入的是 Task 对象（v1 用法）
        if hasattr(task, 'description'):
            task_str = task.description
        else:
            task_str = task
            
        # 调用 v2 的实现
        success, message = super().execute_task(task_str)
        
        # 如果有 current_task，更新其状态
        if self.current_task:
            if success:
                self.current_task.status = TaskStatus.COMPLETED
            else:
                self.current_task.status = TaskStatus.FAILED
                
        return success, message
        
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        v1 的执行摘要方法
        """
        total_actions = 0
        successful_actions = 0
        failed_actions = 0
        
        if hasattr(self, 'steps'):
            for step in self.steps:
                total_actions += len(step.actions)
                for action in step.actions:
                    if action.success:
                        successful_actions += 1
                    else:
                        failed_actions += 1
                        
        return {
            'total_actions': total_actions,
            'successful_actions': successful_actions,
            'failed_actions': failed_actions,
            'total_steps': len(self.steps) if hasattr(self, 'steps') else 0
        }
        
    def reset(self):
        """v1 的重置方法"""
        self.context = {}
        self.steps = []
        self.current_step_index = 0
        self.current_task = None


# 创建别名以保持向后兼容
def create_v1_compatible_cli(*args, **kwargs):
    """
    创建一个兼容 v1 接口的 CLI 实例
    """
    return AgentCLI_Compat(*args, **kwargs)