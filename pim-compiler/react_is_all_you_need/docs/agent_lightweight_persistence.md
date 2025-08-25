# Agent轻量级持久化设计

## 概述

轻量级Agent持久化采用**只持久化类型层**的极简设计，使用单个Markdown文件完整定义一个Agent。这种设计追求简单、可读、易于版本控制，适合快速原型开发和知识驱动的Agent系统。

## 设计理念

### 核心原则

1. **单文件定义**：一个`.agent.md`文件完整描述一个Agent
2. **纯文本格式**：Markdown格式，人类可读可写
3. **无状态设计**：不持久化实例状态，每次运行都是全新开始
4. **知识驱动**：Agent的能力完全由知识文件定义

### 与重量级方案对比

| 特性 | Docker式重量级 | Markdown轻量级 |
|------|---------------|----------------|
| 持久化范围 | 类型层+实例层 | 仅类型层 |
| 文件格式 | JSON/二进制 | Markdown |
| 状态管理 | 支持checkpoint | 无状态 |
| 复杂度 | 高 | 低 |
| 适用场景 | 生产环境 | 原型/开发 |

## Agent定义格式

### 完整示例：`coordinator.agent.md`

```markdown
# Coordinator Agent

## 元信息
- **ID**: coordinator_agent
- **版本**: 1.0.0
- **作者**: system
- **创建时间**: 2024-01-15
- **标签**: #coordinator #workflow #zero-knowledge

## 接口定义

我是一个零知识协调Agent，能够协调复杂的工作流而无需领域知识。

### 输入
- `task_description`: 任务描述（自然语言）
- `success_criteria`: 成功判定条件

### 输出
- `execution_result`: 执行结果
- `status_report`: 状态报告

### 使用示例
```
输入: "从PIM文件生成FastAPI应用，确保测试100%通过"
输出: "任务完成，生成了FastAPI应用，所有测试通过"
```

## 依赖工具

### 必需工具
- `psm_generation_agent`: PIM转PSM工具
- `code_generation_agent`: 代码生成工具

### 可选工具
- `debug_agent`: 调试修复工具
- `run_app_agent`: 应用运行工具

## 知识库

### 核心知识
- [workflow/coordination_patterns.md](workflow/coordination_patterns.md)
- [workflow/error_recovery.md](workflow/error_recovery.md)

### 参考知识
- [patterns/zero_knowledge.md](patterns/zero_knowledge.md)

## 配置

```yaml
memory:
  level: SMART
  
learning:
  enabled: true
  
exploration:
  project: false
  
llm:
  models:
    - gemini-2.5-pro
    - gpt-4
  temperature: 0
  
execution:
  timeout: 3600
  max_retries: 3
```

## 行为规范

### 工作流程
1. 解析任务描述
2. 识别所需工具
3. 制定执行计划
4. 调用专业Agent
5. 验证结果
6. 生成报告

### 约束条件
- ❌ 不修改输入文件
- ❌ 不删除用户数据
- ✅ 必须验证成功条件
- ✅ 失败时提供明确原因

### 错误处理
- 工具调用失败：重试3次
- 验证失败：调用debug_agent
- 超时：保存进度并报告

## 扩展与组合

### 继承自
- `base_agent.md`

### 可组合
- `monitor_agent.md`: 添加监控能力
- `parallel_agent.md`: 添加并行执行能力

## 测试用例

### 基本测试
```
任务: 生成简单的CRUD应用
期望: 成功生成并通过测试
```

### 错误恢复测试
```
任务: 生成有错误的代码并修复
期望: 自动调用debug_agent修复
```

## 版本历史

### v1.0.0 (2024-01-15)
- 初始版本
- 支持基本的MDA工作流

### v0.9.0 (2024-01-10)
- Beta版本
- 添加错误处理机制
```

## 最简化格式

### 极简版：`simple.agent.md`

```markdown
# Simple Agent

我是一个简单的Agent。

## 工具
- read_file
- write_file

## 知识
- 如何读写文件
- 如何处理文本

## 配置
- llm: gpt-3.5-turbo
- temperature: 0
```

## 使用方式

### 1. 创建Agent

创建一个`.agent.md`文件：

```bash
# 创建Agent定义
cat > my_agent.agent.md << 'EOF'
# My Agent

## 接口
我能帮你处理数据。

## 工具
- data_processor
- validator

## 知识
- data_processing.md
EOF
```

### 2. 加载Agent

```python
def load_agent(agent_file: str) -> dict:
    """从Markdown文件加载Agent定义"""
    
    with open(agent_file, 'r') as f:
        content = f.read()
    
    # 简单解析（实际可用markdown parser）
    agent_def = {
        'name': extract_title(content),
        'interface': extract_section(content, '接口'),
        'tools': extract_list(content, '工具'),
        'knowledge': extract_list(content, '知识'),
        'config': extract_yaml(content, '配置')
    }
    
    return agent_def

# 使用
agent_def = load_agent('coordinator.agent.md')
agent = create_agent_from_definition(agent_def)
```

### 3. 实例化运行

```python
# 每次运行都是全新实例
agent = ReactAgent.from_markdown('coordinator.agent.md')

# 执行任务
result = agent.execute("生成博客应用")

# 运行完即结束，不保存状态
```

## 文件组织

### 单Agent项目
```
my_agent/
├── agent.md           # Agent定义
├── knowledge/         # 知识文件
│   ├── core.md
│   └── patterns.md
└── README.md         # 使用说明
```

### 多Agent项目
```
agents/
├── coordinator.agent.md
├── psm_generator.agent.md
├── code_generator.agent.md
├── debug.agent.md
└── knowledge/           # 共享知识库
    ├── workflow/
    └── patterns/
```

## 版本控制

### Git友好

```bash
# 直接用Git管理
git add coordinator.agent.md
git commit -m "Update coordinator interface"

# 查看变更历史
git log -p coordinator.agent.md

# 比较版本
git diff v1.0.0 v2.0.0 coordinator.agent.md
```

### 版本标记

在文件内使用版本标记：

```markdown
<!-- version: 1.0.0 -->
<!-- parent: base_agent.md@0.9.0 -->
```

## 工具集成

### VSCode支持

创建`.vscode/agent.code-snippets`:

```json
{
  "Agent Definition": {
    "prefix": "agent",
    "body": [
      "# ${1:Agent Name}",
      "",
      "## 接口定义",
      "${2:Agent描述}",
      "",
      "## 工具",
      "- ${3:tool1}",
      "",
      "## 知识",
      "- ${4:knowledge1.md}",
      "",
      "## 配置",
      "```yaml",
      "llm: ${5:gpt-4}",
      "temperature: ${6:0}",
      "```"
    ]
  }
}
```

### 命令行工具

```bash
#!/bin/bash
# agent-cli - 轻量级Agent管理工具

case "$1" in
  new)
    cat > "$2.agent.md" << EOF
# $2 Agent

## 接口定义
TODO: 描述Agent能力

## 工具
- read_file
- write_file

## 知识
- knowledge/base.md

## 配置
\`\`\`yaml
llm: gpt-4
temperature: 0
\`\`\`
EOF
    echo "Created $2.agent.md"
    ;;
    
  run)
    python -c "
from core.react_agent import ReactAgent
agent = ReactAgent.from_markdown('$2')
result = agent.execute('$3')
print(result)
    "
    ;;
    
  validate)
    # 验证Markdown格式
    python -m markdown "$2" > /dev/null
    echo "Agent definition is valid"
    ;;
esac
```

## 高级特性

### 1. 模板继承

```markdown
# Advanced Coordinator Agent
<!-- extends: coordinator.agent.md -->

## 接口定义
<!-- override -->
增强版协调Agent，支持并行执行。

## 工具
<!-- append -->
- parallel_executor
```

### 2. 条件包含

```markdown
## 工具
<!-- if: environment == "production" -->
- monitoring_agent
- alerting_agent
<!-- endif -->
```

### 3. 知识引用

```markdown
## 知识
<!-- include: ../shared/knowledge/base.md -->
<!-- include-pattern: ./knowledge/*.md -->
```

### 4. 动态配置

```markdown
## 配置
<!-- env: LLM_MODEL -->
llm: ${LLM_MODEL:-gpt-4}
<!-- env: TEMPERATURE -->
temperature: ${TEMPERATURE:-0}
```

## 与React Agent集成

### 加载器实现

```python
class MarkdownAgentLoader:
    """从Markdown加载Agent定义"""
    
    @staticmethod
    def load(filepath: str) -> ReactAgentConfig:
        with open(filepath, 'r') as f:
            content = f.read()
        
        # 解析Markdown
        doc = parse_markdown(content)
        
        # 提取配置
        config = ReactAgentConfig(
            name=doc.get('title', 'unnamed'),
            interface=doc.get('interface'),
            knowledge_files=doc.get('knowledge', []),
            **doc.get('config', {})
        )
        
        # 加载工具
        tools = []
        for tool_name in doc.get('tools', []):
            if tool_name.endswith('.agent.md'):
                # 递归加载子Agent作为工具
                sub_agent = MarkdownAgentLoader.load(tool_name)
                tools.append(create_langchain_tool(sub_agent))
            else:
                # 加载标准工具
                tools.append(load_tool(tool_name))
        
        config.tools = tools
        return config

# 使用
config = MarkdownAgentLoader.load('coordinator.agent.md')
agent = GenericReactAgent(config)
```

## 最佳实践

### 1. 保持简单
- 一个文件定义一个Agent
- 使用清晰的标题结构
- 避免过度嵌套

### 2. 知识外置
- Agent定义只包含引用
- 知识内容放在独立文件
- 便于知识复用

### 3. 配置外部化
```markdown
## 配置
<!-- external: config/production.yaml -->
```

### 4. 测试驱动
- 在定义中包含测试用例
- 便于验证Agent行为
- 支持自动化测试

## 迁移路径

### 从轻量级到重量级

```python
def upgrade_to_heavy(markdown_file: str) -> str:
    """将Markdown定义升级为重量级格式"""
    
    md_def = load_markdown(markdown_file)
    
    # 转换为AgentDefinition格式
    agent_def = {
        "apiVersion": "agent/v1",
        "kind": "AgentDefinition",
        "metadata": extract_metadata(md_def),
        "spec": {
            "interface": md_def['interface'],
            "requires": {"tools": md_def['tools']},
            "knowledge": {"static": md_def['knowledge']},
            "config_template": md_def['config']
        }
    }
    
    # 保存为.agentdef
    output = markdown_file.replace('.agent.md', '.agentdef')
    save_json(output, agent_def)
    
    return output
```

## 适用场景

### ✅ 适合
- 快速原型开发
- 个人项目
- 知识驱动的Agent
- 教学演示
- 简单工作流

### ❌ 不适合
- 需要状态持久化
- 生产环境部署
- 复杂的Agent集群
- 需要checkpoint/restore
- 高并发场景

## 总结

轻量级Agent持久化通过**单个Markdown文件**提供了：

1. **极简设计**：一个文件定义一切
2. **人类友好**：Markdown格式易读易写
3. **版本控制友好**：纯文本便于diff和merge
4. **快速迭代**：修改即生效，无需构建
5. **知识驱动**：Agent能力由知识定义

这种设计理念是：
> "Agent的本质是知识+工具+配置，而不是代码"

适合快速开发和原型验证，需要生产部署时可以无缝升级到重量级方案。