"""GenericReactAgent 调试器

提供对 GenericReactAgent 执行流程的调试能力，包括断点、单步执行、状态查看等功能。

基于 LangGraph 执行流程的三个原子步骤：
1. THINK（思考）：AI 分析当前状态，决定下一步行动
2. ACT（行为）：执行具体操作（调用工具或生成响应）
3. OBSERVE（观察）：获取执行结果，更新状态
"""

import os
import sys
import json
import time
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from core.react_agent import GenericReactAgent


class StepType(Enum):
    """原子步骤类型"""
    THINK = "THINK"      # AI 思考决策
    ACT = "ACT"          # 执行行动（工具调用或响应）
    OBSERVE = "OBSERVE"  # 观察结果
    UPDATE_WORLD_VIEW = "UPDATE_WORLD_VIEW"    # 更新客观视图（world_overview.md）
    UPDATE_PERSPECTIVE = "UPDATE_PERSPECTIVE"  # 更新主观视图（.agent_perspectives/）


class StepMode(Enum):
    """调试执行模式"""
    RUN = "RUN"              # 正常运行
    STEP = "STEP"            # 单步执行
    STEP_OVER = "STEP_OVER"  # 步过（跳过工具调用内部）
    STEP_IN = "STEP_IN"      # 步入（进入工具调用）
    STEP_OUT = "STEP_OUT"    # 步出（退出当前层级）


@dataclass
class ExecutionStep:
    """执行步骤记录"""
    step_type: StepType
    timestamp: datetime
    data: Dict[str, Any]
    depth: int = 0  # 调用深度（用于 step in/out）


@dataclass
class Breakpoint:
    """断点基类"""
    id: str
    enabled: bool = True
    hit_count: int = 0
    
    def should_break(self, context: Dict[str, Any]) -> bool:
        """判断是否应该中断"""
        raise NotImplementedError


@dataclass
class StepBreakpoint(Breakpoint):
    """步骤断点：在特定类型的步骤暂停"""
    step_type: StepType = field(default=StepType.THINK)
    
    def should_break(self, context: Dict[str, Any]) -> bool:
        if not self.enabled:
            return False
        return context.get("step_type") == self.step_type


@dataclass
class ToolBreakpoint(Breakpoint):
    """工具断点：在调用特定工具时暂停"""
    tool_name: str = ""
    
    def should_break(self, context: Dict[str, Any]) -> bool:
        if not self.enabled:
            return False
        if context.get("step_type") != StepType.ACT:
            return False
        tool_calls = context.get("tool_calls", [])
        return any(call.get("name") == self.tool_name for call in tool_calls)


@dataclass
class AgentBreakpoint(Breakpoint):
    """Agent 断点：在调用特定子 Agent 时暂停"""
    agent_name: str = ""
    
    def should_break(self, context: Dict[str, Any]) -> bool:
        if not self.enabled:
            return False
        if context.get("step_type") != StepType.ACT:
            return False
        tool_calls = context.get("tool_calls", [])
        # 检查是否是 Agent 调用
        for call in tool_calls:
            tool_name = call.get("name", "")
            if self.agent_name.lower() in tool_name.lower():
                # 额外检查是否真的是 Agent
                is_agent = any(keyword in tool_name.lower() 
                             for keyword in ['agent', 'generator', 'runner', 'reviewer', 'manager'])
                if is_agent:
                    return True
        return False


@dataclass
class ConditionalBreakpoint(Breakpoint):
    """条件断点：满足特定条件时暂停"""
    condition: Callable[[Dict[str, Any]], bool] = field(default=lambda ctx: False)
    condition_str: str = ""  # 条件的字符串表示（用于显示）
    
    def should_break(self, context: Dict[str, Any]) -> bool:
        if not self.enabled:
            return False
        try:
            return self.condition(context)
        except Exception as e:
            print(f"条件断点评估失败: {e}")
            return False


class ReactAgentDebugger:
    """GenericReactAgent 调试器"""
    
    def __init__(self, agent: GenericReactAgent):
        """初始化调试器
        
        Args:
            agent: 要调试的 GenericReactAgent 实例
        """
        self.agent = agent
        self.breakpoints: List[Breakpoint] = []
        self.step_mode = StepMode.RUN
        self.current_state: Dict[str, Any] = {}
        self.execution_history: List[ExecutionStep] = []
        self.call_stack: List[str] = []  # 调用栈
        self.current_depth = 0  # 当前调用深度
        self.paused = False
        self.continue_execution = True
        
        # 调试输出控制
        self.verbose = True
        self.show_messages = True
        self.show_tools = True
        
        # 保存原始的 executor
        self._original_executor = agent._executor
        
    def add_breakpoint(self, breakpoint: Breakpoint) -> str:
        """添加断点
        
        Args:
            breakpoint: 断点对象
            
        Returns:
            断点 ID
        """
        self.breakpoints.append(breakpoint)
        return breakpoint.id
    
    def remove_breakpoint(self, breakpoint_id: str) -> bool:
        """删除断点
        
        Args:
            breakpoint_id: 断点 ID
            
        Returns:
            是否成功删除
        """
        for i, bp in enumerate(self.breakpoints):
            if bp.id == breakpoint_id:
                del self.breakpoints[i]
                return True
        return False
    
    def enable_breakpoint(self, breakpoint_id: str, enabled: bool = True) -> bool:
        """启用/禁用断点
        
        Args:
            breakpoint_id: 断点 ID
            enabled: 是否启用
            
        Returns:
            是否成功设置
        """
        for bp in self.breakpoints:
            if bp.id == breakpoint_id:
                bp.enabled = enabled
                return True
        return False
    
    def list_breakpoints(self) -> List[Dict[str, Any]]:
        """列出所有断点"""
        result = []
        for bp in self.breakpoints:
            info = {
                "id": bp.id,
                "type": bp.__class__.__name__,
                "enabled": bp.enabled,
                "hit_count": bp.hit_count
            }
            
            if isinstance(bp, StepBreakpoint):
                info["step_type"] = bp.step_type.value
            elif isinstance(bp, ToolBreakpoint):
                info["tool_name"] = bp.tool_name
            elif isinstance(bp, ConditionalBreakpoint):
                info["condition"] = bp.condition_str
                
            result.append(info)
        return result
    
    def _check_breakpoints(self, context: Dict[str, Any]) -> Optional[Breakpoint]:
        """检查是否命中断点
        
        Args:
            context: 当前执行上下文
            
        Returns:
            命中的断点对象，如果没有命中则返回 None
        """
        for bp in self.breakpoints:
            if bp.should_break(context):
                bp.hit_count += 1
                return bp
        return None
    
    def _record_step(self, step_type: StepType, data: Dict[str, Any]):
        """记录执行步骤"""
        step = ExecutionStep(
            step_type=step_type,
            timestamp=datetime.now(),
            data=data,
            depth=self.current_depth
        )
        self.execution_history.append(step)
    
    def _update_state(self, **kwargs):
        """更新当前状态"""
        self.current_state.update(kwargs)
    
    def _format_message(self, message: BaseMessage) -> str:
        """格式化消息显示"""
        if isinstance(message, HumanMessage):
            return f"👤 用户: {message.content}"
        elif isinstance(message, SystemMessage):
            return f"💻 系统: {message.content[:100]}..."
        elif isinstance(message, AIMessage):
            if hasattr(message, 'tool_calls') and message.tool_calls:
                tools = ", ".join(tc.get('name', 'unknown') for tc in message.tool_calls)
                return f"🤔 AI 决定调用工具: {tools}"
            else:
                return f"💬 AI: {message.content}"
        elif isinstance(message, ToolMessage):
            content = message.content
            if len(content) > 200:
                content = content[:200] + "..."
            return f"🔧 工具结果 ({message.name}): {content}"
        else:
            return f"❓ {type(message).__name__}: {str(message)[:100]}..."
    
    def _print_state(self):
        """打印当前状态"""
        print("\n" + "="*80)
        print("📊 调试器状态视图")
        print("="*80)
        
        # 1. 基本执行信息
        print("\n🎯 执行状态:")
        print(f"  当前步骤类型: {self.current_state.get('step_type', 'N/A')}")
        print(f"  调用深度: {self.current_depth}")
        print(f"  执行历史长度: {len(self.execution_history)} 步")
        print(f"  调试模式: {self.step_mode.value}")
        
        # 2. 当前消息详情
        if "last_message" in self.current_state:
            last_msg = self.current_state["last_message"]
            print(f"\n💬 当前消息:")
            print(f"  类型: {type(last_msg).__name__}")
            
            # 根据消息类型显示不同信息
            if hasattr(last_msg, 'content'):
                content = last_msg.content
                if len(content) > 200:
                    print(f"  内容: {content[:200]}...")
                else:
                    print(f"  内容: {content}")
                    
            if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
                print(f"  工具调用数: {len(last_msg.tool_calls)}")
                
            if hasattr(last_msg, 'name'):
                print(f"  工具名称: {last_msg.name}")
        
        # 3. 消息历史
        if self.show_messages and "messages" in self.current_state:
            messages = self.current_state["messages"]
            print(f"\n📜 消息历史 (最近 5 条，共 {len(messages)} 条):")
            # 显示最近的 5 条消息
            for i, msg in enumerate(messages[-5:]):
                print(f"  [{len(messages)-5+i}] {self._format_message(msg)}")
        
        # 4. 工具调用详情
        if self.show_tools and "tool_calls" in self.current_state:
            tool_calls = self.current_state["tool_calls"]
            if tool_calls:
                print(f"\n🔧 工具调用详情:")
                for i, tc in enumerate(tool_calls):
                    print(f"  [{i}] 工具: {tc.get('name', 'unknown')}")
                    args = tc.get('args', {})
                    print(f"      参数:")
                    for key, value in args.items():
                        value_str = str(value)
                        if len(value_str) > 100:
                            value_str = value_str[:100] + "..."
                        print(f"        - {key}: {value_str}")
                    
                    # 检查是否是子 Agent
                    tool_name = tc.get('name', '')
                    is_agent = any(kw in tool_name.lower() 
                                 for kw in ['agent', 'generator', 'runner', 'reviewer', 'manager'])
                    if is_agent:
                        print(f"      类型: 子 Agent ⭐")
                    else:
                        print(f"      类型: 普通工具")
        
        # 5. Agent 信息
        print(f"\n🤖 Agent 信息:")
        print(f"  名称: {self.agent.name}")
        print(f"  工作目录: {self.agent.work_dir}")
        print(f"  记忆级别: {self.agent.config.memory_level}")
        print(f"  LLM 模型: {self.agent.config.llm_model}")
        
        # 6. 调用栈（仅子 Agent）
        if self.call_stack:
            print(f"\n📚 Agent 调用栈:")
            for i, frame in enumerate(self.call_stack):
                print(f"  [{i}] {frame}")
        else:
            print(f"\n📚 Agent 调用栈: (空)")
        
        # 7. 断点信息
        active_bps = [bp for bp in self.breakpoints if bp.enabled]
        if active_bps:
            print(f"\n🔴 活跃断点 ({len(active_bps)} 个):")
            for bp in active_bps[:3]:  # 只显示前3个
                bp_info = f"  - {bp.id} ({bp.__class__.__name__})"
                if hasattr(bp, 'step_type'):
                    bp_info += f" - {bp.step_type.value}"
                elif hasattr(bp, 'tool_name'):
                    bp_info += f" - {bp.tool_name}"
                elif hasattr(bp, 'agent_name'):
                    bp_info += f" - {bp.agent_name}"
                elif hasattr(bp, 'condition_str'):
                    bp_info += f" - {bp.condition_str}"
                print(bp_info)
        
        # 8. 执行统计
        if self.execution_history:
            step_counts = {}
            for step in self.execution_history:
                step_type = step.step_type.value
                step_counts[step_type] = step_counts.get(step_type, 0) + 1
            
            print(f"\n📈 执行统计:")
            for step_type, count in step_counts.items():
                print(f"  {step_type}: {count} 次")
        
        # 9. 内存和知识文件（如果可用）
        if hasattr(self.agent, 'prior_knowledge') and self.agent.prior_knowledge:
            print(f"\n📚 知识文件: 已加载 ({len(self.agent.prior_knowledge)} 字符)")
            
        if hasattr(self.agent, 'memory') and self.agent.memory:
            print(f"💾 记忆系统: 活跃")
        
        print("="*80)
    
    def _handle_debug_command(self) -> bool:
        """处理调试命令
        
        Returns:
            是否继续执行
        """
        while True:
            command = input("\n🐛 调试器> ").strip().lower()
            
            if command in ["c", "continue"]:
                self.step_mode = StepMode.RUN
                return True
                
            elif command in ["s", "step"]:
                self.step_mode = StepMode.STEP
                return True
                
            elif command in ["si", "step in", "stepin"]:
                # 检查当前是否有子 Agent 调用
                if "tool_calls" in self.current_state:
                    tool_calls = self.current_state["tool_calls"]
                    has_agent_tool = any(
                        any(keyword in tc.get('name', '').lower() 
                            for keyword in ['agent', 'generator', 'runner', 'reviewer', 'manager'])
                        for tc in tool_calls
                    )
                    if not has_agent_tool:
                        print("⚠️  当前工具调用不是子 Agent，step in 不可用")
                        continue
                self.step_mode = StepMode.STEP_IN
                return True
                
            elif command in ["so", "step out", "stepout"]:
                if not self.call_stack:
                    print("⚠️  当前不在子 Agent 中，step out 不可用")
                    continue
                self.step_mode = StepMode.STEP_OUT
                return True
                
            elif command in ["sv", "step over", "stepover"]:
                self.step_mode = StepMode.STEP_OVER
                return True
                
            elif command in ["p", "print"]:
                self._print_state()
                
            elif command in ["b", "breakpoints"]:
                bps = self.list_breakpoints()
                if bps:
                    print("\n🔴 断点列表:")
                    for bp in bps:
                        status = "✓" if bp["enabled"] else "✗"
                        print(f"  [{status}] {bp['id']}: {bp['type']} - {bp}")
                else:
                    print("没有设置断点")
                    
            elif command in ["h", "history"]:
                print(f"\n📜 执行历史 (最近 10 步):")
                for step in self.execution_history[-10:]:
                    indent = "  " * step.depth
                    print(f"{indent}{step.timestamp.strftime('%H:%M:%S')} - {step.step_type.value}")
                    
            elif command in ["q", "quit"]:
                self.continue_execution = False
                return False
                
            elif command in ["?", "help"]:
                print("""
调试命令:
  (c)ontinue      - 继续执行到下一个断点
  (s)tep          - 执行一个原子步骤
  (si)step in     - 步入子 Agent 调用（仅对子 Agent 有效）
  (so)step out    - 步出当前子 Agent（仅在子 Agent 内有效）
  (sv)step over   - 步过工具调用
  (p)rint         - 打印当前状态
  (b)reakpoints   - 列出所有断点
  (h)istory       - 显示执行历史
  (sm)             - 列出所有消息的索引和预览
  sm X            - 显示第 X 个消息的详细内容
  (q)uit          - 退出调试
  (?)help         - 显示帮助
  
注意：step in/out 仅对子 Agent 调用有效，普通工具调用请使用 step over
""")
            elif command == "sm" or (command.startswith("sm ") and len(command.split()) == 1):
                # 列出所有消息的索引和预览
                messages = self.current_state.get("messages", [])
                if not messages:
                    print("没有消息")
                else:
                    print(f"\n📬 消息列表 (共 {len(messages)} 条):")
                    print("="*80)
                    for i, msg in enumerate(messages):
                        # 消息类型图标
                        type_icon = {
                            "HumanMessage": "👤",
                            "AIMessage": "🤖",
                            "ToolMessage": "🔧",
                            "SystemMessage": "💻"
                        }.get(type(msg).__name__, "❓")
                        
                        # 预览内容
                        preview = ""
                        if hasattr(msg, 'content'):
                            preview = msg.content[:100].replace('\n', ' ')
                            if len(msg.content) > 100:
                                preview += "..."
                        elif hasattr(msg, 'tool_calls') and msg.tool_calls:
                            tools = [tc.get('name', 'unknown') for tc in msg.tool_calls]
                            preview = f"调用工具: {', '.join(tools)}"
                        
                        print(f"[{i:3d}] {type_icon} {type(msg).__name__:15s} | {preview}")
                    print("="*80)
                    print("提示: 使用 'sm X' 查看特定消息的详细内容")
                    
            elif command.startswith("sm ") and len(command.split()) == 2:
                # sm x - 显示第x个消息的详细内容
                parts = command.split()
                if parts[1].isdigit():
                    msg_index = int(parts[1])
                    messages = self.current_state.get("messages", [])
                    
                    if 0 <= msg_index < len(messages):
                        msg = messages[msg_index]
                        print(f"\n📧 消息 #{msg_index}")
                        print("="*80)
                        print(f"类型: {type(msg).__name__}")
                        
                        # 显示消息内容
                        if hasattr(msg, 'content'):
                            print(f"\n内容:")
                            print("-"*40)
                            print(msg.content)
                            print("-"*40)
                        
                        # 显示工具调用信息
                        if hasattr(msg, 'tool_calls') and msg.tool_calls:
                            print(f"\n工具调用 ({len(msg.tool_calls)} 个):")
                            for i, tc in enumerate(msg.tool_calls):
                                print(f"\n  [{i}] {tc.get('name', 'unknown')}")
                                print(f"      ID: {tc.get('id', 'N/A')}")
                                print(f"      参数:")
                                for key, value in tc.get('args', {}).items():
                                    value_str = str(value)
                                    if len(value_str) > 200:
                                        value_str = value_str[:200] + "..."
                                    print(f"        {key}: {value_str}")
                        
                        # 显示工具消息的额外信息
                        if hasattr(msg, 'name'):
                            print(f"\n工具名称: {msg.name}")
                        
                        if hasattr(msg, 'tool_call_id'):
                            print(f"工具调用 ID: {msg.tool_call_id}")
                        
                        # 显示其他属性
                        if hasattr(msg, 'additional_kwargs') and msg.additional_kwargs:
                            print(f"\n额外信息: {msg.additional_kwargs}")
                        
                        print("="*80)
                    else:
                        print(f"⚠️  无效的消息索引: {msg_index}")
                        print(f"有效范围: 0 到 {len(messages)-1}")
                else:
                    print("⚠️  用法: sm <索引>")
                    print("例如: sm 0")
                    
            else:
                print(f"未知命令: {command}，输入 ? 查看帮助")
    
    def _should_pause(self, step_type: StepType, context: Dict[str, Any]) -> bool:
        """判断是否应该暂停
        
        Args:
            step_type: 当前步骤类型
            context: 执行上下文
            
        Returns:
            是否应该暂停
        """
        # 检查断点
        bp = self._check_breakpoints(context)
        if bp:
            print(f"\n🔴 断点命中: {bp.id} (类型: {bp.__class__.__name__})")
            return True
        
        # 检查步进模式
        if self.step_mode == StepMode.STEP:
            return True
            
        elif self.step_mode == StepMode.STEP_IN:
            # 步入模式：总是暂停
            return True
            
        elif self.step_mode == StepMode.STEP_OUT:
            # 步出模式：当深度减少时暂停
            if self.current_depth < len(self.call_stack):
                return True
                
        elif self.step_mode == StepMode.STEP_OVER:
            # 步过模式：同层级或更高层级时暂停
            if self.current_depth <= len(self.call_stack):
                return True
        
        return False
    
    def execute_task(self, task: str) -> None:
        """执行任务（调试模式）
        
        Args:
            task: 要执行的任务描述
        """
        print("\n🐛 调试器已启动")
        print("输入 ? 查看可用命令\n")
        
        # 重置状态
        self.execution_history.clear()
        self.call_stack.clear()
        self.current_depth = 0
        self.continue_execution = True
        self.current_state.clear()
        
        # 包装 agent 的 stream 方法
        original_stream = self.agent._executor.stream
        
        def debug_stream(inputs: Dict[str, Any], config: Optional[RunnableConfig] = None, **kwargs):
            """调试版本的 stream 方法"""
            
            # 初始化
            all_messages = []
            
            for event in original_stream(inputs, config=config, **kwargs):
                if not self.continue_execution:
                    break
                    
                messages = event.get("messages", [])
                if messages:
                    all_messages = messages
                    last_message = messages[-1]
                    
                    # 识别步骤类型
                    step_type = None
                    tool_calls = []
                    
                    if isinstance(last_message, HumanMessage):
                        # 用户输入
                        step_type = StepType.THINK
                        
                    elif isinstance(last_message, AIMessage):
                        if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                            # AI 决定调用工具
                            step_type = StepType.ACT
                            tool_calls = last_message.tool_calls
                        else:
                            # AI 生成响应
                            step_type = StepType.THINK
                            
                    elif isinstance(last_message, ToolMessage):
                        # 工具返回结果
                        step_type = StepType.OBSERVE
                        
                    elif isinstance(last_message, SystemMessage):
                        # 系统消息，跳过
                        continue
                    
                    if step_type:
                        # 更新状态
                        context = {
                            "step_type": step_type,
                            "messages": all_messages,
                            "last_message": last_message,
                            "tool_calls": tool_calls,
                            "depth": self.current_depth
                        }
                        self._update_state(**context)
                        
                        # 记录步骤
                        self._record_step(step_type, {
                            "message_type": type(last_message).__name__,
                            "content_preview": str(last_message)[:100]
                        })
                        
                        # 显示步骤信息
                        if self.verbose:
                            indent = "  " * self.current_depth
                            print(f"\n{indent}⚡ {step_type.value}: {self._format_message(last_message)}")
                        
                        # 检查是否需要暂停
                        if self._should_pause(step_type, context):
                            self.paused = True
                            self._print_state()
                            
                            # 处理调试命令
                            if not self._handle_debug_command():
                                break
                        
                        # 更新调用栈（只对子 Agent 调用）
                        if step_type == StepType.ACT and tool_calls:
                            for tc in tool_calls:
                                tool_name = tc.get('name', 'unknown')
                                # 检查是否是子 Agent 调用
                                # 子 Agent 工具通常包含 "agent" 或特定后缀
                                is_agent_tool = any(keyword in tool_name.lower() 
                                                  for keyword in ['agent', 'generator', 'runner', 'reviewer', 'manager'])
                                
                                if is_agent_tool:
                                    self.call_stack.append(f"{tool_name}()")
                                    self.current_depth += 1
                                    if self.verbose:
                                        print(f"\n📍 进入子 Agent: {tool_name}")
                                        
                        elif step_type == StepType.OBSERVE:
                            # 只有当前工具是子 Agent 时才更新调用栈
                            if self.call_stack and hasattr(last_message, 'name'):
                                tool_name = last_message.name
                                is_agent_tool = any(keyword in tool_name.lower() 
                                                  for keyword in ['agent', 'generator', 'runner', 'reviewer', 'manager'])
                                if is_agent_tool:
                                    self.call_stack.pop()
                                    self.current_depth = max(0, self.current_depth - 1)
                                    if self.verbose:
                                        print(f"\n📍 退出子 Agent: {tool_name}")
                
                yield event
        
        # 临时替换 stream 方法
        self.agent._executor.stream = debug_stream
        
        try:
            # 执行任务
            self.agent.execute_task(task)
        finally:
            # 恢复原始 stream 方法
            self.agent._executor.stream = original_stream
            
            if self.continue_execution:
                print("\n✅ 调试会话结束")
            else:
                print("\n⛔ 调试会话中断")
            
            # 显示执行统计
            print(f"\n📊 执行统计:")
            print(f"  总步骤数: {len(self.execution_history)}")
            
            # 统计各类步骤
            step_counts = {}
            for step in self.execution_history:
                step_counts[step.step_type.value] = step_counts.get(step.step_type.value, 0) + 1
            
            for step_type, count in step_counts.items():
                print(f"  {step_type}: {count}")


def create_quick_breakpoints() -> List[Breakpoint]:
    """创建常用断点集合"""
    return [
        StepBreakpoint(id="think_bp", step_type=StepType.THINK),
        StepBreakpoint(id="act_bp", step_type=StepType.ACT),
        StepBreakpoint(id="observe_bp", step_type=StepType.OBSERVE),
        ToolBreakpoint(id="file_write_bp", tool_name="write_file"),
        ToolBreakpoint(id="cmd_exec_bp", tool_name="execute_command"),
        ConditionalBreakpoint(
            id="error_bp",
            condition=lambda ctx: "error" in str(ctx.get("last_message", "")).lower(),
            condition_str="消息包含 'error'"
        ),
    ]


if __name__ == "__main__":
    # 简单的命令行测试
    print("ReactAgentDebugger 测试模式")
    print("请使用 debug_demo.py 来运行完整的调试示例")