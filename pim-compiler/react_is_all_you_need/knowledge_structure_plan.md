# 知识文件目录结构规划

基于Python包的概念，将知识文件组织成以下结构：

```
knowledge/
├── __init__.md                    # 知识包索引
├── core/                          # 核心知识
│   ├── __init__.md
│   ├── system_prompt.md           # 系统提示词
│   ├── data_management.md         # 数据管理
│   └── world_overview_generation.md # 世界概览生成
├── programming/                   # 编程相关
│   ├── __init__.md
│   ├── python_programming_knowledge.md
│   ├── fastapi_generation_knowledge.md
│   ├── pim_to_psm_knowledge.md
│   └── 编程规范知识.md
├── workflow/                      # 工作流相关
│   ├── __init__.md
│   ├── python_workflow_obsession.md
│   ├── planning_obsession.md
│   ├── bpmn_obsession.md
│   └── task_dependencies.md
├── coordination/                  # 协作相关
│   ├── __init__.md
│   ├── delegation_best_practices.md
│   ├── context_passing.md
│   ├── result_extraction.md
│   └── efficient_coordination.md
├── output/                        # 输出相关
│   ├── __init__.md
│   ├── structured_output.md
│   ├── role_based_output.md
│   └── perspective_templates.md
├── best_practices/               # 最佳实践
│   ├── __init__.md
│   ├── absolute_path_usage.md
│   ├── code_review_ethics.md
│   ├── test_execution_best_practices.md
│   └── simple_approach.md
└── experimental/                 # 实验性知识
    ├── __init__.md
    ├── conflict_test.md
    └── 综合知识.md

```

## 目录说明

1. **core/** - 核心系统知识，所有agent都应该了解的基础知识
2. **programming/** - 编程语言、框架、代码生成相关
3. **workflow/** - 工作流程、任务执行模式相关
4. **coordination/** - 多agent协作、任务委派相关
5. **output/** - 输出格式、展示方式相关
6. **best_practices/** - 各种最佳实践和规范
7. **experimental/** - 实验性或临时的知识文件

## __init__.md 内容示例

每个目录的 __init__.md 文件应包含：
- 该知识包的用途说明
- 包含的知识文件列表
- 使用建议

## 使用方式

在代码中引用时，可以使用类似Python导入的路径：
```python
knowledge_files=[
    "knowledge/core/system_prompt.md",
    "knowledge/programming/python_programming_knowledge.md",
    "knowledge/workflow/planning_obsession.md"
]
```

或者导入整个包：
```python
knowledge_files=[
    "knowledge/core/",  # 导入core包下所有知识
    "knowledge/best_practices/absolute_path_usage.md"  # 导入特定文件
]
```