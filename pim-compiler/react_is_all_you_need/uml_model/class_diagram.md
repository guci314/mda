# React Agent Minimal - 类图 (Class Diagram)

## 概述
React Agent Minimal是一个极简的Agent框架，基于"React + 文件系统 = 图灵完备"的理论。

## 核心类结构

```mermaid
classDiagram
    %% 基础抽象类
    class Function {
        <<abstract>>
        -name: str
        -description: str
        -parameters: Dict
        -return_type: str
        +__init__(name, description, parameters, return_type)
        +execute(**kwargs): str
        +to_openai_function(): Dict
        +__call__(**kwargs): str
    }

    %% 核心Agent类
    class ReactAgentMinimal {
        -work_dir: Path
        -agent_name: str
        -model: str
        -api_key: str
        -base_url: str
        -max_rounds: int
        -knowledge_files: List[str]
        -knowledge_content: str
        -compact_memory: str
        -compact_threshold: int
        -messages: List[Dict]
        -function_instances: List[Function]
        -functions: List[Dict]
        +__init__(work_dir, name, ...)
        +execute(**kwargs): str
        +append_tool(tool: Function)
        +add_function(function: Function)
        -_create_function_instances(): List[Function]
        -_build_minimal_prompt(): str
        -_load_knowledge(): str
        -_load_knowledge_package(package_path: Path)
        -_resolve_knowledge_files(files: List[str]): List[str]
        -_call_llm(messages: List[Dict]): Dict
        -_should_compress(): bool
        -_compress_memory(): str
        -_load_compact_memory(): bool
        -_save_compact_memory(content: str)
    }

    %% 工具类
    class ReadFileTool {
        -work_dir: Path
        +execute(**kwargs): str
    }

    class WriteFileTool {
        -work_dir: Path
        +execute(**kwargs): str
    }

    class AppendFileTool {
        -work_dir: Path
        +execute(**kwargs): str
    }

    class ExecuteCommandTool {
        -work_dir: Path
        +execute(**kwargs): str
    }

    class SearchTool {
        -api_key: str
        +execute(**kwargs): str
    }

    class NewsSearchTool {
        -api_key: str
        +execute(**kwargs): str
    }

    %% ExecutionContext工具
    class ExecutionContext {
        -project: Dict
        +execute(**kwargs): str
        -_init_project(goal: str): str
        -_add_tasks(tasks: List[str]): str
        -_remove_tasks(tasks: List[str]): str
        -_start_task(task: str): str
        -_complete_task(task: str, result: str): str
        -_fail_task(task: str, result: str): str
        -_set_state(state: str): str
        -_get_state(): str
        -_set_data(key: str, value: Any): str
        -_get_data(key: str): str
        -_delete_data(key: str): str
        -_get_context(): str
    }

    %% 继承关系
    Function <|-- ReactAgentMinimal
    Function <|-- ReadFileTool
    Function <|-- WriteFileTool
    Function <|-- AppendFileTool
    Function <|-- ExecuteCommandTool
    Function <|-- SearchTool
    Function <|-- NewsSearchTool
    Function <|-- ExecutionContext

    %% 组合关系
    ReactAgentMinimal "1" *-- "0..*" Function : contains
    ReactAgentMinimal ..> ReadFileTool : creates
    ReactAgentMinimal ..> WriteFileTool : creates
    ReactAgentMinimal ..> AppendFileTool : creates
    ReactAgentMinimal ..> ExecuteCommandTool : creates
    ReactAgentMinimal ..> ExecutionContext : creates
    ReactAgentMinimal ..> SearchTool : creates
```

## 类职责说明

### 1. Function (抽象基类)
- **职责**: 定义所有可调用函数的接口
- **特点**: 
  - 统一的execute接口
  - 支持OpenAI function calling格式
  - 实现__call__使其可直接调用

### 2. ReactAgentMinimal (核心Agent)
- **职责**: 主要的Agent实现，协调LLM和工具调用
- **特点**:
  - 继承自Function，自身也是可调用的函数
  - 管理知识文件加载
  - 实现Compact记忆压缩机制
  - 支持工具组合（可添加其他Agent作为工具）

### 3. 工具类 (Tools)
- **ReadFileTool**: 读取文件
- **WriteFileTool**: 写入文件（覆盖模式）
- **AppendFileTool**: 追加文件内容
- **ExecuteCommandTool**: 执行shell命令
- **SearchTool**: 搜索互联网
- **NewsSearchTool**: 搜索新闻

### 4. ExecutionContext
- **职责**: 内存中的任务管理器
- **特点**:
  - 不持久化，纯内存操作
  - 管理项目目标、任务列表、状态
  - 提供通用KV存储

## 设计模式

1. **策略模式**: Function接口定义统一的执行策略
2. **组合模式**: Agent可以包含其他Agent作为工具
3. **模板方法**: Function基类定义执行框架
4. **单一职责**: 每个工具类只负责一种操作

## 核心特性

1. **极简设计**: 整个框架代码约500行
2. **知识驱动**: 行为通过知识文件定义，而非硬编码
3. **Compact记忆**: 70k tokens自动压缩机制
4. **工具组合**: Agent可以作为其他Agent的工具
5. **纯内存ExecutionContext**: 不依赖文件持久化