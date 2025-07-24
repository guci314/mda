# Agent CLI 项目总结

## 项目概述

Agent CLI 是一个通用的 LLM Agent 命令行工具，从原来的 DeepSeek CLI 演进而来。它支持任何兼容 OpenAI API 的 LLM 服务，让用户可以根据需求自由选择最适合的 AI 提供商。

## 核心特性

### 1. 多提供商支持
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **DeepSeek**: 中国直连，极低成本
- **通义千问**: 阿里云服务，企业级稳定
- **智谱清言**: GLM-4，中文优化
- **月之暗面**: 支持超长文本（128k）
- **自定义**: 任何兼容 OpenAI API 的服务

### 2. 统一接口
```python
# 所有提供商使用相同的接口
from agent_cli import AgentCLI, LLMConfig

# 方式1：自动检测
cli = AgentCLI()

# 方式2：指定提供商
config = LLMConfig.from_env("deepseek")
cli = AgentCLI(llm_config=config)

# 方式3：完全自定义
config = LLMConfig(
    api_key="your-key",
    base_url="https://api.example.com/v1",
    model="your-model",
    provider="custom"
)
cli = AgentCLI(llm_config=config)
```

### 3. 功能完整
- 任务规划和执行
- 文件操作（读取、写入、列表）
- 内容分析
- 代码生成
- PIM 到 PSM 转换
- 批处理支持

## 技术架构

### 依赖
- **LangChain**: 统一的 LLM 接口
- **Pydantic**: 数据验证和配置管理
- **Python 3.8+**: 类型注解支持

### 核心组件
1. **LLMConfig**: 配置管理
2. **AgentCLI**: 主执行引擎
3. **Tool System**: 可扩展的工具系统
4. **ExecutionPlan**: 任务规划和跟踪

## 使用场景

### 1. 代码生成
```bash
python -m agent_cli run "创建用户认证系统" --provider deepseek
```

### 2. PIM 转换
```bash
python -m agent_cli convert models/user.md --provider qwen
```

### 3. 文档分析
```bash
python -m agent_cli run "分析项目文档结构" --provider openai --model gpt-4
```

## 性能和成本对比

| 提供商 | 速度 | 质量 | 成本 | 适用场景 |
|--------|------|------|------|----------|
| GPT-4 | ★★★ | ★★★★★ | $$$$$ | 复杂任务 |
| GPT-3.5 | ★★★★ | ★★★★ | $$ | 日常使用 |
| DeepSeek | ★★★★ | ★★★★ | $ | 高性价比 |
| 通义千问 | ★★★★ | ★★★★ | $$ | 企业应用 |
| 智谱GLM | ★★★ | ★★★★ | $$$ | 中文场景 |

## 迁移指南

从 DeepSeek CLI 迁移：
1. 包名: `deepseek_cli` → `agent_cli`
2. 类名: `DeepSeekCLI` → `AgentCLI`
3. 配置: 添加 `LLM_PROVIDER=deepseek`

## 最佳实践

### 1. 选择合适的提供商
- **成本敏感**: DeepSeek
- **质量优先**: OpenAI GPT-4
- **中文处理**: 通义千问或智谱
- **长文本**: 月之暗面

### 2. 优化性能
- 使用批处理减少 API 调用
- 实现缓存避免重复处理
- 选择合适的模型大小

### 3. 错误处理
- 设置重试机制
- 实现降级策略
- 记录详细日志

## 未来规划

1. **功能增强**
   - 流式响应支持
   - 函数调用 (Function Calling)
   - 多轮对话管理

2. **提供商扩展**
   - Claude API 支持
   - 本地模型支持 (Ollama)
   - 更多国产模型

3. **工具生态**
   - 插件系统
   - Web UI
   - VS Code 扩展

## 贡献

欢迎贡献代码、报告问题或添加新的 LLM 提供商支持！

项目地址：`agent_cli/`

## 总结

Agent CLI 通过解耦 LLM 提供商，实现了真正的通用性和灵活性。用户可以根据具体需求（成本、性能、地域等）选择最合适的 AI 服务，同时保持代码的一致性和可移植性。