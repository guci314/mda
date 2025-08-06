#!/usr/bin/env python3
"""演示：使用 langchain_agent_tool.py 实现 Agent 协作"""

import os
import sys
from pathlib import Path
import httpx

# 环境设置
sys.path.insert(0, str(Path(__file__).parent))

# Gemini API 配置
# 使用环境变量设置代理
os.environ["HTTP_PROXY"] = "http://localhost:7890"
os.environ["HTTPS_PROXY"] = "http://localhost:7890"
http_client = None  # Gemini 将使用环境变量中的代理

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from langchain_agent_tool import (
    AgentToolWrapper, 
    create_langchain_tool,
    GenericAgentTool
)
from langchain_core.tools import tool


def main():
    import time
    start_time = time.time()
    
    print("=== 使用 langchain_agent_tool.py 的 Agent 协作演示 ===\n")
    
    # 创建共享的工作目录
    work_dir = Path("output/shared_workspace_langchain")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 步骤1：创建专门的子 Agent
    print("1. 创建专门的子 Agent...")
    
    # 获取绝对路径
    abs_work_dir = work_dir.resolve()
    
    # 代码生成 Agent
    code_gen_config = ReactAgentConfig(
        work_dir=str(abs_work_dir),
        memory_level=MemoryLevel.NONE,
        knowledge_files=[
            "knowledge/best_practices/absolute_path_usage.md",
            "knowledge/output/role_based_output.md"        # 基于角色的输出指南
        ],
        llm_model="gemini-2.5-flash",
        llm_base_url="https://generativelanguage.googleapis.com/v1beta/",
        llm_api_key_env="GOOGLE_API_KEY",
        llm_temperature=0,
        interface=f"专门生成各种编程语言的高质量代码文件，支持 Python、JavaScript、Java 等。工作目录：{abs_work_dir}",
        enable_world_overview=False,  # 子 Agent 不需要生成 world_overview
        http_client=http_client
    )
    code_gen_agent = GenericReactAgent(code_gen_config, name="code_generator")
    
    # 为 code_runner 创建受限的工具集
    from tools import create_tools
    all_tools = create_tools(str(abs_work_dir))
    
    # 只保留读取和执行相关的工具，排除写入工具
    code_runner_tools = []
    allowed_tool_names = ['read_file', 'list_directory', 'execute_command', 'search_code', 'search_files']
    for tool in all_tools:
        if tool.name in allowed_tool_names:
            code_runner_tools.append(tool)
    
    # 代码运行 Agent
    code_run_config = ReactAgentConfig(
        work_dir=str(abs_work_dir),
        memory_level=MemoryLevel.NONE,
        knowledge_files=[
            "knowledge/best_practices/absolute_path_usage.md",
            "knowledge/output/role_based_output.md",       # 基于角色的输出指南
            "knowledge/best_practices/test_execution_best_practices.md"  # 测试执行最佳实践
        ],
        knowledge_strings=[
            """# 重要规则：不要修改代码

作为 code_runner，你的职责是：
1. **只运行代码，不修改代码，也不生成代码**
2. **如实报告执行结果**，无论成功还是失败
3. **不要尝试修复错误**，只需要清楚地描述错误信息
4. **不要生成修复建议**，让其他 Agent 处理修复

记住：你是一个测试运行器，不是代码修复器。你的价值在于提供准确的执行反馈。
"""
        ],
        llm_model="gemini-2.5-flash",
        llm_base_url="https://generativelanguage.googleapis.com/v1beta/",
        llm_api_key_env="GOOGLE_API_KEY",
        llm_temperature=0,
        interface=f"专门运行和测试代码，提供执行结果和错误分析。不要修改代码，也不要生成代码。工作目录：{abs_work_dir}",
        enable_world_overview=False,  # 子 Agent 不需要生成 world_overview
        http_client=http_client
    )
    code_run_agent = GenericReactAgent(code_run_config, name="code_runner", custom_tools=code_runner_tools)
    
    # 代码审查 Agent
    code_review_config = ReactAgentConfig(
        work_dir=str(abs_work_dir),
        memory_level=MemoryLevel.NONE,
        knowledge_files=[
            "knowledge/best_practices/absolute_path_usage.md",
            "knowledge/best_practices/code_review_ethics.md",     # 代码审查职业道德
            "knowledge/output/role_based_output.md"        # 基于角色的输出指南
        ],
        llm_model="gemini-2.5-flash",
        llm_base_url="https://generativelanguage.googleapis.com/v1beta/",
        llm_api_key_env="GOOGLE_API_KEY",
        llm_temperature=0,
        interface=f"专门审查代码质量，提供改进建议和最佳实践指导。工作目录：{abs_work_dir}",
        enable_world_overview=False,  # 子 Agent 不需要生成 world_overview
        http_client=http_client
    )
    code_review_agent = GenericReactAgent(code_review_config, name="code_reviewer")
    
    # 步骤2：使用 langchain_agent_tool.py 创建工具
    print("2. 使用 langchain_agent_tool.py 创建工具...")
    
    # 方式1：使用 AgentToolWrapper
    code_gen_wrapper = AgentToolWrapper(code_gen_agent)
    code_run_wrapper = AgentToolWrapper(code_run_agent)
    code_review_wrapper = AgentToolWrapper(code_review_agent)
    
    # 方式2：使用 create_langchain_tool 创建 LangChain 兼容工具
    code_gen_tool = create_langchain_tool(code_gen_agent)
    code_gen_tool.name = "code_generator"
    code_gen_tool.description = code_gen_agent.interface
    
    # 方式3：使用 GenericAgentTool 类
    code_run_tool = GenericAgentTool(code_run_agent)
    code_review_tool = GenericAgentTool(code_review_agent)
    
    # 额外的辅助工具（注释掉有问题的工具）
    # @tool
    # def list_workspace_files() -> str:
    #     """列出工作目录中的所有文件"""
    #     files = []
    #     for file in work_dir.iterdir():
    #         if file.is_file():
    #             files.append(file.name)
    #     return f"工作目录中的文件: {', '.join(files) if files else '无文件'}"
    
    # 步骤3：创建主协调 Agent（也使用 GenericReactAgent）
    print("3. 创建主协调 Agent（使用 GenericReactAgent）...")
    
    # 从tools模块创建基本工具
    from tools import create_tools
    
    # 创建基本工具（使用主agent的工作目录）
    basic_tools = create_tools(str(work_dir))
    
    # 从中提取需要的文件操作工具
    write_file = None
    read_file = None
    list_directory = None
    
    for t in basic_tools:
        if t.name == "write_file":
            write_file = t
        elif t.name == "read_file":
            read_file = t
        elif t.name == "list_directory":
            list_directory = t
    
    # 准备所有工具
    tools = [
        # 基本文件操作工具（用于BPMN文件管理）
        write_file,
        read_file,
        list_directory,
        # 子Agent工具
        code_gen_tool,
        code_run_tool,
        code_review_tool
        # list_workspace_files  # 暂时移除有问题的工具
    ]
    
    # 创建主协调 Agent 配置
    main_config = ReactAgentConfig(
        work_dir=str(abs_work_dir),
        memory_level=MemoryLevel.SMART,  # 使用智能记忆以便更好地协调
        knowledge_files=[
            "knowledge/best_practices/absolute_path_usage.md",     # 绝对路径使用规范
            "knowledge/output/role_based_output.md",       # 基于角色的输出指南
            # "knowledge/workflow/bpmn_obsession.md",          # BPMN 强迫症（已移除）
            # "knowledge/intent_declaration_workflow.md",  # 意图声明工作流（React自带，已移除）
            "knowledge/coordination/delegation_best_practices.md",
            "knowledge/workflow/task_dependencies.md", 
            "knowledge/coordination/context_passing.md",
            "knowledge/coordination/result_extraction.md"
        ],
        llm_model="gemini-2.5-flash",
        llm_base_url="https://generativelanguage.googleapis.com/v1beta/",
        llm_api_key_env="GOOGLE_API_KEY",
        llm_temperature=0,
        interface=f"协调多个专家 Agent 完成复杂的软件开发任务。工作目录：{abs_work_dir}",
        http_client=http_client
    )
    
    # 创建主 Agent，传入自定义工具
    main_agent = GenericReactAgent(main_config, name="project_manager", custom_tools=tools)
    
    # 步骤4：执行复杂任务
    print("4. 执行协作任务\n")
    
    task = f"""# MathUtils 开发意图

**目标**：获得一个高质量的、经过充分测试的 MathUtils 类

**具体要求**：
- 在 {abs_work_dir}/math_utils.py 创建 MathUtils 类
- 包含方法：add, subtract, multiply, divide, power
- 所有方法都要有适当的类型检查和错误处理

**约束条件**：
- 代码必须通过所有测试
- 如果测试失败，允许最多 3 次修复机会
- 每次失败时，要将具体错误信息反馈给代码生成器
- 最终代码需要通过质量审查

**期望结果**：
- 一个功能完整、质量优秀的 math_utils.py 文件
- 所有测试通过的证明
- 代码质量评分（1-10分）和改进建议

**授权决策**：
- 你可以自主决定如何协调各个专家 Agent
- 你可以根据情况调整执行顺序
- 你可以在必要时要求更详细的错误信息
- 如果超过 3 次仍失败，请总结失败原因

**注意事项**：
- code_runner 只能运行代码，不能创建文件
- 如果需要测试文件，应该让 code_generator 创建

请根据这些意图，灵活协调代码生成器、测试运行器和代码审查员完成任务。记住，这是一个经验主义的过程——通过行动和观察来获得最佳结果。
"""
    
    print("主协调 Agent 开始工作...\n")
    
    try:
        # 使用 GenericReactAgent 执行任务
        main_agent.execute_task(task)
        
        print("\n=== 任务完成 ===")
        
    except Exception as e:
        print(f"执行出错: {e}")
    
    # 显示工作目录中的文件
    print(f"\n=== 工作目录 {work_dir} 中的文件 ===")
    files_in_dir = list(work_dir.iterdir())
    # 只显示实际存在的文件
    actual_files = [f for f in files_in_dir if f.is_file()]
    
    for file in actual_files:
        print(f"- {file.name}")
        # 如果是 Python 文件，显示内容预览
        if file.suffix == '.py':
            print(f"  内容预览:")
            content = file.read_text()
            preview = content[:200] + "..." if len(content) > 200 else content
            print(f"  {preview}")
    
    print("\n=== 演示完成 ===")
    print("这个演示展示了：")
    print("- 使用 langchain_agent_tool.py 的三种方式创建工具")
    print("- 多个专家 Agent 协作完成复杂任务")
    print("- GenericReactAgent 作为主协调者（使用自定义工具）")
    print("- 完整的开发工作流：生成、运行、审查、优化")
    
    # 打印执行时间
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"\n执行时间：{execution_time:.2f} 秒")


if __name__ == "__main__":
    main()