# Action 架构设计方案

## 背景
当前 agent_cli 需要一个清晰的 action 执行架构，将执行逻辑与认知逻辑分离。核心需求：
- 支持读文件、写文件、执行代码等基础操作
- 可扩展到其他领域
- 与 LLM 推理层解耦

## 方案1：自定义 ActionExecutor 架构

### 设计结构
```
领域特定层：
├── ActionType          # 动作模式定义（schema）
│   ├── name           # 动作名称
│   ├── description    # 动作描述
│   └── parameters     # 参数类型声明（JSON Schema）
├── Action             # 动作实例
│   ├── action_type    # 引用的 ActionType
│   └── parameters     # 具体参数值
└── ActionExecutor     # 抽象执行器
    └── ProgrammingActionExecutor  # 编程领域执行器
        ├── read_file
        ├── write_file
        └── run_python

通用认知层：
├── Task               # 任务
├── Step               # 步骤
└── AgentCLI          # 推理和编排
```

### 优势
- **清晰的层次**：领域特定与通用认知分离
- **类型安全**：通过 schema 验证参数
- **自描述**：LLM 可以理解每个 action 的用途
- **可扩展**：容易添加新的领域执行器

### 劣势
- 需要自己实现所有基础设施
- 需要维护 schema 验证逻辑
- 与现有生态系统集成需要额外工作

### 示例
```python
# 定义 ActionType
read_file_type = ActionType(
    name="read_file",
    description="读取文件内容",
    parameters={
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "文件路径"}
        },
        "required": ["path"]
    }
)

# 创建 Action 实例
action = Action(
    action_type=read_file_type,
    parameters={"path": "hello.py"}
)

# 执行
executor = ProgrammingActionExecutor()
result = executor.execute(action)
```

## 方案2：使用 LangChain Tools

### 设计结构
```
使用 LangChain 现有架构：
├── BaseTool              # LangChain 的工具基类
├── StructuredTool        # 支持结构化输入
└── 自定义 Tools
    ├── ReadFileTool
    ├── WriteFileTool
    └── PythonREPLTool    # LangChain 内置
```

### 优势
- **成熟生态**：LangChain 有大量现成的工具
- **标准化**：遵循 LangChain 的工具协议
- **集成方便**：与 LangChain 的 Agent 框架无缝集成
- **内置功能**：错误处理、重试、日志等

### 劣势
- 依赖 LangChain 框架
- 工具定义相对固定
- 自定义需要遵循 LangChain 的模式

### 示例
```python
from langchain.tools import StructuredTool
from langchain.agents import initialize_agent

def read_file(path: str) -> str:
    """读取文件内容"""
    with open(path, 'r') as f:
        return f.read()

read_tool = StructuredTool.from_function(
    func=read_file,
    name="read_file",
    description="读取文件内容"
)

# 使用 LangChain Agent
agent = initialize_agent(
    tools=[read_tool, write_tool, python_repl],
    llm=llm,
    agent="structured-chat-zero-shot-react-description"
)
```

## 方案3：使用 MCP (Model Context Protocol)

### 设计结构
```
MCP 架构：
├── MCP Server           # 提供工具的服务器
│   ├── Resources       # 文件、数据等资源
│   ├── Tools           # 可执行的操作
│   └── Prompts         # 提示模板
└── MCP Client          # agent_cli 作为客户端
    └── 通过标准协议调用工具
```

### 优势
- **标准协议**：跨语言、跨平台的标准
- **分布式**：工具可以运行在不同进程/机器
- **安全隔离**：工具在独立环境中执行
- **生态系统**：可以使用任何 MCP 兼容的工具

### 劣势
- 相对较新，生态还在发展
- 需要运行 MCP 服务器
- 增加了系统复杂度
- 网络通信开销

### 示例
```python
# MCP 服务器端定义
@server.tool()
async def read_file(path: str) -> str:
    """读取文件内容"""
    async with aiofiles.open(path, 'r') as f:
        return await f.read()

# 客户端使用
async with ClientSession(server_url) as session:
    result = await session.call_tool("read_file", {"path": "hello.py"})
```

## 方案对比

| 特性 | 方案1 (自定义) | 方案2 (LangChain) | 方案3 (MCP) |
|------|--------------|------------------|-------------|
| 实现复杂度 | 中等 | 低 | 高 |
| 灵活性 | 高 | 中 | 高 |
| 生态系统 | 无 | 丰富 | 发展中 |
| 维护成本 | 高 | 低 | 中 |
| 性能 | 最佳 | 好 | 一般 |
| 扩展性 | 好 | 好 | 最佳 |
| 标准化 | 自定义 | LangChain 标准 | 开放标准 |

## 建议

1. **快速原型**：选择方案2（LangChain），利用现有生态快速实现
2. **长期发展**：选择方案3（MCP），符合行业标准发展方向
3. **特殊需求**：选择方案1（自定义），完全控制实现细节

### 混合方案
也可以考虑混合方案：
- 短期：使用 LangChain Tools 快速实现基础功能
- 中期：在 LangChain 基础上包装自定义的 ActionExecutor 接口
- 长期：迁移到 MCP 标准，保持向后兼容