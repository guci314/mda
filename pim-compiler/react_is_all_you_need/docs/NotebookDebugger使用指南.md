# Notebook Debugger 使用指南

## 概述

NotebookReactAgentDebugger 是专为 Jupyter Notebook 环境设计的调试器，它继承了基础调试器的所有功能，并添加了：

1. **交互式 UI 控制面板**：使用按钮控制调试流程
2. **智能分析功能**：使用 Gemini 2.0 Flash 分析当前状态是否存在 bug
3. **异步执行支持**：适合 Notebook 的交互式环境

## 安装要求

```bash
pip install google-generativeai ipywidgets
```

## 快速开始

### 1. 设置 API 密钥

```python
import os

# 方式1：环境变量
os.environ["GEMINI_API_KEY"] = "your-api-key"

# 方式2：.env 文件
from dotenv import load_dotenv
load_dotenv()

# 方式3：创建调试器时传入
debugger = NotebookReactAgentDebugger(agent, gemini_api_key="your-api-key")
```

### 2. 创建调试器

```python
from react_agent import GenericReactAgent, ReactAgentConfig
from react_agent_debugger_notebook import create_notebook_debugger

# 创建 Agent
config = ReactAgentConfig(work_dir="output/debug")
agent = GenericReactAgent(config)

# 创建 Notebook 调试器
debugger = create_notebook_debugger(agent)
```

### 3. 使用控制面板

```python
# 创建交互式控制面板
control_panel = debugger.create_control_panel()
display(control_panel)

# 执行任务
debugger.execute_task("创建一个 hello.py 文件")
```

## 核心功能：analysis() 方法

`analysis()` 方法是 Notebook 调试器的核心功能，它使用 Gemini 2.0 Flash 来智能分析当前执行状态。

### 工作原理

1. **收集上下文信息**
   - 当前步骤类型和执行历史
   - 最近的消息内容
   - 工具调用记录
   - 潜在的问题模式

2. **智能分析**
   - 检测错误关键词
   - 识别重复的工具调用
   - 分析执行效率问题
   - 判断调用深度异常

3. **返回结构化结果**
   ```json
   {
       "has_bug": true,
       "severity": "中等",
       "bug_type": "重复调用",
       "description": "工具 write_file 被连续调用了3次",
       "solution": "检查循环逻辑，避免重复操作",
       "additional_observations": ["执行步骤过多", "可能存在死循环"]
   }
   ```

### 使用场景

#### 场景1：断点触发时分析

```python
# 在断点触发后，点击"分析"按钮或手动调用
result = debugger.analysis()

if result.get("has_bug"):
    print(f"发现 {result['severity']} 级别的 bug: {result['description']}")
    print(f"建议: {result['solution']}")
```

#### 场景2：自动触发分析

```python
# 创建条件断点，在特定情况下自动分析
debugger.add_breakpoint(
    ConditionalBreakpoint(
        "auto_analyze",
        lambda ctx: "error" in str(ctx.get("last_message", "")).lower(),
        "错误时触发分析"
    )
)
```

#### 场景3：批量分析历史

```python
# 查看所有分析记录
for analysis in debugger.analysis_results:
    if analysis.get("has_bug"):
        print(f"{analysis['timestamp']}: {analysis['bug_type']}")
```

## 分析能力详解

### 1. 错误检测

- 识别常见错误关键词（error, failed, exception, not found）
- 检测权限问题
- 发现文件操作失败

### 2. 性能问题

- 执行步骤过多（超过20步）
- 重复调用同一工具
- 调用深度异常（超过3层）

### 3. 逻辑问题

- AI 决策困惑（"I'm not sure", "unclear"）
- 工具调用模式异常
- 消息流程不合理

### 4. 优化建议

- 提供具体的解决方案
- 识别潜在的改进点
- 建议更好的实现方式

## 交互式控制面板

控制面板提供以下按钮：

| 按钮 | 功能 | 说明 |
|------|------|------|
| 继续 (c) | 继续执行到下一个断点 | 恢复正常执行 |
| 单步 (s) | 执行一个原子步骤 | THINK/ACT/OBSERVE |
| 步入 (si) | 进入子 Agent 调用 | 仅对子 Agent 有效 |
| 步出 (so) | 退出当前子 Agent | 需要在子 Agent 内部 |
| 步过 (sv) | 跳过工具调用细节 | 不进入内部执行 |
| 分析 🔍 | 触发智能分析 | 使用 Gemini 分析状态 |
| 退出 (q) | 结束调试会话 | 停止执行 |

## 高级用法

### 1. 自定义分析提示词

```python
# 继承并重写 _build_analysis_prompt 方法
class CustomDebugger(NotebookReactAgentDebugger):
    def _build_analysis_prompt(self, context):
        # 自定义提示词逻辑
        return f"特定领域的分析提示词..."
```

### 2. 扩展分析维度

```python
# 重写 _prepare_analysis_context 方法
def _prepare_analysis_context(self):
    context = super()._prepare_analysis_context()
    
    # 添加自定义分析维度
    context["custom_metric"] = self.calculate_custom_metric()
    
    return context
```

### 3. 集成外部分析工具

```python
# 在分析结果中集成其他工具
def analysis(self):
    gemini_result = super().analysis()
    
    # 集成其他分析
    static_analysis = run_static_analyzer()
    gemini_result["static_analysis"] = static_analysis
    
    return gemini_result
```

## 最佳实践

### 1. 合理设置断点

```python
# 在关键决策点设置断点
debugger.add_breakpoint(StepBreakpoint("think", StepType.THINK))

# 在可能出错的地方设置条件断点
debugger.add_breakpoint(
    ConditionalBreakpoint(
        "error_check",
        lambda ctx: "error" in str(ctx.get("last_message", "")).lower(),
        "错误检测"
    )
)
```

### 2. 定期分析

- 在长时间运行的任务中定期触发分析
- 在关键操作前后进行分析
- 保存分析历史用于后续改进

### 3. 结合手动检查

- 分析结果仅供参考
- 结合手动状态查看（使用基础调试器的 print 功能）
- 验证分析建议的有效性

## 故障排除

### 问题：Gemini API 调用失败

**解决方案**：
1. 检查 API 密钥是否正确
2. 确认网络连接正常
3. 查看 API 配额是否充足

### 问题：分析结果不准确

**解决方案**：
1. 提供更多上下文信息
2. 调整分析提示词
3. 结合多次分析结果判断

### 问题：Notebook 界面无响应

**解决方案**：
1. 确保使用了正确的事件循环
2. 避免在主线程中阻塞
3. 使用异步执行方法

## 示例：完整的调试会话

```python
# 1. 创建调试器
debugger = create_notebook_debugger(agent)

# 2. 设置智能断点
debugger.add_breakpoint(
    ConditionalBreakpoint(
        "smart_bp",
        lambda ctx: len(debugger.execution_history) > 10 or 
                   "error" in str(ctx.get("last_message", "")).lower(),
        "步骤过多或出现错误"
    )
)

# 3. 创建控制面板
display(debugger.create_control_panel())

# 4. 执行任务
debugger.execute_task("""
创建一个 Python 项目：
1. 创建主程序文件
2. 添加错误处理
3. 编写测试用例
4. 运行测试
""")

# 5. 查看分析报告
for result in debugger.analysis_results:
    if result.get("has_bug"):
        print(f"Bug: {result['description']}")
        print(f"解决方案: {result['solution']}")
```

## 总结

NotebookReactAgentDebugger 通过集成 Gemini 2.0 Flash，为 Agent 调试提供了智能分析能力。它不仅能帮助发现 bug，还能提供优化建议，是提高 Agent 开发效率的强大工具。

记住：
- 分析功能是辅助工具，最终判断仍需要开发者
- 合理设置断点可以提高分析效率
- 保存分析历史有助于持续改进 Agent