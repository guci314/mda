# 修复 DeepSeek Token 计数问题

## 问题描述

使用 DeepSeek 模型时，`ConversationSummaryBufferMemory` 会报错：
```
NotImplementedError: get_num_tokens_from_messages() is not presently implemented for model cl100k_base
```

## 解决方案

### 方案1：使用 Token 计数补丁（推荐）

已创建 `deepseek_token_counter.py`，自动为 DeepSeek 添加 token 计数功能。

**使用方法**：
```bash
# 确保安装了 tiktoken
pip install tiktoken

# 运行时会自动应用补丁
python direct_react_agent_v3_fixed.py --memory smart
```

### 方案2：使用窗口记忆替代

如果补丁不工作，可以使用 `ConversationBufferWindowMemory` 替代：

```python
# 替换
ConversationSummaryBufferMemory(
    llm=self.llm,
    max_token_limit=30000
)

# 为
ConversationBufferWindowMemory(
    k=50,  # 保留最近50轮对话
    memory_key="chat_history",
    return_messages=True
)
```

### 方案3：临时降级为无记忆模式

```bash
# 如果记忆功能有问题，可以暂时使用无记忆模式
python direct_react_agent_v3_fixed.py --memory none
```

### 方案4：手动实现简单的 token 计数

```python
# 在 _create_llm 方法后添加
def simple_token_counter(self, messages):
    """简单的 token 估算"""
    total_chars = sum(len(str(m.content)) for m in messages)
    # 粗略估算：平均每 3-4 个字符一个 token
    return total_chars // 3

# 猴子补丁
self.llm.get_num_tokens_from_messages = simple_token_counter
```

## 根本原因

1. LangChain 的 `ChatOpenAI` 类期望模型提供 token 计数方法
2. DeepSeek 使用自定义模型名称，不在 OpenAI 的标准模型列表中
3. `ConversationSummaryBufferMemory` 依赖 token 计数来决定何时压缩历史

## 长期解决方案

1. 等待 LangChain 官方支持 DeepSeek
2. 使用自定义的 Memory 类
3. 向 LangChain 提交 PR 添加 DeepSeek 支持

## 推荐配置

对于现在，建议：

```bash
# 使用已修复的版本
python direct_react_agent_v3_fixed.py --memory smart

# 如果还有问题，使用 pro 模式（不需要 token 计数）
python direct_react_agent_v3_fixed.py --memory pro --session-id my_project
```