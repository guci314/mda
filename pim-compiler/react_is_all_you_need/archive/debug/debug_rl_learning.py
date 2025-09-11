#!/usr/bin/env python3
"""
强化学习式调试知识优化
只提供简单奖励，让系统自己发现优化模式
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path.cwd()))

from core.react_agent_minimal import ReactAgentMinimal

print("🧠 强化学习式元认知优化")
print("=" * 60)

# 创建元认知Agent - 只给最简单的指导
meta_agent = ReactAgentMinimal(
    work_dir=".",
    name="rl_meta_agent",
    description="通过试错学习优化",
    model="kimi-k2-turbo-preview",
    knowledge_files=[
        "knowledge/meta_cognitive_simple.md"
    ]
)

# 极简任务 - 只定义奖励，不定义方法
task = """
# 任务：优化调试流程

## 历史数据
- 某Agent用了86轮完成调试
- 测试最终100%通过

## 奖励函数
```python
def reward(rounds, success):
    if not success:
        return -100  # 失败惩罚
    else:
        return max(0, 100 - rounds)  # 轮数越少奖励越高
```

## 你的任务
1. 分析为什么需要86轮
2. 发现可以优化的模式
3. 将发现写入`knowledge/mda/debugging_unified.md`

## 限制
- 不要参考`debug_error_patterns.md`（人类知识）
- 自己发现优化模式
- 目标：让未来调试获得更高奖励（更少轮数）

## 可用信息
86轮调试的关键失败点：
- 轮1-30：重复尝试不同测试命令
- 轮31-60：逐个文件修复Pydantic兼容性
- 轮61-86：逐个修复其他错误

请自己发现：什么导致了低效？如何改进？
"""

result = meta_agent.execute(task=task)

print("\n" + "=" * 60)
print("✅ 强化学习式优化完成")
if result:
    print(f"\nAgent自主发现的模式：")
    print(result[:1000])
print("=" * 60)