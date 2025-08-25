# React Agent 核心模块文档

## 目录结构概览

```
core/
├── __init__.py                 # 模块初始化
├── react_agent.py              # 核心Agent实现
├── tools.py                    # 工具集定义
├── langchain_agent_tool.py    # Agent as Tool机制
├── debug_tools.py              # 调试专用工具
└── README.md                   # 基础说明文档
```

## 核心模块详解

### 1. react_agent.py - React Agent主体实现

**主要组件：**
- `GenericReactAgent`: 基于LangChain的通用React Agent实现
- `ReactAgentConfig`: Agent配置类
- `MemoryLevel`: 记忆级别枚举

**核心特性：**
1. **三级记忆系统**
   - NONE: 无记忆，每次执行独立
   - SMART: 智能缓冲，会话级记忆
   - PRO: 持久存储，跨会话记忆

2. **先验知识注入**
   - 支持通过knowledge_files注入领域知识
   - 支持include机制动态加载知识

3. **LLM灵活配置**
   - 支持任何OpenAI兼容的LLM
   - 默认集成DeepSeek、Kimi、Gemini等模型
   - 支持自定义base_url和API key

4. **React执行循环**
   - Thought: 思考当前状态和下一步
   - Action: 执行工具调用
   - Observation: 观察执行结果

**使用示例：**
```python
config = ReactAgentConfig(
    work_dir="output",
    memory_level=MemoryLevel.SMART,
    knowledge_files=["knowledge/python.md"],
    llm_model="google/gemini-2.5-pro",
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY"
)
agent = GenericReactAgent(config, name="my_agent")
result = agent.execute_task("创建一个REST API服务")
```

### 2. tools.py - 工具集定义

**工具类别：**

1. **文件操作工具**
   - `read_file`: 读取文件内容
   - `write_file`: 写入文件
   - `edit_lines`: 编辑文件特定行
   - `append_to_file`: 追加内容到文件
   - `create_directory`: 创建目录
   - `list_directory`: 列出目录内容

2. **搜索工具**
   - `search_files`: 搜索文件内容
   - `find_symbol`: 查找代码符号
   - `search_definition`: 搜索定义
   - `find_file`: 查找文件路径

3. **执行工具**
   - `execute_command`: 执行shell命令
   - `run_python`: 执行Python代码

4. **Web工具（可选）**
   - `google_search`: Google搜索
   - `read_web_page`: 读取网页内容

**设计理念：**
- 工具集定义了Agent的"计算边界"
- 类似操作系统的系统调用接口
- 工具是Agent与外部世界交互的唯一方式

### 3. langchain_agent_tool.py - Agent as Tool机制

**核心功能：**
- `AgentToolWrapper`: 将Agent包装为可调用的工具
- `create_langchain_tool`: 创建LangChain兼容的工具

**实现原理：**
1. 将整个Agent封装为一个Tool
2. 其他Agent可以调用这个Tool
3. 实现Agent间的协作和层级调用

**使用场景：**
- 多Agent协作系统
- 专家Agent系统（每个Agent负责特定领域）
- 层级化任务分解

**示例：**
```python
# 创建专家Agent配置
expert_config = ReactAgentConfig(
    work_dir="output",
    llm_model="google/gemini-2.5-pro",
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY"
)
expert_agent = GenericReactAgent(expert_config, name="python_expert")

# 包装为工具
expert_tool = create_langchain_tool(
    expert_agent,
    name="python_expert",
    description="Python编程专家"
)

# 主Agent配置
main_config = ReactAgentConfig(
    work_dir="output",
    llm_model="google/gemini-2.5-pro",
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY"
)
main_agent = GenericReactAgent(main_config)
main_agent.add_tool(expert_tool)
```

### 4. debug_tools.py - 调试专用工具

**功能模块：**

1. **调试笔记管理**
   - 记录错误历史
   - 保存修复策略
   - 归档调试会话

2. **Python语法错误修复**
   - AST解析和错误定位
   - 自动修复常见语法错误
   - 智能缩进修正

3. **调试状态压缩**
   - 防止调试笔记过大
   - 自动归档历史记录
   - 保留关键调试信息

**核心函数：**
- `compress_debug_notes`: 压缩调试笔记
- `fix_python_syntax`: 修复Python语法错误
- `archive_debug_session`: 归档调试会话

## 设计理念总结

### 1. 自然语言虚拟机
- React循环 = CPU取指-执行循环
- 知识文件 = 程序
- 工具集 = 系统调用
- Agent协作 = 分布式计算

### 2. 知识驱动编程
- 通过知识文件定义行为，而非硬编码
- 支持动态知识注入和include机制
- 知识可组合、可复用

### 3. 工具闭包原则
- 工具集定义了Agent的能力边界
- 所有外部交互必须通过工具
- 工具是Agent的"系统调用接口"

## 扩展性设计

1. **LLM无关性**：支持任何OpenAI兼容的LLM
2. **工具可扩展**：易于添加新工具
3. **知识可组合**：知识文件可自由组合
4. **Agent可嵌套**：Agent可作为工具被调用

## 最佳实践

1. **选择合适的记忆级别**
   - 简单任务用NONE
   - 交互式任务用SMART
   - 长期项目用PRO

2. **合理组织知识文件**
   - 按领域分类
   - 保持知识文件精简
   - 使用include机制组合

3. **工具使用原则**
   - 优先使用已有工具
   - 避免重复造轮子
   - 工具粒度要合适

## 相关文档

- [自然语言虚拟机设计文档](../docs/自然语言虚拟机设计文档.md)
- [React作为自然语言CPU理论](../docs/React作为自然语言CPU理论.md)
- [Agent协作模式](../docs/agent_cooperation_patterns.md)

