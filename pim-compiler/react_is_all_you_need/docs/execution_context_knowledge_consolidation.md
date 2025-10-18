# ExecutionContext知识整合

## 整合目标

**将ExecutionContext的知识集中到system_prompt中**

### 原因

1. **减少知识分散**：不需要智能体到处找ExecutionContext的说明
2. **默认加载**：system_prompt默认加载，智能体启动就知道
3. **避免冗余**：一个地方维护，不需要多个文件

## 整合方案

### 删除的文件

**contract_function_context_stack.md**

**原因**：
- 内容已整合到system_prompt_minimal.md
- 避免知识重复
- 减少智能体需要主动读取的文件数量

### 整合到的位置

**knowledge/minimal/system/system_prompt_minimal.md**

**整合的内容**：
1. Context栈规则（契约函数调用契约函数必须压栈）
2. 函数类型识别方法（定义标记 + 索引查询）
3. 执行决策流程（查询索引 → 判断类型 → 决定是否压栈）
4. Context栈完整示例（@sayHello1 → @sayHello2 → @sayHello3）
5. 软约束函数对比（直接执行，不压栈）
6. 智能体必须理解的要点

## 整合后的结构

### system_prompt_minimal.md章节

```markdown
## 契约函数执行规则

### 强制要求
- 使用ExecutionContext
- 严格按步骤执行
- 外部化中间状态

### Context栈规则（重要）⚠️
- 契约函数调用契约函数 → 必须压栈
- 函数类型识别方法
- 执行决策流程
- Context栈完整示例
- 软约束函数对比
- 智能体必须理解的要点

### ExecutionContext基本用法
- init_project
- add_tasks
- start_task/complete_task
- set_data/get_data
- push/pop（栈操作）

### 核心原则
- 外部化判断
- 符号主义验证
- 严格执行
```

## 整合的好处

### 1. 集中管理

**之前**：
```
system_prompt_minimal.md - ExecutionContext基本用法
contract_function_context_stack.md - Context栈规则
knowledge_function_concepts.md - 知识函数概念
```

**现在**：
```
system_prompt_minimal.md - ExecutionContext完整知识
  ├─ 基本用法
  ├─ Context栈规则
  └─ 执行决策
```

### 2. 默认可用

**之前**：
- system_prompt默认加载（基本用法）
- contract_function_context_stack需要主动读取（栈规则）

**现在**：
- system_prompt默认加载（完整知识）
- 智能体启动就知道所有规则

### 3. 减少文件数

**知识文件数量**：
- 删除1个文件
- 减少智能体需要主动读取的文件
- 简化知识结构

## 需要手动删除的文件

由于权限问题，无法自动删除，请手动执行：

```bash
rm /Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/contract_function_context_stack.md
```

## 索引更新

删除文件后需要重新生成索引：

```bash
cd /Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need
python3.12 test_knowledge_index.py
```

**预期结果**：
- contract_function_context_stack.md相关的函数定义会消失
- 总函数数会减少（因为它包含了示例函数定义）

## 相关文档更新

需要更新引用contract_function_context_stack.md的文档：

### 1. self_awareness.md

**删除引用**：
```markdown
> 📖 详细说明见：`contract_function_context_stack.md`
```

**改为**：
```markdown
> 📖 详细说明见system_prompt中的"Context栈规则"章节
```

### 2. docs/fix_contract_function_context_stack_bug.md

**更新**：
- 说明知识已整合到system_prompt
- 不再引用contract_function_context_stack.md

## 总结

### 整合完成

✅ **ExecutionContext知识现在集中在**：
- `knowledge/minimal/system/system_prompt_minimal.md`

✅ **包含内容**：
- ExecutionContext基本用法
- Context栈规则（契约函数调用）
- 函数类型识别
- 执行决策流程
- 完整示例

✅ **好处**：
- 知识集中，不分散
- 默认加载，启动就知道
- 维护简单，一个地方更新

### 下一步

1. 手动删除contract_function_context_stack.md
2. 重新生成索引
3. 更新相关文档的引用
4. 验证Context栈执行是否正确