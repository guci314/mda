# Agent CLI 推理策略说明

## 概述

Agent CLI 实现了三种推理策略：

1. **符号主义推理（Symbolic Reasoning）** - 基于规则的传统方法
2. **连接主义推理（Connectionist Reasoning）** - 基于LLM的智能方法
3. **混合策略（Hybrid Strategy）** - 结合两者优势的实用方法

## 推理策略对比

### 符号主义推理
- **原理**：使用预定义的规则和模式匹配
- **优点**：快速、可预测、无需API调用
- **缺点**：灵活性差、需要不断更新规则
- **适用场景**：简单、重复性的任务

### 连接主义推理
- **原理**：使用LLM理解任务语义并做出决策
- **优点**：灵活、智能、自适应
- **缺点**：依赖API、成本较高、速度较慢
- **适用场景**：复杂、创造性的任务

### 混合策略（默认）
- **原理**：优先使用LLM，失败时回退到规则
- **优点**：平衡了灵活性和可靠性
- **缺点**：实现复杂度较高
- **适用场景**：生产环境的最佳选择

## 核心实现

### 1. 任务规划（Planning）

```python
def plan(self, task_description: str) -> Task:
    """使用LLM智能规划任务步骤"""
    # LLM分析任务并生成执行步骤
    # 支持JSON格式和文本格式的响应
    # 失败时使用默认规则
```

### 2. 动作决策（Action Decision）

```python
def _decide_action(self, thought: str, step: str) -> Action:
    """基于LLM推理决定下一个动作"""
    # LLM根据当前思考和步骤决定动作类型
    # 返回结构化的动作对象
    # 失败时调用_decide_action_symbolic
```

### 3. 生成策略（Generation Strategy）

```python
def _create_generate_action(self, step: str) -> Action:
    """使用LLM决定生成策略"""
    # LLM分析需要生成什么内容
    # 提供详细的提示词和约束
    # 优化生成质量
```

## 使用示例

### 测试不同推理方法

```bash
# 运行推理策略对比演示
python agent_cli/demo_reasoning.py

# 测试连接主义推理
python agent_cli/test_connectionist.py
```

### 在代码中使用

```python
from agent_cli.core import AgentCLI, LLMConfig

# 创建使用混合策略的CLI（默认）
config = LLMConfig.from_env("deepseek")
cli = AgentCLI(llm_config=config)

# 执行任务 - 自动使用智能推理
success, message = cli.execute_task("创建用户认证系统")
```

## 配置选项

### 环境变量

```bash
# .env 文件配置
LLM_PROVIDER=deepseek  # 或 moonshot
DEEPSEEK_API_KEY=your-key
MOONSHOT_API_KEY=your-key

# 可选：调整LLM参数
DEEPSEEK_MODEL=deepseek-chat
TEMPERATURE=0.3  # 控制创造性（0.0-1.0）
```

### 代码配置

```python
# 自定义LLM配置
config = LLMConfig(
    api_key="your-key",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    temperature=0.3,
    max_tokens=1000  # 限制响应长度
)
```

## 最佳实践

### 1. 任务描述
- 清晰、具体的任务描述能获得更好的规划
- 包含必要的上下文信息
- 明确期望的输出

### 2. 错误处理
- 混合策略自动处理LLM失败
- 监控日志了解决策过程
- 设置合理的超时和重试

### 3. 成本优化
- 使用`max_tokens`限制响应长度
- 缓存常见任务的规划结果
- 对简单任务考虑使用符号规则

## 架构优势

### Task/Step/Action 三层架构

1. **Task层**：管理整体任务生命周期
   - 任务描述和目标
   - 全局上下文
   - 进度跟踪

2. **Step层**：组织逻辑执行步骤
   - 步骤状态管理
   - 迭代控制
   - 失败处理

3. **Action层**：执行具体操作
   - 动作类型和参数
   - 执行结果
   - 错误信息

## 扩展和自定义

### 添加新的动作类型

```python
class CustomAction(Enum):
    API_CALL = "api_call"
    DATABASE_QUERY = "database_query"

# 在_decide_action中添加映射
action_type_map["API_CALL"] = CustomAction.API_CALL
```

### 自定义推理策略

```python
class MyAgentCLI(AgentCLI):
    def _decide_action(self, thought: str, step: str) -> Action:
        # 实现自定义推理逻辑
        pass
```

## 性能考虑

- LLM调用延迟：每次约1-3秒
- 建议批量处理相关任务
- 使用异步调用提高并发
- 监控API配额和费用

## 未来改进

1. **推理优化**
   - 实现推理结果缓存
   - 支持批量推理
   - 优化提示词工程

2. **更多LLM支持**
   - 添加本地模型支持
   - 支持多模型ensemble
   - 动态模型选择

3. **高级功能**
   - 支持多轮对话推理
   - 实现推理链（Chain of Thought）
   - 添加推理可视化