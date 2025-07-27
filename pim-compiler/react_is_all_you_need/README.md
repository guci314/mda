# React Is All You Need

基于 LangChain React Agent 的通用任务执行框架，支持先验知识注入和三级记忆系统。

## 核心文件

### 1. `direct_react_agent_v4_generic.py`
通用 React Agent 实现，特点：
- 领域无关的系统提示词
- 先验知识注入机制
- 三级记忆系统（none/smart/pro）
- 自动大括号转义
- 工具规范描述支持

### 2. `langchain_agent_tool.py`
LangChain 框架集成工具：
- `AgentToolWrapper` - 接受 GenericReactAgent 实例的封装器
- 多种集成方式（@tool、StructuredTool、BaseTool）
- 专用工具创建函数（代码生成、文件处理等）

### 3. `agent_tool.py`
最简单的工具封装：
- 单个 `Tool` 类
- 单个 `execute(task: str) -> str` 方法
- 自动临时目录管理

### 4. `tool_specification_example.py`
演示如何将工具规范传递给 LangChain：
- 三种传递方法的示例
- 完整的 LangChain Agent 集成示例

### 5. `deepseek_token_counter.py`
修复 DeepSeek 模型的 token 计数问题

### 6. `先验知识.md`
FastAPI 代码生成的领域知识示例

## 快速开始

### 1. 基本使用
```python
from direct_react_agent_v4_generic import GenericReactAgent, GeneratorConfig, MemoryLevel

# 创建配置
config = GeneratorConfig(
    output_dir="output",
    memory_level=MemoryLevel.NONE,
    knowledge_file="先验知识.md"
)

# 创建 Agent
agent = GenericReactAgent(config)

# 执行任务
agent.execute_task("创建一个用户管理系统")
```

### 2. 作为工具使用
```python
from agent_tool import Tool

tool = Tool()
result = tool.execute("创建一个 REST API")
print(result)
```

### 3. LangChain 集成
```python
from langchain_agent_tool import create_langchain_tool
from direct_react_agent_v4_generic import GenericReactAgent, GeneratorConfig

# 创建带规范的 Agent
config = GeneratorConfig(
    output_dir="output",
    specification="专门生成 Python 代码的工具"
)
agent = GenericReactAgent(config)

# 创建 LangChain 工具
tool = create_langchain_tool(agent)
```

## 命令行使用

```bash
# 使用默认配置
python direct_react_agent_v4_generic.py

# 自定义任务
python direct_react_agent_v4_generic.py --task "创建一个博客系统"

# 使用不同的知识文件
python direct_react_agent_v4_generic.py --knowledge-file django_knowledge.md

# 启用持久化记忆
python direct_react_agent_v4_generic.py --memory pro --session-id my_project
```

## 记忆级别

- **none**: 无记忆，每次对话独立
- **smart**: 智能缓冲，保留最近 50 条消息
- **pro**: 持久化存储，使用 SQLite 数据库

## 自定义先验知识

创建新的领域知识文件（如 `django_knowledge.md`），包含：
- 项目结构规范
- 代码模板
- 最佳实践
- 常用模式

注意：代码中的 `{}` 会自动转义，无需手动处理。

## 环境要求

- Python 3.8+
- 设置环境变量：`DEEPSEEK_API_KEY`

## 安装依赖

```bash
pip install langchain langchain-openai langchain-community tiktoken
```