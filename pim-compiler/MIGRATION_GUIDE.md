# 从 DeepSeek CLI 迁移到 Agent CLI

## 概述

Agent CLI 是 DeepSeek CLI 的升级版本，支持多种 LLM 提供商，而不仅限于 DeepSeek。这个迁移指南将帮助您从 deepseek_cli 平滑过渡到 agent_cli。

## 主要变化

### 1. 包名变更
- 旧：`deepseek_cli`
- 新：`agent_cli`

### 2. 类名变更
- 旧：`DeepSeekCLI`, `DeepSeekLLM`
- 新：`AgentCLI`, `LLMConfig`

### 3. 配置方式
- 旧：只支持 DeepSeek
- 新：支持多种 LLM 提供商

## 代码迁移

### 导入语句

```python
# 旧代码
from deepseek_cli import DeepSeekCLI, DeepSeekLLM

# 新代码
from agent_cli import AgentCLI, LLMConfig
```

### 基本使用

```python
# 旧代码
cli = DeepSeekCLI()
success, message = cli.execute_task("你的任务")

# 新代码（使用 DeepSeek）
cli = AgentCLI()  # 自动从环境变量读取配置
success, message = cli.execute_task("你的任务")

# 或显式指定 DeepSeek
config = LLMConfig.from_env("deepseek")
cli = AgentCLI(llm_config=config)
```

### API Key 配置

```bash
# 旧环境变量
export DEEPSEEK_API_KEY="your-key"

# 新环境变量（额外需要）
export LLM_PROVIDER=deepseek
export DEEPSEEK_API_KEY="your-key"
```

## 命令行迁移

### 配置命令

```bash
# 旧命令
python -m deepseek_cli setup

# 新命令
python -m agent_cli setup
# 选择 deepseek 作为提供商
```

### 运行任务

```bash
# 旧命令
python -m deepseek_cli run "任务"

# 新命令
python -m agent_cli run "任务" --provider deepseek
# 或设置 LLM_PROVIDER=deepseek 后直接运行
python -m agent_cli run "任务"
```

### PIM 转换

```bash
# 旧命令
python -m deepseek_cli convert input.md

# 新命令
python -m agent_cli convert input.md --provider deepseek
```

## 新功能

### 1. 多提供商支持

```python
# 使用 OpenAI
config = LLMConfig.from_env("openai")
cli = AgentCLI(llm_config=config)

# 使用通义千问
config = LLMConfig.from_env("qwen")
cli = AgentCLI(llm_config=config)
```

### 2. 提供商切换

```bash
# 查看所有提供商
python -m agent_cli providers

# 查看价格对比
python -m agent_cli providers --prices

# 测试不同提供商
python -m agent_cli test --provider openai
python -m agent_cli test --provider deepseek
```

### 3. 模型选择

```bash
# 使用特定模型
python -m agent_cli run "任务" --provider openai --model gpt-4
```

## 兼容性说明

### 保持兼容的部分
- 核心功能完全兼容
- 执行流程保持一致
- 工具系统相同
- 文件操作不变

### 需要调整的部分
- 类名和导入路径
- 环境变量配置
- 命令行参数

## 快速迁移脚本

创建一个 `migrate.py` 文件：

```python
#!/usr/bin/env python3
"""快速迁移脚本"""
import os
import sys

# 检查 DeepSeek 配置
deepseek_key = os.getenv("DEEPSEEK_API_KEY")
if deepseek_key:
    print("✅ 检测到 DeepSeek API Key")
    
    # 设置新的环境变量
    os.environ["LLM_PROVIDER"] = "deepseek"
    
    # 创建 .env 文件
    with open(".env", "w") as f:
        f.write(f"LLM_PROVIDER=deepseek\n")
        f.write(f"DEEPSEEK_API_KEY={deepseek_key}\n")
    
    print("✅ 配置已迁移到 .env 文件")
    print("\n现在可以使用 agent_cli 了：")
    print("  python -m agent_cli run '你的任务'")
else:
    print("❌ 未找到 DEEPSEEK_API_KEY")
    print("请先设置：export DEEPSEEK_API_KEY='your-key'")
```

## 常见问题

### Q: 我必须迁移吗？
A: 不是必须的。如果您只使用 DeepSeek，deepseek_cli 仍然可以正常工作。但 agent_cli 提供了更多选择和灵活性。

### Q: 迁移后性能会变化吗？
A: 不会。使用相同的 LLM 提供商时，性能完全一致。

### Q: 可以同时使用两个包吗？
A: 可以，它们是独立的包，互不影响。

### Q: 如何选择最合适的提供商？
A: 
- 中国用户：DeepSeek（最便宜）、通义千问（稳定）
- 国际用户：OpenAI（最强）
- 长文本：月之暗面（128k）
- 企业用户：通义千问（合规）

## 获取帮助

- 查看文档：`agent_cli/README.md`
- 运行测试：`python -m agent_cli test`
- 查看帮助：`python -m agent_cli --help`