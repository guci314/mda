# ReactAgentDebugger - GenericReactAgent 调试器

## 概述

ReactAgentDebugger 是一个专为 GenericReactAgent 设计的交互式调试器，基于 LangGraph 执行流程的原子步骤模型，提供断点、单步执行、状态查看等调试功能。

## 特性

- 🎯 **三种断点类型**：步骤断点、工具断点、条件断点
- 🚶 **灵活的执行控制**：单步执行、步入、步出、步过
- 📊 **状态实时查看**：消息历史、工具调用、调用栈
- 📈 **执行可视化**：生成 Mermaid 流程图和时序图
- 🔍 **深度追踪**：支持嵌套工具调用的调试

## 文件结构

```
react_agent_debugger.py    # 核心调试器实现
├── ReactAgentDebugger     # 主调试器类
├── StepBreakpoint         # 步骤断点
├── ToolBreakpoint         # 工具断点
└── ConditionalBreakpoint  # 条件断点

debug_demo.py             # 交互式演示程序
test_debugger.py          # 快速测试脚本
debug_visualizer.py       # 执行流程可视化工具

docs/
└── ReactAgentDebugger使用指南.md  # 详细文档
```

## 快速开始

### 1. 运行演示程序

```bash
# 交互式演示菜单
python debug_demo.py

# 快速测试
python test_debugger.py
```

### 2. 基本使用

```python
from react_agent import GenericReactAgent, ReactAgentConfig
from react_agent_debugger import ReactAgentDebugger, StepType, StepBreakpoint

# 创建 agent
config = ReactAgentConfig(work_dir="output/debug")
agent = GenericReactAgent(config)

# 创建调试器并设置断点
debugger = ReactAgentDebugger(agent)
debugger.add_breakpoint(StepBreakpoint("bp1", StepType.THINK))

# 执行任务
debugger.execute_task("创建一个 hello.txt 文件")
```

### 3. 调试命令

| 命令 | 说明 |
|------|------|
| `c` | 继续执行 |
| `s` | 单步执行 |
| `si` | 步入工具调用 |
| `so` | 步出当前层级 |
| `p` | 查看当前状态 |
| `sm` | 列出所有消息的索引和预览 |
| `sm X` | 显示第 X 个消息的详细内容 |
| `?` | 帮助信息 |

## 原子步骤模型

基于 LangGraph 的执行流程，调试器将执行过程分解为三个原子步骤：

1. **THINK（思考）** - AI 分析状态，决定行动
2. **ACT（行为）** - 执行工具调用或生成响应  
3. **OBSERVE（观察）** - 获取结果，更新状态

## 断点示例

### 步骤断点
```python
# 在所有思考步骤暂停
debugger.add_breakpoint(StepBreakpoint("think", StepType.THINK))
```

### 工具断点
```python
# 在调用 write_file 时暂停
debugger.add_breakpoint(ToolBreakpoint("write", "write_file"))
```

### 条件断点
```python
# 当出现错误时暂停
debugger.add_breakpoint(
    ConditionalBreakpoint(
        "error",
        lambda ctx: "error" in str(ctx.get("last_message", "")).lower(),
        "包含错误"
    )
)
```

## 高级功能

### 执行流程可视化

使用 `debug_visualizer.py` 生成可视化报告：

```python
from debug_visualizer import DebugVisualizer

# 生成 Markdown 报告（包含 Mermaid 图）
report = DebugVisualizer.generate_report(
    debugger.execution_history,
    "debug_report.md"
)
```

生成的报告包含：
- 执行统计
- Mermaid 流程图
- 时序图
- 详细执行历史

## 调试技巧

1. **理解 Agent 思考过程**
   - 在 THINK 步骤设置断点
   - 查看消息历史理解上下文

2. **调试工具调用**
   - 使用工具断点定位特定工具
   - 使用 step in 查看工具参数

3. **处理错误**
   - 设置条件断点捕获错误
   - 查看调用栈定位问题源头

4. **优化性能**
   - 分析执行历史找出瓶颈
   - 使用 step over 跳过已验证部分

## 扩展开发

调试器设计为可扩展架构，可以：

- 创建自定义断点类型
- 添加新的调试命令
- 集成到 IDE 或 Web UI
- 导出执行日志进行分析

## 注意事项

- 调试模式会降低执行速度
- 生产环境请关闭调试功能
- 复杂任务可能产生大量执行历史

## 相关资源

- [使用指南](docs/ReactAgentDebugger使用指南.md) - 详细文档
- [GenericReactAgent](react_agent.py) - 被调试的 Agent
- [LangGraph 文档](https://python.langchain.com/docs/langgraph) - 底层框架

## 贡献

欢迎提交 Issue 和 Pull Request 来改进调试器功能。