# 知识库索引

本知识库包含React Agent系统所需的各类知识文件，按照Python包的概念组织成模块化结构。

## 知识包导出 (Exports)

```python
# 所有可用的知识包
exports = {
    "core": "knowledge/core/",
    "programming": "knowledge/programming/",
    "workflow": "knowledge/workflow/",
    "coordination": "knowledge/coordination/",
    "output": "knowledge/output/",
    "best_practices": "knowledge/best_practices/",
    "mda": "knowledge/mda/",
    "project_exploration": "knowledge/project_exploration/",
    "experimental": "knowledge/experimental/"
}
```

## 知识包结构

### core/ - 核心知识
系统核心功能相关的基础知识，所有agent都应该了解。
- `system_prompt.md` - 系统提示模板
- `default_knowledge.md` - 默认知识配置
- `data_management.md` - 数据管理策略
- `world_overview_generation.md` - 世界观生成

### programming/ - 编程知识
编程语言、框架、代码生成相关的专业知识。
- `python_programming_knowledge.md` - Python编程知识
- `编程规范知识.md` - 编程规范和最佳实践

### workflow/ - 工作流知识
任务执行模式、流程控制相关的知识。
- `sequential_thinking.md` - 顺序思维模式
- `workflow_engine.md` - 工作流引擎实现
- `json_notebook_patterns.md` - JSON笔记本模式
- `execution_strategies.md` - 执行策略和优化
- `task_dependencies.md` - 任务依赖管理
- `planning_obsession.md` - 详细规划方法
- `python_workflow_obsession.md` - Python工作流
- `bpmn_obsession.md` - BPMN流程管理

### coordination/ - 协作知识
多agent协作、任务委派、上下文传递相关的知识。
- `efficient_coordination.md` - 高效协作策略
- `context_passing.md` - 上下文传递机制
- `delegation_best_practices.md` - 任务委派最佳实践
- `result_extraction.md` - 结果提取和整合

### mda/ - MDA架构知识
模型驱动架构相关的完整知识体系。
- `pim_to_psm_knowledge.md` - PIM到PSM转换
- `generation_knowledge.md` - 代码生成策略
- `fastapi_generation_knowledge.md` - FastAPI生成
- `debugging_knowledge.md` - 调试知识库
- `debugging_workflow.md` - 调试工作流
- `syntax_fix_strategies.md` - 语法修复策略
- `coordinator_workflow.md` - 协调工作流

### project_exploration/ - 项目探索
项目理解和分析相关的知识。
- `4plus1_exploration_prompt.md` - 4+1架构视图
- `uml_exploration_prompt.md` - UML建模方法

### output/ - 输出知识
输出格式化、展示模板相关的知识。
- `structured_output.md` - 结构化输出
- `role_based_output.md` - 基于角色的输出
- `perspective_templates.md` - 视角模板

### best_practices/ - 最佳实践
各种编程和系统设计的最佳实践。
- `absolute_path_usage.md` - 绝对路径使用
- `code_review_ethics.md` - 代码审查道德
- `simple_approach.md` - 简单方法论
- `test_execution_best_practices.md` - 测试执行最佳实践

### experimental/ - 实验性知识
实验性或临时的知识文件，可能会调整或移除。
- `conflict_test.md` - 冲突测试
- `综合知识.md` - 综合性知识

## 使用方式

### 通过导出名称导入（推荐）
```python
from knowledge import exports

# 导入特定知识包
knowledge_files = [
    exports["core"],           # 核心知识
    exports["workflow"],        # 工作流知识
    exports["mda"]             # MDA架构知识
]
```

### 导入特定文件
```python
knowledge_files = [
    "knowledge/core/system_prompt.md",
    "knowledge/programming/python_programming_knowledge.md"
]
```

### 导入整个模块
```python
# 导入core模块的所有知识文件
knowledge_files = ["knowledge/core/"]
```

### 混合导入
```python
knowledge_files = [
    "knowledge/core/",  # 导入整个core模块
    "knowledge/best_practices/absolute_path_usage.md"  # 导入特定文件
]
```

### 场景化导入示例

#### 生成Agent配置
```python
# 代码生成Agent
knowledge_files = [
    exports["mda"],  # MDA完整知识
    exports["programming"]  # 编程知识
]
```

#### 调试Agent配置
```python
# 专门的调试Agent
knowledge_files = [
    "knowledge/mda/debugging_knowledge.md",
    "knowledge/mda/debugging_workflow.md",
    "knowledge/mda/syntax_fix_strategies.md"
]
```

#### 协调Agent配置
```python
# Pipeline协调Agent
knowledge_files = [
    exports["coordination"],  # 协作知识
    "knowledge/mda/coordinator_workflow.md"  # MDA协调流程
]
```

#### 项目分析Agent配置
```python
# 项目理解Agent
knowledge_files = [
    exports["project_exploration"],  # 项目探索方法
    exports["core"]  # 核心知识
]
```

## 知识包依赖关系

```
knowledge/
├── __init__.md (主索引)
├── core/ (基础依赖)
│   └── __init__.md
├── programming/ 
│   └── __init__.md
├── workflow/
│   └── __init__.md
├── coordination/
│   └── __init__.md
├── mda/ (依赖: core, programming, workflow)
│   └── __init__.md
├── project_exploration/ (依赖: core)
│   └── __init__.md
├── output/
│   └── __init__.md
├── best_practices/
│   └── __init__.md
└── experimental/
    └── __init__.md
```

## 维护指南

### 添加新知识文件
1. 确定最合适的知识包目录
2. 将文件放入相应目录
3. 更新该目录的 `__init__.md`，添加文件说明
4. 如需要，更新根 `__init__.md` 的导出列表

### 创建新知识包
1. 在 knowledge/ 下创建新目录
2. 创建该目录的 `__init__.md`
3. 在根 `__init__.md` 的 exports 中添加新包
4. 记录包的用途和包含的模块

### 知识文件命名规范
- 使用小写字母和下划线
- 名称应描述性强
- 避免过长的文件名
- 相关文件使用相同前缀

### 版本控制
- 每个知识包的 `__init__.md` 应记录更新历史
- 重大更改需要在根 `__init__.md` 中说明
- 实验性知识先放入 experimental/ 目录

## 质量标准

### 知识文件应包含
- 明确的用途说明
- 适用对象描述
- 使用示例
- 最佳实践
- 注意事项

### 知识包应保持
- 单一职责原则
- 低耦合高内聚
- 清晰的依赖关系
- 完整的文档说明

## 更新历史

- 2024-08-10: 添加所有包的 `__init__.md` 文件
- 2024-08-10: 创建统一的导出机制
- 2024-08-10: 添加 MDA 和 project_exploration 包