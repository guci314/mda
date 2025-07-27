# Agent CLI Framework - 支持多动作执行的智能体框架

## 概述

Agent CLI Framework 是一个通用的智能体开发框架，支持动态规划和多动作执行。它采用两层决策模型（战略层和战术层），让智能体能够在执行过程中动态调整策略。

## 核心特性

### 1. 动态执行架构
- **两层决策模型**：步骤层（战略）和动作层（战术）
- **一个步骤多个动作**：智能体可以在一个步骤中执行多个相关动作
- **动态计划调整**：根据执行结果动态调整后续步骤
- **智能决策**：基于上下文和历史结果做出最优决策

### 2. 通用认知框架
- **感知-分析-决策-执行**循环
- **上下文感知**：维护执行上下文和状态
- **模式识别**：识别任务模式并应用相应策略
- **自适应学习**：从执行历史中学习和优化

### 3. 完整测试框架
- **单元测试**：测试单个智能体功能
- **集成测试**：测试智能体协作
- **性能测试**：测试响应时间和吞吐量
- **多格式报告**：JSON、HTML、Markdown

## 快速开始

### 安装

```bash
cd pim-compiler
pip install -r requirements.txt
```

### 创建智能体

```python
from agent_cli.core.agent_base import Agent, AgentMetadata, AgentCapability

class MyAgent(Agent):
    def __init__(self):
        super().__init__(
            metadata=AgentMetadata(
                name="my_agent",
                description="我的智能体",
                version="1.0.0",
                author="作者",
                capabilities=[AgentCapability.CODE_GENERATION]
            )
        )
    
    def plan(self, task: Dict[str, Any]) -> List[Step]:
        """制定执行计划"""
        return [
            Step(
                name="step1",
                description="第一步",
                expected_output="预期输出"
            )
        ]
    
    def execute_action(self, action: str, params: Dict[str, Any]) -> ActionResult:
        """执行具体动作"""
        if action == "generate_code":
            # 实现代码生成逻辑
            code = self._generate_code(params)
            return ActionResult(
                success=True,
                data={"code": code},
                message="代码生成成功"
            )
```

### 运行智能体

```bash
# 使用命令行
./agent-cli run my_agent --input '{"task": "generate", "language": "python"}'

# 使用 Python API
from agent_cli.core.agent_executor import AgentExecutor
from agent_cli.core.agent_registry import AgentRegistry

registry = AgentRegistry()
registry.register(MyAgent())

executor = AgentExecutor(registry)
result = executor.execute("my_agent", {"task": "generate"})
```

## 测试框架

### 创建测试套件

```json
{
  "name": "my_agent_test_suite",
  "description": "智能体测试套件",
  "agent_name": "my_agent",
  "test_cases": [
    {
      "name": "test_basic_generation",
      "description": "测试基本代码生成",
      "input": {
        "task": "generate",
        "language": "python",
        "description": "生成 Hello World"
      },
      "expected_output": {
        "status": "success"
      },
      "expected_actions": [
        "analyze_requirements",
        "generate_code"
      ],
      "timeout": 30
    }
  ]
}
```

### 运行测试

```bash
# 生成测试模板
./agent-cli test generate my_agent

# 运行测试
./agent-cli test run my_agent_test.json

# 查看报告
./agent-cli test show test_report_my_agent_*.json

# 统计分析
./agent-cli test stats --agent my_agent
```

## 架构设计

### 核心组件

```
agent_cli/
├── core/                    # 核心框架
│   ├── agent_base.py       # 智能体基类
│   ├── agent_executor.py   # 执行器
│   ├── agent_registry.py   # 注册中心
│   ├── agent_runtime.py    # 运行时环境
│   └── test_runner.py      # 测试运行器
├── agents/                  # 内置智能体
│   ├── code_generator.py   # 代码生成
│   ├── web_searcher.py     # 网络搜索
│   └── data_analyzer.py    # 数据分析
├── commands/               # CLI 命令
│   ├── agent_command.py    # agent 命令
│   ├── run_command.py      # run 命令
│   └── test_command.py     # test 命令
└── utils/                  # 工具函数
    └── report_viewer.py    # 报告查看器
```

### 执行流程

```
1. 任务输入
   ↓
2. 智能体规划（生成步骤列表）
   ↓
3. 步骤执行循环
   ├─→ 思考当前进展
   ├─→ 决策下一动作
   ├─→ 执行动作
   ├─→ 更新上下文
   └─→ 判断步骤完成？
       ├─ 否：继续循环
       └─ 是：进入下一步骤
   ↓
4. 任务完成
```

## 高级特性

### 1. 动态计划调整

智能体可以在执行过程中调整计划：

```python
def _decide_step_completion(self, step: Step, thought: str) -> StepDecision:
    """决定步骤是否完成，以及是否需要调整后续步骤"""
    
    # 基于当前进展决定
    if self._found_unexpected_complexity():
        return StepDecision(
            is_complete=False,
            suggested_next_steps=[
                Step("handle_complexity", "处理复杂情况")
            ]
        )
```

### 2. 多动作协同

一个步骤可以包含多个协同动作：

```python
# 步骤：生成完整的 API 服务
actions = [
    ("read_file", {"path": "requirements.md"}),      # 读取需求
    ("analyze_requirements", {"content": content}),   # 分析需求
    ("generate_code", {"type": "models"}),           # 生成模型
    ("generate_code", {"type": "api"}),              # 生成 API
    ("generate_code", {"type": "tests"}),            # 生成测试
    ("write_files", {"files": generated_files})      # 写入文件
]
```

### 3. 上下文管理

智能体维护执行上下文：

```python
context = {
    "task_id": "123",
    "step_history": [...],
    "action_results": {...},
    "learned_patterns": {...},
    "error_recovery": {...}
}
```

### 4. 错误恢复

内置错误恢复机制：

```python
try:
    result = self.execute_action(action, params)
except ActionError as e:
    # 自动尝试恢复策略
    recovery_action = self._determine_recovery_action(e)
    result = self.execute_action(recovery_action.action, recovery_action.params)
```

## 内置智能体

### 1. 代码生成智能体 (code_generator)
- 支持多种编程语言
- 自动语法验证
- 代码优化建议

### 2. 网络搜索智能体 (web_searcher)
- 智能查询构建
- 结果相关性排序
- 信息提取和总结

### 3. 数据分析智能体 (data_analyzer)
- 数据加载和清洗
- 统计分析
- 可视化生成

## 最佳实践

### 1. 智能体设计原则
- **单一职责**：每个智能体专注于特定领域
- **可组合性**：智能体之间可以协作
- **可测试性**：提供清晰的输入输出接口
- **错误处理**：优雅处理各种异常情况

### 2. 测试驱动开发
1. 先编写测试用例
2. 实现智能体功能
3. 运行测试验证
4. 迭代优化

### 3. 性能优化
- 使用动作缓存避免重复计算
- 并行执行独立动作
- 优化 LLM 调用次数
- 使用流式处理大数据

## 常见问题

### Q: 如何调试智能体执行过程？
A: 使用 `--verbose` 参数查看详细日志：
```bash
./agent-cli run my_agent --input '{}' --verbose
```

### Q: 如何限制智能体的执行时间？
A: 在测试用例中设置 `timeout` 参数，或在代码中使用：
```python
executor = AgentExecutor(registry, timeout=60)  # 60秒超时
```

### Q: 如何扩展智能体能力？
A: 继承 `AgentCapability` 枚举并在智能体中实现相应功能：
```python
class AgentCapability(Enum):
    CUSTOM_CAPABILITY = "custom_capability"
```

## 贡献指南

欢迎贡献新的智能体、改进框架功能或修复问题！

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

## 许可证

MIT License

## 相关文档

- [测试指南](docs/testing_guide.md)
- [架构设计](动态执行架构设计.md)
- [API 文档](docs/api_reference.md)
- [示例代码](examples/)