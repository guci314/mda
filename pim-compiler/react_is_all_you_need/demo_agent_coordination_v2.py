#!/usr/bin/env python3
"""演示：使用 GenericReactAgent 作为主 Agent 协调其他 Agent"""

import os
import sys
from pathlib import Path

# 环境设置
sys.path.insert(0, str(Path(__file__).parent))
os.environ.pop('http_proxy', None)
os.environ.pop('https_proxy', None)
os.environ.pop('all_proxy', None)

from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from langchain_core.tools import tool


def main():
    print("=== 使用 GenericReactAgent 作为主 Agent ===\n")
    
    # 创建共享的工作目录
    work_dir = Path("output/shared_workspace_v2")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 步骤1：创建两个子 Agent 作为工具
    print("1. 创建子 Agent 工具...")
    
    # 代码生成 Agent
    code_gen_config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        llm_model="kimi-k2-0711-preview",
        llm_base_url="https://api.moonshot.cn/v1",
        llm_api_key_env="MOONSHOT_API_KEY",
        llm_temperature=0,
        interface="专门生成代码的Agent"
    )
    code_gen_agent = GenericReactAgent(code_gen_config, name="代码生成Agent")
    
    @tool
    def code_generator(task: str) -> str:
        """代码生成 Agent - 专门生成代码文件"""
        print(f"   [代码生成 Agent] 收到任务: {task}")
        code_gen_agent.execute_task(task)
        return f"代码已生成在 {work_dir} 目录中"
    
    # 代码运行 Agent
    code_run_config = ReactAgentConfig(
        work_dir=str(work_dir),
        memory_level=MemoryLevel.NONE,
        llm_model="kimi-k2-0711-preview",
        llm_base_url="https://api.moonshot.cn/v1",
        llm_api_key_env="MOONSHOT_API_KEY",
        llm_temperature=0,
        interface="专门运行代码的Agent"
    )
    code_run_agent = GenericReactAgent(code_run_config, name="代码运行Agent")
    
    @tool
    def code_runner(file_name: str) -> str:
        """代码运行 Agent - 运行指定的代码文件"""
        print(f"   [代码运行 Agent] 收到任务: 运行 {file_name}")
        file_path = work_dir / file_name
        if not file_path.exists():
            return f"错误：文件 {file_name} 不存在于工作目录 {work_dir}"
        
        task = f"运行Python文件 {file_path} 并返回输出结果"
        code_run_agent.execute_task(task)
        return f"已执行 {file_name}"
    
    # 步骤2：创建主 Agent - 使用 GenericReactAgent
    print("2. 创建主 Agent（使用 GenericReactAgent）...")
    
    # 主 Agent 配置
    main_config = ReactAgentConfig(
        work_dir="output/main_v2",
        memory_level=MemoryLevel.NONE,
        llm_model="kimi-k2-0711-preview",
        llm_base_url="https://api.moonshot.cn/v1",
        llm_api_key_env="MOONSHOT_API_KEY",
        llm_temperature=0,
#         interface=f"""项目协调管理者

# 你有两个专门的 Agent 工具可以调用：
# 1. code_generator: 代码生成 Agent，可以生成各种代码文件
# 2. code_runner: 代码运行 Agent，可以运行代码文件并返回结果

# 重要：
# - 所有文件都会生成在共享工作目录 {work_dir} 中
# - 调用 code_runner 时，只需要提供文件名（如 hello_world.py），不需要完整路径

# 请根据任务需求，合理调度这两个 Agent 完成工作。"""
    )
    
    # 创建主 Agent，使用自定义工具
    custom_tools = [code_generator, code_runner]
    main_agent = GenericReactAgent(main_config, name="主协调Agent", custom_tools=custom_tools)
    
    # 步骤3：执行任务
    print("3. 执行协调任务\n")
    
#     task = """请完成以下任务：
# 1. 使用 code_generator 生成一个 hello_world.py 程序，要求打印 "Hello World from GenericReactAgent!"
# 2. 使用 code_runner 运行 hello_world.py，并告诉我输出结果
# """
    task = """请完成以下任务：
1. 生成一个 hello_world.py 程序，要求打印 "Hello World from GenericReactAgent!"
2. 运行 hello_world.py，并告诉我输出结果
"""
    
    print("主 Agent 开始协调工作...\n")
    
    # 使用 GenericReactAgent 的 execute_task 方法
    main_agent.execute_task(task)
    
    # 显示工作目录中的文件
    print(f"\n=== 工作目录 {work_dir} 中的文件 ===")
    for file in work_dir.iterdir():
        if file.is_file():
            print(f"- {file.name}")
    
    print("\n=== 演示完成 ===")
    print("这个版本展示了：")
    print("- 使用 GenericReactAgent 作为主 Agent")
    print("- 主 Agent 使用自定义工具（两个子 Agent）")
    print("- 完全基于 GenericReactAgent 的架构")


if __name__ == "__main__":
    main()