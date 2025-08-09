# Sequential Thinking 完整知识

## 概述

Sequential Thinking是一种结构化的思维链模式，通过维护thought_chain.json文件来实现复杂的推理和决策过程。它支持线性思考、分支探索、修正回溯等高级功能。

## 核心概念

### 1. 思维链（Thought Chain）

思维链是一系列相互关联的思考步骤，每个步骤都：
- 基于前面的思考结果
- 产生新的洞察或决策
- 可能触发分支或修正

### 2. JSON笔记本

使用JSON文件作为持久化的"思维记忆"：
- **可追溯**：完整记录思考过程
- **可修正**：支持回溯和修改
- **可分支**：探索多种可能性

## JSON结构规范

### 完整结构
```json
{
  "session_id": "唯一会话标识",
  "created_at": "创建时间",
  "total_thoughts_estimate": 8,  // 预估需要的思考步骤数
  "current_thought": 0,          // 当前完成的思考数
  "status": "thinking|completed|paused",
  "thoughts": [],                // 思考步骤数组
  "branches": {},                // 分支管理
  "conclusions": {},             // 最终结论
  "metadata": {}                 // 额外元数据
}
```

### Thought结构
```json
{
  "id": 1,
  "content": "详细的思考内容",
  "timestamp": "时间戳",
  "type": "initial|continuation|revision|branch|conclusion",
  "revises": null,              // 修正的thought id
  "branch_from": null,          // 分支起点
  "branch_id": null,            // 分支标识
  "confidence": 0.8,            // 置信度 (0-1)
  "tags": ["标签1", "标签2"],   // 分类标签
  "evidence": [],               // 支撑证据
  "next_possible": []           // 可能的下一步
}
```

### 分支管理
```json
"branches": {
  "branch_name": {
    "from_thought": 2,         // 分支起点
    "thoughts": [3, 4],        // 包含的thoughts
    "status": "active|merged|abandoned",
    "conclusion": "分支结论"
  }
}
```

## 执行策略

### 1. 循环执行模式

```python
while not completed:
    state = read_file("thought_chain.json")
    
    if needs_more_thoughts(state):
        add_next_thought(state)
    elif needs_revision(state):
        revise_thought(state)
    elif needs_branch(state):
        create_branch(state)
    elif ready_to_conclude(state):
        finalize_conclusions(state)
    else:
        mark_completed(state)
```

### 2. JSON操作原则

**关键原则：永远不要使用search_replace操作JSON！**

正确的操作流程：
1. `read_file` - 读取完整JSON
2. 内存中修改数据结构
3. `write_file` - 写入完整JSON

```python
# ✅ 正确方法
data = json.loads(read_file("thought_chain.json"))
data["thoughts"].append(new_thought)
data["current_thought"] += 1
write_file("thought_chain.json", json.dumps(data))

# ❌ 错误方法
search_replace("thought_chain.json", 
    '"current_thought": 3',
    '"current_thought": 4')  # 危险！可能破坏JSON结构
```

### 3. 递增式策略

不要试图一次性完成所有思考，而是：
- 每次添加一个thought
- 立即保存状态
- 检查是否需要继续
- 重复直到完成

## 思考类型详解

### 1. Initial（初始思考）
```json
{
  "type": "initial",
  "content": "问题定义和需求分析",
  "confidence": 0.95,
  "tags": ["requirements", "problem_definition"]
}
```
用于开始整个思考过程，通常包含问题理解和目标设定。

### 2. Continuation（延续思考）
```json
{
  "type": "continuation",
  "content": "基于前面的分析，继续深入",
  "confidence": 0.85
}
```
线性推进思考，每步基于前一步的结果。

### 3. Branch（分支思考）
```json
{
  "type": "branch",
  "branch_id": "alternative_solution",
  "branch_from": 2,
  "content": "探索另一种可能的方案",
  "confidence": 0.7
}
```
创建分支探索不同的可能性。

### 4. Revision（修正思考）
```json
{
  "type": "revision",
  "revises": 3,
  "content": "发现之前的分析有误，需要修正",
  "confidence": 0.9
}
```
修正之前的错误或不完整的思考。

### 5. Conclusion（总结思考）
```json
{
  "type": "conclusion",
  "content": "综合所有分析，得出最终结论",
  "confidence": 0.95
}
```
总结整个思考过程，形成最终决策。

## 高级特性

### 1. 置信度管理

每个thought都有置信度评分：
- **0.9-1.0**: 非常确定
- **0.7-0.9**: 较为确定
- **0.5-0.7**: 中等确定
- **< 0.5**: 需要更多信息

低置信度的thought可能触发：
- 更多的探索分支
- 寻求额外信息
- 修正和重新评估

### 2. 多分支探索

支持同时探索多个方案：
```json
"branches": {
  "solution_a": {
    "from_thought": 2,
    "thoughts": [3, 4, 5],
    "evaluation": "性能好但成本高"
  },
  "solution_b": {
    "from_thought": 2,
    "thoughts": [6, 7],
    "evaluation": "成本低但需要更多开发时间"
  }
}
```

### 3. 动态调整

可以根据思考进展动态调整：
- 增加或减少预估的思考步骤数
- 改变思考方向
- 合并或放弃分支

## 实施模板

### 架构设计任务
```python
thoughts_template = [
    {"type": "initial", "focus": "需求分析"},
    {"type": "continuation", "focus": "技术选型"},
    {"type": "branch", "focus": "方案A探索"},
    {"type": "branch", "focus": "方案B探索"},
    {"type": "continuation", "focus": "性能对比"},
    {"type": "continuation", "focus": "成本分析"},
    {"type": "revision", "focus": "修正评估"},
    {"type": "conclusion", "focus": "最终决策"}
]
```

### 问题调试任务
```python
thoughts_template = [
    {"type": "initial", "focus": "问题识别"},
    {"type": "continuation", "focus": "根因分析"},
    {"type": "branch", "focus": "假设1验证"},
    {"type": "branch", "focus": "假设2验证"},
    {"type": "revision", "focus": "排除错误假设"},
    {"type": "continuation", "focus": "解决方案设计"},
    {"type": "continuation", "focus": "实施验证"},
    {"type": "conclusion", "focus": "问题解决总结"}
]
```

## 质量检查清单

### 执行前检查
- [ ] thought_chain.json已初始化
- [ ] 目标明确（需要多少个thoughts）
- [ ] 分支策略清晰

### 执行中检查
- [ ] 每个thought内容充实（>50字）
- [ ] 置信度评分合理
- [ ] 分支管理正确
- [ ] 状态及时更新

### 执行后验证
- [ ] 达到预定thought数量
- [ ] 所有分支都有结论
- [ ] conclusions.main已填写
- [ ] status标记为completed
- [ ] 生成了相应的文档

## 最佳实践

### 1. 思考深度
- 每个thought应该有实质性内容
- 避免表面化的分析
- 提供具体的证据和推理

### 2. 分支策略
- 在关键决策点创建分支
- 充分探索每个分支
- 明确记录选择理由

### 3. 修正机制
- 发现错误立即修正
- 保留修正历史
- 说明修正原因

### 4. 结论质量
- 综合所有思考结果
- 提供清晰的决策
- 包含备选方案

## 常见问题

### Q: 为什么不能用search_replace？
A: JSON是结构化数据，部分替换可能破坏结构完整性。必须作为整体读写。

### Q: 如何处理超长思维链？
A: 可以分阶段保存，创建checkpoint，或使用多个关联的JSON文件。

### Q: 分支过多怎么办？
A: 设置分支数量上限，优先探索高置信度分支，及时剪枝低价值分支。

## 扩展应用

1. **协作思考**：多个Agent共享thought_chain.json
2. **思维模板**：预定义的思考模式库
3. **思维可视化**：将JSON转换为思维导图
4. **思维审计**：追踪和评估决策质量
5. **思维学习**：从历史思维链中提取模式

## 总结

Sequential Thinking通过JSON笔记本实现了：
- ✅ 结构化的思考过程
- ✅ 可追溯的决策历史
- ✅ 灵活的分支探索
- ✅ 自主的执行循环

这是React Agent"知识驱动"理念的完美体现。