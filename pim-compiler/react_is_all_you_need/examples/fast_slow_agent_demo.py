#!/usr/bin/env python3
"""
异构Agent协作示例：快速响应 + 深度思考

用户体验：
- 问题立即得到响应（fast_agent）
- 复杂任务后台深度处理（slow_agent）
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.react_agent_minimal import ReactAgentMinimal

# 快速Agent（用于用户交互）
fast_agent = ReactAgentMinimal(
    name="fast_responder",
    description="快速响应Agent - 负责用户交互",
    work_dir=".",
    model="x-ai/grok-code-fast-1",  # 快速模型
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    stateful=False  # 无状态，更快
)

# 慢速Agent（用于深度思考）
slow_agent = ReactAgentMinimal(
    name="deep_thinker",
    description="深度思考Agent - 负责复杂任务",
    work_dir=".",
    model="anthropic/claude-sonnet-4.5",  # 强模型
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    stateful=True  # 有状态，深度思考
)

# 将slow_agent注册为fast_agent的工具
fast_agent.add_function(slow_agent)

print("=" * 60)
print("异构Agent协作演示")
print("=" * 60)

# 场景1：简单问题 - fast_agent直接回答
print("\n场景1：简单问题（快速响应）")
print("-" * 60)
question1 = "什么是RESTful API？"
print(f"用户: {question1}")
print("fast_agent响应...")

result1 = fast_agent.execute(task=question1)
print(f"回答: {result1[:200]}...")

# 场景2：复杂任务 - fast_agent委托给slow_agent
print("\n\n场景2：复杂任务（委托给深度思考Agent）")
print("-" * 60)
question2 = "设计一个微服务架构，包括API网关、服务发现、配置中心"
print(f"用户: {question2}")
print("fast_agent识别到复杂任务，委托给deep_thinker...")

# fast_agent会识别到这是复杂任务，自动委托
result2 = fast_agent.execute(task=f"""
这是一个复杂的架构设计任务：{question2}

请调用deep_thinker来处理，因为这需要深度思考。
""")

print(f"结果: {result2[:300]}...")

print("\n" + "=" * 60)
print("演示完成！")
print("=" * 60)
print("\n关键洞察：")
print("- 简单问题：快速模型立即回答（用户体验好）")
print("- 复杂任务：强模型深度思考（质量高）")
print("- 成本优化：大部分用快速模型，少部分用强模型")
