#!/usr/bin/env python3
"""条件断点设置示例

展示 ReactAgentDebugger 中各种条件断点的设置方法和使用场景。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from react_agent_debugger import (
    ReactAgentDebugger,
    ConditionalBreakpoint,
    StepType
)


def demo_basic_conditional_breakpoints():
    """基础条件断点示例"""
    print("=== 基础条件断点示例 ===\n")
    
    # 创建 Agent
    config = ReactAgentConfig(
        work_dir="output/debug_conditional",
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat",
        llm_temperature=0
    )
    agent = GenericReactAgent(config, name="conditional_demo")
    
    # 创建调试器
    debugger = ReactAgentDebugger(agent)
    
    print("1. 消息内容条件断点\n")
    
    # 示例 1: 当消息包含特定关键词时暂停
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_error",
            condition=lambda ctx: "error" in str(ctx.get("last_message", "")).lower(),
            condition_str="消息包含 'error'"
        )
    )
    
    # 示例 2: 当消息包含特定文件名时暂停
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_python_file",
            condition=lambda ctx: ".py" in str(ctx.get("last_message", "")),
            condition_str="消息提到 Python 文件"
        )
    )
    
    # 示例 3: 当 AI 决定调用工具时暂停
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_ai_tool_decision",
            condition=lambda ctx: (
                ctx.get("step_type") == StepType.ACT and 
                len(ctx.get("tool_calls", [])) > 0
            ),
            condition_str="AI 决定调用工具"
        )
    )
    
    print("已设置的条件断点：")
    for bp in debugger.list_breakpoints():
        if bp["type"] == "ConditionalBreakpoint":
            print(f"  - {bp['id']}: {bp['condition']}")
    
    print("\n执行任务...")
    debugger.execute_task("""
    1. 创建一个 test.py 文件
    2. 尝试读取一个不存在的文件 (会产生 error)
    3. 列出目录内容
    """)


def demo_advanced_conditional_breakpoints():
    """高级条件断点示例"""
    print("\n\n=== 高级条件断点示例 ===\n")
    
    config = ReactAgentConfig(
        work_dir="output/debug_advanced",
        memory_level=MemoryLevel.SMART,
        llm_model="deepseek-chat"
    )
    agent = GenericReactAgent(config, name="advanced_demo")
    debugger = ReactAgentDebugger(agent)
    
    print("2. 复杂条件断点\n")
    
    # 示例 4: 基于执行历史的条件
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_after_5_steps",
            condition=lambda ctx: len(debugger.execution_history) >= 5,
            condition_str="执行超过 5 步"
        )
    )
    
    # 示例 5: 基于工具调用参数的条件
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_large_file",
            condition=lambda ctx: any(
                tc.get("name") == "write_file" and 
                len(str(tc.get("args", {}).get("content", ""))) > 100
                for tc in ctx.get("tool_calls", [])
            ),
            condition_str="写入大文件（内容超过 100 字符）"
        )
    )
    
    # 示例 6: 基于多个工具调用的条件
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_multiple_tools",
            condition=lambda ctx: len(ctx.get("tool_calls", [])) > 1,
            condition_str="同时调用多个工具"
        )
    )
    
    # 示例 7: 基于调用深度的条件（适用于子 Agent）
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_deep_call",
            condition=lambda ctx: ctx.get("depth", 0) > 0,
            condition_str="在子 Agent 调用内部"
        )
    )
    
    print("执行复杂任务...")
    debugger.execute_task("""
    创建一个包含多个文件的项目：
    1. 创建 main.py，包含一个长函数（超过 100 字符）
    2. 创建 config.json 配置文件
    3. 创建 README.md 说明文档
    4. 同时检查所有文件是否创建成功
    """)


def demo_stateful_conditional_breakpoints():
    """有状态的条件断点示例"""
    print("\n\n=== 有状态的条件断点示例 ===\n")
    
    config = ReactAgentConfig(
        work_dir="output/debug_stateful",
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat"
    )
    agent = GenericReactAgent(config, name="stateful_demo")
    debugger = ReactAgentDebugger(agent)
    
    print("3. 有状态的条件断点\n")
    
    # 创建一个计数器来跟踪特定事件
    call_counter = {"write_file": 0, "read_file": 0}
    
    def count_and_check(ctx):
        """统计工具调用并在第二次写文件时触发"""
        for tc in ctx.get("tool_calls", []):
            tool_name = tc.get("name", "")
            if tool_name in call_counter:
                call_counter[tool_name] += 1
        
        # 第二次写文件时触发
        return call_counter["write_file"] == 2
    
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_second_write",
            condition=count_and_check,
            condition_str="第二次写入文件"
        )
    )
    
    # 创建一个跟踪特定文件的断点
    target_files = set()
    
    def track_python_files(ctx):
        """跟踪 Python 文件的创建"""
        for tc in ctx.get("tool_calls", []):
            if tc.get("name") == "write_file":
                file_path = tc.get("args", {}).get("file_path", "")
                if file_path.endswith(".py"):
                    target_files.add(file_path)
        
        # 当创建了 3 个 Python 文件时触发
        return len(target_files) >= 3
    
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_three_python_files",
            condition=track_python_files,
            condition_str="创建了 3 个 Python 文件"
        )
    )
    
    print("执行任务...")
    debugger.execute_task("""
    创建一个 Python 包：
    1. 创建 __init__.py
    2. 创建 main.py
    3. 创建 utils.py
    4. 创建 test_main.py
    5. 创建 README.md
    """)
    
    print(f"\n统计结果：")
    print(f"  写文件次数: {call_counter['write_file']}")
    print(f"  Python 文件: {target_files}")


def demo_context_aware_breakpoints():
    """上下文感知断点示例"""
    print("\n\n=== 上下文感知断点示例 ===\n")
    
    config = ReactAgentConfig(
        work_dir="output/debug_context",
        memory_level=MemoryLevel.SMART,
        llm_model="deepseek-chat"
    )
    agent = GenericReactAgent(config, name="context_demo")
    debugger = ReactAgentDebugger(agent)
    
    print("4. 上下文感知断点\n")
    
    # 示例 8: 基于消息历史的条件
    def check_conversation_pattern(ctx):
        """检查对话模式：用户提问 -> AI 思考 -> 工具调用"""
        messages = ctx.get("messages", [])
        if len(messages) < 3:
            return False
        
        # 检查最近的消息模式
        recent = messages[-3:]
        pattern_match = (
            any("?" in str(m) for m in recent) and  # 有问题
            ctx.get("step_type") == StepType.ACT     # 正在调用工具
        )
        return pattern_match
    
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_qa_pattern",
            condition=check_conversation_pattern,
            condition_str="问答模式后的工具调用"
        )
    )
    
    # 示例 9: 基于执行结果的条件
    def check_tool_failure(ctx):
        """检查工具执行是否失败"""
        if ctx.get("step_type") != StepType.OBSERVE:
            return False
        
        last_msg = ctx.get("last_message", None)
        if last_msg and hasattr(last_msg, "content"):
            content = str(last_msg.content).lower()
            failure_keywords = ["error", "failed", "not found", "exception"]
            return any(keyword in content for keyword in failure_keywords)
        return False
    
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_tool_failure",
            condition=check_tool_failure,
            condition_str="工具执行失败"
        )
    )
    
    # 示例 10: 组合条件
    def complex_condition(ctx):
        """组合多个条件：在 THINK 步骤且消息超过 50 字符"""
        return (
            ctx.get("step_type") == StepType.THINK and
            len(str(ctx.get("last_message", ""))) > 50 and
            len(ctx.get("messages", [])) > 5
        )
    
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            id="bp_complex",
            condition=complex_condition,
            condition_str="复杂条件：THINK + 长消息 + 对话超过5轮"
        )
    )
    
    print("执行任务...")
    debugger.execute_task("""
    1. 当前目录下有哪些文件？
    2. 尝试读取 config.json（可能不存在）
    3. 如果文件不存在，创建一个默认配置
    4. 再次确认文件是否创建成功
    """)


def print_conditional_breakpoint_guide():
    """打印条件断点设置指南"""
    print("\n" + "="*80)
    print("📋 条件断点设置指南")
    print("="*80)
    
    print("""
## 基本语法

```python
debugger.add_breakpoint(
    ConditionalBreakpoint(
        id="唯一标识符",
        condition=lambda ctx: 布尔表达式,
        condition_str="条件描述（用于显示）"
    )
)
```

## 上下文参数 (ctx)

ctx 字典包含以下键：
- step_type: 当前步骤类型 (StepType.THINK/ACT/OBSERVE)
- messages: 完整消息历史列表
- last_message: 最新的消息对象
- tool_calls: 工具调用列表（仅在 ACT 步骤）
- depth: 当前调用深度

## 常用条件示例

### 1. 基于消息内容
```python
# 包含特定关键词
lambda ctx: "error" in str(ctx.get("last_message", "")).lower()

# 消息长度
lambda ctx: len(str(ctx.get("last_message", ""))) > 100

# 特定文件类型
lambda ctx: ".py" in str(ctx.get("last_message", ""))
```

### 2. 基于步骤类型
```python
# 只在 THINK 步骤
lambda ctx: ctx.get("step_type") == StepType.THINK

# AI 调用工具时
lambda ctx: ctx.get("step_type") == StepType.ACT and len(ctx.get("tool_calls", [])) > 0
```

### 3. 基于工具调用
```python
# 特定工具
lambda ctx: any(tc.get("name") == "write_file" for tc in ctx.get("tool_calls", []))

# 工具参数
lambda ctx: any(
    tc.get("name") == "write_file" and 
    "test" in tc.get("args", {}).get("file_path", "")
    for tc in ctx.get("tool_calls", [])
)

# 多个工具
lambda ctx: len(ctx.get("tool_calls", [])) > 1
```

### 4. 基于执行历史
```python
# 执行步数（需要访问 debugger）
lambda ctx: len(debugger.execution_history) > 10

# 消息数量
lambda ctx: len(ctx.get("messages", [])) > 5
```

### 5. 复杂条件组合
```python
# AND 条件
lambda ctx: (
    ctx.get("step_type") == StepType.ACT and
    "python" in str(ctx.get("last_message", "")).lower() and
    len(ctx.get("tool_calls", [])) > 0
)

# OR 条件
lambda ctx: (
    "error" in str(ctx.get("last_message", "")).lower() or
    "failed" in str(ctx.get("last_message", "")).lower()
)
```

## 有状态的条件

使用闭包或外部变量跟踪状态：

```python
# 计数器
counter = {"calls": 0}
def count_calls(ctx):
    if ctx.get("step_type") == StepType.ACT:
        counter["calls"] += 1
    return counter["calls"] >= 3

# 状态机
state = {"phase": "init"}
def check_phase(ctx):
    # 根据条件更新状态
    if "setup" in str(ctx.get("last_message", "")):
        state["phase"] = "setup"
    return state["phase"] == "setup" and ctx.get("step_type") == StepType.ACT
```

## 最佳实践

1. **保持条件简单**：复杂条件难以调试
2. **使用描述性 ID**：方便管理断点
3. **提供清晰的描述**：condition_str 应准确描述触发条件
4. **避免副作用**：条件函数应该是纯函数（除非需要状态）
5. **处理异常**：使用 get() 方法避免 KeyError
6. **性能考虑**：条件会频繁执行，避免耗时操作

## 调试条件断点

如果条件断点不工作：
1. 打印 ctx 内容查看可用数据
2. 使用 try-except 捕获异常
3. 添加日志输出调试条件逻辑
4. 简化条件逐步测试
""")
    
    print("="*80)


if __name__ == "__main__":
    # 创建输出目录
    for dir_name in ["debug_conditional", "debug_advanced", "debug_stateful", "debug_context"]:
        Path(f"output/{dir_name}").mkdir(parents=True, exist_ok=True)
    
    print("🎯 条件断点设置示例")
    print("="*80)
    print("这个演示展示了各种条件断点的设置方法")
    print("="*80)
    
    # 显示指南
    print_conditional_breakpoint_guide()
    
    input("\n按回车键开始演示...")
    
    # 运行各个示例
    print("\n" + "="*80)
    print("开始运行示例...")
    print("="*80)
    
    try:
        demo_basic_conditional_breakpoints()
    except KeyboardInterrupt:
        print("\n跳过基础示例")
    
    choice = input("\n继续高级示例？(y/n): ")
    if choice.lower() == 'y':
        try:
            demo_advanced_conditional_breakpoints()
        except KeyboardInterrupt:
            print("\n跳过高级示例")
    
    choice = input("\n继续有状态示例？(y/n): ")
    if choice.lower() == 'y':
        try:
            demo_stateful_conditional_breakpoints()
        except KeyboardInterrupt:
            print("\n跳过有状态示例")
    
    choice = input("\n继续上下文感知示例？(y/n): ")
    if choice.lower() == 'y':
        try:
            demo_context_aware_breakpoints()
        except KeyboardInterrupt:
            print("\n跳过上下文感知示例")
    
    print("\n✅ 所有示例完成！")