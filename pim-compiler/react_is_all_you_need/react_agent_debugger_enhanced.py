"""增强版 React Agent 调试器 - 支持视图更新步骤

在原有调试器基础上，增加了对客观视图和主观视图更新的调试支持。
"""

from typing import Optional, Dict, Any
from react_agent_debugger import ReactAgentDebugger, StepType, ExecutionStep
from react_agent import GenericReactAgent
from perspective_agent import PerspectiveAgent
from datetime import datetime


class EnhancedReactAgentDebugger(ReactAgentDebugger):
    """增强版调试器，支持视图更新步骤"""
    
    def __init__(self, agent: GenericReactAgent):
        super().__init__(agent)
        
        # 检查是否是 PerspectiveAgent
        self.is_perspective_agent = isinstance(agent, PerspectiveAgent)
        
        # 包装视图相关方法
        self._wrap_view_methods()
    
    def _wrap_view_methods(self):
        """包装 Agent 的视图更新方法以捕获调试事件"""
        
        # 1. 包装 world_overview 生成
        if hasattr(self.agent, '_execute_internal_task'):
            original_execute = self.agent._execute_internal_task
            
            def debug_execute_internal_task(task: str):
                # 检查是否是 world_overview 任务
                if hasattr(self.agent, '_pending_overview_task') and task == self.agent._pending_overview_task:
                    # 创建 UPDATE_WORLD_VIEW 步骤
                    step = ExecutionStep(
                        step_type=StepType.UPDATE_WORLD_VIEW,
                        timestamp=datetime.now(),
                        data={
                            'action': 'generate',
                            'reason': 'File does not exist',
                            'task': task[:200] + '...' if len(task) > 200 else task,
                            'work_dir': str(self.agent.work_dir)
                        },
                        depth=self.current_depth
                    )
                    
                    self.execution_history.append(step)
                    self._update_current_state('world_view_status', 'generating')
                    
                    # 检查断点
                    if self._should_break_at_step(step):
                        self._handle_breakpoint(step)
                
                # 执行原始方法
                result = original_execute(task)
                
                # 如果是 world_overview 任务，记录完成
                if hasattr(self.agent, '_pending_overview_task') and task == self.agent._pending_overview_task:
                    self._update_current_state('world_view_status', 'generated')
                
                return result
            
            self.agent._execute_internal_task = debug_execute_internal_task
        
        # 2. 包装 perspective 更新（如果是 PerspectiveAgent）
        if self.is_perspective_agent:
            # 包装 record_observation
            if hasattr(self.agent, 'record_observation'):
                original_record = self.agent.record_observation
                
                def debug_record_observation(category: str, content: str, 
                                           severity: str = "info", context: Optional[str] = None):
                    # 创建 UPDATE_PERSPECTIVE 步骤
                    step = ExecutionStep(
                        step_type=StepType.UPDATE_PERSPECTIVE,
                        timestamp=datetime.now(),
                        data={
                            'action': 'add_observation',
                            'category': category,
                            'content': content[:100] + '...' if len(content) > 100 else content,
                            'severity': severity,
                            'context': context
                        },
                        depth=self.current_depth
                    )
                    
                    self.execution_history.append(step)
                    self._update_current_state('last_observation', {
                        'category': category,
                        'severity': severity,
                        'time': datetime.now().strftime('%H:%M:%S')
                    })
                    
                    # 检查断点
                    if self._should_break_at_step(step):
                        self._handle_breakpoint(step)
                    
                    # 执行原始方法
                    return original_record(category, content, severity, context)
                
                self.agent.record_observation = debug_record_observation
            
            # 包装 update_insight
            if hasattr(self.agent, 'update_insight'):
                original_update = self.agent.update_insight
                
                def debug_update_insight(topic: str, summary: str, details: list, recommendations: list):
                    # 创建 UPDATE_PERSPECTIVE 步骤
                    step = ExecutionStep(
                        step_type=StepType.UPDATE_PERSPECTIVE,
                        timestamp=datetime.now(),
                        data={
                            'action': 'update_insight',
                            'topic': topic,
                            'summary': summary[:100] + '...' if len(summary) > 100 else summary,
                            'detail_count': len(details),
                            'recommendation_count': len(recommendations)
                        },
                        depth=self.current_depth
                    )
                    
                    self.execution_history.append(step)
                    self._update_current_state('last_insight', {
                        'topic': topic,
                        'time': datetime.now().strftime('%H:%M:%S')
                    })
                    
                    # 检查断点
                    if self._should_break_at_step(step):
                        self._handle_breakpoint(step)
                    
                    # 执行原始方法
                    return original_update(topic, summary, details, recommendations)
                
                self.agent.update_insight = debug_update_insight
    
    def _format_step_info(self, step: ExecutionStep) -> str:
        """格式化步骤信息（重写以支持新步骤类型）"""
        # 先调用父类方法处理标准步骤
        if step.step_type in [StepType.THINK, StepType.ACT, StepType.OBSERVE]:
            return super()._format_step_info(step)
        
        # 处理新的步骤类型
        indent = "  " * step.depth
        
        if step.step_type == StepType.UPDATE_WORLD_VIEW:
            action = step.data.get('action', 'unknown')
            if action == 'generate':
                reason = step.data.get('reason', '')
                work_dir = step.data.get('work_dir', '')
                return f"{indent}🌍 更新客观视图: 生成 world_overview.md\n" \
                       f"{indent}   原因: {reason}\n" \
                       f"{indent}   目录: {work_dir}"
            elif action == 'update':
                reason = step.data.get('update_reason', '')
                return f"{indent}🌍 更新客观视图: 更新 world_overview.md\n" \
                       f"{indent}   原因: {reason}"
        
        elif step.step_type == StepType.UPDATE_PERSPECTIVE:
            action = step.data.get('action', 'unknown')
            if action == 'add_observation':
                category = step.data.get('category', '')
                content = step.data.get('content', '')
                severity = step.data.get('severity', 'info')
                severity_icon = {'info': 'ℹ️', 'warning': '⚠️', 'critical': '🔴'}.get(severity, '•')
                return f"{indent}👁️ 更新主观视图: 记录观察\n" \
                       f"{indent}   {severity_icon} [{category}] {content}"
            elif action == 'update_insight':
                topic = step.data.get('topic', '')
                summary = step.data.get('summary', '')
                return f"{indent}💡 更新主观视图: 更新洞察\n" \
                       f"{indent}   主题: {topic}\n" \
                       f"{indent}   概要: {summary}"
        
        return f"{indent}❓ 未知步骤类型: {step.step_type}"
    
    def execute_task(self, task: str) -> None:
        """执行任务（增强调试模式）"""
        print("\n🐛 增强调试器已启动")
        print("支持视图更新步骤调试")
        print("输入 ? 查看可用命令\n")
        
        # 调用父类的 execute_task
        super().execute_task(task)


# 使用示例
if __name__ == "__main__":
    from react_agent import ReactAgentConfig, MemoryLevel
    from pathlib import Path
    
    # 创建测试目录
    test_dir = Path("output/debug_enhanced_test")
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建配置（启用所有视图功能）
    config = ReactAgentConfig(
        work_dir=str(test_dir),
        memory_level=MemoryLevel.SMART,
        enable_world_overview=True,
        enable_perspective=True,
        knowledge_files=["knowledge/core/system_prompt.md"]
    )
    
    # 创建 PerspectiveAgent
    agent = PerspectiveAgent(config, name="debug_test", role="code_reviewer")
    
    # 创建增强调试器
    debugger = EnhancedReactAgentDebugger(agent)
    
    # 添加视图相关断点
    from react_agent_debugger import StepBreakpoint
    debugger.add_breakpoint(StepBreakpoint(step_type=StepType.UPDATE_WORLD_VIEW))
    debugger.add_breakpoint(StepBreakpoint(step_type=StepType.UPDATE_PERSPECTIVE))
    
    # 执行任务
    debugger.execute_task("""分析当前目录并记录你的观察。
使用 record_observation 记录至少一个观察。
使用 update_insight 总结一个洞察。""")