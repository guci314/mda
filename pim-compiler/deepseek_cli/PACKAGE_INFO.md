# DeepSeek CLI 包结构说明

## 包结构

```
deepseek_cli/
├── __init__.py          # 包初始化，导出主要类和函数
├── __main__.py          # 命令行入口，支持 python -m deepseek_cli
├── core.py              # 核心实现，包含 DeepSeekCLI 和 DeepSeekLLM
├── setup.py             # API 配置工具
├── test_cli.py          # 测试脚本
├── demo.py              # 功能演示
├── gemini_cli_reference.py  # Gemini CLI 参考实现
├── README.md            # 详细文档
├── USAGE.md             # 使用指南
└── PACKAGE_INFO.md      # 本文件
```

## 模块说明

### core.py
- **DeepSeekCLI**: 主要的 CLI 实现类
- **DeepSeekLLM**: DeepSeek API 封装
- **ExecutionPlan**: 执行计划数据结构
- **Action**: 动作定义
- **Tool**: 工具基类及实现（FileReader, FileWriter, FileLister）

### setup.py
- **setup_deepseek()**: 交互式配置 API
- **test_deepseek_api()**: 测试 API 连接
- **save_config()**: 保存配置到文件
- **check_deepseek_prices()**: 显示价格信息

### test_cli.py
- **test_deepseek_cli()**: 测试 DeepSeek CLI 功能
- **test_gemini_cli_core()**: 测试 Gemini CLI 参考实现
- **generate_comparison_report()**: 生成对比报告

### demo.py
- **demo_basic_usage()**: 基本用法演示
- **demo_task_planning()**: 任务规划演示
- **demo_code_analysis()**: 代码分析演示
- **demo_batch_processing()**: 批处理演示
- **demo_error_handling()**: 错误处理演示

### __main__.py
命令行接口，支持以下命令：
- `setup`: 配置 API
- `demo`: 运行演示
- `test`: 运行测试
- `run`: 执行任务
- `convert`: PIM 到 PSM 转换

## 快速开始

### 1. 作为包使用

```python
from deepseek_cli import DeepSeekCLI, DeepSeekLLM

# 创建 CLI 实例
cli = DeepSeekCLI()

# 执行任务
success, message = cli.execute_task("你的任务")
```

### 2. 命令行使用

```bash
# 配置
python -m deepseek_cli setup

# 运行任务
python -m deepseek_cli run "任务描述"

# 转换 PIM
python -m deepseek_cli convert input.md -o output.md
```

### 3. 使用快捷脚本

```bash
# 在项目根目录
./deepseek setup
./deepseek run "任务描述"
./deepseek convert models/user.md
```

## 环境要求

- Python 3.8+
- requests 库
- DeepSeek API Key

## 配置文件

配置保存在以下位置：
- `.env`: 环境变量
- `deepseek_config.json`: JSON 配置

## API 集成

### 与 PIM Compiler 集成

```python
# 在 pure_gemini_compiler.py 中
from deepseek_cli import DeepSeekCLI

def compile_with_deepseek(pim_file, platform):
    cli = DeepSeekCLI()
    task = f"将 {pim_file} 转换为 {platform} 平台的 PSM"
    return cli.execute_task(task)
```

### 自定义工具

```python
from deepseek_cli import Tool

class CustomTool(Tool):
    def execute(self, params):
        # 实现自定义工具逻辑
        return "tool result"

# 添加到 CLI
cli = DeepSeekCLI()
cli.tools["custom"] = CustomTool()
```

## 扩展性

### 添加新的动作类型

1. 在 `core.py` 的 `ActionType` 枚举中添加新类型
2. 在 `_decide_action()` 方法中添加判断逻辑
3. 在 `_execute_action()` 方法中添加执行逻辑

### 自定义 LLM 提供者

继承 `DeepSeekLLM` 类并重写 `_call_api()` 方法：

```python
class CustomLLM(DeepSeekLLM):
    def _call_api(self, messages, temperature=0.3):
        # 实现自定义 API 调用
        pass
```

## 性能优化

- 使用批处理减少 API 调用
- 实现缓存机制避免重复处理
- 并发执行提高效率
- 大文件分块处理

## 故障排除

1. **API Key 错误**: 运行 `python -m deepseek_cli setup`
2. **网络超时**: 增加 timeout 参数
3. **Token 限制**: 使用分块处理
4. **导入错误**: 确保在正确的目录运行

## 版本信息

- 当前版本: 1.0.0
- 最后更新: 2025-07-24
- 作者: PIM Compiler Team