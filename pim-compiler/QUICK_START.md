# PIM Compiler 快速开始指南

## 概述

PIM Compiler 是一个基于 LLM 的 PIM（平台无关模型）编译器，可以将业务模型编译为平台特定实现。

## 安装

```bash
# 1. 克隆代码
cd /home/guci/aiProjects/mda/pim-compiler

# 2. 安装依赖
pip install -r requirements.txt

# 3. 设置环境变量
export DEEPSEEK_API_KEY=your-actual-api-key
export PIM_HOME=/opt/pim-engine
```

## 使用方法

### 1. 使用 CLI 工具

```bash
# 编译 PIM 文件
./pimc compile examples/user_management.md

# 编译并生成代码
./pimc generate examples/user_management.md --code-output ./generated

# 查看支持的平台
./pimc list-platforms
```

### 2. 在代码中使用

```python
from pathlib import Path
from compiler.core.compiler_config import CompilerConfig
from compiler.transformers.deepseek_compiler import DeepSeekCompiler

# 创建配置
config = CompilerConfig(
    target_platform="fastapi",
    output_dir=Path("./output")
)

# 创建编译器
compiler = DeepSeekCompiler(config)

# 编译 PIM 文件
result = compiler.compile(Path("examples/user_management.md"))

if result.success:
    print(f"编译成功: {result.psm_file}")
else:
    print(f"编译失败: {result.errors}")
```

## 架构说明

```
PIM 文件 (Markdown/YAML)
    ↓
DeepSeek LLM 解析
    ↓
PIM Model (业务模型)
    ↓
IR (中间表示)
    ↓
PSM Model (平台特定模型)
    ↓
PSM 文件 / 代码生成
```

## 关键组件

1. **BaseCompiler**: 抽象编译器基类，定义编译流程
2. **DeepSeekCompiler**: 使用 DeepSeek LLM 的具体实现
3. **PIMModel/PSMModel/IRModel**: 数据模型定义
4. **CompilerConfig**: 编译器配置
5. **CLI (pimc)**: 命令行工具

## 注意事项

1. **需要有效的 DEEPSEEK_API_KEY** 才能运行编译器
2. 编译结果会缓存以减少 API 调用
3. 支持的平台：fastapi, spring, django, flask
4. 输入格式：Markdown (推荐), YAML, JSON

## 已修复的问题

1. ✅ Pylance 类型错误（Optional 类型注解）
2. ✅ Python dataclass 继承问题（字段默认值）
3. ✅ 模块导入路径问题

## 待完成

- [ ] 实现 YAML/JSON PIM 加载器
- [ ] 添加更多平台支持
- [ ] 完善代码生成功能
- [ ] 添加更多测试用例

## 测试

```bash
# 运行结构测试（不需要 API key）
python tests/test_structure.py

# 运行完整测试（需要 API key）
export DEEPSEEK_API_KEY=your-key
python tests/test_compiler.py
```