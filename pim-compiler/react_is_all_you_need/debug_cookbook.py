#!/usr/bin/env python3
"""条件断点实用手册

包含各种实际场景的条件断点设置示例。
"""

import os
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from react_agent_debugger import ReactAgentDebugger, ConditionalBreakpoint, StepType


class ConditionalBreakpointCookbook:
    """条件断点实用手册"""
    
    @staticmethod
    def error_detection_breakpoints():
        """错误检测相关的断点"""
        return [
            # 检测任何错误
            ConditionalBreakpoint(
                "bp_any_error",
                lambda ctx: any(word in str(ctx.get("last_message", "")).lower() 
                              for word in ["error", "exception", "failed", "失败"]),
                "检测到错误关键词"
            ),
            
            # 文件不存在错误
            ConditionalBreakpoint(
                "bp_file_not_found",
                lambda ctx: "file not found" in str(ctx.get("last_message", "")).lower() or
                           "no such file" in str(ctx.get("last_message", "")).lower(),
                "文件不存在错误"
            ),
            
            # 权限错误
            ConditionalBreakpoint(
                "bp_permission_denied",
                lambda ctx: "permission denied" in str(ctx.get("last_message", "")).lower() or
                           "access denied" in str(ctx.get("last_message", "")).lower(),
                "权限拒绝错误"
            ),
            
            # 工具执行失败
            ConditionalBreakpoint(
                "bp_tool_failure",
                lambda ctx: (ctx.get("step_type") == StepType.OBSERVE and
                           "exit code" in str(ctx.get("last_message", "")).lower() and
                           "Exit code: 0" not in str(ctx.get("last_message", ""))),
                "工具执行返回非零退出码"
            ),
        ]
    
    @staticmethod
    def file_operation_breakpoints():
        """文件操作相关的断点"""
        return [
            # 创建任何文件
            ConditionalBreakpoint(
                "bp_file_create",
                lambda ctx: any(tc.get("name") == "write_file" 
                              for tc in ctx.get("tool_calls", [])),
                "创建文件操作"
            ),
            
            # 创建特定类型文件
            ConditionalBreakpoint(
                "bp_python_file_create",
                lambda ctx: any(tc.get("name") == "write_file" and
                              tc.get("args", {}).get("file_path", "").endswith(".py")
                              for tc in ctx.get("tool_calls", [])),
                "创建 Python 文件"
            ),
            
            # 大文件操作
            ConditionalBreakpoint(
                "bp_large_file",
                lambda ctx: any(tc.get("name") == "write_file" and
                              len(str(tc.get("args", {}).get("content", ""))) > 1000
                              for tc in ctx.get("tool_calls", [])),
                "写入大文件（超过1000字符）"
            ),
            
            # 删除操作（危险）
            ConditionalBreakpoint(
                "bp_delete_operation",
                lambda ctx: any(tc.get("name") in ["delete_file", "remove_file"] or
                              ("rm " in str(tc.get("args", {}).get("command", "")))
                              for tc in ctx.get("tool_calls", [])),
                "删除文件操作（危险）"
            ),
        ]
    
    @staticmethod
    def performance_breakpoints():
        """性能相关的断点"""
        # 需要访问 debugger 实例
        def create_performance_breakpoints(debugger):
            return [
                # 执行时间过长
                ConditionalBreakpoint(
                    "bp_slow_execution",
                    lambda ctx: (len(debugger.execution_history) > 0 and
                               (datetime.now() - debugger.execution_history[0].timestamp).seconds > 10),
                    "执行时间超过10秒"
                ),
                
                # 执行步骤过多
                ConditionalBreakpoint(
                    "bp_too_many_steps",
                    lambda ctx: len(debugger.execution_history) > 20,
                    "执行步骤超过20步"
                ),
                
                # 重复调用同一工具
                ConditionalBreakpoint(
                    "bp_repeated_tool",
                    lambda ctx: _check_repeated_tools(debugger, ctx),
                    "5步内重复调用同一工具"
                ),
            ]
        return create_performance_breakpoints
    
    @staticmethod
    def ai_behavior_breakpoints():
        """AI 行为相关的断点"""
        return [
            # AI 无法决策
            ConditionalBreakpoint(
                "bp_ai_confused",
                lambda ctx: (ctx.get("step_type") == StepType.THINK and
                           any(phrase in str(ctx.get("last_message", "")).lower()
                               for phrase in ["i'm not sure", "i don't know", "unclear", "confused"])),
                "AI 表示困惑或不确定"
            ),
            
            # AI 请求确认
            ConditionalBreakpoint(
                "bp_ai_confirmation",
                lambda ctx: any(phrase in str(ctx.get("last_message", "")).lower()
                              for phrase in ["confirm", "are you sure", "is this correct", "确认"]),
                "AI 请求用户确认"
            ),
            
            # 多工具调用
            ConditionalBreakpoint(
                "bp_multi_tool_call",
                lambda ctx: len(ctx.get("tool_calls", [])) > 1,
                "AI 同时调用多个工具"
            ),
        ]
    
    @staticmethod
    def data_validation_breakpoints():
        """数据验证相关的断点"""
        return [
            # 空内容
            ConditionalBreakpoint(
                "bp_empty_content",
                lambda ctx: any(tc.get("name") == "write_file" and
                              not tc.get("args", {}).get("content", "").strip()
                              for tc in ctx.get("tool_calls", [])),
                "尝试写入空文件"
            ),
            
            # 敏感信息检测
            ConditionalBreakpoint(
                "bp_sensitive_info",
                lambda ctx: any(word in str(ctx.get("last_message", "")).lower()
                              for word in ["password", "secret", "api_key", "token"]),
                "检测到可能的敏感信息"
            ),
            
            # 路径遍历攻击
            ConditionalBreakpoint(
                "bp_path_traversal",
                lambda ctx: any("../" in str(tc.get("args", {})) or
                              "..\\" in str(tc.get("args", {}))
                              for tc in ctx.get("tool_calls", [])),
                "检测到路径遍历尝试"
            ),
        ]
    
    @staticmethod
    def workflow_breakpoints():
        """工作流相关的断点"""
        # 创建状态机
        workflow_state = {"phase": "init", "files_created": 0}
        
        def phase_transition(ctx):
            """跟踪工作流阶段转换"""
            # 检测阶段转换
            msg = str(ctx.get("last_message", "")).lower()
            
            if "setup" in msg or "initialize" in msg:
                workflow_state["phase"] = "setup"
            elif "test" in msg or "verify" in msg:
                workflow_state["phase"] = "testing"
            elif "complete" in msg or "done" in msg:
                workflow_state["phase"] = "complete"
            
            # 统计文件创建
            for tc in ctx.get("tool_calls", []):
                if tc.get("name") == "write_file":
                    workflow_state["files_created"] += 1
            
            # 在测试阶段且已创建文件时触发
            return (workflow_state["phase"] == "testing" and 
                   workflow_state["files_created"] > 0)
        
        return [
            ConditionalBreakpoint(
                "bp_workflow_phase",
                phase_transition,
                "进入测试阶段"
            ),
        ]


def _check_repeated_tools(debugger, ctx):
    """检查是否在最近5步内重复调用同一工具"""
    if len(debugger.execution_history) < 5:
        return False
    
    recent_tools = []
    for step in debugger.execution_history[-5:]:
        if step.step_type == StepType.ACT:
            # 从步骤数据中提取工具名
            tool_data = step.data.get("tool_calls", [])
            recent_tools.extend([tc.get("name") for tc in tool_data])
    
    # 检查当前工具是否在最近调用中
    current_tools = [tc.get("name") for tc in ctx.get("tool_calls", [])]
    for tool in current_tools:
        if recent_tools.count(tool) >= 2:  # 已经调用过2次
            return True
    return False


def demo_cookbook():
    """演示条件断点手册的使用"""
    print("=== 条件断点实用手册演示 ===\n")
    
    # 创建 Agent
    config = ReactAgentConfig(
        work_dir="output/debug_cookbook",
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0
    )
    agent = GenericReactAgent(config, name="cookbook_demo")
    debugger = ReactAgentDebugger(agent)
    
    # 选择要使用的断点集
    print("选择断点集：")
    print("1. 错误检测")
    print("2. 文件操作")
    print("3. AI 行为")
    print("4. 数据验证")
    print("5. 全部启用")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    # 添加相应的断点
    if choice == "1" or choice == "5":
        for bp in ConditionalBreakpointCookbook.error_detection_breakpoints():
            debugger.add_breakpoint(bp)
            print(f"✓ 添加断点: {bp.condition_str}")
    
    if choice == "2" or choice == "5":
        for bp in ConditionalBreakpointCookbook.file_operation_breakpoints():
            debugger.add_breakpoint(bp)
            print(f"✓ 添加断点: {bp.condition_str}")
    
    if choice == "3" or choice == "5":
        for bp in ConditionalBreakpointCookbook.ai_behavior_breakpoints():
            debugger.add_breakpoint(bp)
            print(f"✓ 添加断点: {bp.condition_str}")
    
    if choice == "4" or choice == "5":
        for bp in ConditionalBreakpointCookbook.data_validation_breakpoints():
            debugger.add_breakpoint(bp)
            print(f"✓ 添加断点: {bp.condition_str}")
    
    # 性能断点需要传入 debugger
    if choice == "5":
        for bp in ConditionalBreakpointCookbook.performance_breakpoints()(debugger):
            debugger.add_breakpoint(bp)
            print(f"✓ 添加断点: {bp.condition_str}")
    
    print(f"\n共设置 {len(debugger.breakpoints)} 个断点")
    
    # 执行测试任务
    print("\n执行测试任务...")
    debugger.execute_task("""
    1. 创建一个 config.json 文件，包含 API 配置
    2. 尝试读取 secret.key 文件（可能不存在）
    3. 创建一个大的 data.txt 文件（超过 1000 字符）
    4. 运行 ls 命令查看文件
    5. 如果有错误，尝试修复
    """)


if __name__ == "__main__":
    # 创建输出目录
    Path("output/debug_cookbook").mkdir(parents=True, exist_ok=True)
    
    print("📚 条件断点实用手册")
    print("="*80)
    print("这个手册包含了各种实用的条件断点示例")
    print("="*80)
    print()
    
    # 显示可用的断点类别
    print("可用的断点类别：")
    print("\n1. 🚨 错误检测断点")
    for bp in ConditionalBreakpointCookbook.error_detection_breakpoints():
        print(f"   - {bp.condition_str}")
    
    print("\n2. 📁 文件操作断点")
    for bp in ConditionalBreakpointCookbook.file_operation_breakpoints():
        print(f"   - {bp.condition_str}")
    
    print("\n3. 🤖 AI 行为断点")
    for bp in ConditionalBreakpointCookbook.ai_behavior_breakpoints():
        print(f"   - {bp.condition_str}")
    
    print("\n4. 🔍 数据验证断点")
    for bp in ConditionalBreakpointCookbook.data_validation_breakpoints():
        print(f"   - {bp.condition_str}")
    
    print("\n5. ⚡ 性能监控断点")
    print("   - 执行时间超过10秒")
    print("   - 执行步骤超过20步")
    print("   - 5步内重复调用同一工具")
    
    input("\n按回车键开始演示...")
    demo_cookbook()