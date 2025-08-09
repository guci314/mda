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
            "knowledge/mda/syntax_fix_strategies.md"     # 语法修复策略
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
    
    # 为调试Agent添加额外的系统提示，指导其使用正确的工具
    agent._system_prompt = (agent._system_prompt or "") + """

## 调试流程指导

你必须完成完整的调试流程，不要只初始化就返回！

### Python语法错误修复策略（重要）
**优先使用 fix_python_syntax_errors 工具！**
- 遇到缩进错误（IndentationError）：立即使用 fix_python_syntax_errors 工具
- 遇到括号不匹配（SyntaxError: unmatched）：立即使用 fix_python_syntax_errors 工具  
- 遇到多个语法错误：使用 fix_python_syntax_errors 一次性修复整个文件
- 避免使用 edit_lines 逐行修复语法错误！这会导致反复修复同样的问题。

### 执行流程（必须全部完成）
1. 调用 init_debug_notes 工具初始化调试笔记
2. 使用 execute_command 运行 pytest -xvs 获取测试结果
3. 如果有失败：
   - 对于语法错误：立即使用 fix_python_syntax_errors 工具
   - 对于其他错误：使用 read_file、search_replace 或 write_file 修复
   - 更新 debug_notes.json 记录修复尝试
4. 再次运行 pytest 验证修复
5. 重复步骤3-4直到所有测试通过
6. 更新最终的 debug_notes.json

### 返回条件
- 成功：所有测试通过（0 failed），返回"调试完成，所有测试通过"
- 失败：达到最大尝试次数（10次），返回"需要人工介入"
- 继续：如果需要更多步骤，返回"需要继续调试，请再次调用"
"""
    return agent


def create_coordinator_agent(work_dir: str, llm_config: dict, 
                           generation_tool, debug_tool) -> GenericReactAgent:
    """创建协调两个子Agent的主Agent"""
    
    # 主Agent配置 - 只负责协调
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[],  # 主Agent不需要领域知识
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
    
    # 意图声明风格的任务描述
    task = f"""
## 目标
从PSM文件生成一个完全可工作的FastAPI应用，确保所有测试100%通过。

## 输入
- PSM文件：{psm_file}
- 输出目录：{work_dir}


## TODO管理要求
你必须在 {work_dir}/coordinator_todo.json 文件中维护任务清单。

初始TODO结构：
```json
{{
  "tasks": [
    {{"id": 1, "task": "生成FastAPI应用代码", "status": "pending"}},
    {{"id": 2, "task": "运行pytest测试验证", "status": "pending"}},
    {{"id": 3, "task": "如果测试失败，调用调试Agent修复", "status": "pending"}},
    {{"id": 4, "task": "确认所有测试100%通过", "status": "pending"}}
  ],
  "current_task": null,
  "completed_count": 0,
  "total_count": 4
}}
```

每次开始和完成任务时，使用 write_file 工具更新TODO文件：
- 开始任务时：设置 status = "in_progress"，更新 current_task
- 完成任务时：设置 status = "completed"，更新 completed_count
- 跳过任务时：设置 status = "skipped"

## 执行策略
你有以下主要工具可以使用：
1. **write_file** - 用于创建和更新TODO笔记（以及其他文件）
2. **execute_command** - 用于运行命令（如pytest）
3. **code_generator** - 用于生成代码（子Agent工具）
4. **code_debugger** - 用于修复测试失败（子Agent工具）
还有其他文件操作和搜索工具。

请按照以下流程执行：
1. 首先，创建TODO笔记文件（使用write_file写入coordinator_todo.json）
2. 使用 code_generator 生成FastAPI应用（更新TODO：任务1完成）
3. 使用 execute_command 运行 `cd {work_dir} && python -m pytest tests/ -xvs` 验证代码（更新TODO：任务2完成）
4. 如果测试有失败：
   - 使用 code_debugger 修复所有错误，传递明确的任务：
     "修复测试错误直到全部通过。你必须完成整个调试流程，不要只初始化就返回。
      
      【重要】你有一个专门的工具 fix_python_syntax_errors 用于修复Python语法错误：
      - 遇到任何缩进错误（IndentationError）：使用 fix_python_syntax_errors 工具
      - 遇到括号不匹配（SyntaxError）：使用 fix_python_syntax_errors 工具
      - 这个工具会自动重写整个文件，避免逐行修复的问题
      
      使用你的所有工具，特别是 fix_python_syntax_errors 处理语法错误。
      持续修复直到所有测试通过或达到最大尝试次数。"
   - 如果 code_debugger 返回"需要继续调试"，立即再次调用它
   - 循环调用 code_debugger 直到返回"调试完成"或"需要人工介入"
   - 再次使用 execute_command 运行测试确认修复成功
   - 检查 debug_notes.json 确认调试Agent记录了所有活动
5. 确认所有测试通过（更新TODO：任务4完成）

## 重要提示
- 每个任务开始和结束都要更新TODO笔记
- 必须完成整个流程，不要在生成代码后就停止
- 必须实际运行测试并查看结果
- 如果测试失败，必须调用调试Agent修复
- **绝对不要自己使用sed或其他命令修改代码，只能通过code_debugger修复**
- **如果code_debugger需要更多步骤，必须继续调用它，不要放弃**
- 只有当看到所有测试通过才能结束任务

现在开始执行，记得维护TODO笔记，确保达到100%测试通过的目标。

## 成功标准
- TODO列表中的每一项任务都必须完成（status为"completed"或"skipped"）
- FastAPI应用成功生成在指定目录
- 运行 `pytest tests/ -xvs` 所有测试必须通过（0个失败）
- 如果有测试失败，必须修复直到100%通过
- coordinator_todo.json 的 completed_count 必须等于 total_count

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