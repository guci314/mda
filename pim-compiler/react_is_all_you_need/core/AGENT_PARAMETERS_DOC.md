# React Agent 初始化参数完整说明

## ReactAgentConfig 配置类参数

### 基础配置

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `work_dir` | str | 必需 | 工作目录路径，Agent的工作空间，必须预先存在 |
| `additional_config` | dict | None | 额外的配置字典，用于扩展配置 |

### 记忆系统配置

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `memory_level` | MemoryLevel | MemoryLevel.SMART | 记忆级别：<br>- NONE: 无记忆，每次执行独立<br>- SMART: 智能缓冲，会话级记忆<br>- PRO: 持久存储，跨会话记忆 |
| `session_id` | str | f"session_{timestamp}" | 会话ID，用于区分不同对话 |
| `max_token_limit` | int | 30000 | 最大token限制（SMART模式），超出后自动压缩 |
| `db_path` | str | "memory.db" | SQLite数据库路径（PRO模式） |
| `show_memory_updates` | bool | True | 是否显示记忆更新通知（错误纠正始终显示） |

### 知识系统配置

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `knowledge_files` | List[str] | ["knowledge/core/default_knowledge.md"] | 知识文件路径列表，支持include机制 |
| `knowledge_file` | str | None | 单个知识文件路径（已废弃，建议使用knowledge_files） |
| `knowledge_strings` | List[str] | [] | 知识字符串列表，直接提供知识内容而非文件 |
| `interface` | str | None | Agent接口声明，描述Agent的能力和用途 |
| `system_prompt_file` | str | "knowledge/core/system_prompt.md" | 系统提示词文件路径 |
| `knowledge_extraction_limit` | int | 自动推断 | 知识提取文件大小限制（bytes），根据模型自动设置 |

### LLM配置

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `llm_model` | str | "deepseek-chat" | LLM模型名称，支持任何OpenAI兼容模型 |
| `llm_base_url` | str | "https://api.deepseek.com/v1" | LLM API基础URL |
| `llm_api_key_env` | str | "DEEPSEEK_API_KEY" | API密钥的环境变量名 |
| `llm_temperature` | float | 0 | 温度参数，控制输出随机性（0=确定性） |
| `context_window` | int | 自动推断 | 模型上下文窗口大小（tokens），根据模型自动设置 |
| `http_client` | httpx.Client | None | 自定义HTTP客户端（用于代理等） |
| `llm_max_tokens` | int | 16384 | LLM输出的最大token数 |

### 缓存配置

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `cache_path` | str | None | 自定义缓存路径，None使用全局默认缓存 |
| `enable_cache` | bool | True | 是否启用LLM缓存，提高重复查询速度 |

### Agent内部存储配置

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `agent_home` | str | ".agents" | Agent内部存储目录，独立于工作目录 |
| `enable_world_overview` | bool | True | （已废弃）是否启用世界概览功能 |
| `enable_perspective` | bool | False | 是否启用视角功能 |

### 项目探索配置

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `enable_project_exploration` | bool | False | 是否启用项目探索功能,如果启用会把代码库投影到uml先验框架 |
| `exploration_interval` | int | 86400 | 项目探索间隔时间（秒），默认24小时 |
| `exploration_prompt` | str | None | 项目探索提示词 |
| `exploration_prompt_file` | str | None | 项目探索提示词文件路径 |
| `auto_reload_on_exploration` | bool | True | 项目探索完成后是否自动重载 |

## GenericReactAgent 初始化参数

| 参数名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `config` | ReactAgentConfig | 必需 | Agent配置对象，包含所有配置参数 |
| `name` | str | f"Agent-{llm_model}" | Agent名称，用于标识和创建独立存储目录 |
| `custom_tools` | List[Any] | None | 自定义工具列表，扩展Agent能力 |


## 使用示例

### 基础配置示例
```python
from core.react_agent import GenericReactAgent, ReactAgentConfig, MemoryLevel

# 最简配置
config = ReactAgentConfig(
    work_dir="./my_project",
    llm_model="google/gemini-2.5-pro",
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY"
)
agent = GenericReactAgent(config)
```

### 使用OpenRouter示例
```python
config = ReactAgentConfig(
    work_dir="./my_project",
    llm_model="google/gemini-2.5-pro",
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY",
    memory_level=MemoryLevel.SMART
)

agent = GenericReactAgent(config, name="gemini_agent")
```

### 完整配置示例
```python
config = ReactAgentConfig(
    # 基础配置
    work_dir="./my_project",
    additional_config={"custom_key": "custom_value"},
    
    # 记忆系统
    memory_level=MemoryLevel.PRO,
    session_id="project_session_001",
    max_token_limit=50000,
    db_path="./data/agent_memory.db",
    show_memory_updates=True,
    
    # 知识系统
    knowledge_files=[
        "knowledge/python.md",
        "knowledge/best_practices.md"
    ],
    knowledge_strings=["Always follow PEP8"],
    interface="Python Development Expert",
    system_prompt_file="prompts/python_expert.md",
    knowledge_extraction_limit=200*1024,  # 200KB
    
    # LLM配置
    llm_model="google/gemini-2.5-pro",
    llm_base_url="https://openrouter.ai/api/v1",
    llm_api_key_env="OPENROUTER_API_KEY",
    llm_temperature=0.1,
    context_window=128000,
    llm_max_tokens=8192,
    
    # 缓存配置
    cache_path="./cache/llm_cache.db",
    enable_cache=True,
    
    # Agent存储
    agent_home="~/.my_agents",
    enable_perspective=True,
    
    # 项目探索
    enable_project_exploration=True,
    exploration_interval=3600,  # 每小时探索一次
    exploration_prompt="分析项目结构和依赖", # 这个参数有值，按照这个提示词分析代码库，如果没有值，按照uml先验框架分析代码库
    auto_reload_on_exploration=True
)

# 创建Agent并添加自定义工具
from langchain_core.tools import tool

@tool
def custom_calculator(expression: str) -> str:
    """计算数学表达式"""
    return str(eval(expression))

agent = GenericReactAgent(
    config,
    name="advanced_agent",
    custom_tools=[custom_calculator]
)

# 执行任务
result = agent.execute_task("创建一个REST API服务")
```

## 配置最佳实践

### 1. 记忆级别选择
- **NONE**: 适合简单、独立的任务，无需上下文
- **SMART**: 适合交互式开发、调试等需要短期记忆的场景
- **PRO**: 适合长期项目、需要跨会话记忆的场景

### 2. Token限制设置
- 默认值通常足够，会根据模型自动调整
- 如果处理大型文件或长对话，可手动增加`max_token_limit`
- 建议设置为模型上下文窗口的60-80%

### 3. 知识文件组织
- 将领域知识分类到不同文件
- 使用include机制组合知识
- 避免单个知识文件过大（建议<100KB）

### 4. LLM选择
- **Gemini 2.5 Pro**: 速度快，效果好，通过OpenRouter访问
- **DeepSeek**: 性价比高，适合一般任务
- **GPT-4**: 能力强，成本较高
- **Claude**: 上下文窗口大，适合长文本

### 5. 缓存策略
- 开发阶段建议启用缓存，提高迭代速度
- 生产环境可根据需要禁用或使用独立缓存
- 定期清理缓存文件避免占用过多空间

## 注意事项

1. **工作目录必须存在**：Agent不会创建工作目录，只在其中操作
2. **API密钥安全**：始终使用环境变量，不要硬编码
3. **OpenRouter配置**：需要在OpenRouter平台注册并获取API密钥
4. **内存管理**：PRO模式会持久化存储，注意磁盘空间
5. **并发安全**：同一Agent实例不建议并发执行任务