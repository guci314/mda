#!/usr/bin/env python3
"""
使用React Agent + JSON笔记本实现工作流引擎

这个实现展示了如何仅使用React Agent的标准工具（read_file, write_file）
和JSON笔记本来实现完整的工作流引擎功能，包括：
- 步骤执行
- 条件分支
- 并行处理
- 错误处理
- 审批流程
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime
from enum import Enum

sys.path.insert(0, str(Path(__file__).parent))

from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel


# class WorkflowType(Enum):
#     """工作流类型"""
#     DEPLOYMENT = "deployment"  # 部署流程
#     APPROVAL = "approval"      # 审批流程
#     DATA_PIPELINE = "data_pipeline"  # 数据处理管道
#     INCIDENT_RESPONSE = "incident_response"  # 事件响应流程


def create_workflow_agent(work_dir: str) -> GenericReactAgent:
    """创建使用JSON笔记本实现工作流引擎的Agent"""
    
    # 使用OpenRouter访问Gemini-2.5-pro
    config = ReactAgentConfig(
        work_dir=work_dir,
        memory_level=MemoryLevel.SMART,
        knowledge_files=[
            "knowledge/workflow/workflow_engine.md",  # 工作流引擎核心知识
            "knowledge/workflow/json_notebook_patterns.md",  # JSON操作模式
            "knowledge/workflow/execution_strategies.md"  # 执行策略
        ],
        enable_project_exploration=False,
        llm_model="google/gemini-2.5-pro",  # 使用Gemini 2.5 Pro via OpenRouter
        llm_base_url="https://openrouter.ai/api/v1",
        llm_api_key_env="OPENROUTER_API_KEY",
        llm_temperature=0
    )
    
    agent = GenericReactAgent(config, name="workflow_engine_agent")
    
    agent.interface = """使用JSON笔记本实现工作流引擎的Agent
    
我通过维护 workflow_state.json 文件来管理工作流执行：
- 每个步骤的执行状态
- 条件分支决策
- 并行任务管理
- 错误处理和回滚
- 审批记录
"""
    
    # 简化系统提示，主要依赖知识文件
    agent._system_prompt = (agent._system_prompt or "") + """

## 工作流引擎执行任务

你是一个工作流引擎执行器。你的知识文件已经包含了完整的执行策略和模式。

请根据知识文件中的指导：
1. 使用workflow_state.json管理工作流状态
2. 遵循JSON笔记本操作模式（完整读-修改-写）
3. 按照执行策略处理各种步骤类型
4. 实现自驱动循环直到完成

记住：知识文件是你的执行指南，严格遵循其中的规范和最佳实践。
"""
    
    return agent


def demo_deployment_workflow():
    """演示：软件部署工作流"""
    
    print("=" * 80)
    print("工作流引擎演示：软件部署流程")
    print("=" * 80)
    
    work_dir = Path("output/workflow_engine")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_workflow_agent(str(work_dir))
    
    task = """
使用workflow_state.json实现一个软件部署工作流。

## 工作流定义

### 步骤：
1. **代码检查** (action)
   - 运行单元测试
   - 代码质量检查
   
2. **构建** (action)
   - 编译代码
   - 生成Docker镜像
   
3. **部署决策** (condition)
   - 如果是生产环境 → 需要审批
   - 如果是测试环境 → 直接部署
   
4. **审批流程** (approval) - 仅生产环境
   - 等待管理员审批
   
5. **并行部署** (parallel)
   - 部署到多个服务器
   - 更新负载均衡器
   
6. **健康检查** (action)
   - 验证服务状态
   - 检查响应时间
   
7. **通知** (action)
   - 发送部署成功通知

## 执行要求
- 完整记录每个步骤的执行
- 模拟一个生产环境部署（需要审批）
- 并行部署到3个服务器
- 生成deployment_report.md

## 成功条件
✅ 所有步骤执行完成
✅ 审批流程正确处理
✅ 并行任务全部成功
✅ 生成部署报告
"""
    
    print("\n任务：执行软件部署工作流")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    # 读取并展示工作流状态
    workflow_file = work_dir / "workflow_state.json"
    if workflow_file.exists():
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print("\n工作流执行结果：")
        print("-" * 40)
        print(f"工作流ID: {workflow.get('workflow_id')}")
        print(f"类型: {workflow.get('type')}")
        print(f"状态: {workflow.get('status')}")
        
        print("\n步骤执行情况：")
        for step in workflow.get('steps', []):
            status_icon = "✅" if step['status'] == 'completed' else "❌"
            print(f"  {status_icon} {step['name']} ({step['type']}) - {step['status']}")
        
        if workflow.get('approvals'):
            print("\n审批记录：")
            for approval_id, approval in workflow['approvals'].items():
                print(f"  {approval_id}: {approval['status']} - {approval.get('comment', '')}")
    
    return workflow if workflow_file.exists() else None


def demo_data_pipeline():
    """演示：数据处理管道工作流"""
    
    print("\n" + "=" * 80)
    print("工作流引擎演示：ETL数据管道")
    print("=" * 80)
    
    work_dir = Path("output/workflow_data_pipeline")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_workflow_agent(str(work_dir))
    
    task = """
使用workflow_state.json实现一个ETL数据处理管道。

## 工作流定义

### 步骤：
1. **数据提取** (parallel)
   - 从MySQL提取用户数据
   - 从MongoDB提取订单数据
   - 从Redis提取会话数据
   
2. **数据验证** (action)
   - 检查数据完整性
   - 验证数据格式
   
3. **数据质量检查** (condition)
   - 如果错误率 > 5% → 触发告警流程
   - 如果错误率 <= 5% → 继续处理
   
4. **数据转换** (parallel)
   - 清洗数据
   - 标准化格式
   - 计算衍生指标
   
5. **数据加载** (action)
   - 写入数据仓库
   - 更新索引
   
6. **报告生成** (action)
   - 生成处理统计
   - 记录异常数据

## 执行要求
- 模拟处理100万条数据
- 错误率设为3%（正常流程）
- 记录每个阶段的处理时间
- 生成data_pipeline_report.md

## 变量设置
```json
{
  "total_records": 1000000,
  "error_rate": 0.03,
  "sources": ["mysql", "mongodb", "redis"],
  "target": "data_warehouse"
}
```
"""
    
    print("\n任务：执行ETL数据管道")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    # 分析执行结果
    workflow_file = work_dir / "workflow_state.json"
    if workflow_file.exists():
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print("\n数据管道执行统计：")
        print("-" * 40)
        
        variables = workflow.get('variables', {})
        print(f"处理记录数: {variables.get('total_records', 0):,}")
        print(f"错误率: {variables.get('error_rate', 0):.1%}")
        print(f"数据源: {', '.join(variables.get('sources', []))}")
        
        # 统计并行任务
        parallel_groups = workflow.get('parallel_groups', {})
        if parallel_groups:
            print(f"\n并行任务组: {len(parallel_groups)}")
            for group_id, group in parallel_groups.items():
                print(f"  {group_id}: {len(group['steps'])} 个任务")
    
    return workflow if workflow_file.exists() else None


def demo_incident_response():
    """演示：事件响应工作流"""
    
    print("\n" + "=" * 80)
    print("工作流引擎演示：安全事件响应")
    print("=" * 80)
    
    work_dir = Path("output/workflow_incident")
    work_dir.mkdir(parents=True, exist_ok=True)
    
    agent = create_workflow_agent(str(work_dir))
    
    task = """
使用workflow_state.json实现一个安全事件响应工作流。

## 工作流定义

### 步骤：
1. **事件检测** (action)
   - 接收安全告警
   - 初步分类（严重性：高）
   
2. **严重性评估** (condition)
   - 如果严重性 = 高 → 立即响应
   - 如果严重性 = 中 → 计划响应
   - 如果严重性 = 低 → 记录观察
   
3. **立即响应** (parallel) - 高严重性分支
   - 隔离受影响系统
   - 通知安全团队
   - 启动日志收集
   
4. **根因分析** (action)
   - 分析攻击向量
   - 识别影响范围
   
5. **修复决策** (approval)
   - 安全主管审批修复方案
   
6. **修复执行** (parallel)
   - 应用安全补丁
   - 更新防火墙规则
   - 强化系统配置
   
7. **验证** (action)
   - 确认威胁已消除
   - 系统功能正常
   
8. **事后总结** (action)
   - 生成事件报告
   - 更新应急预案

## 执行要求
- 模拟一个高严重性安全事件
- 审批通过修复方案
- 记录完整的响应时间线
- 生成incident_report.md

## 事件详情
```json
{
  "incident_id": "SEC-2024-001",
  "type": "unauthorized_access",
  "severity": "high",
  "affected_systems": ["web_server_1", "database_1"],
  "detection_time": "2024-01-15T10:30:00Z"
}
```
"""
    
    print("\n任务：执行安全事件响应流程")
    print("-" * 40)
    
    result = agent.execute_task(task)
    
    # 展示响应时间线
    workflow_file = work_dir / "workflow_state.json"
    if workflow_file.exists():
        with open(workflow_file, 'r') as f:
            workflow = json.load(f)
        
        print("\n事件响应时间线：")
        print("-" * 40)
        
        for step in workflow.get('steps', []):
            if step['status'] == 'completed':
                print(f"⏱️ {step.get('started_at', 'N/A')}: {step['name']}")
        
        print(f"\n总体状态: {workflow.get('status')}")
        
        # 显示关键指标
        variables = workflow.get('variables', {})
        if variables:
            print("\n关键指标：")
            print(f"  事件ID: {variables.get('incident_id')}")
            print(f"  严重性: {variables.get('severity')}")
            print(f"  影响系统: {len(variables.get('affected_systems', []))}")
    
    return workflow if workflow_file.exists() else None


def main():
    """主函数"""
    
    print("选择工作流演示：")
    print("1. 软件部署流程")
    print("2. ETL数据管道")
    print("3. 安全事件响应")
    print("4. 运行所有演示")
    
    choice = input("\n请选择 (1-4): ").strip() or "1"
    
    if choice == "1":
        demo_deployment_workflow()
    elif choice == "2":
        demo_data_pipeline()
    elif choice == "3":
        demo_incident_response()
    else:
        workflows = []
        workflows.append(demo_deployment_workflow())
        workflows.append(demo_data_pipeline())
        workflows.append(demo_incident_response())
        
        # 总结所有工作流
        print("\n" + "=" * 80)
        print("工作流引擎总结")
        print("=" * 80)
        
        print("\n已执行的工作流：")
        for i, workflow in enumerate(workflows, 1):
            if workflow:
                print(f"{i}. {workflow.get('type', 'unknown')}: {workflow.get('status')}")
        
        print("\n关键特性展示：")
        print("✅ 步骤执行与状态管理")
        print("✅ 条件分支与决策")
        print("✅ 并行任务处理")
        print("✅ 审批流程集成")
        print("✅ 错误处理与重试")
        print("✅ 完整的执行追踪")
    
    print("\n演示完成！")
    print("\n结论：React Agent + JSON笔记本 = 灵活的工作流引擎")


if __name__ == "__main__":
    # 直接运行第一个演示
    demo_deployment_workflow()