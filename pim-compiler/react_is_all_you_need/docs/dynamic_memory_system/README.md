# 动态记忆系统文档

本目录包含了 GenericReactAgent 动态记忆系统的设计和实施文档。

## 重要更新：废除 World Overview

基于 "知识即程序" 的理念，我们决定废除独立的 `world_overview.md`，将环境认知整合到动态记忆系统中。详见：
- [统一环境认知设计](./unified_environment_cognition.md)
- [环境认知实现示例](./environment_cognition_implementation.py)

## 文档结构

### 1. [动态记忆系统设计](./dynamic_memory_system.md)
核心设计理念和四层记忆架构的详细说明。

**主要内容**：
- 核心理念：静态记忆 ≠ 知识，动态验证 + 可更新记忆 = 活知识
- 四层架构：元知识层、原理层、接口层、实现层
- 记忆验证和更新机制
- 实施步骤

### 2. [记忆格式示例](./memory_format_example.md)
展示如何从现有的扁平格式迁移到分层格式。

**主要内容**：
- 现有格式的问题分析
- 改进后的分层格式示例
- 元数据结构设计
- 使用示例

### 3. [改进的知识提取提示词](./improved_knowledge_extraction_prompt.md)
新的知识提取提示词模板，支持分层知识提取。

**主要内容**：
- 分层知识提取策略
- 元数据自动添加
- 压缩策略改进
- 使用知识时的验证策略

### 4. [记忆系统迁移指南](./memory_migration_guide.md)
从现有系统到动态记忆系统的详细迁移计划。

**主要内容**：
- 四阶段迁移计划
- 向后兼容策略
- 具体实施步骤
- 成功标准

### 5. [统一环境认知设计](./unified_environment_cognition.md)
将环境认知整合到动态记忆系统的设计方案。

**主要内容**：
- 废除 world_overview 的理由
- 环境认知层设计
- 渐进式学习策略
- 实现优势

### 6. [环境认知实现示例](./environment_cognition_implementation.py)
展示如何实现环境认知子系统的 Python 代码。

**主要内容**：
- EnvironmentCognition 类实现
- 文件访问学习机制
- 项目理解推断
- 与 Agent 的集成方式

## 快速开始

1. **理解概念**：先阅读[动态记忆系统设计](./dynamic_memory_system.md)
2. **查看示例**：通过[记忆格式示例](./memory_format_example.md)了解具体格式
3. **开始迁移**：按照[迁移指南](./memory_migration_guide.md)逐步实施

## 核心改进

| 问题 | 解决方案 |
|------|---------|
| 过时的代码行号 | 搜索模式 + 实时验证 |
| 扁平化存储 | 分层架构，差异化管理 |
| 被动更新 | 主动监控 + 置信度衰减 |
| 死记硬背 | 记住方法而非结果 |

## 实施时间表

- **第1周**：标注现有知识，添加分类标签
- **第2-3周**：实现验证机制
- **第2个月**：完成分层存储
- **第3个月**：实现智能更新

## 相关代码

- 知识提取实现：`react_agent.py` 中的 `_update_extracted_knowledge_sync` 方法
- 知识存储位置：`.agents/{agent_name}/long_term_data/`
- 配置项：`ReactAgentConfig` 中的 `knowledge_extraction_limit`