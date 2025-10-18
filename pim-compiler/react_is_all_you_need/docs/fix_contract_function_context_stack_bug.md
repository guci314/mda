# Bug修复：契约函数必须使用Context栈

## Bug描述

**问题**：执行@sayHello1时，智能体在单个Context中平铺所有步骤，没有为嵌套的契约函数调用启动新Context。

**错误执行**：
```
执行@sayHello1
├─ 初始化1个Context: "执行契约函数 @sayHello1"
├─ 添加4个Task:
│   ├─ 执行@sayHello1函数
│   ├─ 调用@sayHello2函数  ← 应该启动新Context，但没有
│   ├─ 调用@sayHello3函数  ← 应该启动新Context，但没有
│   └─ 计算最终结果
└─ 在同一个Context中执行所有Task

问题：
- 没有Context栈
- 没有函数调用栈语义
- @sayHello2和@sayHello3没有独立的栈帧
```

**正确执行**（应该是）：
```
执行@sayHello1
├─ context.push("执行@sayHello1")  # depth=1
├─ x = "kkk"
├─ 调用@sayHello2 → context.push("执行@sayHello2")  # depth=2
│  ├─ x = "ppp"
│  ├─ 调用@sayHello3 → context.push("执行@sayHello3")  # depth=3
│  │  ├─ return "qqq"
│  │  └─ context.pop()  # 返回"qqq"
│  ├─ z = "pppqqq"
│  └─ context.pop()  # 返回"pppqqq"
├─ z = "kkkpppqqq"
└─ context.pop()  # 返回"kkkpppqqq"

正确：
- 有Context栈（depth: 1→2→3→2→1→0）
- 每个契约函数有独立的栈帧
- 符合函数调用栈语义
```

## 修复方案

### 设计决策

根据你的指导：

1. **识别机制**：显式标记
   - `## 函数 @x` = 软约束函数
   - `## 契约函数 @y` = 契约函数，必须启动新Context栈帧

2. **实现位置**：在Agent执行引擎中（自动化）
   - 智能体执行时自动检测函数类型
   - 自动决定是否push/pop Context

3. **Context栈复杂度**：已实现
   - ExecutionContext已有push/pop方法
   - 只需告诉智能体规则即可

### 实现方式

**不需要改代码，只需更新知识文件**：

#### 1. 创建知识文件
`knowledge/contract_function_context_stack.md`
- 说明Context栈规则
- 提供查询索引的方法
- 给出完整执行示例

#### 2. 更新system_prompt
`knowledge/minimal/system/system_prompt_minimal.md`
- 在"契约函数执行规则"章节添加Context栈规则
- 说明如何查询函数类型
- 提供执行决策伪代码

## 关键规则

### 规则1：查询函数类型

```python
# 读取知识函数索引
index = read_file("knowledge_function_index.json")
index_data = json.loads(index)

# 查询函数类型
func_info = index_data["functions"][func_name]
func_type = func_info["func_type"]  # "contract" 或 "soft"
```

### 规则2：契约函数 → 压栈

```python
if func_type == "contract":
    # 压栈
    context(action="push", goal=f"执行@{func_name}")

    # 执行契约函数
    # ...

    # 出栈并获取返回值
    result = context(action="pop")
    return_value = result.get("return_value")
```

### 规则3：软约束函数 → 直接执行

```python
if func_type == "soft":
    # 直接执行，不需要Context栈
    result = execute_simple_function(func_name)
```

## 执行流程对比

### Bug执行（错误）

```python
# 执行@sayHello1
context.init_project(goal="执行@sayHello1")  # 单个Context
context.add_tasks([
    "执行@sayHello1",
    "调用@sayHello2",  # ❌ 应该压栈
    "调用@sayHello3",  # ❌ 应该压栈
    "计算结果"
])

# 问题：平铺的Task列表，没有栈结构
```

### 正确执行（修复后）

```python
# 执行@sayHello1
context.push(goal="执行@sayHello1")  # 压栈，depth=1

x = "kkk"

# 遇到"调用@sayHello2"
# 查询索引：是契约函数
context.push(goal="执行@sayHello2")  # 压栈，depth=2

  x = "ppp"

  # 遇到"调用@sayHello3"
  # 查询索引：是契约函数
  context.push(goal="执行@sayHello3")  # 压栈，depth=3

    return "qqq"

  result = context.pop()  # 出栈，depth=2
  y = "qqq"
  z = "pppqqq"

result = context.pop()  # 出栈，depth=1
y = "pppqqq"
z = "kkkpppqqq"

context.pop()  # 出栈，depth=0
return "kkkpppqqq"

# 正确：有栈结构，符合函数调用语义
```

## 智能体需要理解的要点

### 1. 知识函数索引是关键

**索引文件**：`knowledge_function_index.json`

**包含信息**：
```json
{
  "functions": {
    "sayHello1": {
      "func_type": "contract",  ← 类型信息
      "signature": "",
      ...
    },
    "loadBooks": {
      "func_type": "soft",  ← 类型信息
      "signature": "",
      ...
    }
  }
}
```

**智能体必须**：
- 执行知识函数前查询索引
- 根据func_type决定是否使用Context栈

### 2. Context工具的push/pop方法

**已实现的方法**：
```python
# 压栈（进入新的契约函数）
context(action="push", goal="执行@sayHello2")
# 返回: {"status": "success", "context_id": "xxx", "depth": 2}

# 出栈（契约函数完成）
context(action="pop")
# 返回: {
#     "status": "success",
#     "goal": "执行@sayHello2",
#     "return_value": "可以在这里记录返回值",
#     "depth": 1
# }
```

**智能体应该**：
- 调用契约函数前：push
- 契约函数完成后：pop
- 通过pop的返回值传递函数返回值

### 3. 递归调用自动处理

```python
def 执行契约函数(func_name):
    # 自动压栈
    context.push(goal=f"执行@{func_name}")

    # 读取函数定义并执行
    definition = load_function_definition(func_name)

    for step in definition.steps:
        if "调用@" in step or "@" in step:
            # 提取被调用的函数
            called_func = extract_function_name(step)

            # 查询类型
            called_type = query_function_type(called_func)

            if called_type == "contract":
                # 递归调用（会自动压栈）
                result = 执行契约函数(called_func)
            else:
                # 直接调用
                result = execute_simple(called_func)

    # 自动出栈
    context.pop()
```

## 验证方法

### 测试用例

执行以下测试，检查Context栈是否正确：

```python
# 测试1：单个契约函数
general_agent.execute("执行@sayHello3")
# 期望：context.push → 执行 → context.pop
# depth: 0 → 1 → 0

# 测试2：嵌套契约函数调用
general_agent.execute("执行@sayHello1")
# 期望：
# depth: 0 → 1 (@sayHello1)
#        → 2 (@sayHello2)
#        → 3 (@sayHello3)
#        → 2 (返回)
#        → 1 (返回)
#        → 0 (返回)

# 测试3：软约束函数调用
general_agent.execute("执行@loadBooks")
# 期望：直接执行，不改变depth
```

### 验证标准

**正确的输出应该显示**：
- ✅ push操作：进入Context: 执行@sayHello2
- ✅ depth变化：1 → 2 → 3 → 2 → 1 → 0
- ✅ pop操作：退出Context: 执行@sayHello2
- ✅ 返回值传递：qqq → pppqqq → kkkpppqqq

## 相关文件

### 创建的知识文件
- `knowledge/contract_function_context_stack.md` - Context栈规则详解

### 修改的文件
- `knowledge/minimal/system/system_prompt_minimal.md` - 添加Context栈规则
- `core/react_agent_minimal.py` - 修复add_function重复Bug

### 相关工具
- `core/tools/context_stack.py` - Context栈实现（已存在）
- `knowledge_function_index.json` - 函数类型索引

## 总结

### Bug的本质

**不是代码Bug，是执行语义Bug**：
- 代码层面：ExecutionContext已支持push/pop ✅
- 知识层面：智能体不知道何时该push/pop ❌

### 修复方案

**通过知识告诉智能体**：
- 什么是契约函数
- 如何查询函数类型
- 何时启动新Context栈帧
- 如何正确使用push/pop

### 核心洞察

**知识驱动执行**：
- 不需要改代码（工具已有push/pop）
- 只需告诉智能体规则
- 智能体会自动检测并正确执行

这就是"知识驱动开发"的体现：用知识而非代码定义行为！

### 下一步

让智能体重新执行 `执行@sayHello1`，验证Context栈是否正确工作。