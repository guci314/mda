# Agent创建知识

## 核心原则
"人类不会安排文盲当美国总统" - 为任务选择合适的工具是常识

## Agent创建决策树

### 1. 任务复杂度评估
```
简单任务（< 3步）:
  → 单个Agent
  → 快速LLM
  → 最小知识文件

中等任务（3-10步）:
  → 1-2个Agent
  → 平衡型LLM
  → 相关知识文件

复杂任务（> 10步）:
  → 多个专门Agent
  → 智能LLM协调
  → 完整知识体系
```

### 2. Agent专长设计

#### 文件操作专家
- 职责: ls, cat, mkdir, rm, cp, mv
- LLM: 快速模型（grok-fast, gemini-flash）
- 知识: 文件系统操作

#### 代码生成专家
- 职责: 创建代码文件、实现功能
- LLM: 代码优化模型（deepseek, claude）
- 知识: generation_knowledge.md

#### 调试修复专家
- 职责: 分析错误、修复bug、优化性能
- LLM: 深度理解模型（deepseek, claude）
- 知识: debugging_unified.md

#### 文档编写专家
- 职责: README、API文档、技术文档
- LLM: 长文本模型（kimi, claude）
- 知识: documentation_knowledge.md

#### 测试专家
- 职责: 编写测试、运行测试、覆盖率分析
- LLM: 精确模型（deepseek）
- 知识: test_knowledge.md

### 3. Agent组合模式

#### 串行模式
```
Agent1 → Agent2 → Agent3
适用: 有依赖关系的任务流
```

#### 并行模式
```
     → Agent1 →
Main → Agent2 → Merge
     → Agent3 →
适用: 独立任务的并发执行
```

#### 层级模式
```
Manager
  ├── Worker1
  ├── Worker2
  └── Worker3
适用: 复杂项目的分层管理
```

## Agent生命周期

### 创建阶段
1. 分析任务需求
2. 选择合适LLM
3. 配置知识文件
4. 初始化Agent

### 执行阶段
1. 接收任务
2. 调用工具
3. 记录状态
4. 返回结果

### 销毁阶段
1. 保存执行日志
2. 更新知识库
3. 释放资源

## 常见模式

### 快速原型模式
- 使用最快的LLM
- 最小化配置
- 适合POC和演示

### 生产级模式
- 使用稳定的LLM
- 完整错误处理
- 详细日志记录

### 学习模式
- 记录所有决策
- 更新知识库
- 持续优化

## 最佳实践

1. **单一职责**: 每个Agent专注一个领域
2. **知识继承**: 共享通用知识，特化专门知识
3. **错误隔离**: Agent失败不影响其他Agent
4. **状态透明**: 清晰记录每个Agent的状态
5. **资源优化**: 根据任务选择成本最优的LLM