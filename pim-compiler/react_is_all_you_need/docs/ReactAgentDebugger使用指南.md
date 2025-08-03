# ReactAgentDebugger 使用指南

## 概述

ReactAgentDebugger 是一个为 GenericReactAgent 设计的调试工具，它可以帮助开发者深入理解 Agent 的执行流程，调试复杂的任务执行逻辑，优化提示词和知识文件。

## 核心概念

### 1. 原子步骤（Atomic Steps）

基于 LangGraph 的执行流程，调试器将 Agent 的执行过程分解为三个原子步骤：

- **THINK（思考）**：AI 分析当前状态，决定下一步行动
- **ACT（行为）**：执行具体操作（调用工具或生成响应）
- **OBSERVE（观察）**：获取执行结果，更新状态

### 2. 断点类型

#### 2.1 步骤断点（StepBreakpoint）
在特定类型的原子步骤暂停：
```python
# 在每个 THINK 步骤暂停
debugger.add_breakpoint(StepBreakpoint("bp1", StepType.THINK))
```

#### 2.2 工具断点（ToolBreakpoint）
在调用特定工具时暂停：
```python
# 在调用 write_file 工具时暂停
debugger.add_breakpoint(ToolBreakpoint("bp2", "write_file"))
```

#### 2.3 Agent 断点（AgentBreakpoint）
在调用特定子 Agent 时暂停：
```python
# 在调用 code_generator Agent 时暂停
debugger.add_breakpoint(AgentBreakpoint("bp_agent", "code_generator"))
```

#### 2.4 条件断点（ConditionalBreakpoint）
满足特定条件时暂停：

##### 基本语法
```python
debugger.add_breakpoint(
    ConditionalBreakpoint(
        id="唯一标识符",
        condition=lambda ctx: 布尔表达式,
        condition_str="条件描述"
    )
)
```

##### 上下文参数 (ctx)
- `step_type`: 当前步骤类型 (THINK/ACT/OBSERVE)
- `messages`: 完整消息历史
- `last_message`: 最新消息
- `tool_calls`: 工具调用列表
- `depth`: 调用深度

##### 常用条件示例

**1. 基于消息内容**
```python
# 包含错误信息
lambda ctx: "error" in str(ctx.get("last_message", "")).lower()

# 消息长度超过阈值
lambda ctx: len(str(ctx.get("last_message", ""))) > 100

# 提到特定文件
lambda ctx: ".py" in str(ctx.get("last_message", ""))
```

**2. 基于步骤类型**
```python
# 只在思考步骤
lambda ctx: ctx.get("step_type") == StepType.THINK

# AI 决定调用工具
lambda ctx: (
    ctx.get("step_type") == StepType.ACT and 
    len(ctx.get("tool_calls", [])) > 0
)
```

**3. 基于工具调用**
```python
# 调用特定工具
lambda ctx: any(
    tc.get("name") == "write_file" 
    for tc in ctx.get("tool_calls", [])
)

# 基于工具参数
lambda ctx: any(
    tc.get("name") == "write_file" and
    "test" in tc.get("args", {}).get("file_path", "")
    for tc in ctx.get("tool_calls", [])
)
```

**4. 组合条件**
```python
# AND 条件
lambda ctx: (
    ctx.get("step_type") == StepType.ACT and
    "python" in str(ctx.get("last_message", "")).lower()
)

# OR 条件
lambda ctx: (
    "error" in str(ctx.get("last_message", "")).lower() or
    "failed" in str(ctx.get("last_message", "")).lower()
)
```

**5. 有状态条件**
```python
# 使用外部计数器
counter = {"calls": 0}
def count_calls(ctx):
    if ctx.get("step_type") == StepType.ACT:
        counter["calls"] += 1
    return counter["calls"] >= 3

debugger.add_breakpoint(
    ConditionalBreakpoint("bp_3rd_call", count_calls, "第3次调用工具")
)
```

### 3. 执行控制

调试器支持多种执行控制模式：

- **RUN**：正常运行到下一个断点
- **STEP**：执行一个原子步骤
- **STEP_IN**：步入子 Agent 调用内部（仅对子 Agent 有效）
- **STEP_OUT**：退出当前子 Agent（仅在子 Agent 内部有效）
- **STEP_OVER**：跳过工具调用细节

**重要说明**：
- `step in` 和 `step out` 仅对子 Agent 调用有效
- 对于普通工具（如 write_file、execute_command），使用 `step over` 即可
- 调试器会自动识别子 Agent 调用，并在调用栈中跟踪

## 快速开始

### 1. 基本使用

```python
from react_agent import GenericReactAgent, ReactAgentConfig
from react_agent_debugger import ReactAgentDebugger, StepType, StepBreakpoint

# 创建 agent
config = ReactAgentConfig(work_dir="output/debug")
agent = GenericReactAgent(config)

# 创建调试器
debugger = ReactAgentDebugger(agent)

# 设置断点
debugger.add_breakpoint(StepBreakpoint("bp1", StepType.THINK))

# 执行任务
debugger.execute_task("创建一个 hello.txt 文件")
```

### 2. 调试命令

在调试会话中，可以使用以下命令：

| 命令 | 简写 | 说明 |
|------|------|------|
| continue | c | 继续执行到下一个断点 |
| step | s | 执行一个原子步骤 |
| step in | si | 步入工具调用 |
| step out | so | 步出当前层级 |
| step over | sv | 步过工具调用 |
| print | p | 打印当前状态 |
| breakpoints | b | 列出所有断点 |
| history | h | 显示执行历史 |
| sm | - | 列出所有消息的索引和预览 |
| sm X | - | 显示第 X 个消息的详细内容 |
| help | ? | 显示帮助信息 |
| quit | q | 退出调试 |

## 高级功能

### 1. 复杂条件断点

```python
# 在调用深度大于 2 时暂停
debugger.add_breakpoint(
    ConditionalBreakpoint(
        "deep_call",
        lambda ctx: ctx.get("depth", 0) > 2,
        "调用深度 > 2"
    )
)

# 在处理 Python 文件时暂停
debugger.add_breakpoint(
    ConditionalBreakpoint(
        "python_file",
        lambda ctx: any(".py" in str(tc.get("args", {})) 
                      for tc in ctx.get("tool_calls", [])),
        "处理 Python 文件"
    )
)
```

### 2. 断点管理

```python
# 列出所有断点
breakpoints = debugger.list_breakpoints()

# 禁用断点
debugger.enable_breakpoint("bp1", enabled=False)

# 删除断点
debugger.remove_breakpoint("bp1")
```

### 3. 状态检查

在调试会话中，使用 `p` 命令可以查看：

- 当前步骤类型
- 消息历史
- 工具调用信息
- 调用栈
- 执行深度

### 4. 查看消息

#### 列出所有消息 (sm)

使用 `sm` 命令可以查看所有消息的列表：

```
🐛 调试器> sm

📬 消息列表 (共 5 条):
================================================================================
[  0] 👤 HumanMessage     | 创建一个 hello.txt 文件
[  1] 💻 SystemMessage    | 你是一个智能助手，能够帮助用户完成各种任务...
[  2] 🤖 AIMessage        | 调用工具: write_file
[  3] 🔧 ToolMessage      | 文件创建成功
[  4] 🤖 AIMessage        | 我已经成功创建了 hello.txt 文件，内容为 "Hello, World!"
================================================================================
提示: 使用 'sm X' 查看特定消息的详细内容
```

#### 查看特定消息详情 (sm X)

使用 `sm X` 命令可以查看特定索引的消息详情：

```
🐛 调试器> sm 0

📧 消息 #0
================================================================================
类型: HumanMessage

内容:
----------------------------------------
创建一个 hello.txt 文件
----------------------------------------
================================================================================
```

该命令会显示：
- 消息类型（HumanMessage/AIMessage/ToolMessage/SystemMessage）
- 消息内容全文
- 工具调用详情（如果是 AIMessage）
- 工具名称和参数（如果包含工具调用）
- 工具调用 ID 等额外信息

## 可观察的状态信息

触发断点时，使用 `p` 命令可以查看以下详细状态：

### 1. 🎯 执行状态
- **当前步骤类型**：THINK/ACT/OBSERVE
- **调用深度**：子 Agent 嵌套层级
- **执行历史长度**：已执行的步骤数
- **调试模式**：RUN/STEP/STEP_IN/STEP_OUT/STEP_OVER

### 2. 💬 当前消息
- **消息类型**：HumanMessage/AIMessage/ToolMessage/SystemMessage
- **消息内容**：完整或截断显示（超过200字符）
- **工具调用数**：当前消息包含的工具调用
- **工具名称**：如果是工具返回消息

### 3. 📜 消息历史
- **总消息数**：完整对话历史长度
- **最近消息**：最近5条消息的格式化显示
- **消息类型分布**：各类消息的数量

### 4. 🔧 工具调用详情
- **工具名称**：被调用的工具
- **调用参数**：完整参数键值对（长参数会截断）
- **工具类型**：识别是普通工具还是子 Agent
- **调用顺序**：多个工具调用的索引

### 5. 🤖 Agent 信息
- **Agent 名称**：当前 Agent 的标识
- **工作目录**：文件操作的基础路径
- **记忆级别**：NONE/SMART/PRO
- **LLM 模型**：使用的语言模型

### 6. 📚 Agent 调用栈
- **栈内容**：仅显示子 Agent 调用
- **调用层级**：从外到内的调用顺序
- **当前深度**：嵌套层数

### 7. 🔴 断点信息
- **活跃断点数**：当前启用的断点
- **断点详情**：类型、条件、目标
- **命中次数**：各断点的触发统计

### 8. 📈 执行统计
- **步骤分布**：THINK/ACT/OBSERVE 各执行了多少次
- **执行效率**：识别执行模式和瓶颈

### 9. 💾 系统状态
- **知识文件**：是否加载及大小
- **记忆系统**：是否激活
- **工作目录内容**：当前创建的文件

### 状态查看示例

```
================================================================================
📊 调试器状态视图
================================================================================

🎯 执行状态:
  当前步骤类型: ACT
  调用深度: 1
  执行历史长度: 8 步
  调试模式: STEP

💬 当前消息:
  类型: AIMessage
  工具调用数: 1

📜 消息历史 (最近 5 条，共 12 条):
  [7] 👤 用户: 创建一个 hello.py 文件
  [8] 💻 系统: 你是一个智能助手...
  [9] 🤔 AI 决定调用工具: write_file
  [10] 🔧 工具结果 (write_file): 文件创建成功
  [11] 💬 AI: 我已经创建了 hello.py 文件

🔧 工具调用详情:
  [0] 工具: write_file
      参数:
        - file_path: hello.py
        - content: print("Hello, World!")
      类型: 普通工具

🤖 Agent 信息:
  名称: demo_agent
  工作目录: output/debug_demo
  记忆级别: MemoryLevel.SMART
  LLM 模型: deepseek-chat

📚 Agent 调用栈: (空)

🔴 活跃断点 (2 个):
  - bp_act (StepBreakpoint) - ACT
  - bp_write (ToolBreakpoint) - write_file

📈 执行统计:
  THINK: 3 次
  ACT: 3 次
  OBSERVE: 2 次

📚 知识文件: 已加载 (2456 字符)
💾 记忆系统: 活跃
================================================================================
```

## 调试技巧

### 1. 调试提示词问题

当 Agent 行为不符合预期时：
1. 在 THINK 步骤设置断点
2. 观察 AI 的决策过程
3. 检查系统提示词和知识文件是否正确加载

### 2. 调试工具调用

当工具调用出错时：
1. 在特定工具设置断点
2. 检查工具参数是否正确
3. 使用 step in 进入工具执行细节

### 3. 调试复杂工作流

对于多步骤任务：
1. 使用条件断点捕获特定状态
2. 使用执行历史追踪问题源头
3. 使用 step over 快速跳过已验证的部分

## 示例场景

### 场景 1：调试文件操作错误

```python
# 设置断点捕获错误
debugger.add_breakpoint(
    ConditionalBreakpoint(
        "file_error",
        lambda ctx: "file not found" in str(ctx.get("last_message", "")).lower(),
        "文件未找到错误"
    )
)
```

### 场景 2：分析决策逻辑

```python
# 在所有 THINK 步骤暂停，分析 AI 决策
debugger.add_breakpoint(StepBreakpoint("think_bp", StepType.THINK))
debugger.verbose = True  # 显示详细信息
```

### 场景 3：优化工具使用

```python
# 监控所有工具调用
debugger.add_breakpoint(StepBreakpoint("act_bp", StepType.ACT))

# 执行任务后，查看工具调用统计
# 在调试会话结束后会显示执行统计
```

## 最佳实践

1. **从简单开始**：先使用步骤断点理解基本流程
2. **逐步细化**：根据发现的问题添加更具体的断点
3. **保存断点配置**：为常见调试场景创建断点集合
4. **结合日志**：设置 `DEBUG=1` 环境变量查看更多细节
5. **注意性能**：调试模式会降低执行速度，生产环境请关闭

## 故障排除

### 问题：断点不触发
- 检查断点是否启用
- 确认断点条件是否正确
- 使用 `list_breakpoints()` 查看断点状态

### 问题：执行卡住
- 使用 `q` 命令退出调试
- 检查是否有无限循环的工具调用
- 降低任务复杂度进行分步调试

### 问题：状态信息不全
- 确保 `verbose = True`
- 使用 `p` 命令手动查看状态
- 检查消息历史长度限制

## 扩展开发

调试器设计为可扩展的，您可以：

1. 创建自定义断点类型
2. 添加新的调试命令
3. 实现图形化调试界面
4. 集成到 IDE 中

```python
# 自定义断点示例
class MemoryBreakpoint(Breakpoint):
    """当记忆使用超过阈值时暂停"""
    def __init__(self, id: str, threshold: int):
        super().__init__(id)
        self.threshold = threshold
    
    def should_break(self, context: Dict[str, Any]) -> bool:
        messages = context.get("messages", [])
        return len(messages) > self.threshold
```

## 总结

ReactAgentDebugger 是理解和优化 GenericReactAgent 行为的强大工具。通过合理使用断点和执行控制，您可以：

- 深入理解 Agent 的思考过程
- 快速定位和解决问题
- 优化提示词和知识文件
- 提高 Agent 的执行效率

记住，调试不仅是解决问题的工具，也是学习 Agent 行为模式的最佳方式。