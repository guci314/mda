#!/usr/bin/env python3
"""
演示如何使用Workflow知识包

这个文件展示了如何使用知识文件驱动React Agent执行：
1. Sequential Thinking - 结构化思维链
2. Workflow Engine - 工作流引擎
"""

import os
import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


def create_agent_with_knowledge(
    work_dir: str,
    knowledge_type: str = "sequential_thinking"
) -> GenericReactAgent:
    """创建使用知识文件的Agent
    
    Args:
        work_dir: 工作目录
        knowledge_type: 知识类型 ('sequential_thinking' 或 'workflow_engine')
    """
    
    # 在中国使用Gemini需要配置代理
    import httpx
    http_client = httpx.Client(
        proxy='socks5://127.0.0.1:7890',
        timeout=30,
        verify=False
    )
    
    # 根据类型选择知识文件
    if knowledge_type == "sequential_thinking":
        knowledge_files = [
            "knowledge/workflow/sequential_thinking.md",
            "knowledge/workflow/json_notebook_patterns.md",
            "knowledge/workflow/execution_strategies.md"
        ]
        agent_name = "sequential_thinking_agent"
        interface = """Sequential Thinking Agent
        
我使用thought_chain.json实现结构化思考：
- 线性和分支思考
- 置信度评估
- 修正机制
"""
    else:  # workflow_engine
        knowledge_files = [
            "knowledge/workflow/workflow_engine.md",
            "knowledge/workflow/json_notebook_patterns.md",
            "knowledge/workflow/execution_strategies.md"
        ]
        agent_name = "workflow_engine_agent"
        interface = """Workflow Engine Agent
        
我使用workflow_state.json管理工作流：
- 步骤执行
- 条件分支
- 并行处理
- 审批流程
"""
    
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=knowledge_files,
        enable_project_exploration=False,
        llm_model="gemini-2.5-pro",
        llm_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        llm_api_key_env="GEMINI_API_KEY",
        llm_temperature=0,
        http_client=http_client
    )
    
    agent = GenericReactAgent(config, name=agent_name)
    agent.interface = interface
    
    # 最小化的系统提示 - 完全依赖知识文件
    agent._system_prompt = (agent._system_prompt or "") + """
你的知识文件包含了完整的执行指南。请严格遵循知识文件中的模式和最佳实践。
"""
    
    return agent


def demo_sequential_thinking():
    """演示Sequential Thinking"""
    print("=" * 80)
    print("Sequential Thinking 演示（知识驱动）")
    print("=" * 80)
    
    work_dir = Path("output/demo_sequential_knowledge")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_agent_with_knowledge(
        str(work_dir), 
        knowledge_type="sequential_thinking"
    )
    
    task = """
使用Sequential Thinking分析：如何构建一个高性能的搜索引擎？

要求：
1. 至少8个思考步骤
2. 探索至少2个技术方案（如：倒排索引 vs 向量搜索）
3. 评估每个方案的优缺点
4. 给出最终建议
5. 生成search_engine_design.md文档
"""
    
    print("\n执行任务...")
    result = agent.execute_task(task)
    
    # 检查结果
    thought_file = work_dir / "thought_chain.json"
    if thought_file.exists():
        with open(thought_file, 'r') as f:
            thoughts = json.load(f)
        
        print(f"\n✅ 完成 {len(thoughts.get('thoughts', []))} 个思考步骤")
        print(f"✅ 状态: {thoughts.get('status')}")
        
        if thoughts.get('branches'):
            print(f"✅ 探索了 {len(thoughts['branches'])} 个分支")
        
        if thoughts.get('conclusions', {}).get('main'):
            print(f"✅ 结论: {thoughts['conclusions']['main'][:100]}...")


def demo_workflow_engine():
    """演示Workflow Engine"""
    print("\n" + "=" * 80)
    print("Workflow Engine 演示（知识驱动）")
    print("=" * 80)
    
    work_dir = Path("output/demo_workflow_knowledge")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_agent_with_knowledge(
        str(work_dir),
        knowledge_type="workflow_engine"
    )
    
    task = """
创建一个机器学习模型训练工作流：

步骤：
1. **数据准备** (action) - 加载和预处理数据
2. **数据验证** (condition) - 检查数据质量
   - 如果质量合格 → 继续
   - 如果质量不合格 → 数据清洗
3. **数据清洗** (action) - 可选步骤
4. **特征工程** (parallel)
   - 特征提取
   - 特征选择
   - 特征编码
5. **模型训练** (parallel)
   - 训练随机森林
   - 训练XGBoost
   - 训练神经网络
6. **模型评估** (action) - 比较模型性能
7. **最佳模型选择** (condition)
   - 如果满足阈值 → 部署
   - 如果不满足 → 调参重训
8. **模型部署** (approval) - 需要审批
9. **监控设置** (action) - 配置监控

要求：
- 记录完整的执行流程
- 生成ml_pipeline_report.md
"""
    
    print("\n执行任务...")
    result = agent.execute_task(task)
    
    # 检查结果
    workflow_file = work_dir / "workflow_state.json"
    if workflow_file.exists():
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print(f"\n✅ 工作流ID: {workflow.get('workflow_id')}")
        print(f"✅ 状态: {workflow.get('status')}")
        
        completed = sum(1 for s in workflow.get('steps', []) 
                       if s['status'] == 'completed')
        total = len(workflow.get('steps', []))
        print(f"✅ 完成步骤: {completed}/{total}")
        
        if workflow.get('parallel_groups'):
            print(f"✅ 并行组: {len(workflow['parallel_groups'])}")


def compare_approaches():
    """对比两种方法"""
    print("\n" + "=" * 80)
    print("知识驱动 vs 硬编码对比")
    print("=" * 80)
    
    comparison = """
| 特性 | 硬编码方法 | 知识驱动方法 |
|-----|-----------|-------------|
| **代码量** | 200+ 行系统提示 | 10 行引用知识文件 |
| **可维护性** | 需要修改代码 | 只需更新知识文件 |
| **可重用性** | 每个场景都要重写 | 知识文件可复用 |
| **扩展性** | 修改困难 | 易于扩展 |
| **版本控制** | 代码和逻辑混合 | 知识独立管理 |
| **调试** | 困难 | 清晰的知识追踪 |

### 结论
知识驱动方法的优势：
1. ✅ 更清晰的关注点分离
2. ✅ 更好的可维护性
3. ✅ 更强的可重用性
4. ✅ 符合"知识即程序"理念
"""
    print(comparison)


def main():
    """主函数"""
    print("选择演示：")
    print("1. Sequential Thinking（知识驱动）")
    print("2. Workflow Engine（知识驱动）")
    print("3. 对比分析")
    print("4. 运行所有演示")
    
    # 默认运行所有
    choice = "4"
    
    if choice == "1":
        demo_sequential_thinking()
    elif choice == "2":
        demo_workflow_engine()
    elif choice == "3":
        compare_approaches()
    else:
        demo_sequential_thinking()
        demo_workflow_engine()
        compare_approaches()
    
    print("\n" + "=" * 80)
    print("演示完成！")
    print("知识文件位置：knowledge/workflow/")
    print("=" * 80)


if __name__ == "__main__":
    main()