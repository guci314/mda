# 世界状态

## 系统架构
### 架构概览
```
React Agent Minimal架构
- 核心：ReactAgentMinimal（约500行代码）
- 知识系统：Markdown知识文件驱动行为
- 内存管理：冯诺依曼架构（CPU + 文件系统）
```

## 项目结构
### 核心目录
- `core/`：React Agent核心代码
- `knowledge/`：知识文件（系统行为定义）
- `.notes/`：Agent私有笔记
- `.sessions/`：任务执行日志
- `docs/`：架构文档

### 关键文件
- `core/react_agent_minimal.py`：核心Agent实现
- `knowledge/mandatory_protocol.md`：强制执行协议
- `knowledge/system_prompt.md`：系统提示词
- `knowledge/structured_notes.md`：内存管理架构
- `knowledge/large_file_handling.md`：大文件处理优化

## 技术栈
### 语言和框架
- 主语言：Python 3.x
- LLM接口：OpenAI兼容API
- 支持模型：Kimi、DeepSeek、Claude、Gemini、Qwen

## 最近更新
### 2025-09-08：处理工作流消息 workflow_calc_20250908_045924
- 任务: 计算2+2
- 结果: 4
- 影响: 完成工作流，回复给张三

### 2025-09-08：处理工作流消息 workflow_calc_20250908_045727
- 任务: 计算2+2
- 结果: 4
- 影响: 完成工作流，回复给张三

### 2025-09-08：处理计算任务 calc_20250908_044801
- 任务: 计算2+2等于几？
- 结果: 4
- 影响: 验证简单任务处理流程

### 2025-09-08：处理计算任务
- 任务: 计算2+2等于几？
- 结果: 4
- 影响: 验证简单任务处理流程

### 2025-09-05：修复PSM示例缺少task_process.md维护
- 问题：PSM生成Agent未创建工作内存
- 原因：system_prompt.md示例不完整
- 解决：在示例中加入task_process.md维护步骤
- 影响：确保所有Agent遵守图灵完备要求

### 2025-09-05：Claude Code开始遵守内存管理协议
- 目的：通过自举验证理论正确性
- 实施：Claude Code使用TodoWrite和维护所有必需文件
- 价值：帮助发现协议设计缺陷和bug
- 记录：已更新CLAUDE.md明确遵守要求

## 常见问题
### 已知陷阱
- task_process.md必须在第1轮创建，每轮更新
- 知识文件中的示例会直接影响Agent行为
- 不能为了优化速度而跳过内存管理协议

### Agent活动记录
- react_agent：最后活动 2025-09-08（处理工作流消息 workflow_calc_20250908_045924）
- claude_code：最后活动 2025-09-05（修复知识文件）
- psm_generation_agent：最后活动 2025-09-05（生成PSM文档）

---
记录时间：2025-09-08 05:00:00
状态类型：任务完成记录