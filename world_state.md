# 世界状态

## 系统架构

### 架构概览

```
用户请求 → Agent分析 → SONIC方法论应用 → 结构化输出
    │           │              │              │
    ▼           ▼              ▼              ▼
总结任务 → 模式识别 → 双维度记忆 → 知识积累
```

### 核心组件

- **SONIC 方法论**：

  - 职责：提供音速学习框架
  - 位置：pim-compiler/react_is_all_you_need/knowledge/structured_notes.md
  - 依赖：双维度记忆理论
  - 接口：三种执行路径（音速/加速/标准）

- **双维度记忆系统**：
  - 职责：管理 Agent 的认知状态
  - 位置：四象限记忆体系
  - 依赖：结构化笔记策略
  - 接口：agent_knowledge.md, task_process.md, world_state.md

## 项目结构

### 核心目录

- `pim-compiler/react_is_all_you_need/`: SONIC 方法论实现
  - `knowledge/`: 知识管理模块
  - `structured_notes.md`: 核心方法论文档
- `task_process.md`: 当前任务过程记录
- `world_state.md`: 世界状态快照

### 关键文件

- **方法论文档**：structured_notes.md - SONIC 方法论核心
- **任务记录**：task_process.md - 当前任务执行过程
- **状态快照**：world_state.md - 世界状态记录

## 技术栈

### 语言和框架

- 主语言：Markdown 文档
- 方法论：SONIC™ (Self-Organizing Neural Intelligence through Cognitive notes)
- 认知框架：双维度记忆理论

### 数据存储

- 笔记系统：Markdown 文件
- 知识库：agent_knowledge.md
- 过程记录：task_process.md
- 状态快照：world_state.md

## 当前状态

### 任务执行状态

- **当前任务**：SONIC 方法论总结
- **执行模式**：标准路径（新模式）
- **完成状态**：已完成
- **输出结果**：结构化总结文档

### 知识积累状态

- **模式识别**：首次总结 SONIC 方法论
- **经验积累**：建立了文档总结的标准流程
- **知识复用**：为后续类似任务提供参考

## 开发约定

### 笔记规范

- 命名规则：描述性文件名
- 文件组织：按功能分类存储
- 更新标准：事务边界处更新
- 内容格式：Markdown 结构化

### 工作流程

- 任务开始：读取知识库，创建过程记录
- 任务执行：持续更新过程记录
- 任务结束：更新知识库和状态快照

## 配置管理

### 文件结构

- `.notes/{agent_name}/`: Agent 专属笔记目录
- `task_process.md`: 当前任务过程
- `world_state.md`: 世界状态快照
- `agent_knowledge.md`: Agent 知识库

## 常见问题

### 已知模式

- 文档总结任务：标准路径，6-8 轮完成
- 模式识别：基于频率选择执行路径
- 知识提炼：从执行过程提取可复用模式

### 最佳实践

- 强制创建笔记：无论任务多简单
- 事务边界更新：开始和结束时更新状态
- 模式复用：优先使用已知模式

---

记录时间：2024-12-19 15:35:00
状态类型：任务完成
