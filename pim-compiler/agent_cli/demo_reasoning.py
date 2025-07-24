#!/usr/bin/env python3
"""
演示符号主义推理 vs 连接主义推理 vs 混合策略
"""
import sys
import time
from pathlib import Path
from dotenv import load_dotenv
import json

# 加载 .env 文件
load_dotenv()

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_cli.core import Task, Step, Action, ActionType, LLMConfig, AgentCLI


class SymbolicAgentCLI(AgentCLI):
    """纯符号主义推理的 Agent CLI (作为对比)"""
    
    def _decide_action(self, thought: str, step: str) -> Action:
        """纯符号主义决策 - 基于硬编码规则"""
        return self._decide_action_symbolic(thought, step)
    
    def _create_generate_action(self, step: str) -> Action:
        """创建生成动作 - 简单的模板方法"""
        return Action(
            type=ActionType.GENERATE,
            description=f"生成: {step}",
            params={
                "prompt": f"基于当前上下文，{step}。任务背景：{self.context.get('task', '')}",
                "context": self.context
            }
        )
    
    def plan(self, task_description: str) -> Task:
        """制定任务执行计划 - 基于规则的简单方法"""
        steps = self._get_default_steps(task_description)
        
        # 创建任务对象
        new_task = Task(
            description=task_description,
            goal=task_description
        )
        
        # 将步骤添加到任务
        for step_name in steps:
            step = Step(
                name=step_name,
                description=step_name
            )
            new_task.add_step(step)
        
        return new_task


def compare_reasoning_approaches():
    """比较不同的推理方法"""
    print("="*70)
    print("符号主义 vs 连接主义 vs 混合策略推理比较")
    print("="*70)
    
    # 测试任务
    test_task = "将用户管理PIM模型转换为FastAPI的PSM代码"
    
    # 1. 测试符号主义方法
    print("\n1️⃣ 符号主义推理方法（基于规则）")
    print("-" * 50)
    try:
        config = LLMConfig.from_env("deepseek")
        symbolic_cli = SymbolicAgentCLI(llm_config=config)
        
        # 显示计划阶段
        print("📋 计划阶段：使用预定义规则")
        symbolic_task = symbolic_cli.plan(test_task)
        print(f"生成步骤数：{len(symbolic_task.steps)}")
        for i, step in enumerate(symbolic_task.steps):
            print(f"  步骤 {i+1}: {step.name}")
        
        # 模拟决策
        print("\n🎯 决策示例：")
        test_thought = "需要读取PIM文件来了解模型结构"
        test_step = "读取 PIM 文件内容"
        action = symbolic_cli._decide_action(test_thought, test_step)
        print(f"  输入步骤: {test_step}")
        print(f"  决策动作: {action.type.value}")
        print(f"  动作描述: {action.description}")
        
    except Exception as e:
        print(f"❌ 符号主义方法失败: {e}")
    
    # 2. 测试连接主义方法
    print("\n\n2️⃣ 连接主义推理方法（基于LLM）")
    print("-" * 50)
    try:
        config = LLMConfig.from_env("deepseek")
        connectionist_cli = AgentCLI(llm_config=config)
        
        # 显示计划阶段
        print("📋 计划阶段：使用LLM智能分析")
        connectionist_task = connectionist_cli.plan(test_task)
        print(f"生成步骤数：{len(connectionist_task.steps)}")
        for i, step in enumerate(connectionist_task.steps):
            print(f"  步骤 {i+1}: {step.name}")
        
        # 设置上下文
        connectionist_cli.context = {"task": test_task}
        
        # 模拟决策
        print("\n🎯 决策示例：")
        test_thought = "需要读取PIM文件来了解模型结构，特别是实体定义和业务规则"
        test_step = "分析PIM模型结构"
        action = connectionist_cli._decide_action(test_thought, test_step)
        print(f"  输入步骤: {test_step}")
        print(f"  决策动作: {action.type.value}")
        print(f"  动作描述: {action.description}")
        if action.params:
            print(f"  动作参数: {json.dumps(action.params, indent=4, ensure_ascii=False)}")
        
    except Exception as e:
        print(f"❌ 连接主义方法失败: {e}")
    
    # 3. 混合策略说明
    print("\n\n3️⃣ 混合策略推理（LLM + 规则回退）")
    print("-" * 50)
    print("✨ 实现特点：")
    print("  1. 首先尝试使用LLM进行智能决策")
    print("  2. 如果LLM响应格式错误或超时，自动回退到符号规则")
    print("  3. 结合了连接主义的灵活性和符号主义的可靠性")
    print("\n📌 适用场景：")
    print("  - 生产环境：需要高可靠性")
    print("  - 成本控制：减少不必要的LLM调用")
    print("  - 降级处理：LLM服务不可用时仍能工作")
    
    # 4. 对比总结
    print("\n\n📊 方法对比总结")
    print("="*70)
    print("┌─────────────┬──────────────────────┬──────────────────────┐")
    print("│ 特性        │ 符号主义             │ 连接主义             │")
    print("├─────────────┼──────────────────────┼──────────────────────┤")
    print("│ 灵活性      │ 低（规则固定）       │ 高（动态适应）       │")
    print("│ 可解释性    │ 高（规则明确）       │ 低（黑箱决策）       │")
    print("│ 维护成本    │ 高（需更新规则）     │ 低（自动适应）       │")
    print("│ 执行速度    │ 快（无需调用LLM）    │ 慢（需要LLM推理）    │")
    print("│ 准确性      │ 依赖规则完备性       │ 依赖LLM能力          │")
    print("│ 成本        │ 低（无API费用）      │ 高（API调用费用）    │")
    print("└─────────────┴──────────────────────┴──────────────────────┘")
    
    print("\n🎯 混合策略优势：")
    print("  ✅ 兼具两种方法的优点")
    print("  ✅ 提供优雅的降级机制")
    print("  ✅ 平衡性能和智能")
    print("  ✅ 适合生产环境部署")


def test_hybrid_strategy():
    """测试混合策略的实际效果"""
    print("\n\n" + "="*70)
    print("混合策略实战测试")
    print("="*70)
    
    try:
        config = LLMConfig.from_env("deepseek")
        cli = AgentCLI(llm_config=config)
        
        # 测试任务
        task = "分析README文件并生成项目摘要"
        
        print(f"\n📋 执行任务: {task}")
        print("\n执行过程将展示：")
        print("- LLM智能规划任务步骤")
        print("- LLM决策每个动作")
        print("- 如遇错误自动回退到规则")
        
        # 执行任务
        start_time = time.time()
        success, message = cli.execute_task(task)
        duration = time.time() - start_time
        
        print(f"\n✅ 执行结果: {'成功' if success else '失败'}")
        print(f"⏱️  执行时间: {duration:.1f} 秒")
        
        # 显示执行统计
        summary = cli.get_execution_summary()
        print(f"\n📊 执行统计:")
        print(f"   总步骤数: {summary['total_steps']}")
        print(f"   完成步骤: {summary['completed_steps']}")
        print(f"   总动作数: {summary['total_actions']}")
        
        print(f"\n   动作类型分布:")
        for action_type, count in summary['action_types'].items():
            if count > 0:
                print(f"      {action_type}: {count} 次")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # 比较不同推理方法
    compare_reasoning_approaches()
    
    # 测试混合策略
    test_hybrid_strategy()
    
    print("\n\n💡 提示：")
    print("- 符号主义适合规则明确、模式固定的场景")
    print("- 连接主义适合复杂、多变、需要创造性的场景")
    print("- 混合策略是生产环境的最佳选择")