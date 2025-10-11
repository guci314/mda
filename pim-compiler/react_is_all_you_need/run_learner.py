#!/usr/bin/env python3
"""
直接运行Learner Agent，确保生成output.log
"""

import sys
import os
sys.path.insert(0, '/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need')

from core.react_agent_minimal import ReactAgentMinimal

def run_learner_task():
    """直接运行Learner，生成日志"""

    # 创建Learner实例
    learner = ReactAgentMinimal(
        name="learner",
        description="系统的学习核心，负责知识提取、组织和进化",
        work_dir="/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/test_docs",
        model="x-ai/grok-code-fast-1",
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        knowledge_files=[
            "/home/guci/.agent/learner/knowledge.md"
        ],
        stateful=True,  # 保存状态
        max_rounds=20
    )

    # 执行任务
    task = """
    验证你之前创建的知识系统：
    1. 列出wiki目录下的所有文件
    2. 检查knowledge_graph.ttl是否符合Turtle格式
    3. 验证precomputed_index.json的结构
    4. 报告系统的完整性
    """

    result = learner.execute(task=task)

    print("\n" + "="*60)
    print("✅ Learner执行完成")
    print("="*60)
    print(f"结果预览：{result[:500]}...")

    # 检查日志
    log_path = "/home/guci/.agent/learner/output.log"
    if os.path.exists(log_path):
        print(f"\n📝 日志已生成：{log_path}")
        with open(log_path, 'r') as f:
            lines = f.readlines()
            print(f"   日志行数：{len(lines)}")
            print(f"   最后一行：{lines[-1] if lines else '空'}")
    else:
        print("\n⚠️ 日志未生成")

    return result

if __name__ == "__main__":
    run_learner_task()