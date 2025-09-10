# Agent协调知识

## 核心原则
当一个Agent调用其他Agent时，必须理解执行上下文（Execution Context）的边界。

## 执行上下文管理规则 ⚠️

### 重要：每个Agent有独立的执行上下文
1. **你的执行上下文** - 存储在你的task_process.md中
2. **子Agent的执行上下文** - 存储在各自的task_process.md中
3. **不要混淆** - 调用子Agent不会改变你的执行上下文

### 正确的任务管理方式
```python
# ✅ 正确：创建自己的任务
context(action="create", todos=[
    {"task": "调用general_agent清理目录"},
    {"task": "调用psm_generation_agent生成PSM"},
    {"task": "调用code_generation_agent生成代码"},
    {"task": "调用debug_agent修复测试"}
])

# ✅ 正确：标记自己的任务完成
context(action="mark_complete", task_id=1)  # 完成"调用general_agent"任务

# ❌ 错误：试图操作不存在的任务
context(action="mark_complete", task_id=5)  # 你只创建了4个任务！
```

### 调用子Agent的正确流程
1. **标记自己的任务为执行中**
   ```
   context(action="mark_progress", task_id=2)  # "调用psm_generation_agent"
   ```

2. **调用子Agent**
   ```
   psm_generation_agent(task="生成PSM文档...")
   # 子Agent会创建自己的TODO，但与你无关
   ```

3. **标记自己的任务为完成**
   ```
   context(action="mark_complete", task_id=2)  # 完成你的任务2
   ```

## 状态管理

### 使用整数步骤
```python
# ✅ 正确
context(action="set_key", key="当前步骤", value="1")
context(action="set_key", key="当前步骤", value="2")

# ⚠️ 避免小数（grok可能不理解）
context(action="set_key", key="当前步骤", value="1.5")  # 不推荐
```

### 状态描述应该清晰
```python
# ✅ 正确
context(action="set_key", key="当前状态", value="正在调用psm_generation_agent")

# ❌ 避免
context(action="set_key", key="当前状态", value="2.1")  # 含义不清
```

## 最佳实践

### 1. 初始化时创建所有任务
```python
# 一次性创建所有顶层任务
context(action="create", todos=[
    {"task": "清理环境"},
    {"task": "生成PSM"},
    {"task": "生成代码"},
    {"task": "修复测试"}
])
```

### 2. 按顺序执行任务
```python
for task_id in [1, 2, 3, 4]:
    context(action="mark_progress", task_id=task_id)
    # 调用对应的Agent
    result = call_agent(...)
    context(action="mark_complete", task_id=task_id)
```

### 3. 不要创建不存在的任务ID
- 如果创建了4个任务，只能操作1-4
- 不要假设有任务5、6等
- 需要新任务时，使用add操作

### 4. Agent调用是黑盒
- 不需要知道子Agent内部如何工作
- 不需要管理子Agent的TODO
- 只关心子Agent是否完成了任务

## 记住
- **每个Agent的TODO是独立的**
- **只操作你自己创建的任务**
- **调用Agent ≠ 创建新TODO**
- **任务ID必须存在才能操作**

## 适用场景
这个知识适用于任何需要调用其他Agent的场景：
- Project Manager协调多个Agent
- Meta Agent创建和管理Agent
- 任何Agent嵌套调用其他Agent