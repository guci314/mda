# LangChain Tools 集成指南

## 概述

本指南介绍如何在 agent_cli 中使用 LangChain Tools 来替代传统的 action 执行机制。通过集成 LangChain Tools，我们可以：

1. 使用标准化的工具协议
2. 轻松扩展和添加新工具
3. 利用 LangChain 生态系统
4. 获得更好的错误处理和日志支持

## 架构变化

### 之前：自定义 Tool 类
```python
class Tool(ABC):
    @abstractmethod
    def execute(self, params: Dict[str, Any]) -> Any:
        pass

class FileReader(Tool):
    def execute(self, params: Dict[str, Any]) -> str:
        # 实现文件读取
```

### 现在：LangChain Tools
```python
from langchain.tools import BaseTool, StructuredTool

class ReadFileTool(BaseTool):
    name = "read_file"
    description = "读取指定文件的内容"
    args_schema: Type[BaseModel] = ReadFileInput
    
    def _run(self, file_path: str, run_manager=None) -> str:
        # 实现文件读取
```

## 保持三层架构

尽管底层执行机制改变，我们仍然保持 Task/Step/Action 三层架构：

```
Task（任务）
├── Step（步骤）
│   ├── Action（动作）
│   │   └── LangChain Tool（执行）
│   └── Action
│       └── LangChain Tool
└── Step
    └── Action
        └── LangChain Tool
```

## 使用方式

### 1. 基本使用

```python
from agent_cli.core import AgentCLI

# 创建使用 LangChain Tools 的 agent
agent = AgentCLI(use_langchain_tools=True)

# 执行任务
success, result = agent.execute_task("读取文件并分析内容")
```

### 2. 注册自定义工具

```python
from langchain.tools import StructuredTool
from agent_cli.tools import ToolRegistry

# 创建自定义工具
def my_custom_function(param1: str, param2: int) -> str:
    """自定义功能描述"""
    return f"处理结果: {param1} - {param2}"

custom_tool = StructuredTool.from_function(
    func=my_custom_function,
    name="custom_tool",
    description="执行自定义操作"
)

# 注册到 agent
if agent.tool_executor:
    agent.tool_executor.tool_registry.register(custom_tool)
```

### 3. 工具映射

Action 类型到 LangChain 工具的映射：

| ActionType | LangChain Tool | 说明 |
|------------|----------------|------|
| READ_FILE | read_file | 读取文件内容 |
| WRITE_FILE | write_file | 写入文件 |
| LIST_FILES | list_files | 列出文件 |
| ANALYZE | analyze | 分析内容（使用 LLM） |
| GENERATE | generate | 生成内容（使用 LLM） |

## 扩展工具集

### 1. 创建新的 LangChain Tool

```python
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

class MyToolInput(BaseModel):
    """工具输入模型"""
    param1: str = Field(description="参数1描述")
    param2: int = Field(description="参数2描述")

class MyTool(BaseTool):
    name = "my_tool"
    description = "工具描述"
    args_schema: Type[BaseModel] = MyToolInput
    
    def _run(self, param1: str, param2: int, run_manager=None):
        # 实现工具逻辑
        return f"结果: {param1} - {param2}"
```

### 2. 使用 StructuredTool

```python
from langchain.tools import StructuredTool

def process_data(data: dict, format: str = "json") -> str:
    """处理数据并返回格式化结果"""
    if format == "json":
        return json.dumps(data, indent=2)
    else:
        return str(data)

process_tool = StructuredTool.from_function(
    func=process_data,
    name="process_data",
    description="处理和格式化数据"
)
```

### 3. 集成现有 LangChain 工具

```python
from langchain_experimental.tools import PythonREPLTool
from langchain.tools import ShellTool

# 添加 Python REPL 工具
python_tool = PythonREPLTool()
agent.tool_executor.tool_registry.register(python_tool)

# 添加 Shell 工具（谨慎使用）
shell_tool = ShellTool()
agent.tool_executor.tool_registry.register(shell_tool)
```

## 执行模式

### 1. LangChain 模式（推荐）

```python
agent = AgentCLI(use_langchain_tools=True)
```

优势：
- 标准化的工具协议
- 丰富的错误处理
- 自动参数验证
- 更好的日志记录

### 2. 传统模式（向后兼容）

```python
agent = AgentCLI(use_langchain_tools=False)
```

适用于：
- 需要向后兼容的场景
- 简单的文件操作
- 不需要扩展工具的情况

### 3. 混合模式

通过 `HybridExecutor` 支持运行时切换：

```python
from agent_cli.executors import HybridExecutor, ExecutorMode

executor = HybridExecutor(mode=ExecutorMode.LANGCHAIN)

# 运行时切换模式
executor.set_mode(ExecutorMode.LEGACY)
```

## 工具开发最佳实践

### 1. 明确的工具描述

```python
class MyTool(BaseTool):
    name = "tool_name"
    description = "清晰描述工具的功能，帮助 LLM 理解何时使用"
```

### 2. 使用 Pydantic 模型定义输入

```python
class ToolInput(BaseModel):
    """输入参数验证"""
    required_param: str = Field(description="必需参数")
    optional_param: int = Field(default=0, description="可选参数")
```

### 3. 适当的错误处理

```python
def _run(self, **kwargs):
    try:
        # 工具逻辑
        return result
    except SpecificError as e:
        # 返回有意义的错误信息
        return f"Error: {str(e)}"
```

### 4. 日志记录

```python
import logging
logger = logging.getLogger(__name__)

def _run(self, **kwargs):
    logger.info(f"Executing {self.name} with params: {kwargs}")
    # 工具逻辑
```

## 示例：完整的工具实现

```python
from typing import Type, Optional
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun
import logging

logger = logging.getLogger(__name__)

class CodeFormatterInput(BaseModel):
    """代码格式化工具的输入"""
    code: str = Field(description="要格式化的代码")
    language: str = Field(default="python", description="代码语言")
    style: str = Field(default="pep8", description="格式化风格")

class CodeFormatterTool(BaseTool):
    """代码格式化工具"""
    name = "code_formatter"
    description = "格式化代码，支持多种语言和风格"
    args_schema: Type[BaseModel] = CodeFormatterInput
    
    def _run(
        self,
        code: str,
        language: str = "python",
        style: str = "pep8",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """执行代码格式化"""
        logger.info(f"Formatting {language} code with {style} style")
        
        try:
            if language == "python" and style == "pep8":
                # 使用 black 或其他格式化工具
                import black
                formatted = black.format_str(code, mode=black.Mode())
                return formatted
            else:
                # 其他语言的格式化逻辑
                return code
        except Exception as e:
            logger.error(f"Formatting failed: {e}")
            return f"Error formatting code: {str(e)}"
    
    async def _arun(self, **kwargs) -> str:
        """异步版本（如果需要）"""
        return self._run(**kwargs)
```

## 迁移指南

### 从传统 Tool 迁移到 LangChain Tool

1. **修改工具基类**
   - 从 `Tool` 改为 `BaseTool`
   - 实现 `_run` 方法而不是 `execute`

2. **添加元数据**
   - 添加 `name` 和 `description` 属性
   - 定义 `args_schema` 用于参数验证

3. **更新执行逻辑**
   - 使用 `tool_executor.execute()` 而不是直接调用
   - 处理 `ExecutionResult` 返回值

4. **测试兼容性**
   - 确保新旧模式都能正常工作
   - 验证参数映射正确

## 故障排除

### 1. ImportError: No module named 'langchain'

确保安装了必要的依赖：
```bash
pip install langchain langchain-community langchain-experimental
```

### 2. 工具未找到

检查工具是否正确注册：
```python
# 列出所有注册的工具
tools = agent.tool_executor.get_available_tools()
for tool in tools:
    print(f"- {tool['name']}: {tool['description']}")
```

### 3. 参数错误

确保参数名称匹配：
```python
# LangChain 工具期望的参数名
params = {
    "file_path": "test.txt",  # 而不是 "path"
    "content": "Hello"
}
```

## 性能考虑

1. **工具初始化**：在启动时一次性注册所有工具
2. **参数验证**：利用 Pydantic 的验证缓存
3. **异步执行**：对于 I/O 密集型操作使用异步版本
4. **工具复用**：避免重复创建工具实例

## 未来扩展

1. **工具市场**：集成更多 LangChain 社区工具
2. **工具链**：支持工具组合和管道
3. **并行执行**：同时执行多个独立工具
4. **工具版本管理**：支持不同版本的工具共存