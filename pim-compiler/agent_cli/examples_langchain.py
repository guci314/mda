"""
使用 LangChain Tools 的示例
演示如何在 agent_cli 中使用 LangChain 工具
"""
import os
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_cli.core import AgentCLI, LLMConfig
from agent_cli.tools import ToolRegistry, create_validation_tool
from agent_cli.executors import LangChainToolExecutor
from langchain.tools import StructuredTool


def demo_basic_tools():
    """演示基本工具的使用"""
    print("=== 基本工具演示 ===\n")
    
    # 创建 agent 实例（使用 LangChain tools）
    agent = AgentCLI(use_langchain_tools=True)
    
    # 执行一个简单任务
    success, result = agent.execute_task("读取 README.md 文件并分析其内容结构")
    
    print(f"任务完成: {success}")
    print(f"结果: {result}")
    
    # 获取执行摘要
    summary = agent.get_execution_summary()
    print(f"\n执行摘要:")
    print(f"- 总动作数: {summary['total_actions']}")
    print(f"- 成功动作: {summary['successful_actions']}")
    print(f"- 失败动作: {summary['failed_actions']}")


def demo_custom_tools():
    """演示自定义工具的使用"""
    print("\n=== 自定义工具演示 ===\n")
    
    # 创建自定义工具
    def count_words(text: str) -> str:
        """统计文本中的单词数量"""
        words = text.split()
        return f"文本包含 {len(words)} 个单词"
    
    word_count_tool = StructuredTool.from_function(
        func=count_words,
        name="word_counter",
        description="统计文本中的单词数量"
    )
    
    # 创建 agent 并注册自定义工具
    agent = AgentCLI(use_langchain_tools=True)
    
    # 注册自定义工具
    if agent.tool_executor:
        agent.tool_executor.tool_registry.register(word_count_tool)
        print("已注册自定义工具: word_counter")
        
        # 显示所有可用工具
        tools = agent.tool_executor.get_available_tools()
        print("\n可用工具:")
        for tool in tools:
            print(f"- {tool['name']}: {tool['description']}")


def demo_tool_comparison():
    """对比 LangChain 和传统工具执行"""
    print("\n=== 工具执行对比 ===\n")
    
    # 使用 LangChain tools
    print("1. 使用 LangChain Tools:")
    agent_langchain = AgentCLI(use_langchain_tools=True)
    success1, _ = agent_langchain.execute_task("创建一个 test_langchain.txt 文件，内容为 'Hello from LangChain!'")
    print(f"   完成: {success1}")
    
    # 使用传统 tools
    print("\n2. 使用传统 Tools:")
    agent_legacy = AgentCLI(use_langchain_tools=False)
    success2, _ = agent_legacy.execute_task("创建一个 test_legacy.txt 文件，内容为 'Hello from Legacy!'")
    print(f"   完成: {success2}")
    
    # 清理测试文件
    for file in ["test_langchain.txt", "test_legacy.txt"]:
        if Path(file).exists():
            Path(file).unlink()


def demo_validation_tool():
    """演示验证工具的使用"""
    print("\n=== 验证工具演示 ===\n")
    
    # 创建验证工具
    validation_tool = create_validation_tool()
    
    # 创建 agent 并注册验证工具
    agent = AgentCLI(use_langchain_tools=True)
    if agent.tool_executor:
        agent.tool_executor.tool_registry.register(validation_tool)
    
    # 执行代码生成和验证任务
    task = """
    生成一个 Python 函数来计算斐波那契数列，然后验证生成的代码是否有语法错误。
    函数应该接受一个参数 n，返回第 n 个斐波那契数。
    """
    
    success, result = agent.execute_task(task)
    print(f"任务完成: {success}")
    
    # 显示执行的动作
    if agent.current_task:
        print("\n执行的步骤:")
        for i, step in enumerate(agent.current_task.steps):
            print(f"{i+1}. {step.name} - {step.status.value}")
            for action in step.actions:
                print(f"   - {action.type.value}: {action.description}")


def demo_tool_registry():
    """演示工具注册表的使用"""
    print("\n=== 工具注册表演示 ===\n")
    
    # 创建独立的工具注册表
    registry = ToolRegistry()
    
    # 显示默认工具
    print("默认工具:")
    for name, tool in registry.tools.items():
        print(f"- {name}: {tool.description}")
    
    # 添加自定义工具
    def uppercase_text(text: str) -> str:
        """将文本转换为大写"""
        return text.upper()
    
    uppercase_tool = StructuredTool.from_function(
        func=uppercase_text,
        name="uppercase",
        description="将文本转换为大写"
    )
    
    registry.register(uppercase_tool)
    print(f"\n注册新工具: uppercase")
    
    # 执行工具
    result = registry.execute_tool("uppercase", text="hello world")
    print(f"执行结果: {result}")


if __name__ == "__main__":
    print("Agent CLI LangChain Tools 示例\n")
    
    # 确保有 LLM 配置
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY"):
        print("警告: 未找到 LLM API key，某些功能可能无法正常工作")
        print("请设置 OPENAI_API_KEY 或 DEEPSEEK_API_KEY 环境变量")
        print()
    
    # 运行演示
    try:
        demo_basic_tools()
        demo_custom_tools()
        demo_tool_comparison()
        demo_validation_tool()
        demo_tool_registry()
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()