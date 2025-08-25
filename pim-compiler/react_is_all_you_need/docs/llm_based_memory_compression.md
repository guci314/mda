# 基于LLM的连接主义记忆压缩

## 概述

传统的记忆压缩使用基于规则的符号主义方法（截断、提取关键词等），而连接主义方法使用语言模型（LLM）来智能地理解和压缩信息。

## 核心区别

### 符号主义方法（旧）
```python
# 基于规则的压缩
if len(content) > 300:
    return content[:300] + "..."  # 简单截断

# 关键词提取
if "def " in line or "class " in line:
    key_lines.append(line)  # 规则匹配
```

### 连接主义方法（新）
```python
# 使用LLM理解和压缩
response = await llm.chat.completions.create(
    messages=[
        {"role": "system", "content": "智能压缩以下内容，保留关键信息"},
        {"role": "user", "content": original_content}
    ]
)
compressed = response.choices[0].message.content
```

## 优势

### 1. **语义理解**
- LLM理解内容的含义，而不只是匹配模式
- 保留语义重要的信息，去除真正的冗余
- 识别隐含的关系和依赖

### 2. **上下文感知**
- 根据上下文判断信息的重要性
- 理解代码的逻辑关系
- 识别任务的关键步骤

### 3. **智能摘要**
- 生成自然语言摘要，而非机械截断
- 合并相似信息
- 提取关键洞察

### 4. **自适应压缩**
- 根据内容类型自动调整压缩策略
- 代码、文档、对话使用不同的压缩方式
- 保留领域特定的重要信息

## 实现架构

### 1. LLM压缩器（`llm_memory_compressor.py`）

#### 多级清晰度压缩
```python
class ClarityLevel(Enum):
    FULL = 1.0      # 原始内容
    HIGH = 0.7      # 详细摘要（LLM生成）
    MEDIUM = 0.5    # 标准摘要（LLM生成）
    LOW = 0.3       # 简短摘要（LLM生成）
    MINIMAL = 0.1   # 极简标记（LLM生成）
```

#### 压缩提示词示例
```python
HIGH (70%): """
保留所有重要细节和数据
保留关键的因果关系
保留具体的数值和名称
去除冗余和重复内容
"""

MEDIUM (50%): """
保留核心观点和结论
保留关键动作和结果
简化细节描述
合并相似内容
"""

LOW (30%): """
只保留最重要的信息
用一两句话概括
突出行动和结果
省略所有细节
"""

MINIMAL (10%): """
用3-5个词描述
格式：[角色:动作/状态]
"""
```

### 2. 神经网络记忆处理器（`neural_memory_processor.py`）

#### 语义信息提取
```python
# LLM提取语义信息
{
    "concepts": ["API调用", "错误处理"],
    "entities": ["QwenReactAgent", "memory_manager.py"],
    "actions": ["创建", "压缩", "存储"],
    "intent": "优化记忆系统性能",
    "sentiment": "positive"
}
```

#### 语义搜索
- 使用嵌入向量进行相似度搜索
- 理解查询意图，不只是关键词匹配
- 返回语义相关的记忆

#### 记忆巩固
```python
# LLM整合多个记忆
{
    "patterns": ["重复调用write_file", "错误后重试"],
    "key_insights": ["需要批处理优化", "错误处理不完善"],
    "causal_relations": [
        {"cause": "文件过大", "effect": "写入失败"}
    ],
    "consolidated_summary": "主要进行文件操作，存在性能优化空间"
}
```

## 使用示例

### 1. 初始化神经网络记忆
```python
from core.neural_memory_processor import NeuralMemoryProcessor

processor = NeuralMemoryProcessor(
    work_dir="./workspace",
    llm_model="gpt-4o-mini",  # 或其他模型
    enable_semantic_search=True
)
```

### 2. 处理消息
```python
# 自动生成多个清晰度的视图
views = await processor.process_message(message)

# 获取特定清晰度
high_clarity = views[ClarityLevel.HIGH]
minimal = views[ClarityLevel.MINIMAL]
```

### 3. 语义搜索
```python
# 搜索相关记忆
results = await processor.semantic_search(
    "如何处理文件写入错误",
    top_k=5
)
```

### 4. 生成上下文摘要
```python
# LLM智能总结当前状态
summary = await processor.generate_context_summary(
    max_tokens=4000
)
```

## 性能优化

### 1. 批处理
```python
# 批量压缩多个消息
compressed_batch = compressor.compress_message_batch(
    messages=[msg1, msg2, msg3],
    target_clarities=[LOW, MEDIUM, HIGH]
)
```

### 2. 缓存
- 压缩结果缓存到磁盘
- 相同内容不重复压缩
- 支持会话恢复

### 3. 异步处理
- 使用异步API调用
- 并发生成多个视图
- 不阻塞主流程

## 成本考虑

### API调用成本
- GPT-4o-mini: ~$0.15/1M input tokens
- 批处理可降低成本
- 缓存避免重复调用

### 优化策略
1. 使用更便宜的模型（如gpt-3.5-turbo）进行初步压缩
2. 只对重要消息使用高级模型
3. 本地模型（如Llama）用于非关键压缩

## 与现有系统集成

### 方式1：替换现有压缩器
```python
# 在memory_manager.py中
if use_llm_compression:
    from .neural_memory_processor import NeuralMemoryProcessor
    self.processor = NeuralMemoryProcessor(...)
else:
    from .async_memory_processor import AsyncMemoryProcessor
    self.processor = AsyncMemoryProcessor(...)
```

### 方式2：混合使用
```python
# 关键消息用LLM，普通消息用规则
if message_importance == "HIGH":
    view = await llm_compress(message)
else:
    view = rule_based_compress(message)
```

## 未来发展

### 1. 专用压缩模型
- 微调专门的压缩模型
- 针对代码、日志、对话优化

### 2. 多模态压缩
- 支持图片、图表的语义压缩
- 代码执行结果的可视化压缩

### 3. 自主学习
- 根据用户反馈优化压缩策略
- 学习项目特定的重要性模式

### 4. 分布式记忆
- 多Agent共享语义记忆
- 跨会话的知识传递

## 结论

连接主义的LLM压缩方法相比传统的符号主义方法，提供了：
- **更智能的信息保留**：基于语义重要性而非规则
- **更好的压缩质量**：生成的摘要更自然、信息更完整
- **更强的适应性**：自动适应不同类型的内容
- **语义搜索能力**：支持基于意图的记忆检索

虽然成本较高，但通过合理的缓存、批处理和模型选择，可以在性能和成本之间找到平衡。