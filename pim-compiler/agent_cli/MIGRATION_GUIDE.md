# Agent CLI v1 到 v2 迁移指南

## 概述

Agent CLI v2 引入了动态执行架构，解决了 v1 中"一个步骤一个动作"的限制。本指南帮助您从 v1 迁移到 v2。

## 主要变化

### 1. 架构改进

- **v1**: 单一决策器，步骤执行一个动作后立即结束
- **v2**: 双决策器（动作决策器 + 步骤决策器），支持步骤内多动作执行

### 2. API 变化

#### 基本使用（无变化）
```python
# v1 和 v2 相同
from agent_cli import AgentCLI, LLMConfig

config = LLMConfig.from_env()
cli = AgentCLI(config)
success, message = cli.execute_task("你的任务")
```

#### 新增参数
```python
# v2 新增参数
cli = AgentCLI(
    config,
    max_actions_per_step=10,      # 每个步骤最大动作数
    enable_dynamic_planning=True   # 启用动态计划调整
)
```

### 3. 命令行变化

#### 新增选项
```bash
# v2 新增命令行选项
python -m agent_cli run "任务" --max-actions 20
python -m agent_cli run "任务" --no-dynamic
```

## 迁移步骤

### 方法 1：自动迁移（推荐）

```bash
# 切换到 v2
python agent_cli/migrate_to_v2.py

# 检查当前版本
python agent_cli/migrate_to_v2.py --check

# 恢复到 v1（如果需要）
python agent_cli/migrate_to_v2.py --revert
```

### 方法 2：手动迁移

1. 更新导入：
```python
# 旧代码
from agent_cli import AgentCLI

# 新代码（明确使用 v2）
from agent_cli import AgentCLI_V2 as AgentCLI
```

2. 更新初始化：
```python
# 旧代码
cli = AgentCLI(config, enable_symbolic_fallback=True)

# 新代码
cli = AgentCLI(config, enable_dynamic_planning=True)
```

### 方法 3：使用兼容层

如果您有大量旧代码，可以使用兼容层：

```python
from agent_cli.compatibility import create_v1_compatible_cli

# 使用 v1 风格的 API，但底层是 v2
cli = create_v1_compatible_cli(config)
```

## 行为差异

### 1. 步骤执行

**v1 行为**：
```
步骤: 读取并生成代码
  动作 1: read_file
  [步骤结束]
```

**v2 行为**：
```
步骤: 读取并生成代码
  动作 1: read_file
  动作 2: write_file (main.py)
  动作 3: write_file (requirements.txt)
  [步骤完成]
```

### 2. 任务完成率

- v1：任务经常因步骤过早结束而失败
- v2：任务完成率显著提高

## 测试您的迁移

运行以下测试确保迁移成功：

```python
# test_migration.py
from agent_cli import AgentCLI, LLMConfig

config = LLMConfig.from_env()
cli = AgentCLI(config)

# 测试简单任务
task = "创建一个包含 'Hello World' 的 test.txt 文件"
success, message = cli.execute_task(task)

print(f"Success: {success}")
print(f"Message: {message}")

# v2 应该能完成这个任务
# v1 可能只会思考而不创建文件
```

## 故障排除

### 问题 1：导入错误
```
ImportError: cannot import name 'AgentCLI_V2'
```
**解决**：运行迁移脚本 `python migrate_to_v2.py`

### 问题 2：参数错误
```
TypeError: unexpected keyword argument 'enable_symbolic_fallback'
```
**解决**：移除 v1 特有的参数，或使用兼容层

### 问题 3：行为不一致
如果发现行为与预期不符，检查：
1. 是否正确切换到 v2
2. 是否有自定义的步骤逻辑需要调整

## 回滚

如果需要回滚到 v1：

```bash
python agent_cli/migrate_to_v2.py --revert
```

## 获取帮助

- 查看 [动态执行架构设计文档](动态执行架构设计.md)
- 查看 [实现总结](动态执行架构实现总结.md)
- 提交问题到项目仓库