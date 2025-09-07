# OS-Agent与Program-Agent交互架构图

## 1. 整体架构图

```mermaid
graph TB
    subgraph "用户层"
        User[用户]
    end
    
    subgraph "OS层 (管理层)"
        OSAgent[OSAgent<br/>ReactAgentMinimal +<br/>os_agent_knowledge.md]
        OSKnowledge[(OS知识库<br/>- structured_notes.md<br/>- mandatory_protocol.md<br/>- os_agent_knowledge.md)]
    end
    
    subgraph "应用层 (执行层)"
        ProgramAgent[ProgramAgent<br/>ReactAgentMinimal +<br/>task_knowledge.md]
        TaskKnowledge[(任务知识库<br/>- generation_knowledge.md<br/>- debug_knowledge.md<br/>- optimization_knowledge.md)]
    end
    
    subgraph "存储层"
        Sessions[(.sessions/)]
        Notes[(.notes/)]
        WorldState[(world_state.md)]
    end
    
    User -->|任务请求| OSAgent
    OSAgent -->|读取| OSKnowledge
    OSAgent -->|创建实例| ProgramAgent
    ProgramAgent -->|读取| TaskKnowledge
    ProgramAgent -->|返回结果| OSAgent
    OSAgent -->|强制写入| Sessions
    OSAgent -->|更新| Notes
    OSAgent -->|更新| WorldState
    OSAgent -->|返回结果| User
    
    style OSAgent fill:#f9f,stroke:#333,stroke-width:4px
    style ProgramAgent fill:#9ff,stroke:#333,stroke-width:2px
```

## 2. 执行时序图

```mermaid
sequenceDiagram
    participant User as 用户
    participant OS as OSAgent
    participant PA as ProgramAgent
    participant FS as 文件系统
    
    User->>OS: execute("生成博客系统")
    
    Note over OS: 初始化阶段
    OS->>FS: mkdir -p .sessions .notes
    OS->>FS: read agent_knowledge.md
    OS->>FS: read world_state.md
    OS->>FS: write task_process.md (TODO)
    
    Note over OS: 创建ProgramAgent
    OS->>OS: 选择知识文件<br/>[generation_knowledge.md]
    
    OS->>PA: new ReactAgentMinimal(<br/>knowledge=[task_knowledge],<br/>skip_notes=True)
    
    Note over PA: 执行任务
    PA->>PA: 读取任务知识
    PA->>PA: 执行生成逻辑
    PA->>FS: 创建代码文件
    PA-->>OS: return {result, rounds}
    
    Note over OS: 强制笔记管理
    OS->>FS: write .sessions/2024-09-05_generate.md
    OS->>FS: update agent_knowledge.md
    OS->>FS: update world_state.md
    OS->>FS: clear task_process.md
    
    OS-->>User: return "任务完成"
```

## 3. 控制流对比图

### 3.1 当前架构（脆弱）

```mermaid
graph LR
    subgraph "当前架构 - 分布式控制"
        User1[用户] -->|任务| Agent1[ReactAgent]
        Agent1 -->|自主决定| Decision{写笔记?}
        Decision -->|是| Write1[写入笔记]
        Decision -->|否<br/>任务简单| Skip1[跳过]
        Agent1 --> Result1[返回结果]
    end
    
    style Decision fill:#faa,stroke:#333,stroke-width:2px
    style Skip1 fill:#faa,stroke:#333,stroke-width:2px
```

### 3.2 OS-Agent架构（强壮）

```mermaid
graph LR
    subgraph "OS-Agent架构 - 中央控制"
        User2[用户] -->|任务| OS2[OSAgent]
        OS2 -->|创建| PA2[ProgramAgent]
        PA2 -->|纯执行| Exec2[执行任务]
        Exec2 -->|结果| OS2
        OS2 -->|强制| Write2[写入笔记]
        Write2 --> Result2[返回结果]
    end
    
    style OS2 fill:#afa,stroke:#333,stroke-width:4px
    style Write2 fill:#afa,stroke:#333,stroke-width:2px
```

## 4. 知识隔离图

```mermaid
graph TD
    subgraph "知识域隔离"
        subgraph "系统知识域"
            SK1[structured_notes.md]
            SK2[mandatory_protocol.md]
            SK3[os_agent_knowledge.md]
        end
        
        subgraph "任务知识域"
            TK1[generation_knowledge.md]
            TK2[debug_knowledge.md]
            TK3[optimization_knowledge.md]
            TK4[domain_patterns.md]
        end
        
        OSA[OSAgent] -->|只能访问| SK1
        OSA -->|只能访问| SK2
        OSA -->|只能访问| SK3
        
        PA[ProgramAgent] -->|只能访问| TK1
        PA -->|只能访问| TK2
        PA -->|只能访问| TK3
        PA -->|只能访问| TK4
        
        OSA -.->|不能访问| TK1
        PA -.->|不能访问| SK1
    end
    
    style OSA fill:#f9f,stroke:#333,stroke-width:4px
    style PA fill:#9ff,stroke:#333,stroke-width:2px
```

## 5. Function组合图

```mermaid
graph TD
    subgraph "Function = ReactAgentMinimal + Knowledge"
        RAF[ReactAgentMinimal<br/>通用执行器]
        
        K1[os_agent_knowledge.md]
        K2[generation_knowledge.md]
        K3[debug_knowledge.md]
        K4[optimization_knowledge.md]
        
        RAF --> OSF[OSAgent Function]
        K1 --> OSF
        
        RAF --> GenF[Generation Function]
        K2 --> GenF
        
        RAF --> DebugF[Debug Function]
        K3 --> DebugF
        
        RAF --> OptF[Optimize Function]
        K4 --> OptF
    end
    
    style RAF fill:#ff9,stroke:#333,stroke-width:4px
    style OSF fill:#f9f,stroke:#333,stroke-width:2px
    style GenF fill:#9ff,stroke:#333,stroke-width:2px
    style DebugF fill:#9ff,stroke:#333,stroke-width:2px
    style OptF fill:#9ff,stroke:#333,stroke-width:2px
```

## 6. 生命周期管理图

```mermaid
stateDiagram-v2
    [*] --> Idle: OSAgent启动
    
    Idle --> TaskReceived: 收到用户任务
    
    TaskReceived --> Initialize: 初始化笔记系统
    
    Initialize --> CreatePA: 创建ProgramAgent
    
    CreatePA --> Executing: ProgramAgent执行中
    
    Executing --> Success: 执行成功
    Executing --> Failed: 执行失败
    
    Success --> WritingNotes: 写入成功笔记
    Failed --> WritingNotes: 写入失败笔记
    
    WritingNotes --> UpdateKnowledge: 更新知识库
    
    UpdateKnowledge --> UpdateWorld: 更新世界状态
    
    UpdateWorld --> Cleanup: 清理资源
    
    Cleanup --> Idle: 返回结果
    
    note right of WritingNotes
        强制执行
        不依赖ProgramAgent
    end note
    
    note right of Executing
        ProgramAgent不知道
        笔记系统存在
    end note
```

## 7. 错误处理流程图

```mermaid
flowchart TD
    Start([开始执行]) --> TryExec{尝试执行任务}
    
    TryExec -->|成功| Success[获得结果]
    TryExec -->|失败| CatchError[捕获异常]
    
    Success --> WriteSession1[创建成功session]
    CatchError --> WriteSession2[创建失败session]
    
    WriteSession1 --> UpdateKnowledge1[更新知识:成功模式]
    WriteSession2 --> UpdateKnowledge2[更新知识:失败模式]
    
    UpdateKnowledge1 --> UpdateWorld
    UpdateKnowledge2 --> UpdateWorld
    
    UpdateWorld[更新world_state] --> Return([返回给用户])
    
    style CatchError fill:#faa
    style WriteSession2 fill:#ffa
    style WriteSession1 fill:#afa
    style UpdateWorld fill:#aaf
```

## 8. Linux类比图

```mermaid
graph TD
    subgraph "Linux内核架构"
        Kernel[Linux Kernel]
        Process[User Process]
        PageTable[(Page Table)]
        VFS[(VFS)]
        
        Kernel -->|fork()| Process
        Process -->|malloc()| Kernel
        Kernel -->|管理| PageTable
        Kernel -->|管理| VFS
    end
    
    subgraph "OS-Agent架构"
        OSAgent1[OSAgent]
        ProgramAgent1[ProgramAgent]
        Notes1[(.notes/)]
        Sessions1[(.sessions/)]
        
        OSAgent1 -->|创建| ProgramAgent1
        ProgramAgent1 -->|返回结果| OSAgent1
        OSAgent1 -->|管理| Notes1
        OSAgent1 -->|管理| Sessions1
    end
    
    Kernel -.->|对应| OSAgent1
    Process -.->|对应| ProgramAgent1
    PageTable -.->|对应| Notes1
    VFS -.->|对应| Sessions1
    
    style Kernel fill:#f9f
    style OSAgent1 fill:#f9f
    style Process fill:#9ff
    style ProgramAgent1 fill:#9ff
```

## 关键点总结

1. **控制权永不转移**：OSAgent始终掌控全局
2. **知识域隔离**：系统知识与任务知识完全分离
3. **结构性保证**：笔记创建是结构化的，不是可选的
4. **Function组合**：通过知识组合创建不同的Agent Function
5. **生命周期管理**：OSAgent负责ProgramAgent的完整生命周期

这个架构通过清晰的层次分离和控制流设计，确保了笔记系统的可靠性和系统的健壮性。