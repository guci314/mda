# React Agent 架构模型

## 1. 类图

### 核心类关系

```
┌─────────────────────────────────────────────────────┐
│                     Function                         │
│  (Abstract Base Class)                               │
├─────────────────────────────────────────────────────┤
│ + name: str                                          │
│ + description: str                                   │
│ + parameters: dict                                   │
├─────────────────────────────────────────────────────┤
│ + execute(**kwargs) -> str                          │
│ + to_openai_function() -> dict                      │
│ + __call__(task: str) -> str                        │
└─────────────────────────────────────────────────────┘
                            △
                            │ inherits
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────────────────────┐         ┌─────────────────────────┐
│  ReactAgentMinimal    │         │   CreateAgentTool       │
│  (Agent as Function)  │         │   (Tool)                │
├───────────────────────┤         ├─────────────────────────┤
│ + work_dir: Path      │         │ + work_dir: str         │
│ + model: str          │         │ + parent_agent: Agent   │
│ + api_key: str        │         │ + created_agents: dict  │
│ + agent_name: str     │         ├─────────────────────────┤
│ + notes_dir: Path     │         │ + execute(**kwargs)     │
│ + tools: list         │         │ + _get_api_config()     │
│ + tool_instances: list│         └─────────────────────────┘
│ + messages: list      │
│ + knowledge_files:list│
│ + max_rounds: int     │
├───────────────────────┤
│ + execute(task: str)  │
│ + _think()            │
│ + _act()              │
│ + _observe()          │
│ + _update_notes()     │
│ + _load_knowledge()   │
│ + _clean_window()     │
└───────────────────────┘
```

### 关键概念
- **Agent = Function = Tool**: ReactAgentMinimal既是Agent又是Function，可以作为工具被调用
- **继承关系**: 所有工具和Agent都继承自Function基类
- **组合关系**: ReactAgentMinimal包含tool_instances列表，可以包含其他Agent

## 2. 组件图

### 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      React Agent System                      │
├───────────────────┬─────────────────┬───────────────────────┤
│                   │                 │                       │
│  Core Components  │  Knowledge Base │    File System       │
│                   │                 │                       │
│ ┌───────────────┐ │ ┌─────────────┐ │ ┌─────────────────┐ │
│ │ReactAgent     │ │ │structured_  │ │ │.notes/          │ │
│ │Minimal        │◄├─┤notes.md     │ │ │├─agent_name/    │ │
│ └───────┬───────┘ │ └─────────────┘ │ │  ├─agent_       │ │
│         │         │ ┌─────────────┐ │ │  │ knowledge.md │ │
│         ▼         │ │system_      │ │ │  ├─task_        │ │
│ ┌───────────────┐ │ │prompt.md    │ │ │  │ process.md   │ │
│ │Function Base  │◄├─┤             │ │ │  └─world_       │ │
│ └───────┬───────┘ │ └─────────────┘ │ │    state.md     │ │
│         │         │ ┌─────────────┐ │ └─────────────────┘ │
│         ▼         │ │meta_        │ │                     │
│ ┌───────────────┐ │ │cognitive_   │ │ ┌─────────────────┐ │
│ │CreateAgent    │◄├─┤simple.md    │ │ │Working Files    │ │
│ │Tool           │ │ └─────────────┘ │ │(*.py, *.md, etc)│ │
│ └───────────────┘ │ ┌─────────────┐ │ └─────────────────┘ │
│                   │ │debug_       │ │                     │
│                   │ │knowledge.md │ │                     │
│                   │ └─────────────┘ │                     │
└───────────────────┴─────────────────┴───────────────────────┘
```

### 数据流
- **知识加载**: Knowledge Files → ReactAgentMinimal
- **笔记更新**: ReactAgentMinimal → Notes Directory
- **工具调用**: ReactAgentMinimal ↔ Function Tools
- **Agent创建**: CreateAgentTool → New ReactAgentMinimal Instance

## 3. 序列图

### Agent创建和调用流程

```
MetaAgent          CreateAgentTool       NewAgent         Task
    │                     │                  │              │
    ├──analyze task───────▶                  │              │
    │                     │                  │              │
    ├──create_agent()─────▶                  │              │
    │                     │                  │              │
    │              ┌──────┴──────┐           │              │
    │              │ Create new  │           │              │
    │              │ Agent inst. │           │              │
    │              └──────┬──────┘           │              │
    │                     │                  │              │
    │                     ├──new Agent()─────▶              │
    │                     │                  │              │
    │◄────return name─────┤                  │              │
    │                     │                  │              │
    ├──agent_name(task)───────────────────────▶              │
    │                     │                  │              │
    │                     │           ┌──────┴──────┐        │
    │                     │           │Think-Act-   │        │
    │                     │           │Observe loop │        │
    │                     │           └──────┬──────┘        │
    │                     │                  │              │
    │                     │                  ├──execute─────▶
    │                     │                  │              │
    │◄────────────────────result──────────────┤              │
    │                     │                  │              │
```

## 4. 状态图

### Agent生命周期

```
        ┌─────────┐
        │ Created │
        └────┬────┘
             │ initialized
             ▼
        ┌─────────┐
        │  Idle   │◄────────────┐
        └────┬────┘             │
             │ receive task     │
             ▼                  │
        ┌─────────┐             │
        │Thinking │             │
        └────┬────┘             │
             │ generate action  │
             ▼                  │
        ┌─────────┐             │
        │ Acting  │             │
        └────┬────┘             │
             │ execute tool     │
             ▼                  │
        ┌──────────┐            │
        │Observing │            │
        └────┬─────┘            │
             │ process result   │
             ▼                  │
        ┌──────────┐            │
        │ Updating │            │
        │  Notes   │            │
        └────┬─────┘            │
             │                  │
             ├──task complete───┤
             │                  │
             └──continue────────┘
```

## 5. 部署图

### 文件系统结构

```
react_is_all_you_need/
│
├── core/
│   ├── react_agent_minimal.py    [核心Agent实现]
│   ├── tool_base.py              [Function基类]
│   └── tools/
│       └── create_agent_tool.py  [Agent创建工具]
│
├── knowledge/                    [知识文件目录]
│   ├── structured_notes.md       [笔记系统知识]
│   ├── system_prompt.md          [系统提示]
│   ├── meta_cognitive_simple.md  [元认知知识]
│   └── debug_knowledge.md        [调试知识]
│
├── .notes/                       [笔记目录]
│   ├── main_agent/              [主Agent笔记]
│   │   ├── agent_knowledge.md
│   │   ├── task_process.md
│   │   └── world_state.md
│   │
│   └── {agent_name}/            [子Agent笔记]
│       ├── agent_knowledge.md
│       ├── task_process.md
│       └── world_state.md
│
└── test_*.py                    [测试文件]
```

## 6. 核心设计原则

### 架构特点

1. **Agent即Function**
   - Agent继承自Function基类
   - 可以像工具一样被调用
   - 支持多次调用（有状态）

2. **Share Nothing架构**
   - 每个Agent独立的笔记目录
   - 独立的世界状态投影
   - 通过消息传递通信

3. **知识驱动**
   - 行为由Markdown知识文件定义
   - 代码只是执行框架
   - 知识文件即程序

4. **显式压缩**
   - 通过写笔记实现记忆压缩
   - 三层记忆架构
   - 压缩策略可通过知识文件定制

### 记忆层次

```
┌──────────────────────────────────┐
│   工作记忆 (Working Memory)       │
│   - 滑动窗口 (50条消息)           │
└──────────────────────────────────┘
                ▼
┌──────────────────────────────────┐
│   情景记忆 (Episodic Memory)      │
│   - task_process.md              │
└──────────────────────────────────┘
                ▼
┌──────────────────────────────────┐
│   语义记忆 (Semantic Memory)      │
│   - agent_knowledge.md           │
│   - world_state.md               │
└──────────────────────────────────┘
```

## 7. 核心公式

**React + 文件系统 = 冯·诺依曼架构 = 图灵完备 + 无限存储 = 可计算函数的全集**

- React Agent = CPU
- 上下文窗口 = RAM
- 文件系统 = 硬盘
- 知识文件 = 程序
- 工作文件 = 数据