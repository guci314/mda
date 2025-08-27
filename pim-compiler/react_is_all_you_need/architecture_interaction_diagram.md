# React Agent、Memory Manager、VSCode Memory 交互架构图

## 🏗️ 整体架构概览

```mermaid
graph TB
    subgraph "用户层"
        User[👤 用户]
    end

    subgraph "应用层"
        RA[🤖 React Agent<br/>智能代理]
    end

    subgraph "记忆管理层"
        MM[🧠 Memory Manager<br/>统一记忆管理器]
    end

    subgraph "记忆实现层"
        VSM[📁 VSCode Memory<br/>状态记忆系统]
        PM[⏰ Process Memory<br/>过程记忆系统]
        AMP[⚡ Async Memory Processor<br/>异步处理器]
    end

    subgraph "存储层"
        FS[💾 文件系统<br/>潜意识存储]
        Cache[📦 缓存系统<br/>视图缓存]
    end

    User --> RA
    RA --> MM
    MM --> VSM
    MM --> PM
    MM --> AMP
    VSM --> FS
    AMP --> Cache
```

## 🔄 详细交互流程

### 1. 初始化阶段

```mermaid
sequenceDiagram
    participant User as 用户
    participant RA as React Agent
    participant MM as Memory Manager
    participant VSM as VSCode Memory
    participant PM as Process Memory
    participant AMP as Async Memory Processor

    User->>RA: 创建Agent实例
    RA->>MM: 初始化Memory Manager
    MM->>MM: 自动选择记忆模式
    alt 基础模式
        MM->>VSM: 创建VSCode Memory
        MM->>PM: 创建Process Memory
    else 混合模式
        MM->>VSM: 创建VSCode Memory
        MM->>AMP: 创建Async Memory Processor
    else 完整异步模式
        MM->>VSM: 创建AsyncVSCode Memory
        MM->>AMP: 创建Async Memory Processor
    end
    MM->>RA: 返回记忆系统状态
    RA->>User: 显示初始化完成
```

### 2. 文件操作交互

```mermaid
sequenceDiagram
    participant User as 用户
    participant RA as React Agent
    participant MM as Memory Manager
    participant VSM as VSCode Memory
    participant FS as 文件系统

    User->>RA: 请求打开文件
    RA->>RA: 执行read_file工具
    RA->>MM: open_file(file_path, content)
    MM->>VSM: open_file(file_path, content)
    VSM->>VSM: 计算文件哈希
    VSM->>FS: 保存到潜意识存储
    VSM->>VSM: 更新显意识层
    VSM->>VSM: 更新工作集
    VSM->>VSM: 设置焦点
    VSM->>MM: 返回操作结果
    MM->>RA: 返回操作结果
    RA->>User: 返回文件内容
```

### 3. 消息处理交互

```mermaid
sequenceDiagram
    participant User as 用户
    participant RA as React Agent
    participant MM as Memory Manager
    participant AMP as Async Memory Processor
    participant PM as Process Memory
    participant Cache as 缓存系统

    User->>RA: 发送消息
    RA->>MM: add_message(message, importance)
    alt 异步模式
        MM->>AMP: add_message(message, importance)
        AMP->>AMP: 创建多视图消息
        AMP->>AMP: 立即生成FULL/MINIMAL视图
        AMP->>AMP: 异步生成其他视图
        AMP->>Cache: 缓存视图到磁盘
        AMP->>MM: 返回MultiViewMessage
    else 基础模式
        MM->>PM: 消息不存储，仅用于压缩
        PM->>MM: 返回None
    end
    MM->>RA: 返回处理结果
    RA->>User: 继续对话
```

### 4. 记忆压缩交互

```mermaid
sequenceDiagram
    participant RA as React Agent
    participant MM as Memory Manager
    participant VSM as VSCode Memory
    participant AMP as Async Memory Processor
    participant PM as Process Memory

    RA->>MM: compress_messages(messages)
    alt 异步模式
        MM->>AMP: get_optimized_history()
        AMP->>AMP: 根据时间衰减选择视图
        AMP->>AMP: 应用清晰度压缩
        AMP->>MM: 返回优化历史
    else 基础模式
        MM->>PM: compress_messages(messages)
        PM->>PM: 应用时间衰减压缩
        PM->>MM: 返回压缩结果
    end

    RA->>MM: get_memory_context()
    MM->>VSM: compress_for_llm()
    VSM->>VSM: 按优先级选择内容
    VSM->>VSM: 应用分辨率压缩
    VSM->>MM: 返回压缩上下文
    MM->>RA: 返回完整记忆上下文
```

### 5. 状态快照交互

```mermaid
sequenceDiagram
    participant RA as React Agent
    participant MM as Memory Manager
    participant VSM as VSCode Memory
    participant FS as 文件系统

    RA->>MM: save_state(state_name, state_data)
    MM->>VSM: save_state(state_name, state_data)
    VSM->>VSM: 生成状态ID
    VSM->>VSM: 构建状态对象
    VSM->>FS: 保存到states目录
    VSM->>VSM: 更新内存索引
    VSM->>VSM: 自动清理旧状态
    VSM->>MM: 返回状态ID
    MM->>RA: 返回状态ID

    RA->>MM: search(query)
    MM->>VSM: search(query)
    VSM->>VSM: 搜索文件索引
    VSM->>VSM: 搜索事件索引
    VSM->>VSM: 搜索状态索引
    VSM->>MM: 返回搜索结果
    MM->>RA: 返回搜索结果
```

## 🧠 记忆系统层次结构

```mermaid
graph TD
    subgraph "React Agent 层"
        RA[React Agent<br/>智能代理]
        Tools[工具集<br/>read_file, write_file, search_memory]
    end

    subgraph "Memory Manager 层"
        MM[Memory Manager<br/>统一接口]
        Mode[模式选择<br/>BASIC/HYBRID/FULL_ASYNC]
        Interface[统一接口<br/>open_file, add_message, compress_messages]
    end

    subgraph "记忆实现层"
        subgraph "状态记忆"
            VSM[VSCode Memory<br/>文件/事件/状态管理]
            ASM[AsyncVSCode Memory<br/>异步状态记忆]
        end

        subgraph "过程记忆"
            PM[Process Memory<br/>时间衰减压缩]
            AMP[Async Memory Processor<br/>多视图异步处理]
        end
    end

    subgraph "存储层"
        subgraph "潜意识存储"
            FS[文件系统<br/>.vscode_memory/]
            Episodes[事件存储<br/>episodes/]
            States[状态存储<br/>states/]
            Workspace[工作文件<br/>workspace/]
        end

        subgraph "显意识缓存"
            Cache[视图缓存<br/>.message_views/]
            Memory[内存索引<br/>consciousness, attention]
        end
    end

    RA --> Tools
    Tools --> MM
    MM --> Mode
    MM --> Interface
    Interface --> VSM
    Interface --> ASM
    Interface --> PM
    Interface --> AMP
    VSM --> FS
    ASM --> FS
    PM --> Memory
    AMP --> Cache
    AMP --> Memory
```

## 🔧 核心交互接口

### Memory Manager 统一接口

```python
class MemoryManager:
    # 状态记忆接口
    def open_file(self, file_path: str, content: str)
    def close_file(self, file_path: str)
    def search(self, query: str) -> List[Dict]
    def save_episode(self, event: str, data: Dict)
    def save_state(self, state_name: str, state_data: Dict)

    # 过程记忆接口
    def add_message(self, message: Dict, importance: Optional[str] = None)
    def compress_messages(self, messages: List[Dict]) -> Tuple[List[Dict], Dict]

    # 统一接口
    def get_memory_context(self, extra_tokens: int = 0) -> str
    def optimize_message_history(self, messages: List[Dict], protected_count: int = 2) -> List[Dict]
    def should_optimize(self, round_num: int, message_count: int) -> bool
    def get_status(self) -> Dict
    def cleanup(self)
```

### React Agent 工具集成

```python
class ReactAgent:
    def _define_tools(self) -> List[Dict]:
        return [
            {
                "name": "read_file",
                "description": "读取文件内容",
                "parameters": {...}
            },
            {
                "name": "write_file",
                "description": "写入文件内容",
                "parameters": {...}
            },
            {
                "name": "search_memory",
                "description": "搜索记忆内容",
                "parameters": {...}
            }
        ]

    def _execute_tool(self, tool_name: str, arguments: Dict) -> str:
        if tool_name == "read_file":
            # 自动记录到记忆
            self.memory.open_file(file_path, content)
        elif tool_name == "write_file":
            # 自动记录到记忆
            self.memory.open_file(file_path, content)
        elif tool_name == "search_memory":
            # 使用记忆搜索
            return self.memory.search(query)
```

## 📊 数据流向图

```mermaid
flowchart LR
    subgraph "输入流"
        UserInput[用户输入]
        FileOps[文件操作]
        ToolCalls[工具调用]
    end

    subgraph "处理流"
        RA[React Agent]
        MM[Memory Manager]
        VSM[VSCode Memory]
        AMP[Async Processor]
    end

    subgraph "存储流"
        StateMemory[状态记忆<br/>文件/事件/状态]
        ProcessMemory[过程记忆<br/>消息历史]
        Cache[缓存系统<br/>视图缓存]
    end

    subgraph "输出流"
        Context[记忆上下文]
        Compressed[压缩消息]
        SearchResults[搜索结果]
    end

    UserInput --> RA
    FileOps --> RA
    ToolCalls --> RA

    RA --> MM
    MM --> VSM
    MM --> AMP

    VSM --> StateMemory
    AMP --> ProcessMemory
    AMP --> Cache

    StateMemory --> Context
    ProcessMemory --> Compressed
    StateMemory --> SearchResults
    ProcessMemory --> SearchResults
```

## 🎯 交互模式总结

### 1. **初始化模式**

- React Agent 创建 Memory Manager
- Memory Manager 根据配置选择记忆模式
- 初始化相应的记忆组件

### 2. **文件操作模式**

- React Agent 执行文件工具
- 自动调用 Memory Manager 的 open_file
- VSCode Memory 处理文件存储和索引

### 3. **消息处理模式**

- React Agent 接收用户消息
- Memory Manager 根据模式选择处理器
- Async Memory Processor 或 Process Memory 处理消息

### 4. **记忆压缩模式**

- React Agent 需要优化上下文
- Memory Manager 协调状态和过程记忆压缩
- 返回优化后的记忆上下文

### 5. **状态管理模式**

- React Agent 保存项目状态
- Memory Manager 委托给 VSCode Memory
- VSCode Memory 管理状态快照和索引

这种分层架构设计实现了：

- **解耦合**：各层职责清晰，易于维护
- **可扩展**：支持多种记忆模式
- **高性能**：异步处理和缓存优化
- **易使用**：React Agent 提供统一接口




