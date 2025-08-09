#!/usr/bin/env python3
"""
渐进式Sequential Thinking实现

接受某些模型无法一次性完成8个步骤的现实，
采用渐进式方法，每次调用Agent完成一部分。
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


def create_incremental_agent(work_dir: str) -> GenericReactAgent:
    """创建渐进式执行的Agent"""
    
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=["knowledge/sequential_thinking_knowledge.md"],
        enable_project_exploration=False,
        llm_model="kimi-k2-turbo-preview",
        llm_base_url="https://api.moonshot.cn/v1",
        llm_api_key_env="MOONSHOT_API_KEY",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(config, name="incremental_agent")
    agent.interface = """渐进式Sequential Thinking执行器"""
    
    return agent


def incremental_sequential_thinking():
    """渐进式完成Sequential Thinking"""
    
    print("=" * 80)
    print("渐进式Sequential Thinking")
    print("=" * 80)
    print("\n接受模型限制，每次完成一部分")
    
    work_dir = Path("output/incremental_sequential")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_incremental_agent(str(work_dir))
    
    # 初始化
    init_task = """
    创建thought_chain.json，初始化Sequential Thinking结构。
    """
    
    print("\n[1/9] 初始化...")
    agent.execute_task(init_task)
    
    # 定义每个步骤的任务
    step_tasks = [
        """
        读取thought_chain.json，添加第1个thought（需求分析）。
        内容：详细分析电商推荐系统的4个核心需求。
        """,
        """
        读取thought_chain.json，添加第2个thought（技术分支点）。
        内容：说明需要探索协同过滤和深度学习两个方向。
        """,
        """
        读取thought_chain.json，添加第3个thought（协同过滤分支）。
        设置branch_id="collaborative_filtering"，分析UserCF/ItemCF。
        同时更新branches对象。
        """,
        """
        读取thought_chain.json，添加第4个thought（深度学习分支）。
        设置branch_id="deep_learning"，分析Wide&Deep/DeepFM。
        同时更新branches对象。
        """,
        """
        读取thought_chain.json，添加第5个thought（性能对比）。
        对比两个方案的延迟和吞吐量。
        """,
        """
        读取thought_chain.json，添加第6个thought（效果评估）。
        评估两个方案的CTR提升潜力。
        """,
        """
        读取thought_chain.json，添加第7个thought（最终决策）。
        选择最优方案并说明理由。
        """,
        """
        读取thought_chain.json，添加第8个thought（总结）。
        设置type="conclusion"，更新conclusions.main，
        将status改为"completed"。
        """
    ]
    
    # 逐步执行
    for i, task in enumerate(step_tasks, 1):
        print(f"\n[{i+1}/9] 添加thought {i}...")
        result = agent.execute_task(task)
        
        # 检查进度
        chain_file = work_dir / "thought_chain.json"
        if chain_file.exists():
            with open(chain_file, 'r') as f:
                chain = json.load(f)
            print(f"   ✓ 当前thoughts数量: {len(chain.get('thoughts', []))}")
    
    # 生成文档
    doc_task = """
    基于thought_chain.json生成recommendation_system.md架构文档。
    包含：系统概述、技术选型、架构设计、性能优化策略。
    """
    
    print("\n[9/9] 生成架构文档...")
    agent.execute_task(doc_task)
    
    # 验证结果
    print("\n" + "=" * 40)
    print("验证结果")
    print("=" * 40)
    
    chain_file = work_dir / "thought_chain.json"
    if chain_file.exists():
        with open(chain_file, 'r') as f:
            final_chain = json.load(f)
        
        print(f"✅ Thoughts数量: {len(final_chain.get('thoughts', []))}/8")
        print(f"✅ 状态: {final_chain.get('status')}")
        print(f"✅ 分支数: {len(final_chain.get('branches', {}))}")
        
        if final_chain.get('conclusions', {}).get('main'):
            print(f"✅ 结论: {final_chain['conclusions']['main'][:80]}...")
    
    doc_file = work_dir / "recommendation_system.md"
    if doc_file.exists():
        print(f"✅ 架构文档已生成")
    
    print("\n渐进式执行完成！")
    
    return final_chain if chain_file.exists() else None


def analyze_model_limitations():
    """分析模型限制和解决方案"""
    
    print("""
模型限制分析
=====================================

问题：Kimi模型无法一次性完成8个Sequential Thinking步骤

原因分析：
1. 模型的响应模式是"单次任务"而非"循环执行"
2. 知识文件的指导可能超出模型的理解能力
3. 模型倾向于"完成一个明确任务就返回"

解决方案对比：

1. 强制执行器（sequential_thinking_enforcer.py）
   ❌ 违背React + 知识 = 图灵完备理念
   ✅ 确保任务完成

2. 知识驱动（sequential_thinking_knowledge.md）
   ✅ 符合理念
   ❌ 依赖模型能力

3. 渐进式执行（本方案）
   ✅ 平衡理念和实用性
   ✅ 适应模型能力
   ✅ 保持Agent自主性

结论：
- 理想：模型通过知识自主完成
- 现实：需要适应模型能力
- 折中：渐进式引导，保持自主性

这不是失败，而是：
"了解工具的限制，在限制内最大化其能力"
""")


def main():
    """主函数"""
    
    print("选择模式：")
    print("1. 渐进式Sequential Thinking")
    print("2. 分析模型限制")
    print("3. 两者都执行")
    
    choice = input("\n请选择 (1-3): ").strip() or "1"
    
    if choice == "1":
        incremental_sequential_thinking()
    elif choice == "2":
        analyze_model_limitations()
    else:
        incremental_sequential_thinking()
        print("\n" + "=" * 80)
        analyze_model_limitations()


if __name__ == "__main__":
    main()