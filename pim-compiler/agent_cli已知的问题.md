# Agent CLI 已知的问题

## 1. 领域污染问题

### 问题描述
AgentCLI 应该是一个领域无关的通用认知框架，但目前存在严重的领域污染问题。

### 具体表现

#### 1.1 _decide_action 方法中的硬编码提示词
```python
# core.py 中的问题代码
def _decide_action(self, thought: str, step: str) -> Action:
    prompt_content = """根据当前步骤选择合适的工具。
    ...
    2. 对于 write_file 工具，必须从步骤描述中提取文件内容作为 content 参数
    ...
    决定动作（大多数情况使用GENERATE）：
    """
```

这些提示词明显偏向代码生成领域：
- 强调 `write_file` 工具的使用
- 提到"大多数情况使用GENERATE"（虽然 GENERATE 工具已被移除）
- 缺乏对其他领域工具的通用指导

#### 1.2 ActionType 枚举的领域偏向
```python
class ActionType(Enum):
    THINK = "think"
    PLAN = "plan"
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    LIST_FILES = "list_files"
    ANALYZE = "analyze"
    GENERATE = "generate"
    VALIDATE = "validate"
    EXECUTE = "execute"
    COMPLETE = "complete"
```

这些动作类型明显偏向文件操作和代码生成，不适合其他领域（如数据分析、系统管理、自然语言处理等）。

### 影响
1. **限制了框架的通用性**：其他领域使用 AgentCLI 时会受到代码生成领域的干扰
2. **降低了决策准确性**：LLM 可能被误导选择不适合当前领域的工具
3. **增加了维护成本**：每个领域都需要修改核心代码

## 2. 工具管理混乱

### 问题描述
工具定义和实现散落在多个模块中，缺乏统一的管理机制。

### 具体表现

#### 2.1 工具定义位置不当
- `FileReader`、`FileWriter` 等工具应该作为领域特定工具，而不是核心模块的一部分
- `tools.py` 模块混合了工具实现和工具注册

#### 2.2 缺乏工具注册表机制
当前的工具管理方式：
```python
# tools.py
AVAILABLE_TOOLS = {
    "read_file": read_file_tool,
    "write_file": write_file_tool,
    # ...
}
```

这种硬编码方式无法支持动态工具注册和领域特定工具集。

## 3. 解决方案

### 3.1 构建领域无关的认知框架

#### 核心原则
1. **分离核心框架与领域工具**
2. **使用插件式架构**
3. **通过配置而非代码定义领域**

#### 实现方案

##### 1. 抽象的 Action 系统
```python
# core.py - 领域无关的动作类型
class ActionType(Enum):
    THINK = "think"          # 通用思考
    PLAN = "plan"           # 通用规划
    USE_TOOL = "use_tool"   # 使用工具（具体工具由工具注册表决定）
    COMPLETE = "complete"   # 完成任务
```

##### 2. 工具注册表机制
```python
# tool_registry.py
class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self._domains = {}
    
    def register_tool(self, tool: Tool, domain: str = "general"):
        """注册工具到指定领域"""
        self._tools[tool.name] = tool
        if domain not in self._domains:
            self._domains[domain] = []
        self._domains[domain].append(tool.name)
    
    def get_tools_for_domain(self, domain: str) -> List[Tool]:
        """获取特定领域的工具集"""
        tool_names = self._domains.get(domain, [])
        return [self._tools[name] for name in tool_names]
    
    def get_tool_prompt(self, domain: str) -> str:
        """生成领域特定的工具选择提示词"""
        tools = self.get_tools_for_domain(domain)
        # 动态生成工具描述
        return self._generate_tool_descriptions(tools)
```

##### 3. 领域特定工具包
```python
# domains/code_generation/tools.py
class CodeGenerationTools:
    @staticmethod
    def register(registry: ToolRegistry):
        registry.register_tool(
            Tool(
                name="read_file",
                description="读取源代码文件",
                domain="code_generation"
            )
        )
        registry.register_tool(
            Tool(
                name="write_file",
                description="写入代码文件",
                domain="code_generation"
            )
        )

# domains/data_analysis/tools.py
class DataAnalysisTools:
    @staticmethod
    def register(registry: ToolRegistry):
        registry.register_tool(
            Tool(
                name="load_dataset",
                description="加载数据集",
                domain="data_analysis"
            )
        )
        registry.register_tool(
            Tool(
                name="plot_chart",
                description="绘制图表",
                domain="data_analysis"
            )
        )
```

##### 4. 动态决策提示词
```python
# core.py
def _decide_action(self, thought: str, step: str) -> Action:
    # 根据当前领域获取工具提示
    domain = self.config.domain or "general"
    tool_prompt = self.tool_registry.get_tool_prompt(domain)
    
    prompt_content = f"""根据当前步骤选择合适的工具。
    
    当前领域：{domain}
    
    可用工具：
    {tool_prompt}
    
    请根据步骤描述选择最合适的工具。
    """
```

### 3.2 项目结构重组

建议的项目结构：
```
agent_cli/
├── core/                    # 领域无关的核心框架
│   ├── __init__.py
│   ├── agent.py            # AgentCLI 主类
│   ├── models.py           # Task, Step, Action 等核心模型
│   ├── registry.py         # 工具注册表
│   └── executors.py        # 通用执行器接口
├── domains/                 # 领域特定实现
│   ├── code_generation/
│   │   ├── tools.py        # 代码生成工具
│   │   └── prompts.py      # 代码生成提示词
│   ├── data_analysis/
│   │   ├── tools.py        # 数据分析工具
│   │   └── prompts.py      # 数据分析提示词
│   └── system_admin/
│       ├── tools.py        # 系统管理工具
│       └── prompts.py      # 系统管理提示词
└── cli.py                   # 命令行接口
```

### 3.3 使用示例

```python
# 使用代码生成领域
from agent_cli.core import AgentCLI, AgentConfig
from agent_cli.domains.code_generation import CodeGenerationTools

config = AgentConfig(domain="code_generation")
agent = AgentCLI(config)
agent.registry.register_domain_tools(CodeGenerationTools)

# 使用数据分析领域
from agent_cli.domains.data_analysis import DataAnalysisTools

config = AgentConfig(domain="data_analysis")
agent = AgentCLI(config)
agent.registry.register_domain_tools(DataAnalysisTools)
```

## 4. 实施建议

### 阶段一：分离核心与领域（1-2天）
1. 创建 `core/` 目录，移动领域无关代码
2. 创建 `domains/` 目录，移动领域特定代码
3. 实现基础的工具注册表

### 阶段二：实现插件架构（2-3天）
1. 设计工具插件接口
2. 实现动态工具加载
3. 重构决策提示词生成

### 阶段三：迁移现有功能（1-2天）
1. 将现有工具迁移到 `domains/code_generation/`
2. 测试确保功能不受影响
3. 编写迁移文档

## 5. 预期收益

1. **提高通用性**：AgentCLI 可以轻松应用于任何领域
2. **降低耦合度**：核心框架与领域逻辑完全分离
3. **易于扩展**：新领域只需添加工具包，无需修改核心代码
4. **提升决策质量**：领域特定的提示词能提供更准确的指导
5. **便于维护**：清晰的模块划分降低维护成本

## 6. 兼容性考虑

为确保向后兼容，可以：
1. 保留现有的 API 接口
2. 提供迁移工具帮助用户升级
3. 在过渡期同时支持新旧两种方式

## 7. 总结

当前 AgentCLI 的领域污染问题严重影响了其作为通用认知框架的定位。通过构建工具注册表和插件架构，可以彻底解决这一问题，使 AgentCLI 成为真正领域无关的智能代理框架。这不仅能提高框架的通用性和可维护性，还能为未来的扩展奠定坚实基础。