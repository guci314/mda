#!/usr/bin/env python3
"""MDA双Agent架构演示 - 使用Agent as Tool模式"""

import os
import sys
from pathlib import Path
import time
import json

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

# 禁用缓存以提高性能
os.environ['DISABLE_LANGCHAIN_CACHE'] = 'true'

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from core.langchain_agent_tool import AgentToolWrapper, create_langchain_tool
from core.debug_tools import (
    check_and_compress_debug_notes, 
    create_debug_tools
)
from langchain_core.tools import tool

# 如果使用 Gemini 需要导入 httpx
try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


def create_generation_agent(work_dir: str, llm_config: dict) -> GenericReactAgent:
    """创建专注于代码生成的Agent"""
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=["knowledge/mda/generation_knowledge.md"],  # 使用生成专用知识
        enable_project_exploration=False,
        **llm_config
    )
    
    agent = GenericReactAgent(config, name="generation_agent")
    agent.interface = """代码生成专家 - 专注于快速生成高质量代码
    
能力：
- PIM到PSM转换
- FastAPI应用生成
- 快速交付，不做调试

原则：
- 生成即返回，不运行测试
- 遇到问题记录但不修复
- 让调试Agent处理所有错误
"""
    return agent


def create_debug_agent(work_dir: str, llm_config: dict) -> GenericReactAgent:
    """创建专门的调试Agent"""
    
    # 检查并压缩调试笔记
    check_and_compress_debug_notes(work_dir)
    
    # 获取调试专用工具
    debug_tools = create_debug_tools(work_dir)
    
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[
            "knowledge/mda/debugging_knowledge.md",      # 调试专用知识
            "knowledge/mda/syntax_fix_strategies.md",    # 语法修复策略
            "knowledge/mda/debugging_workflow.md"        # 调试工作流程
        ],
        enable_project_exploration=False,
        **llm_config
    )
    
    agent = GenericReactAgent(config, name="debug_agent", custom_tools=debug_tools)
    agent.interface = """调试专家 - 系统性修复代码错误
    
能力：
- 维护调试笔记避免重复修复
- 智能语法错误修复（整文件重写）
- 系统性错误诊断和修复
- 确保100%测试通过
"""
    
    # 简化系统提示，主要依赖知识文件
    agent._system_prompt = (agent._system_prompt or "") + """

## 调试任务执行

你是一个专业的调试Agent。你的知识文件已经包含了：
- 完整的调试工作流程 (debugging_workflow.md)
- 详细的错误处理策略 (debugging_knowledge.md)  
- Python语法修复指南 (syntax_fix_strategies.md)

请严格按照知识文件中的工作流程执行调试任务。

记住：你必须完成完整的调试流程，使用正确的工具（特别是 fix_python_syntax_errors），持续修复直到所有测试通过或达到退出条件。
"""
    return agent


def create_coordinator_agent(work_dir: str, llm_config: dict, 
                           generation_tool, debug_tool) -> GenericReactAgent:
    """创建协调两个子Agent的主Agent"""
    
    # 主Agent配置 - 使用协调知识
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=["knowledge/mda/coordinator_workflow.md"],  # 使用协调工作流知识
        enable_project_exploration=False,
        **llm_config
    )
    
    # 创建主Agent，已经包含了默认工具（write_file, execute_command等）
    # 只需要添加两个子Agent工具
    agent = GenericReactAgent(
        config, 
        name="coordinator_agent",
        custom_tools=[generation_tool, debug_tool]  # 只添加子Agent工具
    )
    
    agent.interface = """MDA Pipeline协调者
    
我协调两个专门的Agent：
1. 生成Agent - 负责代码生成
2. 调试Agent - 负责错误修复

工作流程：
1. 调用生成Agent创建代码
2. 运行测试验证
3. 如有失败，调用调试Agent修复
4. 循环直到100%通过
"""
    
    # 简化系统提示，依赖知识文件
    agent._system_prompt = (agent._system_prompt or "") + """

## 协调任务执行

你是MDA Pipeline的协调者。你的知识文件 coordinator_workflow.md 包含了：
- 完整的执行流程
- TODO管理规范
- 调试Agent循环管理
- 成功标准定义

请严格按照知识文件中的工作流程执行协调任务。
"""
    
    return agent


def main():
    """运行双Agent架构的MDA Pipeline"""
    
    print("=" * 80)
    print("MDA双Agent架构演示")
    print("=" * 80)
    
    # 设置工作目录
    work_dir = Path("output/mda_dual_agent_demo")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # PSM文件路径 (使用已有的PSM)
    psm_file = Path(__file__).parent / "output/mda_demo/library_borrowing_system_psm.md"
    
    # 选择LLM配置
    print("\n选择LLM配置：")
    print("1. DeepSeek (默认)")
    print("2. Kimi k2-turbo (128K上下文)")
    print("3. Gemini 2.5 Pro (via OpenRouter)")
    print("4. Claude Sonnet 4 (via OpenRouter)")
    
    choice = input("请选择 (1-4，默认1): ").strip() or "1"
    
    if choice == "2":
        # Kimi配置
        llm_config = {
            "llm_model": "kimi-k2-turbo-preview",
            "llm_base_url": "https://api.moonshot.cn/v1",
            "llm_api_key_env": "MOONSHOT_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "Kimi k2-turbo (128K上下文)"
    elif choice == "3":
        # Gemini配置 (通过OpenRouter)
        llm_config = {
            "llm_model": "google/gemini-2.5-pro",
            "llm_base_url": "https://openrouter.ai/api/v1",
            "llm_api_key_env": "OPENROUTER_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "Gemini 2.5 Pro (via OpenRouter)"
    elif choice == "4":
        # Claude配置
        llm_config = {
            "llm_model": "anthropic/claude-sonnet-4",
            "llm_base_url": "https://openrouter.ai/api/v1",
            "llm_api_key_env": "OPENROUTER_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "Claude Sonnet 4"
    else:
        # DeepSeek配置（默认）
        llm_config = {
            "llm_model": "deepseek-chat",
            "llm_base_url": "https://api.deepseek.com/v1",
            "llm_api_key_env": "DEEPSEEK_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "DeepSeek"
    
    print(f"\n使用 {llm_name} 作为LLM后端")
    
    # 创建子Agent
    print("\n创建专门的子Agent...")
    generation_agent = create_generation_agent(str(work_dir), llm_config)
    debug_agent = create_debug_agent(str(work_dir), llm_config)
    
    # 将子Agent包装为工具
    print("将子Agent包装为LangChain工具...")
    
    # 设置Agent的名称，这将被create_langchain_tool使用
    generation_agent.name = "code_generator"
    generation_agent.interface = """生成代码的专门Agent，用于PSM生成和FastAPI代码生成
    
输入：生成任务描述
输出：生成的代码文件"""
    
    debug_agent.name = "code_debugger" 
    debug_agent.interface = """调试代码的专门Agent，用于修复测试失败和错误
    
输入：调试任务描述
输出：修复后的代码和调试报告"""
    
    generation_tool = create_langchain_tool(generation_agent)
    debug_tool = create_langchain_tool(debug_agent)
    
    # 创建协调Agent
    print("创建协调Agent...")
    coordinator = create_coordinator_agent(
        str(work_dir), 
        llm_config,
        generation_tool,
        debug_tool
    )
    
    # 执行任务 - 使用意图声明风格
    print("\n" + "=" * 60)
    print("开始执行MDA Pipeline...")
    print("=" * 60)
    
    start_time = time.time()
    
    # 简化的任务描述 - 详细流程在知识文件中
    task = f"""
## 目标
从PSM文件生成一个完全可工作的FastAPI应用，确保所有测试100%通过。

## 输入
- PSM文件：{psm_file}
- 输出目录：{work_dir}

## 执行要求
请按照你的知识文件 coordinator_workflow.md 中定义的标准流程执行：

1. 初始化TODO笔记 (coordinator_todo.json)
2. 调用 code_generator 生成FastAPI应用
3. 运行 pytest 测试验证
4. 如有失败，调用 code_debugger 修复（记住要循环调用直到完成）
5. 确认100%测试通过

## 工具提醒
- code_generator: 生成代码的子Agent
- code_debugger: 修复错误的子Agent（支持 fix_python_syntax_errors 工具）
- execute_command: 运行测试命令
- write_file: 管理TODO笔记

## 成功标准
- 所有TODO任务完成
- pytest tests/ -xvs 显示 0 failed
- coordinator_todo.json 记录完整执行过程

开始执行任务，严格遵循知识文件中的工作流程。
"""
    
    try:
        # 执行完整任务
        result = coordinator.execute_task(task)
        
        elapsed_time = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("执行完成！")
        print("=" * 60)
        print(f"总耗时：{elapsed_time:.1f} 秒")
        
        # 检查协调Agent的TODO笔记
        todo_file = work_dir / "coordinator_todo.json"
        if todo_file.exists():
            with open(todo_file, 'r') as f:
                todo_data = json.load(f)
            
            print("\n📋 任务完成情况（coordinator_todo.json）：")
            for task in todo_data.get('tasks', []):
                status_emoji = {
                    'completed': '✅',
                    'in_progress': '🔄',
                    'pending': '⏳',
                    'skipped': '⏭️'
                }.get(task['status'], '❓')
                print(f"  {status_emoji} {task['task']} [{task['status']}]")
            
            print(f"\n完成进度：{todo_data.get('completed_count', 0)}/{todo_data.get('total_count', 0)}")
        
        # 检查是否有调试笔记（调试Agent必须创建的）
        debug_notes_file = work_dir / "debug_notes.json"
        if debug_notes_file.exists():
            with open(debug_notes_file, 'r') as f:
                notes = json.load(f)
            
            print("\n🔧 调试统计（debug_notes.json）：")
            print(f"- 迭代次数：{notes.get('current_iteration', 0)}")
            print(f"- 修复尝试：{len(notes.get('fix_attempts', []))}")
            print(f"- 错误类型：{len(notes.get('error_history', {}))}")
            
            # 显示成功策略
            successful = [a for a in notes.get('fix_attempts', []) 
                         if a.get('result') == 'success']
            if successful:
                print(f"\n成功的修复策略：")
                for s in successful[:3]:
                    print(f"  - {s.get('strategy', 'unknown')}")
        
        print("\n结果摘要：")
        print(result[:500] if len(result) > 500 else result)
        
    except Exception as e:
        print(f"\n执行失败：{e}")
        import traceback
        traceback.print_exc()
        
    print("finished")


if __name__ == "__main__":
    main()