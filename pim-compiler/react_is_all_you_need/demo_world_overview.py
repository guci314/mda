#!/usr/bin/env python3
"""演示 world_overview.md 自动生成功能

当 Agent 开始在一个新的外部世界（工作目录）工作时，
如果该目录没有 world_overview.md 文件，Agent 会自动生成一个。
"""

import os
import sys
from pathlib import Path
from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel

def main():
    # 获取要分析的目录
    if len(sys.argv) > 1:
        target_dir = Path(sys.argv[1]).resolve()
    else:
        # 默认分析 react_is_all_you_need 项目本身
        target_dir = Path(__file__).parent
    
    if not target_dir.exists():
        print(f"错误：目录 {target_dir} 不存在")
        return
    
    print("=" * 70)
    print("World Overview 自动生成演示")
    print("=" * 70)
    print(f"\n目标目录: {target_dir}")
    
    # 检查是否已有 world_overview.md
    overview_file = target_dir / "world_overview.md"
    if overview_file.exists():
        print(f"\n注意：该目录已有 world_overview.md")
        print("Agent 将直接执行任务，不会重新生成。")
    else:
        print(f"\n该目录没有 world_overview.md")
        print("Agent 将在执行第一个任务前自动生成。")
    
    # 创建 Agent 配置
    config = ReactAgentConfig(
        work_dir=str(target_dir),
        memory_level=MemoryLevel.NONE,
        knowledge_files=[
            "knowledge/core/system_prompt.md",
            "knowledge/programming/python_programming_knowledge.md",
            "knowledge/core/world_overview_generation.md"
        ]
    )
    
    # 创建 Agent
    print(f"\n→ 创建 Agent...")
    agent = GenericReactAgent(config, name="overview_demo")
    
    # 执行一个简单任务
    print(f"\n→ 执行任务：分析项目结构")
    print("=" * 70)
    
    agent.execute_task(
        "请分析当前目录的项目结构，给出简要总结。"
        "如果是代码项目，说明主要功能和技术栈。"
    )
    
    print("\n" + "=" * 70)
    
    # 检查结果
    if overview_file.exists():
        print(f"\n✓ world_overview.md 已生成在: {overview_file}")
        print("\n内容预览:")
        print("-" * 70)
        content = overview_file.read_text()
        preview = content[:800] + "..." if len(content) > 800 else content
        print(preview)
    else:
        print(f"\n✗ world_overview.md 未生成")

if __name__ == "__main__":
    # 可选：启用调试模式
    # os.environ['DEBUG'] = '1'
    
    main()