# Task工具完全指南

## 什么是Task工具？

Task工具是Claude Code中用于**创建和管理子Agent**的核心机制。它解决了复杂任务处理中的上下文管理问题。

## 核心概念

### 1. 问题背景
在处理复杂任务时，单个Agent会遇到：
- **上下文爆炸**：信息太多，超出token限制
- **任务混淆**：多个任务交织，容易出错
- **效率低下**：串行处理，无法并行

### 2. Task工具的解决方案
```
主Agent
  ├── Task → 子Agent1（独立处理任务A）
  ├── Task → 子Agent2（独立处理任务B）
  └── Task → 子Agent3（独立处理任务C）
```

## 工作机制

### 执行流程
1. **主Agent识别需要委派的任务**
2. **调用Task工具创建子Agent**
3. **子Agent在独立上下文中工作**
4. **完成后返回结果给主Agent**
5. **主Agent继续处理**

### 代码层面理解
```python
# Task工具的内部逻辑（简化版）
class Task:
    def execute(self, description, prompt, subagent_type):
        # 1. 创建新的Agent实例
        sub_agent = create_agent(type=subagent_type)

        # 2. 设置独立的上下文
        sub_agent.context = new_context()

        # 3. 执行任务
        result = sub_agent.run(prompt)

        # 4. 返回结果（不返回中间过程）
        return result.summary
```

## 实际应用场景

### 场景1：代码重构项目
```python
# 主Agent协调
Task("分析代码", "找出所有需要重构的部分", "general-purpose")
Task("重构建议", "提供具体重构方案", "general-purpose")
Task("实施重构", "执行重构并生成新代码", "general-purpose")
```

### 场景2：全栈开发
```python
# 并行开发
Task("前端开发", "创建React组件", "general-purpose")
Task("后端开发", "创建API端点", "general-purpose")
Task("数据库设计", "设计表结构", "general-purpose")
```

### 场景3：调试复杂问题
```python
# 分而治之
Task("日志分析", "分析error.log找异常", "general-purpose")
Task("代码审查", "检查相关代码", "general-purpose")
Task("环境检查", "验证配置和依赖", "general-purpose")
```

## 优势总结

### 1. 上下文管理
- **隔离**：每个任务独立上下文
- **清晰**：避免信息混杂
- **高效**：不浪费主对话token

### 2. 任务专注
- **专业**：每个Agent专注一件事
- **质量**：专注带来更好结果
- **可靠**：减少出错概率

### 3. 并行处理
- **速度**：多任务同时进行
- **效率**：充分利用资源
- **体验**：更快得到结果

## 与普通Agent调用的区别

### 普通方式
```
User: "做A，然后做B，然后做C"
Agent: [在同一个上下文中串行处理所有任务]
问题：容易遗忘A的内容，B和C可能混淆
```

### Task工具方式
```
User: "做A，B，C"
Agent:
  → Task创建AgentA处理A
  → Task创建AgentB处理B
  → Task创建AgentC处理C
  → 汇总结果
优势：并行、独立、清晰
```

## 最佳实践

### 1. 任务拆分原则
- **单一职责**：一个Task只做一件事
- **明确边界**：任务之间界限清晰
- **合理粒度**：不要太细也不要太粗

### 2. Prompt编写技巧
- **具体明确**：告诉Agent具体做什么
- **提供上下文**：必要的背景信息
- **指定输出**：期望的结果格式

### 3. 选择合适的subagent_type
- **general-purpose**：大多数任务
- **specialized**：特定领域任务

## 类比理解

### 公司类比
```
CEO（主Agent）
  ├── CTO（技术子Agent）
  ├── CFO（财务子Agent）
  └── CMO（市场子Agent）

每个高管独立处理自己领域，最后向CEO汇报
```

### 计算机类比
```
主进程
  ├── 子进程1（独立内存空间）
  ├── 子进程2（独立内存空间）
  └── 子进程3（独立内存空间）

进程间通过消息传递结果
```

## 总结

Task工具是Claude Code实现**分治策略**的核心机制：
- **分**：将复杂任务分解为子任务
- **治**：每个子Agent独立解决子任务
- **合**：主Agent整合所有结果

这就像是给Claude Code配备了一个**团队**，而不是让一个人做所有事情。