# DeepSeek 64K 上下文窗口优化指南

## 上下文窗口分析

DeepSeek 提供了 **64K tokens** 的上下文窗口，这是一个巨大的优势。合理配置可以让 ReactAgent 记住更多历史，提供更好的连续性。

## Token 计算参考

### 中文/英文 Token 比率
- 英文：约 1 token = 4 字符
- 中文：约 1 token = 1.5-2 字符
- 代码：约 1 token = 3-4 字符

### 典型对话的 Token 消耗
```
一轮简单对话：
- 用户输入：50-200 tokens
- AI 响应：500-2000 tokens
- 总计：约 1000-2000 tokens/轮

一轮代码生成对话：
- 用户输入：100-300 tokens
- AI 响应（含代码）：2000-5000 tokens
- 总计：约 3000-5000 tokens/轮
```

## 优化后的配置

### 默认配置（已更新）
```python
max_token_limit=30000  # 约 30K tokens
```

这个配置可以：
- 保存约 **10-30 轮**完整对话
- 占用约 **50%** 的上下文窗口
- 为系统提示词和当前任务留出充足空间

### 上下文窗口分配建议
```
总窗口：64K tokens
├── 系统提示词：~2K tokens
├── 当前输入：~2K tokens  
├── 记忆缓冲：30K tokens（默认）
└── 安全余量：30K tokens
```

## 自定义配置

### 1. 轻量级项目（快速迭代）
```bash
python direct_react_agent_v3_fixed.py --memory smart --max-tokens 10000
# 保存约 3-10 轮对话，响应更快
```

### 2. 标准项目（默认推荐）
```bash
python direct_react_agent_v3_fixed.py --memory smart
# 使用默认 30000 tokens，平衡性能和记忆
```

### 3. 复杂项目（需要长历史）
```bash
python direct_react_agent_v3_fixed.py --memory smart --max-tokens 50000
# 最大化利用上下文，保存 15-50 轮对话
```

### 4. 超长会话（专业模式）
```bash
python direct_react_agent_v3_fixed.py --memory pro --session-id complex_project
# 使用数据库存储，不受 token 限制
```

## ConversationSummaryBufferMemory 工作原理

```python
ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=30000,  # 缓冲区大小
    memory_key="chat_history",
    return_messages=True
)
```

工作流程：
1. **保留最近对话**：在缓冲区内的对话保持原文
2. **压缩旧对话**：超出限制的早期对话自动摘要
3. **动态调整**：根据对话长度智能管理

## 性能影响

| Token 限制 | 保存轮数 | 延迟影响 | 建议场景 |
|-----------|---------|----------|----------|
| 5,000 | 1-3轮 | 最小 | 简单任务 |
| 10,000 | 3-10轮 | 小 | 快速开发 |
| 30,000 | 10-30轮 | 中等 | 标准项目 |
| 50,000 | 15-50轮 | 较大 | 复杂项目 |

## 监控 Token 使用

查看实际 token 消耗：
```python
# 在代码中添加日志
if self.memory and hasattr(self.memory, 'buffer'):
    current_tokens = self.llm.get_num_tokens_from_messages(
        self.memory.buffer
    )
    logger.info(f"Current memory tokens: {current_tokens}/{self.config.max_token_limit}")
```

## 建议

1. **开始时使用默认值**（30000）
   - 对于 DeepSeek 64K 窗口是个合理的平衡

2. **根据实际需要调整**
   - 简单任务：降低到 10000
   - 复杂调试：提高到 40000-50000

3. **监控实际使用**
   - 如果经常触发摘要，考虑增加限制
   - 如果很少用满，可以降低以提高性能

4. **长期项目直接用 Pro 模式**
   - 不受 token 限制
   - 完整的历史记录

## 总结

将默认 `max_token_limit` 从 3000 提升到 30000 是个明智的选择，充分利用了 DeepSeek 的大上下文窗口优势。用户还可以通过 `--max-tokens` 参数灵活调整，以适应不同的使用场景。