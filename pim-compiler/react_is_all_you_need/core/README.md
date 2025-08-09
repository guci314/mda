# React Agent 核心模块

这个目录包含 React Agent 系统的核心实现。

## 模块说明

### react_agent.py
- **GenericReactAgent**: 主Agent类，实现了"自然语言虚拟机"
- **ReactAgentConfig**: Agent配置类
- **MemoryLevel**: 记忆级别枚举（NONE, SMART, PRO）

核心功能：
- React执行循环（Thought-Action-Observation）
- 多级记忆管理
- 知识提取和压缩
- 项目探索能力

### tools.py
- **create_tools()**: 创建标准工具集

工具集定义了Agent的计算边界，包括：
- 文件操作工具（read_file, write_file, edit_lines等）
- 搜索工具（search_files, find_symbol等）
- 命令执行工具（execute_command）
- Web工具（google_search, read_web_page，可选）

### langchain_agent_tool.py
- **AgentToolWrapper**: 将Agent包装为LangChain工具
- **create_langchain_tool()**: 创建可被其他Agent调用的工具

实现了 Agent as Tool 机制，使得：
- Agent可以调用其他Agent
- 实现多Agent协作
- 构建层级化的Agent系统

## 使用示例

```python
from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel
from core.tools import create_tools
from core.langchain_agent_tool import create_langchain_tool

# 创建Agent
config = ReactAgentConfig(
    work_dir="output",
    memory_level=MemoryLevel.SMART,
    knowledge_files=["knowledge/python_programming.md"]
)

agent = GenericReactAgent(config, name="my_agent")

# 执行任务
result = agent.execute_task("创建一个Hello World程序")

# 将Agent作为工具
agent_tool = create_langchain_tool(agent)
```

## 设计理念

1. **知识驱动**：通过知识文件而非代码定义行为
2. **工具闭包**：工具集定义了计算能力的边界
3. **自然语言CPU**：React循环类似于CPU的取指-执行循环
4. **无需Python类**：通过纯知识就能完成任务

## 核心概念

- **React = 自然语言CPU**
- **知识文件 = 程序**
- **工具集 = 系统调用**
- **Agent协作 = 分布式计算**

详细理论请参考：
- [自然语言虚拟机设计文档](../docs/自然语言虚拟机设计文档.md)
- [React作为自然语言CPU理论](../docs/React作为自然语言CPU理论.md)