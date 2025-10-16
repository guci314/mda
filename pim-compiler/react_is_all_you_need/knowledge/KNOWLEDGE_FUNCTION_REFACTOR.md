# 知识函数重构记录

## 重构目标

明确区分**软约束函数**和**契约函数**，统一知识函数的定义和使用规范。

## 核心概念

### 知识函数分类

| 类型 | 标记格式 | ExecutionContext | 说明 |
|------|---------|-----------------|------|
| **软约束函数** | `函数 @x` | 可选 | Agent自主决定是否使用 |
| **契约函数** | `契约函数 @y` | 强制 | 必须严格使用 |

## 已完成更新

### ✅ 1. knowledge_function_concepts.md（新建）
- 完整定义知识函数概念
- 说明软约束函数vs契约函数
- ExecutionContext使用规则
- 设计原则和演化路径

### ✅ 2. learning_functions.md（完全重写 - 两阶段执行）
**契约函数**：
- `契约函数 @learning()` - 两阶段执行
  - 阶段1（计划）：初始化 + 列出所有TODO
  - 阶段2（执行）：10个步骤，完全外部化状态
- `契约函数 @memory()` - 两阶段执行
  - 阶段1（计划）：初始化 + 列出所有TODO
  - 阶段2（执行）：5个步骤，完全外部化状态

**软约束函数**：
- `函数 @快速记忆()` - ExecutionContext可选

**核心更新**：
- 明确区分计划阶段和执行阶段
- 所有中间状态外部化到ExecutionContext
- 使用`add_tasks`、`start_task`、`complete_task`、`set_data`、`get_data`
- 体现理性主义：先规划后执行，确定性路径

### ✅ 3. system_prompt_minimal.md（更新）
- 添加知识函数概念章节
- 明确契约函数执行规则
- 软约束函数执行策略
- 知识函数索引

### ✅ 4. model_mappings.md（更新）
- 更新为标准格式：`契约函数 @切换模型()`
- 添加ExecutionContext步骤

## 待更新文件

### 🔄 honesty_enforcement.md
当前状态：提到"契约函数验证机制"，但没有使用新标记格式
建议更新：
- 明确标记为 `契约函数` 或 `函数`
- 统一格式

### 🔄 其他知识函数文件

需要审查并更新以下文件：

1. **work_with_expert.md**
   - 当前：`## 契约函数 @work_with_expert`
   - 更新为：`## 契约函数 @work_with_expert()` + ExecutionContext步骤

2. **sequential_thinking.md**
   - 当前：`# @sequential-thinking 契约函数`
   - 更新为：`# 契约函数 @sequential-thinking()` + ExecutionContext步骤

3. **sleep_consolidation.md**
   - 当前：`## 契约函数 @睡眠巩固()`
   - 需评估：是否应为软约束函数？
   - 更新ExecutionContext步骤

4. **auto_trigger_expert.md**
   - 评估其中的函数类型
   - 统一标记格式

5. **precomputed_index_design.md**
   - 提到"与@learning契约函数的集成"
   - 检查是否需要更新

## 知识函数完整清单

### 默认加载（Always）

**契约函数**：
- `契约函数 @learning()` - learning_functions.md
- `契约函数 @memory()` - learning_functions.md
- `契约函数 @切换模型()` - model_mappings.md

**软约束函数**：
- `函数 @快速记忆()` - learning_functions.md

### 按需加载（On-demand）

**待评估**：
- `@work_with_expert()` - work_with_expert.md
- `@sequential-thinking()` - sequential_thinking.md
- `@睡眠巩固()` - sleep_consolidation.md
- 其他...

## 重构原则

### 1. 标记规范
- 软约束函数：`函数 @函数名(参数)`
- 契约函数：`契约函数 @函数名(参数)`

### 2. 格式规范
每个知识函数应包含：
```markdown
## [函数类型] @函数名(参数)

### 函数签名
\```
[函数类型] @函数名(参数)
\```

### [强制要求 / 建议流程]
[描述ExecutionContext使用要求]

### 执行步骤
[详细步骤，契约函数需要ExecutionContext格式]
```

### 3. ExecutionContext规范

**契约函数**（强制）：
```
步骤X: [步骤名称]
\```
context(action='add_step', step='...')
[执行内容]
context(action='complete_step')
\```
```

**软约束函数**（可选）：
```
Agent根据任务复杂度决定是否使用ExecutionContext
- 简单任务 → 直接执行
- 复杂任务 → 使用ExecutionContext
```

## 后续任务

### 高优先级
1. 更新 honesty_enforcement.md
2. 审查所有`@`开头的函数
3. 统一标记格式

### 中优先级
1. 创建知识函数索引文档
2. 更新README.md引用新概念
3. 添加使用示例

### 低优先级
1. 清理旧的、不一致的引用
2. 归档废弃的知识函数
3. 完善文档交叉引用

## 验证清单

重构完成后，每个知识函数应满足：
- [ ] 清晰的函数类型标记（函数 / 契约函数）
- [ ] 明确的ExecutionContext使用要求
- [ ] 标准化的步骤格式
- [ ] 完整的文档结构
- [ ] 在索引中被列出

## 参考文档

- `knowledge_function_concepts.md` - 核心概念
- `learning_functions.md` - 标准范例
- `system_prompt_minimal.md` - 执行规则
