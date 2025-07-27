#!/usr/bin/env python3
"""
交互式 LangChain Plan-and-Execute 演示

让用户可以一步步查看执行过程
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime

# 添加 pim-compiler 到 Python 路径
pim_compiler_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(pim_compiler_path))

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# 设置 LLM
os.environ['LLM_PROVIDER'] = 'deepseek'

from langchain_plan_execute_demo import PlanAndExecuteAgent, ExecutionPlan, Step
from agent_cli.core import LLMConfig


class InteractivePlanAndExecuteAgent(PlanAndExecuteAgent):
    """交互式 Plan-and-Execute Agent"""
    
    def __init__(self, llm_config: LLMConfig, auto_execute: bool = False):
        super().__init__(llm_config)
        self.auto_execute = auto_execute
        
    def execute_task_interactive(self, task: str) -> Dict[str, Any]:
        """交互式执行任务"""
        print(f"\n{'='*60}")
        print(f"🎯 任务: {task}")
        print(f"{'='*60}\n")
        
        # 1. 创建计划
        print("📋 第一步：创建执行计划...")
        input("按回车继续...")
        
        plan = self.planner(task)
        
        print(f"\n✅ 计划创建完成！共 {len(plan.steps)} 个步骤：\n")
        
        # 显示详细计划
        for i, step in enumerate(plan.steps):
            print(f"{'─'*50}")
            print(f"步骤 {step.step_number}: {step.description}")
            print(f"需要工具: {', '.join(step.tools_needed) if step.tools_needed else '自动选择'}")
            print(f"预期结果: {step.expected_outcome}")
            print(f"{'─'*50}\n")
        
        # 询问是否继续
        response = input("是否开始执行计划？(y/n): ")
        if response.lower() != 'y':
            return {"status": "cancelled", "plan": plan.to_dict()}
        
        # 2. 执行计划
        print(f"\n{'='*60}")
        print("🚀 第二步：执行计划")
        print(f"{'='*60}\n")
        
        results = []
        
        for step in plan.steps:
            print(f"\n{'─'*50}")
            print(f"▶ 准备执行步骤 {step.step_number}: {step.description}")
            print(f"{'─'*50}")
            
            if not self.auto_execute:
                response = input("\n执行这个步骤？(y/n/s跳过): ")
                if response.lower() == 'n':
                    break
                elif response.lower() == 's':
                    step.status = "skipped"
                    results.append({
                        "step": step.step_number,
                        "status": "skipped"
                    })
                    continue
            
            try:
                print("\n执行中...")
                
                # 构建执行输入
                step_input = {
                    "input": step.description
                }
                
                # 执行步骤
                result = self.executor.invoke(step_input)
                
                # 更新步骤状态
                step.status = "completed"
                step.result = result.get("output", "")
                
                print(f"\n✅ 步骤 {step.step_number} 完成！")
                print(f"\n结果预览:")
                print("-" * 40)
                result_preview = step.result[:300] + "..." if len(step.result) > 300 else step.result
                print(result_preview)
                print("-" * 40)
                
                results.append({
                    "step": step.step_number,
                    "status": "success",
                    "result": step.result
                })
                
            except Exception as e:
                step.status = "failed"
                step.result = str(e)
                
                print(f"\n❌ 步骤 {step.step_number} 失败: {e}")
                
                results.append({
                    "step": step.step_number,
                    "status": "failed",
                    "error": str(e)
                })
                
                if not self.auto_execute:
                    response = input("\n是否继续执行后续步骤？(y/n): ")
                    if response.lower() != 'y':
                        break
        
        # 3. 总结
        print(f"\n{'='*60}")
        print("📊 执行总结")
        print(f"{'='*60}\n")
        
        completed = sum(1 for s in plan.steps if s.status == "completed")
        failed = sum(1 for s in plan.steps if s.status == "failed")
        skipped = sum(1 for s in plan.steps if s.status == "skipped")
        
        print(f"总步骤数: {len(plan.steps)}")
        print(f"✅ 完成: {completed}")
        print(f"❌ 失败: {failed}")
        print(f"⏭️  跳过: {skipped}")
        
        # 保存结果
        result_data = {
            "task": task,
            "plan": plan.to_dict(),
            "results": results,
            "summary": {
                "total_steps": len(plan.steps),
                "completed": completed,
                "failed": failed,
                "skipped": skipped
            }
        }
        
        # 询问是否保存
        if input("\n是否保存执行结果？(y/n): ").lower() == 'y':
            filename = f"interactive_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(result_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 结果已保存到: {filename}")
        
        return result_data


def main():
    """主函数"""
    print("🤖 交互式 LangChain Plan-and-Execute Agent")
    print("=" * 60)
    
    # 创建配置
    config = LLMConfig.from_env('deepseek')
    print(f"使用 LLM: {config.provider} - {config.model}\n")
    
    # 演示任务
    demo_tasks = [
        "创建一个简单的 Python 函数来计算斐波那契数列",
        "分析当前目录的文件结构并生成报告",
        "创建一个待办事项管理脚本 todo.py",
        "读取并总结 README_langchain_demo.md 的内容"
    ]
    
    print("预设任务:")
    for i, task in enumerate(demo_tasks, 1):
        print(f"{i}. {task}")
    
    print("\n选择一个任务编号，或输入自定义任务")
    choice = input("你的选择: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(demo_tasks):
        task = demo_tasks[int(choice) - 1]
    else:
        task = choice
    
    # 询问执行模式
    auto_mode = input("\n使用自动执行模式？(y/n，默认n): ").lower() == 'y'
    
    # 创建 Agent
    try:
        agent = InteractivePlanAndExecuteAgent(
            llm_config=config,
            auto_execute=auto_mode
        )
        
        # 执行任务
        result = agent.execute_task_interactive(task)
        
        print("\n✨ 演示完成！")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  执行被用户中断")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()