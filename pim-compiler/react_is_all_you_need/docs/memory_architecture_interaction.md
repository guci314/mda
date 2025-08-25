# 记忆系统架构交互图

本文档详细说明 ReactAgent、CognitiveMemoryIntegration 和 NLPLMemorySystem 三者的交互关系。

## 整体架构交互图

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#fff', 'primaryTextColor':'#000', 'primaryBorderColor':'#000', 'lineColor':'#000', 'secondaryColor':'#f5f5f5', 'tertiaryColor':'#fff', 'fontFamily':'Arial', 'fontSize':'16px'}}}%%
graph TB
    subgraph "应用层 Application Layer"
        User[用户]
        ReactAgent[ReactAgent<br/>任务执行器]
    end
    
    subgraph "集成层 Integration Layer"
        CMI[CognitiveMemoryIntegration<br/>认知记忆集成]
    end
    
    subgraph "技术层 Technical Layer"
        SMM[SimpleMemoryManager<br/>滑动窗口]
        MMA[MemoryManagerAdapter<br/>兼容适配器]
    end
    
    subgraph "认知层 Cognitive Layer"
        NLPL[NLPLMemorySystem<br/>认知记忆系统]
        subgraph "4层Agent体系"
            L1[L1 工作Agent]
            L2[L2 观察Agent]
            L3[L3 海马体Agent]
            L4[L4 元认知Agent]
        end
    end
    
    subgraph "存储层 Storage Layer"
        FS[(文件系统<br/>.memory/)]
        subgraph "记忆文件"
            EP[episodic/*.nlpl]
            SE[semantic/*.nlpl]
            PR[procedural/*.nlpl]
            MC[metacognitive/*.nlpl]
        end
    end
    
    User -->|任务| ReactAgent
    ReactAgent -->|消息| MMA
    MMA -->|委托| SMM
    ReactAgent -.->|可选集成| CMI
    
    CMI -->|管理| SMM
    CMI -->|协调| NLPL
    
    SMM -->|消息流| CMI
    CMI -->|触发阈值| L2
    CMI -->|事件累积| L3
    CMI -->|轮数统计| L4
    
    NLPL -->|生成记忆| FS
    L2 -->|观察分析| EP
    L3 -->|知识提取| SE
    L3 -->|技能总结| PR
    L4 -->|系统评估| MC
    
    style User fill:#ffccff,stroke:#000,stroke-width:3px,color:#000
    style ReactAgent fill:#ccccff,stroke:#000,stroke-width:3px,color:#000
    style CMI fill:#ffccff,stroke:#000,stroke-width:3px,color:#000
    style NLPL fill:#ccffcc,stroke:#000,stroke-width:3px,color:#000
    style FS fill:#ffffcc,stroke:#000,stroke-width:3px,color:#000
    style SMM fill:#e6f3ff,stroke:#000,stroke-width:2px,color:#000
    style MMA fill:#ffe6e6,stroke:#000,stroke-width:2px,color:#000
    
    classDef default fill:#fff,stroke:#000,stroke-width:2px,color:#000
    classDef layerStyle fill:#f0f0f0,stroke:#000,stroke-width:3px,color:#000
```

## 详细交互流程

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryTextColor':'#000', 'lineColor':'#000', 'signalColor':'#000', 'signalTextColor':'#000', 'actorTextColor':'#000', 'actorLineColor':'#000'}}}%%
sequenceDiagram
    participant U as 用户
    participant RA as ReactAgent
    participant MMA as MemoryAdapter
    participant CMI as CognitiveMemory<br/>Integration
    participant SMM as SimpleMemory<br/>Manager
    participant NLPL as NLPLMemory<br/>System
    participant L2 as L2观察Agent
    participant FS as 文件系统
    
    U->>RA: 执行任务
    
    loop 任务执行循环
        RA->>RA: 思考 & 工具调用
        RA->>MMA: add_message(消息)
        MMA->>SMM: 转发消息
        
        Note over SMM: 滑动窗口管理
        SMM->>SMM: 检查窗口大小
        SMM->>SMM: 丢弃旧消息
        
        opt 使用认知集成
            MMA->>CMI: 同步消息
            CMI->>CMI: 计数器+1
            
            alt 消息数 % 10 == 0
                CMI->>L2: 触发观察分析
                L2->>NLPL: 生成观察报告
                NLPL->>FS: 写入detailed.nlpl
                NLPL->>FS: 写入summary.nlpl
                NLPL->>FS: 写入gist.nlpl
            else 事件数 >= 50
                CMI->>CMI: 触发海马体巩固
                Note over NLPL: 提取模式和概念
                NLPL->>FS: 写入semantic/*.nlpl
                NLPL->>FS: 写入procedural/*.nlpl
            else 轮数 >= 100
                CMI->>CMI: 触发元认知反思
                Note over NLPL: 系统评估
                NLPL->>FS: 写入metacognitive/*.nlpl
            end
        end
    end
    
    RA->>U: 返回结果
```

## 数据流向图

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#fff', 'primaryTextColor':'#000', 'primaryBorderColor':'#000', 'lineColor':'#000'}}}%%
graph LR
    subgraph "消息流 Message Flow"
        M1[用户输入] --> M2[ReactAgent处理]
        M2 --> M3[工具调用结果]
        M3 --> M4[助手响应]
    end
    
    subgraph "窗口管理 Window Management"
        M4 --> W1[添加到窗口]
        W1 --> W2[检查窗口大小]
        W2 -->|超限| W3[丢弃最旧消息]
        W2 -->|未超限| W4[保留所有消息]
    end
    
    subgraph "认知处理 Cognitive Processing"
        W4 --> C1{检查触发条件}
        C1 -->|10条消息| C2[观察分析]
        C1 -->|50个事件| C3[记忆巩固]
        C1 -->|100轮| C4[元认知反思]
        
        C2 --> C5[生成情景记忆]
        C3 --> C6[提取语义概念]
        C3 --> C7[总结程序技能]
        C4 --> C8[系统优化]
    end
    
    subgraph "持久化 Persistence"
        C5 --> P1[episodic/*.nlpl]
        C6 --> P2[semantic/*.nlpl]
        C7 --> P3[procedural/*.nlpl]
        C8 --> P4[metacognitive/*.nlpl]
    end
    
    style M1 fill:#ffaaaa,stroke:#000,stroke-width:2px,color:#000
    style C1 fill:#aaffaa,stroke:#000,stroke-width:2px,color:#000
    style P1 fill:#aaaaff,stroke:#000,stroke-width:2px,color:#000
    
    classDef default fill:#fff,stroke:#000,stroke-width:2px,color:#000
```

## 组件职责分工

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#fff', 'primaryTextColor':'#000', 'primaryBorderColor':'#000', 'lineColor':'#000'}}}%%
graph TD
    subgraph "ReactAgent 职责"
        RA1[执行任务]
        RA2[调用工具]
        RA3[生成响应]
        RA4[管理执行流程]
    end
    
    subgraph "CognitiveMemoryIntegration 职责"
        CMI1[协调两个系统]
        CMI2[触发认知处理]
        CMI3[管理Agent生命周期]
        CMI4[统计和监控]
    end
    
    subgraph "SimpleMemoryManager 职责"
        SMM1[维护消息窗口]
        SMM2[自动丢弃旧消息]
        SMM3[提供LLM上下文]
        SMM4[消息统计]
    end
    
    subgraph "NLPLMemorySystem 职责"
        NLPL1[生成三层记忆]
        NLPL2[知识提取]
        NLPL3[时间衰减]
        NLPL4[语义搜索]
    end
    
    RA1 --> CMI1
    CMI1 --> SMM1
    CMI2 --> NLPL1
    
    style RA1 fill:#ff9966,stroke:#000,stroke-width:2px,color:#000
    style CMI1 fill:#99ff66,stroke:#000,stroke-width:2px,color:#000
    style SMM1 fill:#6699ff,stroke:#000,stroke-width:2px,color:#000
    style NLPL1 fill:#ff6699,stroke:#000,stroke-width:2px,color:#000
    
    classDef default fill:#fff,stroke:#000,stroke-width:2px,color:#000
```

## 触发机制详解

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#fff', 'primaryTextColor':'#000', 'primaryBorderColor':'#000', 'stateBkg':'#f9f9f9', 'stateBorder':'#000'}}}%%
stateDiagram-v2
    [*] --> 消息接收
    
    消息接收 --> 计数更新: add_message()
    
    计数更新 --> 检查触发条件
    
    state 检查触发条件 {
        [*] --> 消息计数
        消息计数 --> 观察触发: count % 10 == 0
        消息计数 --> 继续: count % 10 != 0
        
        [*] --> 事件计数
        事件计数 --> 巩固触发: events >= 50
        事件计数 --> 继续: events < 50
        
        [*] --> 轮数计数
        轮数计数 --> 反思触发: rounds >= 100
        轮数计数 --> 继续: rounds < 100
    }
    
    观察触发 --> L2观察Agent
    L2观察Agent --> 生成情景记忆
    生成情景记忆 --> 重置计数器
    
    巩固触发 --> L3海马体Agent
    L3海马体Agent --> 提取知识
    提取知识 --> 重置计数器
    
    反思触发 --> L4元认知Agent
    L4元认知Agent --> 系统评估
    系统评估 --> 重置计数器
    
    继续 --> [*]
    重置计数器 --> [*]
```

## 记忆类型与清晰度

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#fff', 'primaryTextColor':'#000', 'primaryBorderColor':'#000', 'lineColor':'#000'}}}%%
graph TD
    subgraph "记忆生成流程"
        Event[事件发生] --> ME[MemoryEvent对象]
        ME --> NLPL[NLPLMemorySystem]
        
        NLPL --> D[detailed.nlpl<br/>完整细节]
        NLPL --> S[summary.nlpl<br/>关键摘要]
        NLPL --> G[gist.nlpl<br/>核心要点]
    end
    
    subgraph "记忆类型"
        D --> Episodic[情景记忆<br/>事件序列]
        S --> Semantic[语义记忆<br/>概念知识]
        G --> Procedural[程序记忆<br/>技能步骤]
    end
    
    subgraph "时间衰减"
        Episodic -->|7天后| RemoveD[删除detailed]
        RemoveD -->|30天后| RemoveS[删除summary]
        RemoveS -->|90天后| Archive[归档gist]
    end
    
    style Event fill:#ffaaaa,stroke:#000,stroke-width:2px,color:#000
    style NLPL fill:#aaffaa,stroke:#000,stroke-width:2px,color:#000
    style Archive fill:#aaaaff,stroke:#000,stroke-width:2px,color:#000
    
    classDef default fill:#fff,stroke:#000,stroke-width:2px,color:#000
```

## API 调用关系

```mermaid
%%{init: {'theme':'base', 'themeVariables': { 'primaryColor':'#fff', 'primaryTextColor':'#000', 'primaryBorderColor':'#000', 'lineColor':'#000', 'classText':'#000'}}}%%
classDiagram
    class ReactAgent {
        +execute_task(task)
        +memory: MemoryManagerAdapter
        -_think_and_act()
        -_call_tools()
    }
    
    class MemoryManagerAdapter {
        +add_message(role_or_msg, content)
        +get_context()
        +save_episode()
        -window_size
        -messages
    }
    
    class CognitiveMemoryIntegration {
        +add_message(role, content)
        +process_task_completion()
        +search_memory(query)
        +get_stats()
        -message_manager: SimpleMemoryManager
        -memory_system: NLPLMemorySystem
        -_trigger_observation()
        -_trigger_consolidation()
        -_trigger_metacognition()
    }
    
    class SimpleMemoryManager {
        +add_message(role, content)
        +get_messages()
        +get_context()
        +get_stats()
        -window_size
        -messages: deque
    }
    
    class NLPLMemorySystem {
        +create_episodic_memory()
        +create_semantic_concept()
        +create_procedural_skill()
        +search_memories()
        +apply_temporal_decay()
        -memory_dir: Path
    }
    
    ReactAgent --> MemoryManagerAdapter: uses
    MemoryManagerAdapter --|> SimpleMemoryManager: extends
    CognitiveMemoryIntegration --> SimpleMemoryManager: manages
    CognitiveMemoryIntegration --> NLPLMemorySystem: coordinates
    CognitiveMemoryIntegration --> ReactAgent: triggers agents
```

## 关键交互点

### 1. ReactAgent → MemoryManagerAdapter
- **时机**：每次生成消息或调用工具
- **数据**：消息字典或分离的参数
- **目的**：维护对话上下文

### 2. CognitiveMemoryIntegration → SimpleMemoryManager
- **时机**：接收新消息
- **数据**：role 和 content
- **目的**：管理滑动窗口

### 3. CognitiveMemoryIntegration → NLPLMemorySystem
- **时机**：达到触发阈值
- **数据**：MemoryEvent 对象
- **目的**：生成认知记忆

### 4. NLPLMemorySystem → 文件系统
- **时机**：创建记忆
- **数据**：NLPL 格式文本
- **目的**：持久化存储

## 使用模式

### 模式1：独立使用 ReactAgent
```python
agent = ReactAgent(work_dir=".", memory_mode=None)
agent.memory = MemoryManagerAdapter()
result = agent.execute_task(task)
```

### 模式2：集成认知记忆
```python
cognitive = CognitiveMemoryIntegration(work_dir=".")
# 在任务执行中调用
cognitive.add_message(role, content)
cognitive.process_task_completion(task_name, success, rounds)
```

### 模式3：直接使用 NLPL
```python
memory = NLPLMemorySystem(".memory")
event = MemoryEvent(...)
detailed, summary, gist = memory.create_episodic_memory(event)
```

## 总结

这个三层架构实现了：
1. **分离关注点**：技术层（消息管理）与认知层（记忆生成）分离
2. **灵活集成**：各组件可独立使用或组合使用
3. **智能触发**：基于阈值的自动认知处理
4. **认知真实**：模拟人类记忆的三层清晰度和时间衰减