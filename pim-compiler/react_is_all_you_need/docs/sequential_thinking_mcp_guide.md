# Sequential Thinking MCP 使用指南

## 概述

Sequential Thinking MCP 是一个强大的元认知工具，通过结构化的思维链（Chain of Thought）方法来解决复杂问题。它模拟人类的思考过程，支持动态调整、反思修正和多路径探索。

## 核心概念

### 1. 思维链（Chain of Thought）
将复杂问题分解为一系列连续的思考步骤，每一步基于前一步的结果，但又可以回头修正。

### 2. 动态调整
- 可以随时调整预估的思考步骤数
- 支持在"结束"后继续添加新的思考
- 能够根据问题复杂度灵活扩展

### 3. 反思机制
- `isRevision`: 标记当前思考是否在修正之前的内容
- `revisesThought`: 指定修正的是第几步思考
- 支持对任何历史思考进行质疑和改进

### 4. 分支探索
- `branchFromThought`: 从某个思考点开始新的探索路径
- `branchId`: 标识不同的探索分支
- 支持并行探索多个解决方案

## 参数详解

```python
{
    "thought": str,           # 当前的思考内容
    "nextThoughtNeeded": bool,# 是否需要继续思考
    "thoughtNumber": int,     # 当前思考步骤编号
    "totalThoughts": int,     # 预估总步骤数（可调整）
    "isRevision": bool,       # 是否在修正之前的思考
    "revisesThought": int,    # 修正的目标思考编号
    "branchFromThought": int, # 分支起点
    "branchId": str,          # 分支标识
    "needsMoreThoughts": bool # 需要更多思考步骤
}
```

## 使用场景

### 1. 复杂问题分解
适用于需要多步骤推理的问题，如：
- 系统架构设计
- 算法优化方案
- 故障诊断流程

### 2. 假设验证
- 生成初步假设
- 逐步验证假设
- 根据验证结果调整假设
- 得出最终结论

### 3. 多方案比较
- 从同一起点探索不同方案
- 并行评估各方案优劣
- 综合比较后选择最优方案

### 4. 知识构建
- 逐步深入理解新概念
- 建立概念间的联系
- 形成结构化的知识体系

## 实际应用示例

### 示例1：调试复杂Bug

```python
# 第1步：识别问题
thought: "用户报告系统在高并发时响应缓慢，需要分析可能的原因"
thoughtNumber: 1
totalThoughts: 5

# 第2步：收集信息
thought: "查看日志发现数据库查询时间异常，可能是索引问题或锁竞争"
thoughtNumber: 2

# 第3步：生成假设
thought: "假设是数据库锁竞争导致，因为日志显示大量WAITING状态"
thoughtNumber: 3

# 第4步：修正假设（发现新信息）
thought: "等等，仔细看日志发现是缺少索引导致全表扫描，不是锁的问题"
thoughtNumber: 4
isRevision: true
revisesThought: 3

# 第5步：验证并解决
thought: "添加索引后，查询时间从5秒降到0.1秒，问题解决"
thoughtNumber: 5
nextThoughtNeeded: false
```

### 示例2：架构决策

```python
# 主线思考
thought: "需要选择微服务间的通信方式：REST vs gRPC vs 消息队列"
thoughtNumber: 1
totalThoughts: 4

# 分支1：探索REST方案
thought: "REST简单易用，但在高频调用场景下性能不佳"
thoughtNumber: 2
branchFromThought: 1
branchId: "REST"

# 分支2：探索gRPC方案  
thought: "gRPC性能优秀，但增加了复杂度和学习成本"
thoughtNumber: 2
branchFromThought: 1
branchId: "gRPC"

# 分支3：探索消息队列
thought: "消息队列解耦最彻底，但增加了延迟和复杂度"
thoughtNumber: 2
branchFromThought: 1
branchId: "MQ"

# 综合决策
thought: "基于团队技术栈和业务需求，选择REST+消息队列的混合方案"
thoughtNumber: 3
needsMoreThoughts: false
```

## 与React Agent的协同

Sequential Thinking MCP 可以与 React Agent 形成强大的协同：

```
Sequential Thinking (元认知层)
    ↓ 规划和推理
React Agent (执行层)
    ↓ 工具调用
实际执行结果
    ↓ 反馈
Sequential Thinking (反思和调整)
```

### 协同模式

1. **规划-执行模式**
   - Sequential Thinking 制定计划
   - React Agent 执行具体步骤
   - 根据结果调整计划

2. **探索-验证模式**
   - Sequential Thinking 探索可能性
   - React Agent 验证假设
   - 基于验证结果选择方案

3. **分析-综合模式**
   - React Agent 收集信息
   - Sequential Thinking 分析综合
   - 形成结构化理解

## 最佳实践

### 1. 开始时低估步骤数
初始设置较少的 `totalThoughts`，根据需要动态增加，避免冗余思考。

### 2. 及时修正错误
发现推理错误时，立即使用 `isRevision` 修正，保持思维链的准确性。

### 3. 合理使用分支
只在真正需要并行探索时使用分支，避免思维链过于复杂。

### 4. 明确结束条件
设置清晰的问题解决标准，达到后设置 `nextThoughtNeeded: false`。

### 5. 保持思考聚焦
每个 thought 聚焦单一概念或推理步骤，避免混杂多个想法。

## 进阶技巧

### 1. 递归思考
对于特别复杂的问题，可以在一个思考步骤中启动新的Sequential Thinking会话。

### 2. 思维模板
为常见问题类型创建思维模板，如：
- 故障诊断：识别→假设→验证→解决
- 方案设计：需求→方案→评估→决策
- 学习理解：概念→联系→应用→总结

### 3. 思维链优化
定期回顾和优化常用的思维链模式，提高问题解决效率。

## 总结

Sequential Thinking MCP 是一个将AI推理过程显式化、结构化的强大工具。通过支持动态调整、反思修正和多路径探索，它能够处理各种复杂的认知任务。

与 React Agent 结合使用时，形成了"思考-计划-执行-反思"的完整认知循环，大大提升了AI系统解决复杂问题的能力。

关键优势：
- **透明性**：思维过程完全可追溯
- **灵活性**：支持动态调整和修正
- **系统性**：结构化的问题解决方法
- **可靠性**：通过反思机制提高准确性