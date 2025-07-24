# Agent CLI - 通用 LLM Agent 命令行工具

## 概述

Agent CLI 是一个通用的 LLM Agent 命令行工具，支持任何兼容 OpenAI API 的 LLM 服务。它不依赖于特定的 AI 提供商，让您可以自由选择最适合的服务。

## 支持的 LLM 提供商

| 提供商 | 特点 | 适用场景 |
|--------|------|----------|
| **OpenAI** | GPT-4/GPT-3.5，性能最强 | 国际用户，高质量需求 |
| **DeepSeek** | 中国直连，性价比极高 | 中国用户，成本敏感 |
| **通义千问** | 阿里云，稳定可靠 | 企业用户，合规需求 |
| **智谱清言** | GLM-4，中文优化 | 中文场景，学术研究 |
| **月之暗面** | 长文本支持 | 文档处理，长对话 |

## 快速开始

### 1. 安装依赖

```bash
pip install langchain-openai langchain-core
```

### 2. 配置 LLM 提供商

```bash
# 交互式配置
python -m agent_cli setup

# 查看所有提供商
python -m agent_cli providers

# 查看价格对比
python -m agent_cli providers --prices
```

### 3. 测试连接

```bash
# 测试默认提供商
python -m agent_cli test

# 测试特定提供商
python -m agent_cli test --provider deepseek
```

### 4. 执行任务

```bash
# 使用默认提供商
python -m agent_cli run "分析 main.py 的代码结构"

# 指定提供商
python -m agent_cli run "创建用户认证系统" --provider openai

# 指定模型
python -m agent_cli run "优化数据库查询" --provider openai --model gpt-4
```

## 使用示例

### PIM 到 PSM 转换

```bash
# 基本转换
python -m agent_cli convert models/user.md

# 指定输出和平台
python -m agent_cli convert models/user.md -o output/user_psm.md -t django

# 使用特定提供商
python -m agent_cli convert models/user.md --provider deepseek
```

### Python API 使用

```python
from agent_cli import AgentCLI, LLMConfig

# 方式1：使用环境变量配置
cli = AgentCLI()

# 方式2：指定提供商
config = LLMConfig.from_env("deepseek")
cli = AgentCLI(llm_config=config)

# 方式3：完全自定义配置
config = LLMConfig(
    api_key="your-api-key",
    base_url="https://api.deepseek.com/v1",
    model="deepseek-chat",
    provider="deepseek"
)
cli = AgentCLI(llm_config=config)

# 执行任务
success, message = cli.execute_task("你的任务")
```

## 环境变量配置

### 通用配置
```bash
# 默认提供商
export LLM_PROVIDER=deepseek  # openai, deepseek, qwen, glm, moonshot
```

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
export OPENAI_MODEL="gpt-3.5-turbo"  # 可选，默认 gpt-3.5-turbo
```

### DeepSeek
```bash
export DEEPSEEK_API_KEY="sk-..."
export DEEPSEEK_MODEL="deepseek-chat"  # 可选
```

### 通义千问
```bash
export DASHSCOPE_API_KEY="sk-..."
export QWEN_MODEL="qwen-turbo"  # 可选
```

### 智谱清言
```bash
export ZHIPU_API_KEY="..."
export GLM_MODEL="glm-4"  # 可选
```

### 月之暗面
```bash
export MOONSHOT_API_KEY="sk-..."
export MOONSHOT_MODEL="moonshot-v1-8k"  # 可选
```

## 高级功能

### 任务规划

```python
from agent_cli import AgentCLI

cli = AgentCLI()
plan = cli.plan("创建完整的电商系统")

print(f"执行步骤 ({len(plan.steps)} 步):")
for i, step in enumerate(plan.steps):
    print(f"{i+1}. {step}")
```

### 内容分析

```python
# 分析代码
with open("app.py", "r") as f:
    code = f.read()

result = cli.analyze_content(
    code,
    "分析代码质量，找出潜在问题"
)
```

### 代码生成

```python
code = cli.generate_code(
    "创建 FastAPI 用户认证端点",
    context={"auth_method": "JWT", "database": "PostgreSQL"}
)
```

### 批处理

```python
import glob
from agent_cli import AgentCLI

# 批量转换 PIM 文件
pim_files = glob.glob("models/*.md")

for pim_file in pim_files:
    cli = AgentCLI()
    psm_file = pim_file.replace(".md", "_psm.md")
    
    task = f"将 {pim_file} 转换为 FastAPI PSM，输出到 {psm_file}"
    success, message = cli.execute_task(task)
    
    print(f"{pim_file}: {'✅' if success else '❌'}")
```

## 集成到现有项目

### 作为 PIM Compiler 后端

```python
# 在 pure_gemini_compiler.py 中
from agent_cli import AgentCLI, LLMConfig

def compile_pim(pim_file, platform, provider="deepseek"):
    config = LLMConfig.from_env(provider)
    cli = AgentCLI(llm_config=config)
    
    task = f"将 {pim_file} 转换为 {platform} 平台的 PSM"
    return cli.execute_task(task)
```

### 自定义工具

```python
from agent_cli import Tool, AgentCLI

class DatabaseQuery(Tool):
    def execute(self, params):
        query = params.get("query")
        # 执行数据库查询
        return "query results"

# 添加自定义工具
cli = AgentCLI()
cli.tools["db_query"] = DatabaseQuery()
```

## 性能优化

### 1. 选择合适的模型
- 简单任务：使用 turbo/chat 模型
- 复杂任务：使用 GPT-4 或 GLM-4
- 长文本：使用 Moonshot 128k

### 2. 并发处理
```python
import concurrent.futures
from agent_cli import AgentCLI

def process_file(file_path):
    cli = AgentCLI()
    return cli.execute_task(f"处理 {file_path}")

# 并发处理多个文件
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    files = ["file1.md", "file2.md", "file3.md"]
    results = list(executor.map(process_file, files))
```

### 3. 缓存机制
```python
import hashlib
import json

cache = {}

def cached_execute(task):
    task_hash = hashlib.md5(task.encode()).hexdigest()
    
    if task_hash in cache:
        return cache[task_hash]
    
    cli = AgentCLI()
    result = cli.execute_task(task)
    cache[task_hash] = result
    
    return result
```

## 价格对比（2024年）

| 提供商 | 输入价格 | 输出价格 | 相对成本 |
|--------|----------|----------|----------|
| OpenAI GPT-3.5 | $0.5/1M | $1.5/1M | 基准 |
| OpenAI GPT-4 | $30/1M | $60/1M | 60x |
| DeepSeek | ¥1/1M | ¥2/1M | 0.02x |
| 通义千问 | ¥8/1M | ¥20/1M | 0.2x |
| 智谱 GLM-4 | ¥100/1M | ¥100/1M | 2x |
| 月之暗面 | ¥12/1M | ¥12/1M | 0.24x |

## 故障排除

### API Key 未设置
```bash
# 检查环境变量
echo $OPENAI_API_KEY
echo $DEEPSEEK_API_KEY

# 重新配置
python -m agent_cli setup
```

### 网络连接问题
- OpenAI：可能需要代理
- 国内提供商：检查防火墙设置
- 使用自定义 base_url 绕过限制

### Token 限制
- 分块处理大文件
- 选择支持长文本的模型
- 优化提示词长度

## 开发路线图

- [ ] 支持更多 LLM 提供商
- [ ] 流式响应支持
- [ ] 函数调用 (Function Calling)
- [ ] 多轮对话管理
- [ ] 插件系统
- [ ] Web UI

## 贡献指南

欢迎贡献代码、报告问题或提出建议！

1. Fork 项目
2. 创建特性分支
3. 提交更改
4. 发起 Pull Request

## 许可证

MIT License