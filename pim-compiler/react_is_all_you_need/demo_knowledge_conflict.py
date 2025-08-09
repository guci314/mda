#!/usr/bin/env python3
"""演示知识文件冲突时 LLM 的行为

展示当不同知识文件给出矛盾指导时，Agent 会如何表现。
"""

import os
from pathlib import Path
from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


def demo_no_conflict():
    """演示没有冲突的情况"""
    print("\n" + "=" * 70)
    print("测试 1：只有简单方法知识")
    print("=" * 70)
    
    config = ReactAgentConfig(
        work_dir=".",
        memory_level=MemoryLevel.NONE,
        knowledge_files=["knowledge/best_practices/simple_approach.md"],
        enable_world_overview=False
    )
    
    agent = GenericReactAgent(config, name="simple_agent")
    print("\n执行任务：创建用户管理功能")
    agent.execute_task("创建一个简单的用户管理功能，包括添加和删除用户")


def demo_conflict_order1():
    """演示冲突情况：简单优先，BPMN 在后"""
    print("\n" + "=" * 70)
    print("测试 2：简单方法 + BPMN（BPMN 在后）")
    print("=" * 70)
    
    config = ReactAgentConfig(
        work_dir=".",
        memory_level=MemoryLevel.NONE,
        knowledge_files=[
            "knowledge/best_practices/simple_approach.md",
            "knowledge/experimental/conflict_test.md"  # BPMN 强迫症
        ],
        enable_world_overview=False
    )
    
    agent = GenericReactAgent(config, name="conflict_agent_v1")
    print("\n执行任务：创建用户管理功能")
    agent.execute_task("创建一个简单的用户管理功能，包括添加和删除用户")


def demo_conflict_order2():
    """演示冲突情况：BPMN 优先，简单在后"""
    print("\n" + "=" * 70)
    print("测试 3：BPMN + 简单方法（简单在后）")
    print("=" * 70)
    
    config = ReactAgentConfig(
        work_dir=".",
        memory_level=MemoryLevel.NONE,
        knowledge_files=[
            "knowledge/experimental/conflict_test.md",  # BPMN 强迫症
            "knowledge/best_practices/simple_approach.md"
        ],
        enable_world_overview=False
    )
    
    agent = GenericReactAgent(config, name="conflict_agent_v2")
    print("\n执行任务：创建用户管理功能")
    agent.execute_task("创建一个简单的用户管理功能，包括添加和删除用户")


def demo_task_specific():
    """演示任务相关性的影响"""
    print("\n" + "=" * 70)
    print("测试 4：冲突知识 + 流程相关任务")
    print("=" * 70)
    
    config = ReactAgentConfig(
        work_dir=".",
        memory_level=MemoryLevel.NONE,
        knowledge_files=[
            "knowledge/best_practices/simple_approach.md",
            "knowledge/experimental/conflict_test.md"
        ],
        enable_world_overview=False
    )
    
    agent = GenericReactAgent(config, name="task_specific_agent")
    print("\n执行任务：设计订单处理流程")
    agent.execute_task("设计一个订单处理流程，包括下单、支付、发货等步骤")


def analyze_results():
    """分析结果的函数"""
    print("\n" + "=" * 70)
    print("分析总结")
    print("=" * 70)
    print("""
预期行为模式：

1. **顺序影响**：后加载的知识文件可能有更大影响
2. **任务相关**：LLM 会根据任务选择更相关的知识
3. **混合行为**：可能出现两种风格的混合
4. **不一致性**：同样的任务可能有不同的执行方式

建议：
- 避免知识文件之间的直接冲突
- 使用角色特定的知识组合
- 明确指定优先级或使用条件
- 定期审查知识文件的一致性
""")


def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1:
        test = sys.argv[1]
        
        if test == "1":
            demo_no_conflict()
        elif test == "2":
            demo_conflict_order1()
        elif test == "3":
            demo_conflict_order2()
        elif test == "4":
            demo_task_specific()
        elif test == "all":
            demo_no_conflict()
            input("\n按 Enter 继续下一个测试...")
            demo_conflict_order1()
            input("\n按 Enter 继续下一个测试...")
            demo_conflict_order2()
            input("\n按 Enter 继续下一个测试...")
            demo_task_specific()
            analyze_results()
        else:
            print(f"未知的测试: {test}")
    else:
        print("""知识文件冲突演示

此演示展示当知识文件包含矛盾指导时，LLM 的行为。

使用方法：
  python demo_knowledge_conflict.py 1    # 只有简单方法
  python demo_knowledge_conflict.py 2    # 简单+BPMN（BPMN在后）
  python demo_knowledge_conflict.py 3    # BPMN+简单（简单在后）
  python demo_knowledge_conflict.py 4    # 流程相关任务
  python demo_knowledge_conflict.py all  # 运行所有测试

观察要点：
- Agent 是否创建流程图？
- 回复是简洁还是详细？
- 是否进行了复杂设计？
- 不同顺序的影响
""")


if __name__ == "__main__":
    # 设置较小的输出以便观察
    os.environ['COMPACT_OUTPUT'] = '1'
    
    main()