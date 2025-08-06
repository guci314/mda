# React Is All You Need 🚀

基于 LangGraph 的下一代 React Agent 实现，支持先验知识注入、三级记忆系统和工具化集成。

## 🌟 最新更新

- **迁移到 LangGraph**：使用 `create_react_agent` 替代传统 LangChain 实现
- **多 Agent 协作优化**：
  - 修复了工具名称兼容性问题（自动处理中文名称）
  - 优化了任务依赖处理（正确识别顺序执行需求）
  - 提升了协作效率（减少 70% 执行时间）
- **Agent as Tool 增强**：`GenericAgentTool` 自动使用 agent.name，无需手动指定
- **增强的执行显示**：可以看到 AI 的思考过程、工具调用和结果
- **优化的系统提示词**：更智能的任务执行策略
- **灵活的知识管理**：支持多文件和动态加载
- **Agent 命名支持**：每个 Agent 可以有自己的名称，便于多 Agent 协作调试
- **自定义工具支持**：GenericReactAgent 现在支持自定义工具集
- **SQLite 缓存配置**：支持全局缓存、自定义路径和禁用缓存

## 📋 目录

- [核心特性](#核心特性)
- [架构设计](#架构设计)
- [快速开始](#快速开始)
- [核心文件说明](#核心文件说明)
- [使用示例](#使用示例)
- [高级功能](#高级功能)
- [最佳实践](#最佳实践)

## 🎯 核心特性

### 1. **基于 LangGraph 的 React Agent**
- 使用最新的 LangGraph `create_react_agent` API
- 不依赖特定的 ReAct 提示词格式
- 原生支持工具调用（Function Calling）
- 更高效的执行流程

### 2. **三级记忆系统**
- **NONE**：无状态执行，适合简单任务
- **SMART**：智能摘要缓冲（ConversationSummaryBufferMemory）
  - 自动管理对话历史
  - 超出限制时智能摘要
  - 充分利用大模型上下文窗口
- **PRO**：SQLite 持久化存储，支持跨会话

### 3. **知识管理系统**
- 支持多个知识文件加载
- `@include` 语法支持文件引用
- 动态知识加载能力
- 自动转义和格式化
- `specification`：Agent 作为工具时的能力描述（非行为控制）
- `knowledge_files`：控制 Agent 行为的知识文件

### 4. **工具生态系统**
完整的工具集，包括：
- 文件操作（读写、创建目录）
- 代码搜索（文件搜索、符号查找）
- 代码修改（搜索替换、行编辑、diff 应用）
- 命令执行
- Web 搜索（可选）

### 5. **多种集成方式**
- 独立命令行工具
- LangChain 工具集成
- Jupyter Notebook 支持
- API 服务化
- Agent as Tool 模式

### 6. **增强功能**
- **Agent 命名**：每个 Agent 可设置名称，输出中显示 `[Agent名称]`
- **自定义工具**：支持为 Agent 指定自定义工具集
- **灵活缓存**：支持配置缓存路径或禁用缓存
- **多 Agent 协作**：Agent 可作为工具被其他 Agent 调用
- **Unix 命令模式**：使用 `/知识文件名 参数` 执行知识程序（知识本质是程序）

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────┐
│                用户输入                          │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│            GenericReactAgent                     │
│  ┌─────────────────────────────────────────┐   │
│  │  系统提示词 + 知识文件                   │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │  LangGraph create_react_agent           │   │
│  └─────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────┐   │
│  │  记忆系统 (None/Smart/Pro)              │   │
│  └─────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────┘
                     ▼
┌─────────────────────────────────────────────────┐
│                工具集                            │
│  文件操作 | 代码搜索 | 代码修改 | 命令执行      │
└─────────────────────────────────────────────────┘
```

## 🚀 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基本使用

```python
from react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel

# 创建配置
config = ReactAgentConfig(
    work_dir="output",
    memory_level=MemoryLevel.SMART,  # 使用智能记忆
    knowledge_files=["knowledge/综合知识.md"],  # 可以加载多个文件
    llm_model="deepseek-chat",  # 默认使用 DeepSeek
    llm_temperature=0,
    name="主Agent"  # 设置 Agent 名称
)

# 创建 Agent
agent = GenericReactAgent(config)

# 执行任务 - 现在会显示详细的执行过程，包含 Agent 名称
agent.execute_task("创建一个用户管理系统的 REST API")
```

### 命令行使用

```bash
# 基本使用
python react_agent.py --task "创建一个博客系统"

# 使用不同的 LLM
python react_agent.py --llm-model gpt-4-turbo-preview \
                      --llm-base-url https://api.openai.com/v1 \
                      --llm-api-key-env OPENAI_API_KEY \
                      --task "分析这个项目的架构"

# 启用持久化记忆
python react_agent.py --memory pro --session-id my_project \
                      --task "继续昨天的开发工作"
```

## 📁 核心文件说明

### 1. **react_agent.py** - 核心实现
- `GenericReactAgent`: 主类，基于 LangGraph，支持自定义工具
- `ReactAgentConfig`: 配置管理，包含 name、cache_path 等新字段
  - `specification`: Agent 作为工具时的能力描述（不是系统提示词）
  - `knowledge_files`: 控制 Agent 行为的知识文件列表
- `CustomSummaryBufferMemory`: 智能记忆实现
- 支持多种 LLM（DeepSeek、OpenAI、Moonshot 等）
- SQLite 缓存支持，可配置路径或禁用

### 2. **tools.py** - 工具集合
包含所有可用工具：
- `write_file` / `read_file`: 文件读写
- `search_files` / `find_symbol`: 代码搜索
- `search_replace` / `edit_lines`: 代码修改
- `apply_diff`: 应用补丁
- `execute_command`: 命令执行
- `google_search` / `read_web_page`: Web 搜索（可选）

### 3. **langchain_agent_tool.py** - LangChain 集成
```python
# 方式1：使用 GenericAgentTool（推荐）
agent = GenericReactAgent(config)
tool = GenericAgentTool(agent)  # 自动处理名称和规范

# 方式2：创建专用工具
code_tool = create_code_generation_tool()
file_tool = create_file_processing_tool()

# 方式3：使用 AgentToolWrapper
wrapper = AgentToolWrapper(agent)
result = wrapper.execute("创建文件")
```

### 4. **demo_agent_coordination_fixed.py** - Agent 协作演示
展示主 Agent 如何协调多个子 Agent：
```python
# 主 Agent 使用自定义工具（两个子 Agent）
# 代码生成 Agent + 代码运行 Agent
# 实现了真正的 Agent as Tool 架构
```

## 💡 使用示例

### 示例 1：代码生成
```python
# 配置专门的代码生成 Agent
config = ReactAgentConfig(
    work_dir="output/codegen",
    knowledge_files=["knowledge/编程规范知识.md"],
    specification="专业的代码生成工具"  # 用于 Agent 作为工具时的描述
)
agent = GenericReactAgent(config)
agent.execute_task("创建一个完整的用户认证系统，包括注册、登录、JWT令牌")
```

### 示例 2：项目分析
```python
# 不加载知识文件，让 Agent 自主探索
config = ReactAgentConfig(
    work_dir="output/analysis",
    knowledge_files=[],  # 不使用知识文件
    memory_level=MemoryLevel.SMART
)
agent = GenericReactAgent(config)
agent.execute_task("分析 /path/to/project 的代码结构和架构设计")
```

### 示例 3：动态知识加载（知识热加载）
```python
agent = GenericReactAgent(config)

# 方式1：使用旧版 load_knowledge（会重建agent但保留memory）
if "fastapi" in task.lower():
    agent.load_knowledge("FastAPI 最佳实践：...")

# 方式2：使用新版热加载（支持多文件和更灵活的配置）
# 热加载新的知识文件
agent.hot_reload_knowledge(["knowledge/fastapi.md", "knowledge/async.md"])

# 重新加载当前知识（文件内容更新后）
agent.hot_reload_knowledge()

# 加载字符串知识
agent.hot_reload_knowledge(knowledge_strings=["新的领域知识..."])

agent.execute_task(task)
```

### 示例 4：Agent as Tool - 多 Agent 协作
```python
from langchain_agent_tool import GenericAgentTool

# 创建两个专门的子 Agent
developer = GenericReactAgent(
    ReactAgentConfig(
        work_dir="shared_workspace",
        specification="Python 开发专家"
    ),
    name="developer"  # 英文名称，符合 API 规范
)

tester = GenericReactAgent(
    ReactAgentConfig(
        work_dir="shared_workspace", 
        specification="代码测试专家"
    ),
    name="tester"
)

# 使用 GenericAgentTool 封装
dev_tool = GenericAgentTool(developer)
test_tool = GenericAgentTool(tester)

# 创建主 Agent，传入工具
manager = GenericReactAgent(
    ReactAgentConfig(
        work_dir="shared_workspace",
        name="manager",
        knowledge_files=[
            "knowledge/delegation_best_practices.md",
            "knowledge/task_dependencies.md"  # 处理任务依赖
        ]
    ),
    custom_tools=[dev_tool, test_tool]
)

# 主 Agent 智能协调（自动识别顺序依赖）
manager.execute_task("""
1. 让开发者创建 utils.py（包含 format_date 函数）
2. 开发完成后，让测试员验证函数是否工作
""")
```

## 🔧 高级功能

### 1. 查看详细执行过程
最新版本会显示：
- 🤔 [Agent名称] AI 思考过程
- 🔧 工具调用决策和参数
- 💬 工具返回结果
- 🤖 [Agent名称] AI 最终回答

### 2. 自定义 LLM 配置
支持任何 OpenAI 兼容的 API：
```python
config = ReactAgentConfig(
    work_dir="output",
    llm_model="claude-3-opus",
    llm_base_url="https://api.anthropic.com/v1",
    llm_api_key_env="ANTHROPIC_API_KEY",
    context_window=200000  # 手动指定上下文窗口
)
```

### 3. 缓存配置
```python
# 使用自定义缓存路径
config = ReactAgentConfig(
    work_dir="output",
    cache_path="my_cache.db"
)

# 禁用缓存
config = ReactAgentConfig(
    work_dir="output",
    enable_cache=False
)

# 全局禁用缓存
os.environ['DISABLE_LANGCHAIN_CACHE'] = 'true'
```

### 4. 工具化使用
将 React Agent 作为工具在更大的系统中使用：
```python
from langchain_agent_tool import GenericAgentTool

# 创建自定义配置的 Agent 工具
agent = GenericReactAgent(custom_config)
tool = GenericAgentTool(agent)  # 自动使用 agent.name，并处理命名规范

# 支持中文名称的 Agent
config = ReactAgentConfig(
    work_dir="output"
)
agent = GenericReactAgent(config, name="开发者")  # 中文名称会自动转换为 "developer"
tool = GenericAgentTool(agent)  # tool.name 为 "developer"

# 在 LangChain 工作流中使用
```

### 示例 5：Unix 命令模式 - 知识即程序
```python
# 使用 Unix 命令格式执行知识程序
agent = GenericReactAgent(config)

# 格式: /知识文件名 参数
# 知识文件作为"程序"，参数作为输入
result = agent.execute_task("/python_programming_knowledge 解释装饰器的工作原理")

# 无参数调用
result = agent.execute_task("/code_review_ethics")

# 系统会：
# 1. 查找知识文件（优先级：长期数据目录 > knowledge目录 > 配置的知识文件）
# 2. 将知识文件内容作为"程序"
# 3. 将参数作为输入传递给程序
# 4. 执行并返回结果
```

## 📚 知识文件

### 知识文件结构
```markdown
# 领域知识标题

## 概念说明
...

## 最佳实践
...

## 代码示例
...

@include [其他知识文件.md]
```

### 预置知识文件
- `综合知识.md`: 主知识文件，使用 include 引入其他文件
- `编程规范知识.md`: 通用编程规范
- `fastapi_generation_knowledge.md`: FastAPI 开发知识
- `pim_to_psm_knowledge.md`: MDA 转换知识
- `delegation_best_practices.md`: 多 Agent 委托最佳实践
- `task_dependencies.md`: 任务依赖处理指南

## 🎯 最佳实践

### 1. 选择合适的记忆级别
- **简单任务** → `MemoryLevel.NONE`
- **多轮对话** → `MemoryLevel.SMART`
- **长期项目** → `MemoryLevel.PRO`

### 2. 知识文件管理
- **小项目**：直接加载所有知识
- **大项目**：动态加载相关知识
- **避免过大**：单个知识文件建议 < 1000 行

### 3. 任务描述技巧
- 明确具体的需求
- 分步骤描述复杂任务
- 提供必要的上下文信息
- 使用"完成后"等词汇明确任务依赖

### 4. 多 Agent 协作
- 使用英文命名 Agent（中文会自动转换）
- 利用 `GenericAgentTool` 简化封装
- 主 Agent 加载任务依赖知识文件
- 明确任务的顺序关系

### 5. 性能优化
- 使用缓存（自动启用）
- 合理设置 `max_token_limit`
- 选择合适的 LLM 模型
- 避免不必要的验证步骤

## 🔍 故障排查

### 递归限制错误
如果遇到 `GraphRecursionError`：
1. 简化任务描述
2. 减少知识文件大小
3. 或修改 `recursion_limit`（已默认设为 100）

### Token 限制
如果超出 token 限制：
1. 使用 `MemoryLevel.SMART` 自动管理
2. 减少知识文件
3. 选择更大上下文的模型

## 📊 性能指标

- **简单任务**：5-10 秒
- **中等复杂度**：30-60 秒  
- **复杂项目**：2-5 分钟
- **多 Agent 协作**：取决于子任务复杂度

影响因素：
- LLM 响应速度（可通过缓存优化）
- 任务复杂度
- 工具调用次数
- 知识文件大小
- Agent 协作层级

## 🤝 贡献指南

欢迎贡献代码、知识文件或使用案例！

## 📄 许可证

MIT License

---

**快速体验**：
- 基础功能：`python react_agent.py --task "创建一个 TODO 应用"`
- Agent 协作：`python demo_efficient_coordination.py`
- 多 Agent 完整演示：`python demo_agent_coordination_langchain.py`
- 工具集成：`python tool_specification_example.py`