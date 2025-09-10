# React Agent Minimal - 序列图 (Sequence Diagram)

## 1. 基本任务执行流程

```mermaid
sequenceDiagram
    participant User
    participant Agent as ReactAgentMinimal
    participant Prompt as Prompt Builder
    participant LLM
    participant Tool as Tool/Function
    participant FS as FileSystem
    
    User->>Agent: execute(task)
    
    activate Agent
    Agent->>Agent: 加载知识文件
    Agent->>Prompt: _build_minimal_prompt()
    Prompt-->>Agent: 系统提示词
    
    loop 执行轮次 (最多max_rounds)
        Agent->>Agent: 构建消息
        Agent->>LLM: _call_llm(messages)
        activate LLM
        LLM-->>Agent: 思考 + 工具调用
        deactivate LLM
        
        alt 需要调用工具
            Agent->>Tool: execute(**kwargs)
            activate Tool
            Tool->>FS: 操作文件/执行命令
            FS-->>Tool: 结果
            Tool-->>Agent: 工具执行结果
            deactivate Tool
            Agent->>Agent: 添加工具结果到消息
        else 任务完成
            Agent-->>User: 返回最终结果
        end
        
        alt 需要压缩记忆
            Agent->>Agent: _should_compress()
            Agent->>Agent: _compress_memory()
            Agent->>Agent: _save_compact_memory()
        end
    end
    deactivate Agent
```

## 2. 工具调用详细流程

```mermaid
sequenceDiagram
    participant Agent as ReactAgentMinimal
    participant LLM
    participant Tool as Function Instance
    participant Base as Function Base
    
    Agent->>LLM: 发送带工具定义的请求
    LLM-->>Agent: 返回tool_calls
    
    loop 每个tool_call
        Agent->>Agent: 查找对应的Function实例
        Agent->>Tool: __call__(**kwargs)
        activate Tool
        Tool->>Base: execute(**kwargs)
        activate Base
        Note over Base: 具体执行逻辑
        Base-->>Tool: 执行结果
        deactivate Base
        Tool-->>Agent: 返回结果
        deactivate Tool
        Agent->>Agent: 记录工具调用结果
    end
    
    Agent->>Agent: 更新消息历史
```

## 3. ExecutionContext使用流程

```mermaid
sequenceDiagram
    participant Agent
    participant EC as ExecutionContext
    participant Memory as 内存存储
    
    Note over Agent: 判断任务复杂度
    
    alt 复杂任务（需要状态管理）
        Agent->>EC: context(action="init_project", goal="...")
        EC->>Memory: 初始化项目状态
        
        Agent->>EC: context(action="add_tasks", tasks=[...])
        EC->>Memory: 添加任务列表
        
        loop 执行任务
            Agent->>EC: context(action="start_task", task="...")
            EC->>Memory: 更新任务状态
            
            Agent->>Agent: 执行具体操作
            
            alt 任务成功
                Agent->>EC: context(action="complete_task", ...)
            else 任务失败
                Agent->>EC: context(action="fail_task", ...)
            end
            EC->>Memory: 更新任务状态
        end
        
        Agent->>EC: context(action="get_context")
        EC-->>Agent: 返回完整上下文
    else 简单任务
        Note over Agent: 直接执行，不使用ExecutionContext
    end
```

## 4. 知识文件加载流程

```mermaid
sequenceDiagram
    participant Agent as ReactAgentMinimal
    participant Resolver as _resolve_knowledge_files
    participant Loader as _load_knowledge
    participant Package as _load_knowledge_package
    participant FS as FileSystem
    
    Agent->>Agent: __init__(knowledge_files=[...])
    
    Agent->>Resolver: 解析知识文件列表
    activate Resolver
    loop 每个文件路径
        Resolver->>Resolver: 处理路径（相对/绝对）
        Resolver->>FS: 检查文件存在
        FS-->>Resolver: 文件状态
    end
    Resolver-->>Agent: 解析后的文件列表
    deactivate Resolver
    
    Agent->>Package: 加载minimal/system包
    activate Package
    Package->>FS: 读取__init__.md
    FS-->>Package: 导出模块列表
    Package->>Agent: 添加系统文件到列表
    deactivate Package
    
    Agent->>Loader: _load_knowledge()
    activate Loader
    loop 每个知识文件
        Loader->>FS: 读取文件内容
        FS-->>Loader: 文件内容
        Loader->>Loader: 合并内容
    end
    Loader-->>Agent: knowledge_content
    deactivate Loader
```

## 5. Agent组合调用流程（Agent作为工具）

```mermaid
sequenceDiagram
    participant User
    participant PM as Project Manager Agent
    participant PSM as PSM Agent
    participant Code as Code Agent
    participant Debug as Debug Agent
    
    User->>PM: 执行MDA工作流
    activate PM
    
    PM->>PM: 分析任务
    PM->>PSM: psm_generation_agent(生成PSM文档)
    activate PSM
    PSM->>PSM: 读取PIM
    PSM->>PSM: 生成PSM
    PSM-->>PM: PSM文档完成
    deactivate PSM
    
    PM->>Code: code_generation_agent(生成代码)
    activate Code
    Code->>Code: 读取PSM
    Code->>Code: 生成代码文件
    Code-->>PM: 代码生成完成
    deactivate Code
    
    PM->>Debug: debug_agent(调试代码)
    activate Debug
    Debug->>Debug: 运行测试
    Debug->>Debug: 修复问题
    Debug-->>PM: 调试完成
    deactivate Debug
    
    PM-->>User: 工作流完成
    deactivate PM
```

## 6. Compact记忆压缩流程

```mermaid
sequenceDiagram
    participant Agent as ReactAgentMinimal
    participant Compress as 压缩逻辑
    participant LLM as 压缩模型
    participant FS as FileSystem
    
    Agent->>Agent: 执行任务
    
    loop 每轮执行后
        Agent->>Agent: _should_compress()
        
        alt tokens > 70000
            Agent->>Compress: _compress_memory()
            activate Compress
            
            Compress->>Compress: 准备压缩prompt
            Compress->>LLM: 调用grok-code-fast-1
            LLM-->>Compress: 压缩后的记忆
            
            Compress->>FS: 保存到compact.md
            FS-->>Compress: 保存成功
            
            Compress->>Agent: 更新compact_memory
            deactivate Compress
            
            Agent->>Agent: 清理消息历史
            Agent->>Agent: 保留系统消息和压缩记忆
        end
    end
```

## 关键交互说明

### 1. 函数调用机制
- 所有工具和Agent都实现Function接口
- 通过`to_openai_function()`转换为LLM可理解的格式
- LLM返回tool_calls后，Agent查找并执行对应函数

### 2. 知识系统
- 知识文件在初始化时加载
- 系统知识优先级高于用户指定知识
- 知识内容直接注入到系统提示词中

### 3. 状态管理
- ExecutionContext提供纯内存的状态管理
- 不进行文件持久化
- 适用于复杂多步骤任务

### 4. 记忆管理
- Compact记忆自动触发压缩
- 使用独立的LLM进行智能压缩
- 压缩后的记忆保存到文件供下次使用

### 5. 工具组合
- Agent可以添加其他Agent作为工具
- 实现了天然的LLM切换和任务分发
- 支持构建复杂的工作流