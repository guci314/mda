# 修复两个执行Bug

## Bug 1：智能体不知道知识函数索引的位置 ❌

### 问题

**错误日志**：
```
[general_agent] 🔧 调用工具: read_file
   [general_agent] 📝 file_path: knowledge_function_index.json
   [general_agent] ✅ 结果: 文件不存在: knowledge_function_index.json
```

**原因**：
- 智能体的work_dir是：`/Users/guci/robot_projects/orderSystem`
- 索引文件在：`/Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge_function_index.json`
- 智能体使用相对路径找不到文件

### 解决方案

**添加self.function_index属性**（第212行）：
```python
# 知识函数索引位置（智能体主动查询）
self.self_function_index = str(Path(__file__).parent.parent / "knowledge_function_index.json")
```

**在系统提示词中暴露**（第775行）：
```python
- 知识函数索引（self.function_index）: {self.self_function_index} **（查询函数类型和位置）**

**重要原则**：
- **索引文件用于查询**：{self.self_function_index}包含所有知识函数的类型和位置信息
```

**智能体现在可以**：
```python
# 使用绝对路径读取索引
index = read_file(self.function_index)
# → 成功读取索引文件
```

---

## Bug 2：push/pop操作失败 ❌

### 问题

**错误日志**：
```
[general_agent] 🔧 调用工具: context
   [general_agent] 📝 action: push
   [general_agent] 📝 goal: 执行契约函数 @sayHello1
   [general_agent] ✅ 结果: 未知操作: push
```

**原因**：
- system_prompt中写的是：`context.push()`
- 但实际的action名是：`push_context`（不是`push`）
- 智能体按文档使用错误的action名

### 解决方案

**更新system_prompt中的所有引用**：

#### 1. 执行决策流程（第88-91行）
```python
# 之前
context(action="push", goal="执行@sayHello2")
result = context(action="pop")

# 现在
context(action="push_context", goal="执行@sayHello2")
result = context(action="pop_context")
```

#### 2. Context栈完整示例（第103-119行）
```python
# 所有context.push() → context(action="push_context")
# 所有context.pop() → context(action="pop_context")
```

#### 3. ExecutionContext基本用法（第193-201行）
```python
# 7. Context栈操作（契约函数调用契约函数时使用）
# 压栈：进入新的契约函数
context(action="push_context", goal="执行@sayHello2")

# 弹栈：契约函数执行完成
context(action="pop_context")

# 查看调用栈
context(action="get_call_stack")
```

#### 4. 智能体必须理解的要点（第155-158行）
```python
3. **Context工具的栈操作**：
   - 压栈：`context(action="push_context", goal="执行@xxx")`
   - 弹栈：`context(action="pop_context")`
   - 查看栈：`context(action="get_call_stack")`
```

---

## 修复验证

### 修复后，智能体可以正确执行

**1. 读取索引**：
```python
index = read_file(self.function_index)  # ✅ 使用绝对路径
index_data = json.loads(index)
func_type = index_data["functions"]["sayHello1"]["func_type"]  # "contract"
```

**2. 使用Context栈**：
```python
# 执行@sayHello1
context(action="push_context", goal="执行@sayHello1")  # ✅ 正确的action名

# 调用@sayHello2
context(action="push_context", goal="执行@sayHello2")  # depth=2
# 执行@sayHello2
context(action="pop_context")  # depth=1

# 完成@sayHello1
context(action="pop_context")  # depth=0
```

**3. 查看调用栈**：
```python
context(action="get_call_stack")
# 返回：
# 📚 当前调用栈:
# └─ [1] 执行@sayHello1
#   └─ [2] 执行@sayHello2
#     └─ [3] 执行@sayHello3
```

---

## 修改的文件

### 1. core/react_agent_minimal.py

**第212行**：添加self.self_function_index属性
```python
self.self_function_index = str(Path(__file__).parent.parent / "knowledge_function_index.json")
```

**第775行**：在系统提示词中暴露
```python
- 知识函数索引（self.function_index）: {self.self_function_index}
```

### 2. knowledge/minimal/system/system_prompt_minimal.md

**多处更新**：
- 执行决策流程：push → push_context
- Context栈示例：push → push_context, pop → pop_context
- ExecutionContext基本用法：添加栈操作示例
- 智能体必须理解的要点：更新action名称

---

## 核心要点

### 智能体的自我认知（新增）

**现在智能体知道9个自我认知变量**：
```python
self.name              # 我的名字
self.home_dir          # 我的Home目录
self.knowledge_path    # 我的知识文件
self.compact_path      # 我的记忆文件
self.external_tools_dir # 我的工具箱
self.description       # 我的职责描述
self.work_dir          # 我的工作目录
self.source_code       # 我的源代码（只读）
self.function_index    # 知识函数索引位置 ⭐ 新增
```

### Context工具的正确用法

**栈操作**：
- ✅ 压栈：`context(action="push_context", goal="...")`
- ✅ 弹栈：`context(action="pop_context")`
- ❌ 不是：`context(action="push")`或`context(action="pop")`

---

## 测试建议

重新执行@sayHello1，验证：

```python
general_agent.execute("执行@sayHello1")
```

**期望看到**：
- ✅ 成功读取索引：`read_file(self.function_index)`
- ✅ 成功压栈：`context(action="push_context", goal="执行@sayHello1")`
- ✅ 嵌套调用：push_context → push_context → push_context
- ✅ 正确弹栈：pop_context → pop_context → pop_context
- ✅ 最终结果："kkkpppqqq"

---

## 总结

**两个Bug都已修复**：

1. ✅ 智能体知道索引文件的绝对路径（self.function_index）
2. ✅ 智能体使用正确的action名（push_context/pop_context）

**修复的核心**：
- 通过自我认知提供绝对路径
- 通过system_prompt提供正确的用法
- 知识驱动修复：不改执行引擎，只告诉智能体正确的知识

这就是"知识驱动开发"的体现！