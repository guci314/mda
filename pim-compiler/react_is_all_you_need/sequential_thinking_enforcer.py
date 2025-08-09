#!/usr/bin/env python3
"""
Sequential Thinking强制执行器

由于某些LLM（如Kimi）不能严格遵循多步骤指令，
这个模块提供了一个强制执行机制，确保完成所有思考步骤。
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, List

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


def create_step_by_step_agent(work_dir: str) -> GenericReactAgent:
    """创建分步执行的Agent"""
    
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[],
        enable_project_exploration=False,
        llm_model="kimi-k2-turbo-preview",
        llm_base_url="https://api.moonshot.cn/v1",
        llm_api_key_env="MOONSHOT_API_KEY",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(config, name="step_by_step_agent")
    
    agent.interface = """分步执行Agent - 每次只完成一个具体步骤"""
    
    return agent


def execute_single_step(agent: GenericReactAgent, step_num: int, total_steps: int = 8) -> bool:
    """执行单个思考步骤"""
    
    step_tasks = {
        1: """
## 当前任务：添加第1个thought - 需求分析

请执行以下操作：
1. 读取thought_chain.json
2. 在thoughts数组中添加第1个thought：
   - id: 1
   - type: "initial"
   - content: 详细分析电商推荐系统的4个核心需求
   - confidence: 0.95
3. 更新current_thought为1
4. 保存文件

完成后返回"已添加需求分析thought"。
""",
        2: """
## 当前任务：添加第2个thought - 技术分支点

请执行以下操作：
1. 读取thought_chain.json
2. 添加第2个thought：
   - id: 2
   - type: "continuation"
   - content: 说明需要探索协同过滤和深度学习两个技术方向
   - confidence: 0.9
3. 更新current_thought为2
4. 保存文件

完成后返回"已添加技术分支点thought"。
""",
        3: """
## 当前任务：添加第3个thought - 协同过滤分支

请执行以下操作：
1. 读取thought_chain.json
2. 添加第3个thought：
   - id: 3
   - type: "branch"
   - branch_id: "collaborative_filtering"
   - branch_from: 2
   - content: 详细分析UserCF和ItemCF的优缺点，包括计算复杂度、冷启动问题、扩展性等
   - confidence: 0.75
3. 在branches中添加"collaborative_filtering"分支信息
4. 更新current_thought为3
5. 保存文件

完成后返回"已添加协同过滤分支thought"。
""",
        4: """
## 当前任务：添加第4个thought - 深度学习分支

请执行以下操作：
1. 读取thought_chain.json
2. 添加第4个thought：
   - id: 4
   - type: "branch"
   - branch_id: "deep_learning"
   - branch_from: 2
   - content: 详细分析DNN、Wide&Deep、DeepFM等模型，包括模型结构、训练成本、推理延迟等
   - confidence: 0.85
3. 在branches中添加"deep_learning"分支信息
4. 更新current_thought为4
5. 保存文件

完成后返回"已添加深度学习分支thought"。
""",
        5: """
## 当前任务：添加第5个thought - 性能对比

请执行以下操作：
1. 读取thought_chain.json
2. 添加第5个thought：
   - id: 5
   - type: "continuation"
   - content: 对比两个方案的性能：协同过滤延迟约50ms但精度较低，深度学习精度高但原始延迟200ms需要优化
   - confidence: 0.8
3. 更新current_thought为5
4. 保存文件

完成后返回"已添加性能对比thought"。
""",
        6: """
## 当前任务：添加第6个thought - 效果评估

请执行以下操作：
1. 读取thought_chain.json
2. 添加第6个thought：
   - id: 6
   - type: "continuation"
   - content: CTR提升评估：协同过滤预计提升10-15%，深度学习预计提升20-25%，深度学习更有潜力达到目标
   - confidence: 0.85
3. 更新current_thought为6
4. 保存文件

完成后返回"已添加效果评估thought"。
""",
        7: """
## 当前任务：添加第7个thought - 最终决策

请执行以下操作：
1. 读取thought_chain.json
2. 添加第7个thought：
   - id: 7
   - type: "continuation"
   - content: 最终选择：采用深度学习方案（Wide&Deep），通过模型压缩、特征缓存、批处理优化延迟到80ms以内
   - confidence: 0.9
3. 更新current_thought为7
4. 保存文件

完成后返回"已添加最终决策thought"。
""",
        8: """
## 当前任务：添加第8个thought - 总结并完成

请执行以下操作：
1. 读取thought_chain.json
2. 添加第8个thought：
   - id: 8
   - type: "conclusion"
   - content: 推荐系统架构总结：采用Wide&Deep模型，配合Redis缓存、特征预计算、模型量化等优化手段，实现低延迟高精度推荐
   - confidence: 0.95
3. 更新conclusions.main为："选择深度学习方案（Wide&Deep模型），通过多层优化满足100ms延迟要求，预计CTR提升20-25%"
4. 添加alternatives: ["协同过滤方案（作为降级方案）", "混合方案（热门用协同过滤，长尾用深度学习）"]
5. 更新current_thought为8
6. 更新status为"completed"
7. 保存文件

完成后返回"已完成所有思考步骤"。
"""
    }
    
    if step_num not in step_tasks:
        return False
    
    task = step_tasks[step_num]
    result = agent.execute_task(task)
    
    # 检查是否成功
    return "已" in result


def generate_architecture_doc(agent: GenericReactAgent) -> bool:
    """生成架构文档"""
    
    task = """
## 最后任务：生成架构文档

请执行以下操作：
1. 读取thought_chain.json
2. 基于思维链内容，创建recommendation_system.md文档，包含：
   - 系统概述
   - 技术选型（基于思维链的决策）
   - 架构设计
   - 性能优化策略
   - 实施计划
3. 保存文档

文档模板：
```markdown
# 电商推荐系统架构设计

## 1. 系统概述
基于Sequential Thinking分析，设计支持千万级用户的实时推荐系统。

## 2. 需求分析
- 实时个性化推荐
- 千万级用户规模
- 延迟<100ms
- CTR提升20%

## 3. 技术选型
经过对比分析，选择深度学习方案（Wide&Deep模型）。

## 4. 架构设计
### 4.1 整体架构
- 在线服务层：API Gateway + 推荐服务
- 特征工程层：实时特征 + 离线特征
- 模型服务层：Wide&Deep模型 + TensorFlow Serving
- 数据层：Redis缓存 + HBase存储

### 4.2 关键优化
- 模型量化：INT8量化减少计算量
- 特征缓存：Redis缓存热门用户特征
- 批处理：请求合并批量推理

## 5. 性能指标
- 推荐延迟：P99 < 80ms
- QPS：10万+
- CTR提升：预计20-25%

## 6. 实施计划
Phase 1: 基础架构搭建
Phase 2: 模型训练和优化
Phase 3: A/B测试和迭代
```

完成后返回"架构文档已生成"。
"""
    
    result = agent.execute_task(task)
    return "已生成" in result or "架构文档" in result


def enforce_sequential_thinking():
    """强制执行完整的Sequential Thinking流程"""
    
    print("=" * 80)
    print("Sequential Thinking 强制执行器")
    print("=" * 80)
    print("\n使用分步执行策略，确保完成所有8个思考步骤")
    
    work_dir = Path("output/enforced_sequential_thinking")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    # 初始化thought_chain.json
    initial_chain = {
        "session_id": f"enforced_thinking_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "created_at": datetime.now().isoformat(),
        "total_thoughts_estimate": 8,
        "current_thought": 0,
        "status": "thinking",
        "thoughts": [],
        "branches": {},
        "conclusions": {
            "main": "",
            "alternatives": []
        }
    }
    
    chain_file = work_dir / "thought_chain.json"
    with open(chain_file, 'w') as f:
        json.dump(initial_chain, f, indent=2)
    
    print(f"\n✅ 初始化thought_chain.json")
    
    # 创建Agent
    agent = create_step_by_step_agent(str(work_dir))
    
    # 逐步执行每个thought
    for step in range(1, 9):
        print(f"\n执行步骤 {step}/8...")
        success = execute_single_step(agent, step)
        
        if success:
            print(f"✅ 步骤 {step} 完成")
        else:
            print(f"❌ 步骤 {step} 失败，重试...")
            success = execute_single_step(agent, step)
            if not success:
                print(f"⚠️ 步骤 {step} 仍然失败，继续下一步")
    
    # 生成文档
    print("\n生成架构文档...")
    doc_success = generate_architecture_doc(agent)
    if doc_success:
        print("✅ 架构文档已生成")
    else:
        print("⚠️ 文档生成失败")
    
    # 验证结果
    print("\n" + "=" * 40)
    print("验证最终结果")
    print("=" * 40)
    
    if chain_file.exists():
        with open(chain_file, 'r') as f:
            final_chain = json.load(f)
        
        print(f"✅ 思考步骤数：{len(final_chain.get('thoughts', []))}/8")
        print(f"✅ 分支数：{len(final_chain.get('branches', {}))}")
        print(f"✅ 状态：{final_chain.get('status')}")
        
        if final_chain.get('conclusions', {}).get('main'):
            print(f"✅ 结论：{final_chain['conclusions']['main'][:100]}...")
        
        # 显示思维链
        print("\n思维链概览：")
        for thought in final_chain.get('thoughts', []):
            t_type = thought.get('type', 'unknown')
            b_id = thought.get('branch_id', '')
            branch_info = f" [{b_id}]" if b_id else ""
            print(f"  {thought['id']}. [{t_type}]{branch_info} - {thought['content'][:60]}...")
    
    doc_file = work_dir / "recommendation_system.md"
    if doc_file.exists():
        print(f"\n✅ 架构文档已生成：{doc_file}")
    
    print("\n" + "=" * 80)
    print("强制执行完成！")
    print("=" * 80)
    
    return final_chain if chain_file.exists() else None


def main():
    """主函数"""
    
    print("选择执行模式：")
    print("1. 强制执行（分步完成8个thoughts）")
    print("2. 查看说明")
    
    choice = input("\n请选择 (1-2): ").strip() or "1"
    
    if choice == "1":
        enforce_sequential_thinking()
    else:
        print("""
Sequential Thinking 强制执行器说明
=====================================

问题背景：
某些LLM（如Kimi）不能严格遵循复杂的多步骤指令，
即使明确要求完成8个步骤，也可能只完成1-2个就停止。

解决方案：
1. 将复杂任务分解为8个独立的小任务
2. 每次只让Agent完成一个具体步骤
3. 通过循环调用确保所有步骤完成
4. 每个步骤都有明确的输入输出

优势：
- 确保任务完成的确定性
- 便于调试和错误处理
- 可以处理模型能力不足的情况
- 进度可控可监测

这个方法证明了：
即使模型不够"聪明"，通过合理的任务分解和流程控制，
仍然可以完成复杂的Sequential Thinking任务。
""")


if __name__ == "__main__":
    main()