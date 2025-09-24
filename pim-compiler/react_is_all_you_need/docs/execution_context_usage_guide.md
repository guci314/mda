# ExecutionContext 正确使用指南

## ✅ 已修复：pop_context 现在正确恢复任务列表

### 修复内容（2025-09-22）
**`pop_context()` 现在能正确恢复父Context的完整状态**，包括任务列表和数据。

### 关键改进
1. **init_project创建根Context**：主函数也有Context，深度为1
2. **push_context保存当前状态**：在创建新Context前保存当前project
3. **pop_context恢复完整状态**：从父Context恢复所有任务和数据
4. **防止过度pop**：不允许pop根Context（深度1）

## 正确的使用模式

### 模式1：完整的任务管理流程（修复后）
```python
# 主函数
context(action="init_project", goal="主函数")  # 创建根Context，深度=1
context(action="add_tasks", tasks=["任务A", "调用子函数", "任务B"])

# 执行任务A
context(action="start_task", task="任务A")
# ... 执行任务A ...
context(action="complete_task", task="任务A")

# 调用子函数
context(action="start_task", task="调用子函数")
context(action="push_context", goal="子函数")  # 深度=2，自动保存当前state

  # 子函数内部
  context(action="add_tasks", tasks=["子任务1", "子任务2"])
  # ... 执行子任务 ...

context(action="pop_context")  # 深度=1，恢复主函数的完整state
# ✅ 任务列表恢复：["任务A"(完成), "调用子函数"(完成), "任务B"(待办)]

# 继续执行任务B
context(action="start_task", task="任务B")
# ... 执行任务B ...
context(action="complete_task", task="任务B")
```

### 模式2：简单函数调用（无任务跟踪）
```python
@简单函数():
  context(action="push_context", goal="执行简单函数")

  # 直接调用，不创建任务
  result1 = @子函数1()
  result2 = @子函数2()
  final = combine(result1, result2)

  context(action="pop_context")
  return final
```

### 模式3：复杂流程（多阶段任务）
```python
@复杂流程():
  context(action="push_context", goal="执行复杂流程")

  # 阶段1：准备
  context(action="add_tasks", tasks=["准备数据"])
  context(action="start_task", task="准备数据")
  data = prepare_data()
  context(action="complete_task", task="准备数据", result="数据已准备")

  # 阶段2：处理（包含子函数调用）
  context(action="add_tasks", tasks=["调用处理函数"])
  context(action="start_task", task="调用处理函数")
  processed = @处理函数(data)  # push/pop自动完成任务

  # 阶段3：完成（重新添加任务）
  context(action="add_tasks", tasks=["保存结果"])
  context(action="start_task", task="保存结果")
  save(processed)
  context(action="complete_task", task="保存结果", result="已保存")

  context(action="pop_context")
  return processed
```

## 修复前的问题（已解决）

### 旧版本问题：pop_context会清空任务列表
在修复前，`pop_context`会创建一个新的空project，导致任务列表丢失。

### ✅ 现在已修复：任务列表正确保存和恢复
```python
# 修复后的正确行为
context(action="init_project", goal="主函数")  # 深度=1
context(action="add_tasks", tasks=["任务1", "任务2", "任务3"])

context(action="push_context", goal="子函数")  # 深度=2，保存主函数state
# ... 子函数逻辑 ...
context(action="pop_context")  # 深度=1，恢复主函数state

# ✅ 任务1、任务2、任务3都还在！
context(action="get_context")  # 可以看到所有任务
```

## 核心原则

### 1. Context栈的层次结构
- **深度0**：无Context（初始状态）
- **深度1**：根Context（主函数，通过init_project创建）
- **深度2+**：嵌套函数调用

### 2. 状态保存和恢复
- **push时自动保存**：当前project保存到当前Context的data中
- **pop时自动恢复**：从父Context的data恢复完整project

### 3. push/pop 即执行
对于函数调用类型的任务，`push_context` + `pop_context` 就代表任务的执行和完成。

### 4. 防护机制
- 不允许pop根Context（深度必须>1）
- 确保总有一个Context在栈中

## 实际案例：@hello 函数执行

### 修复后的正确执行流程
```python
# 深度0 → 深度1（根Context）
init_project("主程序")  # 创建根Context

# 深度1 → 深度2
push_context("执行知识函数: hello")  # 保存根Context的state
add_tasks(["调用hello2函数", "组合最终结果"])

# 深度2 → 深度3
start_task("调用hello2函数")
push_context("执行知识函数: hello2")  # 保存hello的state
add_tasks(["调用hello1函数", "组合hello2结果"])

# 深度3 → 深度4
start_task("调用hello1函数")
push_context("执行知识函数: hello1")  # 保存hello2的state
add_tasks(["返回hello1结果"])
complete_task("返回hello1结果", "今天天气不错")
pop_context()  # 回到深度3，恢复hello2的state

# 深度3：hello2的任务列表自动恢复
start_task("组合hello2结果")  # ✅ 任务存在！
complete_task("组合hello2结果", "人的天性是善良的 今天天气不错")
pop_context()  # 回到深度2，恢复hello的state

# 深度2：hello的任务列表自动恢复
start_task("组合最终结果")  # ✅ 任务存在！
complete_task("组合最终结果", "你好 人的天性是善良的 今天天气不错")
pop_context()  # 回到深度1（根Context）
```

## 总结

### ✅ 修复后的新行为（2025-09-22）
1. **状态完整保存**：push_context时自动保存当前完整state
2. **状态完整恢复**：pop_context时自动恢复父Context的所有任务和数据
3. **层次结构清晰**：init_project创建根Context（深度1），防止过度pop
4. **无需手动管理**：Agent不需要担心任务丢失问题

### 设计优势
- **符合直觉**：函数调用返回后，父函数的状态应该保持不变
- **减少错误**：不需要手动重新添加任务
- **提高效率**：减少了重复的add_tasks操作
- **保持简洁**：知识函数可以更简单地编写