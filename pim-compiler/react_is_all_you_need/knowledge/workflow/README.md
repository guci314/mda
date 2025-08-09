# Workflow知识包

## 概述

本知识包包含了使用React Agent + JSON笔记本实现的两种核心工作流模式：
1. **Sequential Thinking** - 结构化思维链模式
2. **Workflow Engine** - 通用工作流引擎模式

这两种模式都证明了React Agent的核心理念：**React + 知识 = 图灵完备**

## 知识文件结构

```
workflow/
├── README.md                    # 本文件 - 知识包总览
├── sequential_thinking.md       # Sequential Thinking完整知识
├── workflow_engine.md          # 工作流引擎完整知识
├── json_notebook_patterns.md   # JSON笔记本通用模式
└── execution_strategies.md     # 执行策略和最佳实践
```

## 核心理念

### 1. 知识驱动 vs 程序控制

- **知识驱动**：Agent根据知识文件自主执行任务
- **程序控制**：外部程序控制Agent的执行流程

我们选择知识驱动，因为它：
- 保持Agent的自主性
- 符合"自然语言虚拟机"理念
- 知识可移植、可组合、可进化

### 2. JSON笔记本模式

JSON文件既是数据存储，也是"程序状态"：
- **持久化**：所有状态自动保存
- **可追溯**：完整的执行历史
- **灵活性**：支持任意复杂的数据结构
- **透明性**：所有状态可见、可审计

### 3. 工具最小化原则

只使用基础工具（read_file, write_file），通过知识实现复杂功能：
- 避免工具膨胀
- 提高通用性
- 符合"少即是多"原则

## 应用场景对比

| 特性 | Sequential Thinking | Workflow Engine |
|------|-------------------|-----------------|
| **主要用途** | 结构化推理和决策 | 自动化流程执行 |
| **执行模式** | 线性思维链（可分支） | 复杂工作流图（DAG） |
| **状态管理** | 思考步骤和结论 | 丰富的状态机 |
| **特殊能力** | 修正、分支、置信度 | 并行、条件、审批 |
| **典型场景** | 架构设计、问题分析 | CI/CD、数据管道、事件响应 |

## 最佳实践

### 1. 选择合适的模型

推荐使用 **Gemini 2.5 Pro**：
- 优秀的指令遵循能力
- 精确的工具使用
- 快速且成本效益高
- 支持大context（1M tokens）

### 2. 知识文件设计

- **明确的状态机**：定义清晰的状态转换规则
- **自驱动循环**：让Agent自主检查和执行
- **详细的模板**：提供具体的JSON结构示例
- **错误处理**：定义失败和重试策略

### 3. JSON操作策略

**重要**：不要使用search_replace操作JSON！

正确方法：
1. read_file读取完整JSON
2. 在内存中修改数据结构
3. write_file写入完整JSON

### 4. 执行监控

- 使用递增式策略，稳步推进
- 每个步骤立即更新状态
- 详细记录日志信息
- 生成执行报告

## 实现示例

### Sequential Thinking
```python
from core.react_agent import GenericReactAgent, ReactAgentConfig

config = ReactAgentConfig(
    knowledge_files=["knowledge/workflow/sequential_thinking.md"],
    llm_model="gemini-2.5-pro"
)
agent = GenericReactAgent(config)
```

### Workflow Engine
```python
config = ReactAgentConfig(
    knowledge_files=["knowledge/workflow/workflow_engine.md"],
    llm_model="gemini-2.5-pro"
)
agent = GenericReactAgent(config)
```

## 扩展可能性

1. **混合模式**：结合Sequential Thinking的推理能力和Workflow Engine的执行能力
2. **分布式执行**：多个Agent协作完成复杂工作流
3. **智能调度**：基于资源和优先级的动态调度
4. **版本控制**：工作流定义的版本管理
5. **可视化**：实时工作流执行可视化

## 总结

Workflow知识包展示了React Agent的强大能力：
- 仅用基础工具实现复杂功能
- 知识驱动的自主执行
- 灵活可扩展的架构

这不仅是工具的实现，更是编程范式的革新：**自然语言即程序，知识即代码**。