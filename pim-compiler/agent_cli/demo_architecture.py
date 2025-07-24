#!/usr/bin/env python3
"""
演示 Task/Step/Action 三层架构
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
import json

# 加载 .env 文件
load_dotenv()

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent_cli.core import Task, Step, Action, ActionType, StepStatus, TaskStatus, LLMConfig, AgentCLI


def print_task_structure(task: Task):
    """打印任务的三层结构"""
    print("\n" + "="*70)
    print(f"任务结构展示 - Task/Step/Action 三层架构")
    print("="*70)
    
    print(f"\n📋 Task: {task.description}")
    print(f"   状态: {task.status.value}")
    print(f"   目标: {task.goal}")
    
    for i, step in enumerate(task.steps):
        print(f"\n   📌 Step {i+1}: {step.name}")
        print(f"      状态: {step.status.value}")
        print(f"      迭代次数: {step.iteration_count}/{step.max_iterations}")
        
        if step.actions:
            for j, action in enumerate(step.actions):
                print(f"\n      🔧 Action {j+1}: {action.type.value}")
                print(f"         描述: {action.description}")
                if action.duration:
                    print(f"         耗时: {action.duration:.2f} 秒")
                print(f"         成功: {'✅' if action.is_successful else '❌'}")
                if action.error:
                    print(f"         错误: {action.error}")


def demo_architecture():
    """演示三层架构的工作流程"""
    print("=== Agent CLI 三层架构演示 ===")
    
    try:
        # 创建配置
        config = LLMConfig.from_env("deepseek")
        print(f"✅ 使用 LLM: {config.model}")
        
        # 创建CLI
        cli = AgentCLI(llm_config=config)
        
        # 定义一个简单任务
        task_description = "分析一个字符串并计算其中的元音字母数量"
        print(f"\n📋 任务: {task_description}")
        
        # 执行任务
        print("\n开始执行...")
        success, message = cli.execute_task(task_description)
        
        # 显示三层架构
        if hasattr(cli, 'current_task'):
            print_task_structure(cli.current_task)
        
        # 显示执行摘要
        summary = cli.get_execution_summary()
        print(f"\n\n📊 执行摘要:")
        print(f"   任务状态: {summary['status']}")
        print(f"   总步骤数: {summary['total_steps']}")
        print(f"   完成步骤: {summary['completed_steps']}")
        print(f"   总动作数: {summary['total_actions']}")
        if summary.get('duration'):
            print(f"   总耗时: {summary['duration']:.2f} 秒")
        
        print(f"\n   动作类型分布:")
        for action_type, count in summary['action_types'].items():
            if count > 0:
                print(f"      {action_type}: {count} 次")
        
        # 显示架构优势
        print(f"\n\n🎯 三层架构的优势:")
        print("   1. Task 层: 管理整个任务的生命周期和上下文")
        print("   2. Step 层: 组织逻辑步骤，控制迭代和进度")
        print("   3. Action 层: 执行具体操作，记录详细信息")
        print("\n   ✨ 清晰的层次结构让代码更易理解和维护")
        print("   ✨ 每层都有明确的职责和状态管理")
        print("   ✨ 便于追踪执行过程和调试问题")
        
    except Exception as e:
        print(f"\n❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    demo_architecture()