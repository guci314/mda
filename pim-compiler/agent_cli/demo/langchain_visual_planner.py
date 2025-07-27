#!/usr/bin/env python3
"""
LangChain Plan-and-Execute Agent 可视化演示

增强版本，包含：
1. 实时执行可视化
2. Mermaid 图表生成
3. 进度条显示
4. 结果可视化报告
"""

import sys
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
from datetime import datetime
import time
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.panel import Panel
from rich.tree import Tree
from rich.markdown import Markdown
from rich.syntax import Syntax

# 添加 pim-compiler 到 Python 路径
pim_compiler_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(pim_compiler_path))

# 加载环境变量
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

# 复用之前的导入
from langchain_plan_execute_demo import PlanAndExecuteAgent, ExecutionPlan, Step
from agent_cli.core import LLMConfig

# Rich console for beautiful output
console = Console()


class VisualPlanAndExecuteAgent(PlanAndExecuteAgent):
    """带可视化的 Plan-and-Execute Agent"""
    
    def __init__(self, llm_config: LLMConfig):
        super().__init__(llm_config)
        self.console = Console()
        
    def visualize_plan(self, plan: ExecutionPlan) -> str:
        """生成计划的 Mermaid 图表"""
        mermaid = ["graph TD"]
        mermaid.append(f'    Start["{plan.task}"]')
        
        for i, step in enumerate(plan.steps):
            step_id = f"Step{step.step_number}"
            # 转义特殊字符
            desc = step.description.replace('"', "'")
            mermaid.append(f'    {step_id}["{step.step_number}. {desc}"]')
            
            if i == 0:
                mermaid.append(f"    Start --> {step_id}")
            else:
                prev_id = f"Step{plan.steps[i-1].step_number}"
                mermaid.append(f"    {prev_id} --> {step_id}")
            
            # 添加工具信息
            if step.tools_needed:
                tools_id = f"Tools{step.step_number}"
                tools_list = ", ".join(step.tools_needed)
                mermaid.append(f'    {tools_id}{{"🔧 {tools_list}"}}')
                mermaid.append(f"    {step_id} -.-> {tools_id}")
        
        if plan.steps:
            last_step = f"Step{plan.steps[-1].step_number}"
            mermaid.append(f'    {last_step} --> End[✅ 完成]')
        
        return "\n".join(mermaid)
    
    def display_plan(self, plan: ExecutionPlan):
        """美化显示执行计划"""
        # 创建表格
        table = Table(title="📋 执行计划", show_header=True, header_style="bold magenta")
        table.add_column("步骤", style="cyan", width=6)
        table.add_column("描述", style="white")
        table.add_column("工具", style="yellow")
        table.add_column("预期结果", style="green")
        
        for step in plan.steps:
            tools = ", ".join(step.tools_needed) if step.tools_needed else "自动选择"
            table.add_row(
                str(step.step_number),
                step.description,
                tools,
                step.expected_outcome
            )
        
        self.console.print(table)
        
        # 生成并显示 Mermaid 图
        mermaid_code = self.visualize_plan(plan)
        self.console.print("\n📊 执行流程图 (Mermaid):")
        self.console.print(Panel(Syntax(mermaid_code, "mermaid", theme="monokai", line_numbers=True)))
        
        # 保存 Mermaid 图到文件
        mermaid_file = f"plan_flow_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mmd"
        with open(mermaid_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)
        self.console.print(f"\n💾 流程图已保存到: {mermaid_file}")
    
    def execute_task_with_visualization(self, task: str) -> Dict[str, Any]:
        """带可视化的任务执行"""
        # 显示任务
        self.console.print(Panel(task, title="🎯 任务", border_style="blue"))
        
        # 创建计划
        with self.console.status("[bold green]创建执行计划...") as status:
            plan = self.planner(task)
            time.sleep(1)  # 模拟处理时间
        
        # 显示计划
        self.display_plan(plan)
        
        # 询问是否继续
        if input("\n按回车键开始执行 (或输入 'q' 退出): ").lower() == 'q':
            return {"status": "cancelled"}
        
        # 执行计划
        results = []
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=self.console
        ) as progress:
            
            task_progress = progress.add_task(
                f"[cyan]执行任务...", 
                total=len(plan.steps)
            )
            
            for i, step in enumerate(plan.steps):
                # 更新进度描述
                progress.update(
                    task_progress, 
                    description=f"[cyan]步骤 {step.step_number}: {step.description[:40]}..."
                )
                
                # 显示当前步骤
                self.console.print(f"\n{'─'*60}")
                self.console.print(f"[bold yellow]▶ 执行步骤 {step.step_number}:[/bold yellow] {step.description}")
                
                try:
                    # 执行步骤
                    step_input = {
                        "input": step.description,
                        "step_number": step.step_number,
                        "description": step.description,
                        "tools_needed": ", ".join(step.tools_needed) if step.tools_needed else "任意合适的工具",
                        "expected_outcome": step.expected_outcome
                    }
                    
                    # 模拟执行（实际执行）
                    with self.console.status(f"[bold green]执行中...") as status:
                        result = self.executor.invoke(step_input)
                        time.sleep(0.5)  # 模拟处理
                    
                    # 更新状态
                    step.status = "completed"
                    step.result = result.get("output", "")
                    
                    # 显示结果
                    self.console.print(f"[green]✅ 步骤 {step.step_number} 完成[/green]")
                    
                    # 显示结果预览
                    result_preview = step.result[:200] + "..." if len(step.result) > 200 else step.result
                    self.console.print(Panel(result_preview, title="结果", border_style="green"))
                    
                    results.append({
                        "step": step.step_number,
                        "status": "success",
                        "result": step.result
                    })
                    
                except Exception as e:
                    step.status = "failed"
                    step.result = str(e)
                    
                    self.console.print(f"[red]❌ 步骤 {step.step_number} 失败: {e}[/red]")
                    
                    results.append({
                        "step": step.step_number,
                        "status": "failed",
                        "error": str(e)
                    })
                
                # 更新进度条
                progress.update(task_progress, advance=1)
        
        # 生成执行报告
        self.generate_report(plan, results)
        
        return {
            "task": task,
            "plan": plan.to_dict(),
            "results": results
        }
    
    def generate_report(self, plan: ExecutionPlan, results: List[Dict]):
        """生成执行报告"""
        # 创建报告树
        tree = Tree("📊 执行报告")
        
        # 任务信息
        task_branch = tree.add("🎯 任务信息")
        task_branch.add(f"任务: {plan.task}")
        task_branch.add(f"创建时间: {plan.created_at}")
        task_branch.add(f"总步骤数: {len(plan.steps)}")
        
        # 执行结果
        result_branch = tree.add("📈 执行结果")
        
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        
        result_branch.add(f"[green]✅ 成功: {success_count}[/green]")
        result_branch.add(f"[red]❌ 失败: {failed_count}[/red]")
        
        # 详细步骤
        steps_branch = tree.add("📝 步骤详情")
        for step in plan.steps:
            step_info = f"步骤 {step.step_number}: {step.description}"
            if step.status == "completed":
                step_node = steps_branch.add(f"[green]✅ {step_info}[/green]")
            elif step.status == "failed":
                step_node = steps_branch.add(f"[red]❌ {step_info}[/red]")
            else:
                step_node = steps_branch.add(f"[yellow]⏸ {step_info}[/yellow]")
            
            if step.result:
                result_preview = step.result[:100] + "..." if len(step.result) > 100 else step.result
                step_node.add(f"[dim]{result_preview}[/dim]")
        
        self.console.print("\n")
        self.console.print(tree)
        
        # 生成 Markdown 报告
        self.generate_markdown_report(plan, results)
    
    def generate_markdown_report(self, plan: ExecutionPlan, results: List[Dict]):
        """生成 Markdown 格式的报告"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = f"execution_report_{timestamp}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# 执行报告\n\n")
            f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"## 任务信息\n\n")
            f.write(f"- **任务描述**: {plan.task}\n")
            f.write(f"- **创建时间**: {plan.created_at}\n")
            f.write(f"- **总步骤数**: {len(plan.steps)}\n\n")
            
            f.write(f"## 执行流程图\n\n")
            f.write("```mermaid\n")
            f.write(self.visualize_plan(plan))
            f.write("\n```\n\n")
            
            f.write(f"## 执行结果\n\n")
            
            # 统计
            success_count = sum(1 for r in results if r["status"] == "success")
            failed_count = sum(1 for r in results if r["status"] == "failed")
            
            f.write(f"- ✅ 成功步骤: {success_count}\n")
            f.write(f"- ❌ 失败步骤: {failed_count}\n")
            f.write(f"- 成功率: {success_count/len(plan.steps)*100:.1f}%\n\n")
            
            f.write(f"## 步骤详情\n\n")
            
            for step in plan.steps:
                status_icon = "✅" if step.status == "completed" else "❌" if step.status == "failed" else "⏸"
                f.write(f"### {status_icon} 步骤 {step.step_number}: {step.description}\n\n")
                
                f.write(f"- **状态**: {step.status}\n")
                f.write(f"- **工具**: {', '.join(step.tools_needed) if step.tools_needed else '自动选择'}\n")
                f.write(f"- **预期结果**: {step.expected_outcome}\n")
                
                if step.result:
                    f.write(f"\n**实际结果**:\n\n")
                    f.write(f"```\n{step.result}\n```\n\n")
        
        self.console.print(f"\n📄 Markdown 报告已保存到: {report_file}")


def main():
    """主函数 - 可视化演示"""
    os.environ['LLM_PROVIDER'] = 'deepseek'
    config = LLMConfig.from_env('deepseek')
    
    console.print("[bold magenta]🎨 LangChain Plan-and-Execute Agent 可视化演示[/bold magenta]")
    console.print("=" * 60)
    
    # 创建可视化 Agent
    agent = VisualPlanAndExecuteAgent(llm_config=config)
    
    # 演示任务
    demo_tasks = [
        "创建一个简单的计算器程序 calculator.py，支持加减乘除运算",
        "分析 agent_cli/core.py 的代码结构并生成文档",
        "创建一个 Python 脚本来统计当前目录下所有 .py 文件的代码行数"
    ]
    
    console.print("\n[bold cyan]演示任务:[/bold cyan]")
    for i, task in enumerate(demo_tasks, 1):
        console.print(f"  {i}. {task}")
    
    choice = input("\n选择任务 (1-3) 或输入自定义任务: ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(demo_tasks):
        task = demo_tasks[int(choice) - 1]
    else:
        task = choice
    
    # 执行任务
    try:
        result = agent.execute_task_with_visualization(task)
        
        # 保存完整结果
        result_file = f"visual_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        console.print(f"\n💾 完整结果已保存到: {result_file}")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  执行被用户中断[/yellow]")
    except Exception as e:
        console.print(f"\n[red]❌ 执行失败: {e}[/red]")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()