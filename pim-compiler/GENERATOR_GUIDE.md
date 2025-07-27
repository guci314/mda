# PIM Compiler 代码生成器指南

## 概述

PIM Compiler 现在支持多种代码生成器后端，可以根据不同的需求选择合适的生成器：

- **Gemini CLI**: 基于 Google Gemini CLI 的生成器（默认）
- **React Agent**: 基于 LangChain React Agent 的智能生成器
- **Autogen**: 基于 Microsoft Autogen 的多 Agent 协作生成器

## 生成器对比

| 特性 | Gemini CLI | React Agent | Autogen |
|------|------------|-------------|---------|
| **速度** | 快 | 中等 | 较慢 |
| **质量** | 高 | 高 | 最高 |
| **配置复杂度** | 低 | 中 | 高 |
| **API 依赖** | Gemini API | DeepSeek/OpenAI | DeepSeek/OpenAI |
| **错误修复** | 支持 | 部分支持 | 支持 |
| **多 Agent 协作** | 否 | 否 | 是 |
| **增量生成** | 是 | 是 | 是 |
| **成本** | 低 | 中 | 高 |

## 快速开始

### 1. 安装依赖

```bash
# 基础依赖
pip install -r requirements.txt

# React Agent 额外依赖
pip install langchain langchain-openai

# Autogen 额外依赖
pip install pyautogen
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# 选择默认生成器
CODE_GENERATOR_TYPE=gemini-cli  # 或 react-agent, autogen

# Gemini CLI 配置
GEMINI_MODEL=gemini-2.5-pro  # 可选，默认为 gemini-2.5-pro

# React Agent 配置（使用 DeepSeek）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_BASE_URL=https://api.deepseek.com

# Autogen 配置（默认使用 DeepSeek）
DEEPSEEK_API_KEY=your-deepseek-api-key
DEEPSEEK_MODEL=deepseek-chat  # 可选，默认为 deepseek-chat

# Autogen 配置（备选 OpenAI）
# OPENAI_API_KEY=your-openai-api-key
# OPENAI_MODEL=gpt-4
```

### 3. 使用命令行

```bash
# 列出所有可用的生成器
./compile_with_generator.py --list-generators

# 使用默认生成器（Gemini CLI）
./compile_with_generator.py examples/user_management.md

# 使用 React Agent 生成器
./compile_with_generator.py examples/blog.md --generator react-agent

# 使用 Autogen 生成器
./compile_with_generator.py examples/hospital.md --generator autogen

# 指定输出目录和目标平台
./compile_with_generator.py examples/blog.md \
    --generator react-agent \
    --output ./my_output \
    --platform django
```

## 生成器详细说明

### Gemini CLI Generator

**特点**：
- 使用 Google Gemini CLI 命令行工具
- 支持增量修复和错误模式缓存
- 生成速度快，质量稳定
- 支持自动测试和修复

**适用场景**：
- 快速原型开发
- 标准的 CRUD 应用
- 需要快速迭代的项目

**示例**：
```bash
./compile_with_generator.py examples/user_management.md --generator gemini-cli
```

### React Agent Generator

**特点**：
- 使用 LangChain 的 React Agent 架构
- 支持工具调用和自主规划
- 可注入软件工程知识
- 生成的代码结构更专业

**适用场景**：
- 需要复杂业务逻辑的应用
- 要求高代码质量的项目
- 需要自定义生成策略的场景

**示例**：
```bash
export DEEPSEEK_API_KEY=your-api-key
./compile_with_generator.py examples/blog.md --generator react-agent
```

### Autogen Generator

**特点**：
- 多个专门 Agent 协作（架构师、模型设计师、API 设计师、程序员、审查员）
- 生成的代码质量最高
- 支持复杂的系统设计
- 成本较高，速度较慢

**适用场景**：
- 大型企业应用
- 复杂的微服务架构
- 需要最佳实践的生产级代码

**示例**：
```bash
export DEEPSEEK_API_KEY=your-api-key
./compile_with_generator.py examples/hospital.md --generator autogen
```

## 编程接口

### 基本使用

```python
from src.compiler.config import CompilerConfig
from src.compiler.core.configurable_compiler import ConfigurableCompiler

# 创建配置
config = CompilerConfig(
    generator_type="react-agent",
    target_platform="fastapi",
    output_dir=Path("./output")
)

# 创建编译器
compiler = ConfigurableCompiler(config)

# 编译 PIM
result = compiler.compile(Path("my_model.md"))

if result["success"]:
    print(f"Generated code in: {result['output_dir']}")
```

### 切换生成器

```python
# 运行时切换生成器
compiler.switch_generator("autogen")

# 重新编译
result = compiler.compile(Path("another_model.md"))
```

### 自定义生成器

```python
from src.compiler.generators import BaseGenerator, GeneratorConfig, GenerationResult

class MyCustomGenerator(BaseGenerator):
    def generate_psm(self, pim_content: str, platform: str, output_dir: Path) -> GenerationResult:
        # 实现 PSM 生成逻辑
        pass
    
    def generate_code(self, psm_content: str, output_dir: Path, platform: str) -> GenerationResult:
        # 实现代码生成逻辑
        pass

# 注册自定义生成器
from src.compiler.generators import GeneratorFactory
GeneratorFactory.register_generator("my-generator", MyCustomGenerator)

# 使用自定义生成器
config = CompilerConfig(generator_type="my-generator")
```

## 最佳实践

### 1. 选择合适的生成器

- **原型开发**：使用 Gemini CLI，快速迭代
- **生产代码**：使用 React Agent 或 Autogen，确保质量
- **复杂系统**：使用 Autogen，利用多 Agent 协作

### 2. 优化生成质量

**对于 React Agent**：
- 在系统提示词中注入领域知识
- 使用详细的 PSM 描述
- 设置合适的 temperature（建议 0.1）

**对于 Autogen**：
- 提供清晰的需求描述
- 让 Agent 充分讨论和迭代
- 使用代码审查 Agent 确保质量

### 3. 成本控制

- 开发阶段使用 Gemini CLI 或 DeepSeek
- Autogen 现在默认使用 DeepSeek，成本更低
- 只在必要时切换到 GPT-4（通过环境变量）
- 缓存生成结果，避免重复生成

### 4. 错误处理

```python
result = compiler.compile(pim_file)

if not result["success"]:
    print(f"Error: {result['error']}")
    # 查看详细日志
    if result.get("psm_logs"):
        print(f"PSM Logs: {result['psm_logs']}")
    if result.get("code_logs"):
        print(f"Code Logs: {result['code_logs']}")
```

## 故障排除

### Gemini CLI 问题

**问题**：找不到 Gemini CLI
**解决**：确保已安装 Gemini CLI 并在 PATH 中

```bash
npm install -g @google/generative-ai-cli
```

### React Agent 问题

**问题**：API Key 错误
**解决**：检查环境变量设置

```bash
echo $DEEPSEEK_API_KEY
# 或
echo $OPENAI_API_KEY
```

### Autogen 问题

**问题**：Agent 对话超时
**解决**：增加 timeout 配置

```python
config = CompilerConfig(
    generator_type="autogen",
    timeout=1200  # 20 分钟
)
```

## 性能基准

基于用户管理系统（简单 CRUD）的测试结果：

| 生成器 | PSM 生成时间 | 代码生成时间 | 总时间 | 文件数 | 代码质量评分 |
|--------|-------------|-------------|--------|--------|--------------|
| Gemini CLI | 4s | 7s | 11s | 14 | 85/100 |
| React Agent (DeepSeek) | 15s | 45s | 60s | 16 | 90/100 |
| Autogen (DeepSeek) | 30s | 120s | 150s | 18 | 95/100 |

*注：时间会因模型、网络和系统复杂度而异*

## 未来计划

1. **Claude Code Generator**: 集成 Anthropic Claude API
2. **Local LLM Generator**: 支持本地部署的 LLM
3. **Hybrid Generator**: 结合多个生成器的优势
4. **Template Generator**: 基于模板的快速生成
5. **RAG Generator**: 基于检索增强的生成器

## 贡献指南

欢迎贡献新的生成器实现！请参考 `BaseGenerator` 抽象类，确保实现所有必要的方法。

1. 继承 `BaseGenerator`
2. 实现 `generate_psm` 和 `generate_code` 方法
3. 在 `GeneratorFactory` 中注册
4. 添加测试和文档
5. 提交 Pull Request

## 许可证

MIT License