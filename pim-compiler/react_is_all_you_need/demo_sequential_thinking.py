#!/usr/bin/env python3
"""
Sequential Thinking与React Agent集成演示

展示如何使用Sequential Thinking MCP作为元认知层，
指导React Agent进行复杂问题的解决。
"""

import os
import sys
from pathlib import Path
import json
from typing import Dict, Any, List

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from langchain_core.tools import tool


def create_sequential_thinking_tool():
    """创建Sequential Thinking工具的模拟实现"""
    
    # 存储思维链
    thought_chain = []
    
    @tool
    def sequential_think(
        thought: str,
        thought_number: int,
        total_thoughts: int,
        next_thought_needed: bool = True,
        is_revision: bool = False,
        revises_thought: int = None,
        branch_from_thought: int = None,
        branch_id: str = None
    ) -> str:
        """
        Sequential Thinking工具 - 结构化思维链推理
        
        Args:
            thought: 当前思考内容
            thought_number: 当前思考步骤
            total_thoughts: 预估总步骤数
            next_thought_needed: 是否需要继续
            is_revision: 是否在修正之前的思考
            revises_thought: 修正的目标步骤
            branch_from_thought: 分支起点
            branch_id: 分支标识
        """
        entry = {
            "number": thought_number,
            "thought": thought,
            "is_revision": is_revision,
            "revises": revises_thought,
            "branch_from": branch_from_thought,
            "branch_id": branch_id
        }
        
        thought_chain.append(entry)
        
        result = {
            "thought_number": thought_number,
            "total_thoughts": total_thoughts,
            "next_needed": next_thought_needed,
            "chain_length": len(thought_chain)
        }
        
        if is_revision:
            result["revision_info"] = f"Revised thought {revises_thought}"
        
        if branch_id:
            result["branch_info"] = f"Branch '{branch_id}' from thought {branch_from_thought}"
            
        return json.dumps(result, indent=2)
    
    return sequential_think, thought_chain


def create_thinking_agent(work_dir: str) -> GenericReactAgent:
    """创建具有Sequential Thinking能力的Agent"""
    
    # 创建Sequential Thinking工具
    think_tool, thought_chain = create_sequential_thinking_tool()
    
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[],
        enable_project_exploration=False,
        llm_model="deepseek-chat",
        llm_base_url="https://api.deepseek.com/v1",
        llm_api_key_env="DEEPSEEK_API_KEY",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(
        config, 
        name="thinking_agent",
        custom_tools=[think_tool]
    )
    
    agent.interface = """具有元认知能力的Agent
    
能力：
- 使用Sequential Thinking进行结构化推理
- 可以修正和调整思维过程
- 支持多路径探索
- 结合工具执行验证假设
"""
    
    # 添加专门的系统提示
    agent._system_prompt = (agent._system_prompt or "") + """

## Sequential Thinking 使用指南

你配备了 sequential_think 工具用于结构化推理。使用方法：

1. **开始思考**：设置初始 thought_number=1 和预估的 total_thoughts
2. **逐步推进**：每步增加 thought_number，保持思维连贯
3. **修正错误**：发现问题时设置 is_revision=true 和 revises_thought
4. **探索分支**：需要并行探索时设置 branch_from_thought 和 branch_id
5. **结束思考**：达到结论时设置 next_thought_needed=false

### 思考模式

对于复杂问题，使用以下模式：
1. 分析问题 (thought 1)
2. 生成假设 (thought 2-3)
3. 验证假设 (thought 4-5，可能需要调用其他工具)
4. 修正/调整 (如需要，使用 is_revision)
5. 得出结论 (最后一个 thought)

记住：Sequential Thinking是你的"思维草稿纸"，用它来组织和追踪你的推理过程。
"""
    
    return agent, thought_chain


def demo_complex_problem_solving():
    """演示使用Sequential Thinking解决复杂问题"""
    
    print("=" * 80)
    print("Sequential Thinking + React Agent 演示")
    print("=" * 80)
    
    work_dir = Path("output/sequential_thinking_demo")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建Agent
    agent, thought_chain = create_thinking_agent(str(work_dir))
    
    # 复杂问题：设计一个高可用的微服务架构
    task = """
使用Sequential Thinking工具分析并设计一个高可用的微服务架构。

需求：
1. 支持100万日活用户
2. 99.9%可用性
3. 响应时间<200ms
4. 成本可控

请使用sequential_think工具进行结构化分析，包括：
- 问题分解
- 方案探索（可以使用分支探索不同方案）
- 权衡分析
- 最终决策

同时，创建一个架构设计文档 architecture_design.md 记录你的设计。
"""
    
    print("\n任务：设计高可用微服务架构")
    print("-" * 40)
    
    # 执行任务
    result = agent.execute_task(task)
    
    print("\n执行结果：")
    print("-" * 40)
    print(result[:500] + "..." if len(result) > 500 else result)
    
    # 展示思维链
    print("\n思维链追踪：")
    print("-" * 40)
    for i, thought in enumerate(thought_chain, 1):
        prefix = ""
        if thought["is_revision"]:
            prefix = f"[修正步骤{thought['revises']}] "
        if thought["branch_id"]:
            prefix = f"[分支:{thought['branch_id']}] "
        
        print(f"{i}. {prefix}{thought['thought'][:100]}...")
    
    # 检查生成的文档
    design_doc = work_dir / "architecture_design.md"
    if design_doc.exists():
        print("\n✅ 架构设计文档已生成")
        with open(design_doc, 'r') as f:
            content = f.read()
            print(f"   文档大小：{len(content)} 字符")
    
    return thought_chain


def demo_debugging_with_thinking():
    """演示使用Sequential Thinking进行调试"""
    
    print("\n" + "=" * 80)
    print("Sequential Thinking 调试演示")
    print("=" * 80)
    
    work_dir = Path("output/sequential_debugging_demo")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建一个有bug的Python文件
    buggy_code = '''
def calculate_average(numbers):
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)  # Bug: 没有处理空列表

def process_data(data):
    results = []
    for item in data:
        if item > 0:
            results.append(item * 2)
        else:
            results.append(item / 0)  # Bug: 除零错误
    return results

# 测试代码
test_numbers = [1, 2, 3, 4, 5]
print(f"Average: {calculate_average(test_numbers)}")
print(f"Processed: {process_data(test_numbers)}")

# 边界情况测试
empty_list = []
print(f"Empty average: {calculate_average(empty_list)}")  # 会报错
'''
    
    # 写入有bug的文件
    buggy_file = work_dir / "buggy_code.py"
    with open(buggy_file, 'w') as f:
        f.write(buggy_code)
    
    # 创建Agent
    agent, thought_chain = create_thinking_agent(str(work_dir))
    
    # 调试任务
    task = f"""
使用Sequential Thinking工具系统地调试 buggy_code.py 文件。

步骤：
1. 使用 sequential_think 分析可能的问题
2. 读取文件内容
3. 使用 sequential_think 识别具体的bug
4. 使用 sequential_think 设计修复方案
5. 修复代码
6. 使用 sequential_think 总结调试过程

要求：
- 每个重要的推理步骤都要使用 sequential_think 记录
- 如果发现初步分析有误，使用 is_revision 修正
- 最终生成修复后的文件 fixed_code.py
"""
    
    print("\n任务：系统调试Python代码")
    print("-" * 40)
    
    # 执行调试
    result = agent.execute_task(task)
    
    print("\n调试完成！")
    print("-" * 40)
    
    # 展示思维过程
    print("\n调试思维链：")
    for i, thought in enumerate(thought_chain, 1):
        if thought["is_revision"]:
            print(f"  {i}. [修正] {thought['thought'][:80]}...")
        else:
            print(f"  {i}. {thought['thought'][:80]}...")
    
    # 检查修复的文件
    fixed_file = work_dir / "fixed_code.py"
    if fixed_file.exists():
        print("\n✅ 代码已修复并保存到 fixed_code.py")
    
    return thought_chain


def main():
    """主函数"""
    
    print("选择演示：")
    print("1. 复杂问题解决（架构设计）")
    print("2. 系统调试演示")
    print("3. 运行所有演示")
    
    choice = input("\n请选择 (1-3): ").strip() or "1"
    
    if choice == "1":
        demo_complex_problem_solving()
    elif choice == "2":
        demo_debugging_with_thinking()
    else:
        demo_complex_problem_solving()
        demo_debugging_with_thinking()
    
    print("\n演示完成！")


if __name__ == "__main__":
    main()