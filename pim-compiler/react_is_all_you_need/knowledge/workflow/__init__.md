# Workflow 知识包

工作流程设计、任务执行模式相关的知识。

## 包含的知识文件

### planning_obsession.md
- **用途**: 强调详细规划的重要性
- **适用对象**: 项目管理和任务规划agent
- **主要内容**: 任务分解、计划制定、执行策略

### python_workflow_obsession.md
- **用途**: Python项目的工作流最佳实践
- **适用对象**: Python项目开发agent
- **主要内容**: 开发流程、测试流程、部署流程

### bpmn_obsession.md
- **用途**: BPMN工作流的执行和管理
- **适用对象**: 需要执行BPMN流程的agent
- **主要内容**: BPMN解析、状态更新、流程控制

### task_dependencies.md
- **用途**: 任务依赖关系管理
- **适用对象**: 处理复杂任务依赖的agent
- **主要内容**: 依赖分析、执行顺序、并发控制

## 使用建议

1. **项目管理agent**: 重点使用 `planning_obsession.md`
2. **流程执行agent**: 根据具体流程类型选择相应知识
3. **可以组合**: 不同工作流知识可以组合使用

## 示例用法

```python
# 项目管理agent
knowledge_files = [
    "knowledge/workflow/planning_obsession.md",
    "knowledge/workflow/task_dependencies.md"
]

# Python项目agent
knowledge_files = [
    "knowledge/workflow/python_workflow_obsession.md"
]

# 流程自动化agent
knowledge_files = [
    "knowledge/workflow/"  # 导入所有工作流知识
]
```

## 注意事项

1. **流程选择**: 根据项目特点选择合适的工作流模式
2. **避免冲突**: 不同工作流模式可能有冲突，谨慎组合
3. **持续优化**: 根据实践经验不断优化工作流程