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
            "knowledge/mda/debugging_flexible.md",              # 🔄 灵活调试策略
            "knowledge/mda/fix_sqlalchemy_duplicate_table.md",  # SQLAlchemy具体问题修复
            "knowledge/mda/debugging_complete.md",              # 完整调试知识库（合并版）
            "knowledge/mda/debugging_validation.md"             # 验证规范（防止误报成功）
        ],
        enable_project_exploration=False,
        **llm_config
    )
    
    agent = GenericReactAgent(config, name="debug_agent", custom_tools=debug_tools)
    agent.interface = """调试专家 - 灵活修复错误
    
能力：
- 维护调试笔记避免重复修复
- 智能语法错误修复（整文件重写）
- 系统性错误诊断和修复
- 灵活选择修复方案（功能或测试）
- 确保100%测试通过
"""
    
    # 简化系统提示，主要依赖知识文件
    agent._system_prompt = (agent._system_prompt or "") + """

## 调试任务执行

你是一个灵活的调试Agent。你的知识文件 debugging_flexible.md 包含了：
- 灵活的调试策略
- 成本评估方法
- 实用主义原则
- 多种解决方案

记住：
1. 目标是让测试通过，方法可以灵活
2. 选择最小成本的修复方案
3. 可以修改测试文件或功能文件
4. 持续修复直到所有测试通过
"""
    return agent


def create_coordinator_agent(work_dir: str, llm_config: dict, 
                           generation_tool, debug_tool, coordination_mode: str = "workflow") -> GenericReactAgent:
    """创建协调两个子Agent的主Agent
    
    Args:
        coordination_mode: 协调模式 - "workflow"(工作流), "rules"(产生式规则), "goal"(目标驱动), "story"(故事驱动), "machine"(状态机)
    """
    
    # 协调Agent强制使用DeepSeek Reasoner
    coordinator_llm_config = {
        "llm_model": "deepseek-reasoner",
        "llm_base_url": "https://api.deepseek.com/v1",
        "llm_api_key_env": "DEEPSEEK_API_KEY",
        "llm_temperature": 0
    }
    
    # 如果用户提供了httpx_client，保留它
    if "http_client" in llm_config:
        coordinator_llm_config["http_client"] = llm_config["http_client"]
    
    # 添加灵活处理策略（所有模式都需要）
    base_knowledge = ["knowledge/mda/coordinator_flexible.md"]
    
    # 根据模式选择知识文件和配置
    if coordination_mode == "rules":
        knowledge_files = base_knowledge + [
            "knowledge/mda/coordinator_react_rules.md",     # React产生式规则
            "knowledge/mda/coordinator_validation.md"       # 验证规范
        ]
        agent_name = "react_coordinator"
        interface = """React规则协调器 - 基于产生式规则的Pipeline管理
        
我使用IF-THEN规则来协调任务：
- 不需要复杂推理
- 只做条件反射式执行
- 规则驱动的状态转换
"""
        system_prompt_addition = """

## React产生式规则执行器

你使用coordinator_react_rules.md中的产生式规则系统工作。

执行方式：
1. 检查当前状态（code_generated? test_failed_count?）
2. 找到条件满足的规则
3. 执行规则的动作
4. 更新状态

记住：像条件反射一样工作，不需要理解"为什么"。
"""
    elif coordination_mode == "goal":
        knowledge_files = base_knowledge + [
            "knowledge/mda/coordinator_goal_based.md",      # 原始目标驱动知识
            "knowledge/mda/coordinator_validation.md"       # 验证规范
        ]
        agent_name = "goal_coordinator"
        interface = """目标驱动协调器 - 基于目标和验证的Pipeline管理
        
我的唯一目标：让所有测试通过（0 failed）
"""
        system_prompt_addition = """

## 目标驱动执行器

你使用coordinator_goal_based.md中的目标驱动系统工作。

核心循环：
1. 目标：test_failed == 0
2. 验证：运行pytest，获取failed数量
3. 差距：当前failed数量
4. 行动：如果差距>0，采取行动缩小差距
5. 重复：直到差距=0

记住：
- 只关注一个数字：test_failed
- 每次行动后必须验证这个数字
- 不断尝试直到这个数字变成0
"""
    elif coordination_mode == "story":
        knowledge_files = base_knowledge + [
            "knowledge/mda/coordinator_story_based.md",     # 故事形式的目标知识
            "knowledge/mda/coordinator_simple_loop.md"      # 极简循环指令
        ]
        agent_name = "story_coordinator"
        interface = """故事驱动协调器 - 我要完成一个成功的故事
        
就像故事里说的：看到数字不是0就叫调试器，看到0就完成。
"""
        system_prompt_addition = """

## 你的故事

你正在经历coordinator_story_based.md中描述的故事。

记住故事的核心：
1. 运行pytest看failed数量
2. 不是0就叫调试器
3. 是0才能说完成

就像故事里的主角一样：
- 13 failed → 继续
- 11 failed → 继续
- 5 failed → 继续
- 1 failed → 继续
- 0 failed → 完成！

你也要这样做。不要在中途放弃。
故事只有在看到"0 failed"时才能有Happy Ending。
"""
    elif coordination_mode == "machine":
        knowledge_files = base_knowledge + [
            "knowledge/mda/coordinator_state_machine.md"    # 状态机指令
        ]
        agent_name = "machine_coordinator"
        interface = """状态机协调器 - 机械化执行指令
        
我是一个状态机，只执行状态转换，不需要理解。
"""
        system_prompt_addition = """

## 状态机执行器

你是一个状态机。使用coordinator_state_machine.md中的状态转换表。

当前状态 = "START"

执行循环：
1. 根据当前状态执行动作
2. 根据结果查找下一状态
3. 转换到下一状态
4. 重复

关键规则：
- CALL_DEBUGGER后必须回RUN_PYTEST
- 只有看到"0 failed"才能进入COMPLETE
- 忽略debugger的返回内容
- 只相信pytest的输出

记住：你是机器，不是人。
"""
    else:  # workflow模式（默认）
        knowledge_files = base_knowledge + [
            "knowledge/mda/coordinator_workflow.md",        # 工作流知识
            "knowledge/mda/coordinator_validation.md"       # 验证规范
        ]
        agent_name = "coordinator_agent"
        interface = """MDA Pipeline协调者
    
我协调两个专门的Agent：
1. 生成Agent - 负责代码生成
2. 调试Agent - 负责错误修复

工作流程：
1. 调用生成Agent创建代码
2. 运行测试验证
3. 如有失败，调用调试Agent修复
4. 循环直到100%通过
"""
        system_prompt_addition = """

## 协调任务执行

你是MDA Pipeline的协调者。你的知识文件包含了：
- coordinator_workflow.md: 完整的执行流程
- coordinator_validation.md: 严格的验证规范

⚠️ 重要提醒：
1. **必须独立验证测试结果**，不要盲目相信调试Agent
2. **只有看到 "0 failed" 才能声称成功**
3. **诚实报告真实数字**（如：11 failed, 2 passed）
4. **部分成功就是失败**

请严格按照验证规范，诚实地完成任务。
"""
    
    # 主Agent配置 - 使用Gemini配置
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=knowledge_files,
        enable_project_exploration=False,
        **coordinator_llm_config  # 使用Gemini配置而不是用户选择的配置
    )
    
    # 创建主Agent
    agent = GenericReactAgent(
        config, 
        name=agent_name,
        custom_tools=[generation_tool, debug_tool]
    )
    
    agent.interface = interface
    agent._system_prompt = (agent._system_prompt or "") + system_prompt_addition
    
    return agent


def main():
    """运行双Agent架构的MDA Pipeline"""
    
    print("=" * 80)
    print("MDA双Agent架构演示")
    print("=" * 80)
    
    # 设置工作目录
    work_dir = Path("output/mda_dual_agent_demo")
    
    # 清空目录（如果存在）
    if work_dir.exists():
        import shutil
        print(f"\n清空目录: {work_dir}")
        shutil.rmtree(work_dir)
    
    # 重新创建目录
    work_dir.mkdir(parents=True, exist_ok=True)
    print(f"创建新目录: {work_dir}")
    
    # PSM文件路径 (使用已有的PSM)
    psm_file = Path(__file__).parent.parent / "examples/blog_psm.md"
    
    # 选择LLM配置
    print("\n选择LLM配置：")
    print("1. DeepSeek (默认)")
    print("2. Kimi k2-turbo (128K上下文)")
    print("3. Gemini 2.5 Pro (via OpenRouter)")
    print("4. Claude Sonnet 4 (via OpenRouter)")
    print("5. Qwen3-Coder (via OpenRouter)")
    
    choice = input("请选择 (1-5，默认1): ").strip() or "1"
    
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
    elif choice == "5":
        # Qwen3-Coder配置 (通过OpenRouter)
        llm_config = {
            "llm_model": "qwen/qwen3-coder",
            "llm_base_url": "https://openrouter.ai/api/v1",
            "llm_api_key_env": "OPENROUTER_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "Qwen3-Coder (via OpenRouter)"
    else:
        # DeepSeek配置（默认）
        llm_config = {
            "llm_model": "deepseek-chat",
            "llm_base_url": "https://api.deepseek.com/v1",
            "llm_api_key_env": "DEEPSEEK_API_KEY",
            "llm_temperature": 0
        }
        llm_name = "DeepSeek"
    
    print(f"\n子Agent使用 {llm_name} 作为LLM后端")
    print("协调Agent固定使用 DeepSeek Reasoner")
    
    # 选择协调模式
    coordination_mode = "workflow"  # 默认
    
    if "kimi" in llm_name.lower():
        print("\n检测到使用Kimi模型。")
        print("选择协调模式：")
        print("1. 工作流模式（需要状态管理能力）")
        print("2. React规则模式（IF-THEN条件反射）")
        print("3. 目标驱动模式（只关注目标达成）")
        print("4. 故事模式（像故事一样简单）")
        print("5. 状态机模式（机械化执行）【推荐】")
        mode_choice = input("\n请选择 (1-5，默认5): ").strip() or "5"
        
        if mode_choice == "1":
            coordination_mode = "workflow"
        elif mode_choice == "2":
            coordination_mode = "rules"
        elif mode_choice == "3":
            coordination_mode = "goal"
        elif mode_choice == "4":
            coordination_mode = "story"
        else:
            coordination_mode = "machine"
    else:
        print("\n选择协调模式：")
        print("1. 工作流模式（默认，适合推理模型）")
        print("2. React规则模式（条件反射式执行）")
        print("3. 目标驱动模式（灵活追求目标）")
        print("4. 故事模式（通俗易懂的叙事）")
        print("5. 状态机模式（机械化执行）")
        mode_choice = input("请选择 (1-5，默认1): ").strip() or "1"
        
        if mode_choice == "2":
            coordination_mode = "rules"
        elif mode_choice == "3":
            coordination_mode = "goal"
        elif mode_choice == "4":
            coordination_mode = "story"
        elif mode_choice == "5":
            coordination_mode = "machine"
        else:
            coordination_mode = "workflow"
    
    mode_names = {
        "workflow": "工作流模式",
        "rules": "React产生式规则",
        "goal": "目标驱动模式",
        "story": "故事驱动模式",
        "machine": "状态机模式"
    }
    print(f"✅ 使用{mode_names[coordination_mode]}")
    
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
        debug_tool,
        coordination_mode=coordination_mode  # 传递协调模式
    )
    
    # 执行任务 - 使用意图声明风格
    print("\n" + "=" * 60)
    print("开始执行MDA Pipeline...")
    print("=" * 60)
    
    start_time = time.time()
    
    # 根据模式生成不同的任务描述
    if coordination_mode == "machine":
        # 状态机模式的任务描述
        task = f"""
## 🤖 状态机执行

你是一个状态机。不需要理解，只需要执行。

## 初始化
- 工作目录：{work_dir}
- PSM文件：{psm_file}
- 当前状态："START"

## 状态转换表

STATE: START
  如果 app/main.py 不存在 → 调用code_generator → RUN_PYTEST
  如果 app/main.py 存在 → RUN_PYTEST

STATE: RUN_PYTEST
  执行: pytest tests/
  如果 输出包含 "0 failed" → COMPLETE
  如果 输出包含 "X failed" (X≠0) → CALL_DEBUGGER

STATE: CALL_DEBUGGER
  执行: code_debugger
  下一状态: RUN_PYTEST (无条件)

STATE: COMPLETE
  输出: "完成"
  结束

## 关键规则

1. CALL_DEBUGGER后必须回RUN_PYTEST
2. 只有"0 failed"才能COMPLETE
3. 忽略debugger说什么
4. 只看pytest输出

开始执行状态机...
"""
    elif coordination_mode == "story":
        # 故事驱动模式的任务描述
        task = f"""
## 📖 开始你的故事

你要像coordinator_story_based.md里的主角一样，完成一个成功的故事。

## 故事设定
- 地点：{work_dir}
- 任务：让所有测试通过
- 种子：{psm_file}

## 记住故事的规则

**规则只有一条**：
> 看到数字不是0，就叫调试器；看到0，就说完成。

## 你的剧本

1. 先生成代码（如果还没有）：
   - 调用 code_generator

2. 然后开始循环：
   ```
   运行: pytest tests/
   看到: X failed
   
   如果 X 不是 0:
       叫 code_debugger
       回到"运行"
   如果 X 是 0:
       说"完成！"
   ```

## 成功的例子

就像故事里说的：
- 看到 13 failed → 不能停，叫调试器
- 看到 8 failed → 不能停，继续叫
- 看到 3 failed → 不能停，继续叫
- 看到 1 failed → 不能停，继续叫
- 看到 0 failed → 现在可以庆祝了！

## 开始吧

记住：**不是0就不能停**。
这个故事只有一个Happy Ending：看到"0 failed"。

现在，开始你的故事...
"""
    elif coordination_mode == "goal":
        # 目标驱动模式的任务描述
        task = f"""
## 🎯 你的唯一目标
让test_failed数量变成0

## 输入
- PSM文件：{psm_file}
- 输出目录：{work_dir}

## 执行方式 - 目标驱动
使用你的知识文件 coordinator_goal_based.md：

### 核心循环
1. 当前状态：test_failed = ?
2. 目标状态：test_failed = 0
3. 差距：当前值 - 0
4. 如果差距 > 0：采取行动
5. 验证：运行pytest，重新获取test_failed
6. 重复直到差距 = 0

### 可用工具
- code_generator: 生成代码（如果还没有代码）
- code_debugger: 修复错误（如果test_failed > 0）
- execute_command: 运行pytest验证
- write_file: 记录进展

### 关键原则
- 每次行动后必须运行pytest
- 用具体数字报告（如"11 failed"，不是"有些失败"）
- 不断尝试直到test_failed = 0
- 即使有改进也要继续（11→9→5→2→0）

开始追求目标！记住：你的唯一任务就是让test_failed变成0。
"""
    elif coordination_mode == "rules":
        # React规则模式的任务描述
        task = f"""
## 目标
从PSM文件生成100%测试通过的FastAPI应用。

## 输入
- PSM文件：{psm_file}
- 输出目录：{work_dir}

## 执行方式 - React产生式规则
使用你的知识文件 coordinator_react_rules.md 中的产生式规则系统：

### 状态变量（在coordinator_todo.json中跟踪）
- code_generated: bool
- test_failed_count: int
- debug_attempts: int
- current_task: str

### 执行循环
1. 检查当前状态
2. 找到条件满足的规则（IF条件 THEN动作）
3. 执行规则的动作
4. 更新状态
5. 重复直到goal_achieved（test_failed_count == 0）

### 规则示例
- IF NOT code_generated THEN 调用code_generator
- IF test_failed_count > 0 THEN 调用code_debugger
- IF test_failed_count == 0 THEN 标记完成

## 成功条件
test_failed_count == 0 且 test_run == True

记住：像条件反射一样执行，不需要理解"为什么"。
开始执行React规则循环！
"""
    else:
        # 工作流模式的任务描述
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