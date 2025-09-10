# ExecutionContext使用指南

## 核心理念
ExecutionContext是**可选的任务记录本**，用于管理复杂任务。简单任务不需要使用。

## 使用判断：何时需要ExecutionContext？

### ✅ 需要使用的场景
1. **多步骤任务**（3个或更多独立步骤）
2. **复杂调试**（多文件问题、多轮尝试、系统性排查）
3. **项目构建**（创建多个文件、设置配置）
4. **状态跟踪**（需要记住中间结果和决策）
5. **数据分析**（处理多个文件或大量数据）
6. **深度探索**（递归搜索、全面扫描）

### ❌ 不需要使用的场景
1. **简单对话**（解释概念、回答问题）
2. **单文件操作**（读取、简单修改）
3. **简单修复**（除零错误、空值检查等明显问题）
4. **单元测试修复**（修复单个测试文件）
5. **快速查询**（搜索、运行简单命令）
6. **知识问答**（基于已有知识回答）
7. **小改动**（修改单行、添加注释）

## 新API使用方法

### 1. 初始化工作流
```python
# 第一步：总是先初始化项目（含用户原始指令）
context(action="init_project", goal="用户的原始需求描述")
```

### 2. 任务管理
```python
# 批量添加任务
context(action="add_tasks", tasks=["分析", "设计", "实现", "测试"])

# 批量删除任务（如果需要）
context(action="remove_tasks", tasks=["不需要的任务"])

# 执行任务
context(action="start_task", task="分析")
context(action="complete_task", task="分析", result="完成分析，发现3个问题")

# 任务失败
context(action="fail_task", task="实现", result="环境配置错误")
```

### 3. 状态管理
```python
# 设置语义化的当前状态
context(action="set_state", state="正在编译代码...")
context(action="get_state")  # 获取当前状态
```

### 4. 数据存储（自由空间）
```python
# 存储小型数据（状态、计数、标记等）
context(action="set_data", key="error_count", value=3)
context(action="set_data", key="test_results", value={"passed": 10, "failed": 2})

# 读取数据
context(action="get_data", key="error_count")

# 删除数据
context(action="delete_data", key="temp_data")
```

**⚠️ 注意**：
- 只存储小型状态数据（数字、短字符串、小对象）
- **不要存储文档内容** - 直接使用write_file工具
- **不要存储大量文本** - 这不是文档缓存

### 5. 全局查询
```python
# 获取完整执行上下文
context(action="get_context")
```

## API概览

### ✅ 核心API
```python
# 项目管理
context(action="init_project", goal="用户需求")
context(action="add_tasks", tasks=[...])
context(action="remove_tasks", tasks=[...])
context(action="start_task", task="任务名")
context(action="complete_task", task="任务名", result="结果")
context(action="fail_task", task="任务名", result="失败原因")

# 状态管理
context(action="set_state", state="当前状态描述")
context(action="get_state")

# 数据存储
context(action="set_data", key="xxx", value="yyy")
context(action="get_data", key="xxx")
context(action="delete_data", key="xxx")

# 全局查询
context(action="get_context")
```

## 关键优势

1. **语义清晰** - `start_task`、`complete_task`等动作一目了然
2. **任务名代替ID** - 使用描述性名称，避免ID混淆
3. **简化设计** - 只记录不调度，执行顺序由Agent决定
4. **灵活存储** - 通用KV存储提供自由空间
5. **动态调整** - 随时添加/删除任务

## 最佳实践

### 完整工作流示例
```python
# 1. 开始时捕获用户意图
context(action="init_project", goal=user_request)

# 2. 制定执行计划
context(action="add_tasks", tasks=["步骤1", "步骤2", "步骤3"])

# 3. 按Agent决定的顺序执行任务
for task in ["步骤1", "步骤2", "步骤3"]:  # Agent自主决定顺序
    context(action="start_task", task=task)
    context(action="set_state", state=f"正在执行{task}...")
    # ... 执行具体工作 ...
    context(action="complete_task", task=task, result="...")

# 4. 存储重要数据
context(action="set_data", key="final_result", value=result)

# 5. 查看完整上下文
context(action="get_context")
```

## 注意事项

1. **任务名必须唯一** - 使用描述性名称避免重复
2. **执行顺序自主决定** - Agent决定任务执行顺序，工具只负责记录
3. **纯内存操作** - 状态只在内存中维护，不持久化到文件
4. **语义化状态** - 状态描述要清晰，让人一看就懂

## 这解决了什么问题？

1. ✅ **不再有"未找到任务X"错误** - 使用任务名而非ID
2. ✅ **更简单的设计** - 去除复杂的依赖管理，由Agent自主决定
3. ✅ **更像记录本** - 简单记录，不做复杂调度
4. ✅ **灵活的数据存储** - 通用KV存储适应各种需求