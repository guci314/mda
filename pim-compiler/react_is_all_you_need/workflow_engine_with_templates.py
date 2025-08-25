#!/usr/bin/env python3
"""
工作流引擎模板化演示

这个脚本展示了如何使用预定义的工作流模板来执行工作流。
模板提供了工作流的类型定义（显式表达），而JSON状态记录实例执行（显式表达）。

核心理念：
- 类型层（模板）：Markdown格式，人类可读，版本控制
- 实例层（状态）：JSON格式，机器处理，实时更新
- 无需额外代码：纯React Agent + 知识文件
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


def create_workflow_agent(work_dir: str) -> GenericReactAgent:
    """创建支持模板的工作流引擎Agent"""
    
    # 使用OpenRouter访问Gemini-2.5-pro
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[
            "knowledge/workflow/workflow_engine.md",  # 包含模板加载指导
            "knowledge/workflow/json_notebook_patterns.md",
            "knowledge/workflow/execution_strategies.md"
        ],
        enable_project_exploration=False,
        # llm_model="google/gemini-2.5-pro",
        # llm_base_url="https://openrouter.ai/api/v1",
        # llm_api_key_env="OPENROUTER_API_KEY",
        # llm_temperature=0
        
        llm_model="deepseek-chat",
        llm_base_url="https://api.deepseek.com/v1",
        llm_api_key_env="DEEPSEEK_API_KEY",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(config, name="workflow_engine_agent")
    
    agent.interface = """模板化工作流引擎Agent
    
我能够：
1. 从模板文件加载工作流定义
2. 用参数实例化模板
3. 在workflow_state.json中维护模板引用
4. 执行模板定义的工作流步骤
"""
    
    agent._system_prompt = (agent._system_prompt or "") + """

## 模板化工作流执行

你的知识文件已包含模板加载和执行的完整指导。

关键要求：
1. 当任务提到"执行xxx模板"时，使用read_file读取模板
2. 在workflow_state.json中记录template_ref和template_id
3. 用提供的参数值实例化模板
4. 按模板定义执行工作流
5. 支持运行时覆盖模板内容
"""
    
    return agent


def demo_template_deployment():
    """演示：使用部署模板执行工作流"""
    
    print("=" * 80)
    print("模板化工作流演示：软件部署")
    print("=" * 80)
    
    work_dir = Path("output/workflow_template_deploy")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_workflow_agent(str(work_dir))
    
    # 使用绝对路径
    template_path = Path(__file__).parent / "knowledge/workflow/templates/deployment.md"
    
    task = f"""
执行 {template_path} 模板

## 参数
- environment: production
- servers: ["app-server-1", "app-server-2", "app-server-3"]
- version: v2.0.0
- skip_tests: false

## 执行要求
1. 读取并解析模板文件
2. 在workflow_state.json中记录template_ref
3. 用参数实例化工作流
4. 模拟执行所有步骤
5. 生成deployment_report.md

## 成功条件
✅ 模板成功加载
✅ 参数正确应用
✅ workflow_state.json包含template_ref
✅ 所有步骤执行完成
✅ 生成部署报告
"""
    
    print("\n任务：使用部署模板执行工作流")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    # 验证模板引用
    workflow_file = work_dir / "workflow_state.json"
    if workflow_file.exists():
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print("\n模板执行结果：")
        print("-" * 40)
        print(f"模板引用: {workflow.get('template_ref', 'N/A')}")
        print(f"模板ID: {workflow.get('template_id', 'N/A')}")
        print(f"实例ID: {workflow.get('instance_id', 'N/A')}")
        
        if 'parameters' in workflow:
            print("\n应用的参数：")
            for key, value in workflow['parameters'].items():
                print(f"  {key}: {value}")
        
        if 'steps' in workflow:
            print("\n步骤执行：")
            for step in workflow['steps']:
                status_icon = "✅" if step.get('status') == 'completed' else "⏳"
                print(f"  {status_icon} {step.get('name', 'Unknown')}")
    
    return workflow if workflow_file.exists() else None


def demo_template_with_override():
    """演示：使用模板但覆盖部分内容"""
    
    print("\n" + "=" * 80)
    print("模板化工作流演示：自定义部署（覆盖模板）")
    print("=" * 80)
    
    work_dir = Path("output/workflow_template_custom")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_workflow_agent(str(work_dir))
    
    # 使用绝对路径
    template_path = Path(__file__).parent / "knowledge/workflow/templates/deployment.md"
    
    task = f"""
基于 {template_path} 模板执行工作流

## 参数
- environment: staging
- servers: ["staging-server-1"]
- version: v1.9.0-rc1

## 覆盖规则
- 跳过步骤1和步骤2（代码检查和单元测试）- 已在CI中完成
- 在步骤8（健康检查）后增加"性能基准测试"步骤

## 执行要求
1. 加载基础模板
2. 应用覆盖规则
3. 记录覆盖内容到variables.overrides
4. 执行修改后的工作流

## 成功条件
✅ 模板加载成功
✅ 覆盖规则应用成功
✅ 跳过了指定步骤
✅ 增加了新步骤
"""
    
    print("\n任务：使用模板但自定义部分步骤")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    # 检查覆盖记录
    workflow_file = work_dir / "workflow_state.json"
    if workflow_file.exists():
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print("\n自定义执行结果：")
        print("-" * 40)
        
        if 'variables' in workflow and 'overrides' in workflow['variables']:
            print("应用的覆盖：")
            overrides = workflow['variables']['overrides']
            if isinstance(overrides, dict):
                for key, value in overrides.items():
                    print(f"  {key}: {value}")
            else:
                print(f"  {overrides}")
    
    return workflow if workflow_file.exists() else None


def demo_template_data_pipeline():
    """演示：使用数据管道模板"""
    
    print("\n" + "=" * 80)
    print("模板化工作流演示：ETL数据管道")
    print("=" * 80)
    
    work_dir = Path("output/workflow_template_etl")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_workflow_agent(str(work_dir))
    
    # 使用绝对路径
    template_path = Path(__file__).parent / "knowledge/workflow/templates/data_pipeline.md"
    
    task = f"""
执行 {template_path} 模板

## 参数
- sources: ["mysql", "mongodb", "redis"]
- target: "data_warehouse"
- batch_size: 5000
- error_threshold: 0.03
- processing_mode: "batch"

## 执行要求
1. 加载数据管道模板
2. 模拟从多个数据源提取数据
3. 执行数据质量检查
4. 模拟数据转换和加载
5. 生成ETL报告

## 成功条件
✅ 模板加载成功
✅ 并行数据提取模拟成功
✅ 数据质量检查通过
✅ 生成etl_report.md
"""
    
    print("\n任务：执行ETL数据管道")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    return result


def demo_template_incident():
    """演示：使用事件响应模板"""
    
    print("\n" + "=" * 80)
    print("模板化工作流演示：安全事件响应")
    print("=" * 80)
    
    work_dir = Path("output/workflow_template_incident")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_workflow_agent(str(work_dir))
    
    # 使用绝对路径
    template_path = Path(__file__).parent / "knowledge/workflow/templates/incident_response.md"
    
    task = f"""
执行 {template_path} 模板

## 参数
- incident_id: "SEC-2024-001"
- incident_type: "unauthorized_access"
- severity: "high"
- affected_systems: ["web_server_1", "api_gateway", "database_1"]
- detection_source: "siem"
- auto_contain: true

## 场景描述
模拟一个高危安全事件：
- 检测到未授权访问
- 影响多个关键系统
- 需要紧急响应和隔离

## 执行要求
1. 加载事件响应模板
2. 根据severity执行相应响应级别
3. 模拟系统隔离和证据收集
4. 生成事件报告

## 成功条件
✅ 模板加载成功
✅ 紧急响应流程触发
✅ 系统隔离步骤执行
✅ 生成incident_report.md
"""
    
    print("\n任务：执行安全事件响应")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    # 显示响应时间线
    workflow_file = work_dir / "workflow_state.json"
    if workflow_file.exists():
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print("\n事件响应摘要：")
        print("-" * 40)
        
        params = workflow.get('parameters', {})
        print(f"事件ID: {params.get('incident_id')}")
        print(f"严重程度: {params.get('severity')}")
        print(f"响应级别: {workflow.get('variables', {}).get('response_level', 'N/A')}")
        
        # 显示关键步骤
        if 'steps' in workflow:
            print("\n关键响应步骤：")
            critical_steps = ['紧急响应', '系统隔离', '威胁分析', '修复执行']
            for step in workflow['steps']:
                if any(cs in step.get('name', '') for cs in critical_steps):
                    status = "✅ 完成" if step.get('status') == 'completed' else "⏳ 进行中"
                    print(f"  {step['name']}: {status}")
    
    return workflow if workflow_file.exists() else None


def analyze_template_usage():
    """分析模板使用情况"""
    
    print("\n" + "=" * 80)
    print("模板使用分析")
    print("=" * 80)
    
    # 统计各输出目录的执行结果
    output_dirs = [
        "output/workflow_template_deploy",
        "output/workflow_template_custom",
        "output/workflow_template_etl",
        "output/workflow_template_incident"
    ]
    
    template_stats = {}
    
    for dir_path in output_dirs:
        workflow_file = Path(dir_path) / "workflow_state.json"
        if workflow_file.exists():
            with open(workflow_file, 'r') as f:
                workflow = json.load(f)
            
            template_ref = workflow.get('template_ref', 'Unknown')
            template_id = workflow.get('template_id', 'Unknown')
            
            if template_ref not in template_stats:
                template_stats[template_ref] = {
                    'count': 0,
                    'instances': []
                }
            
            template_stats[template_ref]['count'] += 1
            template_stats[template_ref]['instances'].append({
                'instance_id': workflow.get('instance_id'),
                'status': workflow.get('status'),
                'parameters': workflow.get('parameters', {})
            })
    
    print("\n模板使用统计：")
    for template, stats in template_stats.items():
        print(f"\n模板: {template}")
        print(f"  使用次数: {stats['count']}")
        print(f"  实例:")
        for instance in stats['instances']:
            print(f"    - {instance['instance_id']}: {instance['status']}")
    
    print("\n关键发现：")
    print("✅ 模板可以被重复使用")
    print("✅ 参数化实现了灵活性")
    print("✅ 模板引用保持了可追溯性")
    print("✅ 支持运行时覆盖")


def main():
    """主函数"""
    
    print("工作流模板系统演示")
    print("=" * 80)
    print("\n这个演示展示了：")
    print("1. 如何从模板文件加载工作流定义")
    print("2. 如何用参数实例化模板")
    print("3. 如何在JSON中维护模板引用")
    print("4. 如何支持模板覆盖")
    print("\n")
    
    # 选择演示
    print("选择演示：")
    print("1. 标准部署（使用deployment模板）")
    print("2. 自定义部署（覆盖模板部分内容）")
    print("3. ETL管道（使用data_pipeline模板）")
    print("4. 事件响应（使用incident_response模板）")
    print("5. 运行所有演示")
    
    choice = input("\n请选择 (1-5): ").strip() or "1"
    
    if choice == "1":
        demo_template_deployment()
    elif choice == "2":
        demo_template_with_override()
    elif choice == "3":
        demo_template_data_pipeline()
    elif choice == "4":
        demo_template_incident()
    else:
        # 运行所有演示
        results = []
        results.append(demo_template_deployment())
        results.append(demo_template_with_override())
        results.append(demo_template_data_pipeline())
        results.append(demo_template_incident())
        
        # 分析结果
        analyze_template_usage()
        
        print("\n" + "=" * 80)
        print("总结")
        print("=" * 80)
        print("\n核心价值：")
        print("1. **类型层显式表达**：模板文件明确定义工作流类型")
        print("2. **实例层显式表达**：JSON记录实例执行状态")
        print("3. **无需额外代码**：纯React Agent + 知识文件")
        print("4. **灵活且可追溯**：支持重用、覆盖、版本控制")
        
        print("\n设计优势：")
        print("- 人机兼顾：Markdown对人友好，JSON对机器友好")
        print("- 关注点分离：类型定义与实例执行分离")
        print("- 渐进式采用：可从简单自然语言逐步结构化")
        print("- 知识驱动：通过知识文件而非代码实现功能")
    
    print("\n演示完成！")
    print("\n结论：模板化让工作流引擎更强大、更易用、更可维护")


if __name__ == "__main__":
    # 直接运行第一个演示
    demo_template_deployment()