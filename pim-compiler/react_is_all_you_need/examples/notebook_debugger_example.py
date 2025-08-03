#!/usr/bin/env python3
"""Notebook 调试器使用示例

展示如何在普通 Python 脚本中使用 Notebook 调试器的分析功能。
虽然设计用于 Jupyter Notebook，但核心分析功能也可以在脚本中使用。
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from react_agent_debugger_notebook import NotebookReactAgentDebugger
from react_agent_debugger import StepType, ConditionalBreakpoint


def demo_analysis_feature():
    """演示分析功能的使用"""
    print("=== Notebook 调试器分析功能演示 ===\n")
    
    # 设置 Gemini API 密钥
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("请设置 GEMINI_API_KEY 环境变量")
        return
    
    # 创建 Agent
    config = ReactAgentConfig(
        work_dir="output/analysis_demo",
        memory_level=MemoryLevel.SMART,
        llm_model="deepseek-chat",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(config, name="analysis_demo")
    
    # 创建 Notebook 调试器
    debugger = NotebookReactAgentDebugger(agent, api_key)
    
    # 设置一个会触发分析的断点
    analysis_triggered = False
    
    def trigger_analysis(ctx):
        nonlocal analysis_triggered
        # 在第5步触发
        if len(debugger.execution_history) == 5 and not analysis_triggered:
            analysis_triggered = True
            return True
        return False
    
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            "analysis_trigger",
            trigger_analysis,
            "触发分析（第5步）"
        )
    )
    
    # 模拟一个有问题的任务
    print("执行任务：创建一个有潜在问题的场景...\n")
    
    # 重写调试命令处理，自动进行分析
    original_handle_debug = debugger._handle_debug_command
    
    def auto_analyze_handler():
        print("\n🔍 自动触发分析...")
        result = debugger.analysis()
        
        # 打印分析结果
        print("\n📊 分析结果：")
        print(f"发现 Bug: {result.get('has_bug', 'Unknown')}")
        if result.get('has_bug'):
            print(f"严重程度: {result.get('severity', 'N/A')}")
            print(f"Bug 类型: {result.get('bug_type', 'N/A')}")
            print(f"描述: {result.get('description', 'N/A')}")
            print(f"解决方案: {result.get('solution', 'N/A')}")
        
        if result.get('additional_observations'):
            print("\n其他观察：")
            for obs in result['additional_observations']:
                print(f"- {obs}")
        
        # 继续执行
        debugger.step_mode = debugger.step_mode.RUN
        return True
    
    debugger._handle_debug_command = auto_analyze_handler
    
    # 执行任务
    debugger.verbose = False  # 减少输出
    
    try:
        debugger.execute_task("""
        执行以下任务：
        1. 创建 data.txt 文件
        2. 再次创建 data.txt 文件（重复操作）
        3. 尝试读取 missing.txt 文件（不存在）
        4. 创建 config.json 文件
        5. 列出目录内容
        """)
    except Exception as e:
        print(f"\n执行出错: {e}")
    
    # 恢复原始处理器
    debugger._handle_debug_command = original_handle_debug
    
    # 显示所有分析历史
    print(f"\n\n📝 分析历史（共 {len(debugger.analysis_results)} 次）：")
    for i, result in enumerate(debugger.analysis_results):
        print(f"\n--- 分析 #{i+1} ---")
        print(f"时间: {result.get('timestamp', 'N/A')}")
        print(f"发现问题: {result.get('has_bug', False)}")
        if result.get('has_bug'):
            print(f"问题: {result.get('description', 'N/A')}")


def demo_manual_analysis():
    """演示手动分析功能"""
    print("\n\n=== 手动分析演示 ===\n")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return
    
    # 创建简单配置
    config = ReactAgentConfig(
        work_dir="output/manual_analysis",
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat"
    )
    
    agent = GenericReactAgent(config, name="manual_demo")
    debugger = NotebookReactAgentDebugger(agent, api_key)
    
    # 模拟一些执行状态
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    
    # 模拟状态
    debugger.current_state = {
        "step_type": StepType.OBSERVE,
        "messages": [
            HumanMessage(content="创建一个测试文件"),
            AIMessage(content="我将创建测试文件", tool_calls=[{"name": "write_file", "args": {"file_path": "test.txt", "content": "test"}}]),
            ToolMessage(content="Error: Permission denied", name="write_file"),
            AIMessage(content="遇到权限错误，我将重试"),
            AIMessage(content="再次尝试", tool_calls=[{"name": "write_file", "args": {"file_path": "test.txt", "content": "test"}}]),
            ToolMessage(content="Error: Permission denied", name="write_file")
        ],
        "last_message": ToolMessage(content="Error: Permission denied", name="write_file"),
        "tool_calls": []
    }
    
    # 添加一些执行历史
    from react_agent_debugger import ExecutionStep
    from datetime import datetime
    
    for i in range(6):
        step_type = [StepType.THINK, StepType.ACT, StepType.OBSERVE][i % 3]
        debugger.execution_history.append(
            ExecutionStep(
                step_type=step_type,
                timestamp=datetime.now(),
                data={"step": i},
                depth=0
            )
        )
    
    print("模拟状态：遇到重复的权限错误")
    print("\n执行分析...\n")
    
    # 执行分析
    result = debugger.analysis()
    
    print("\n✅ 分析完成")
    print(f"诊断: {'发现问题' if result.get('has_bug') else '正常'}")


def demo_pattern_detection():
    """演示模式检测能力"""
    print("\n\n=== 模式检测演示 ===\n")
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return
    
    config = ReactAgentConfig(
        work_dir="output/pattern_demo",
        memory_level=MemoryLevel.NONE,
        llm_model="deepseek-chat"
    )
    
    agent = GenericReactAgent(config, name="pattern_demo")
    debugger = NotebookReactAgentDebugger(agent, api_key)
    
    # 创建一个检测循环模式的断点
    loop_count = {}
    
    def detect_loop_pattern(ctx):
        """检测工具调用循环"""
        tool_calls = ctx.get("tool_calls", [])
        for tc in tool_calls:
            tool_name = tc.get("name", "")
            loop_count[tool_name] = loop_count.get(tool_name, 0) + 1
            
            # 如果某个工具被调用超过3次，触发分析
            if loop_count[tool_name] > 3:
                print(f"\n⚠️ 检测到潜在循环：工具 '{tool_name}' 已被调用 {loop_count[tool_name]} 次")
                return True
        return False
    
    debugger.add_breakpoint(
        ConditionalBreakpoint(
            "loop_detector",
            detect_loop_pattern,
            "循环模式检测"
        )
    )
    
    # 自动分析处理
    def analyze_on_loop():
        print("\n🔄 检测到循环模式，启动智能分析...")
        result = debugger.analysis()
        
        if result.get("solution"):
            print(f"\n💡 建议: {result['solution']}")
        
        # 询问是否继续
        choice = input("\n是否继续执行？(y/n): ")
        if choice.lower() != 'y':
            debugger.continue_execution = False
            return False
        
        debugger.step_mode = debugger.step_mode.RUN
        return True
    
    debugger._handle_debug_command = analyze_on_loop
    debugger.verbose = False
    
    print("执行任务：模拟可能产生循环的场景...\n")
    
    try:
        debugger.execute_task("""
        不断尝试创建 /root/test.txt 文件，直到成功：
        1. 尝试创建文件
        2. 如果失败，再次尝试
        3. 重复直到成功或尝试5次
        """)
    except KeyboardInterrupt:
        print("\n\n⛔ 执行被用户中断")


if __name__ == "__main__":
    print("🔍 Notebook 调试器分析功能演示")
    print("=" * 80)
    print("本演示展示如何使用 Gemini 2.0 Flash 进行智能 bug 分析")
    print("=" * 80)
    
    # 创建输出目录
    for dir_name in ["analysis_demo", "manual_analysis", "pattern_demo"]:
        Path(f"output/{dir_name}").mkdir(parents=True, exist_ok=True)
    
    # 运行演示
    try:
        # 1. 基础分析功能
        demo_analysis_feature()
        
        # 2. 手动分析
        demo_manual_analysis()
        
        # 3. 模式检测
        demo_pattern_detection()
        
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n\n✅ 所有演示完成！")
    print("\n提示：在 Jupyter Notebook 中使用时，可以获得更好的交互体验。")