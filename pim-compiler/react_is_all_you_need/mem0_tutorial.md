# Mem0 框架教程：为AI Agent添加记忆功能

## 概述

Mem0 是一个开源的AI Agent记忆层框架，它允许AI助手和Agent记住过去的交互、存储用户偏好，并实现个性化的AI体验。Mem0 支持多种记忆类型，包括工作记忆、事实记忆、情节记忆和语义记忆。

## 安装

### 使用 pip 安装

```bash
pip install mem0ai
```

### 使用 npm 安装（如果需要前端集成）

```bash
npm install mem0ai
```

## 快速开始

### 1. 获取 API 密钥

访问 [Mem0 平台](https://app.mem0.ai/) 注册账户并获取 API 密钥。

### 2. 初始化客户端

```python
import os
from mem0 import Memory

# 设置 API 密钥
os.environ["MEM0_API_KEY"] = "your_api_key_here"

# 初始化记忆客户端
memory = Memory()
```

### 3. 添加记忆

```python
# 添加用户偏好
memory.add("我喜欢科幻小说", user_id="user_123", metadata={"category": "preference"})

# 添加事实信息
memory.add("用户的生日是1990年5月15日", user_id="user_123", metadata={"type": "fact"})
```

### 4. 检索记忆

```python
# 检索相关记忆
related_memories = memory.search("用户喜欢什么类型的书？", user_id="user_123")
print(related_memories)
```

## 核心功能

### 记忆类型

Mem0 支持四种类型的记忆：

1. **工作记忆 (Working Memory)**：短期会话意识
2. **事实记忆 (Factual Memory)**：长期结构化知识（如偏好、设置）
3. **情节记忆 (Episodic Memory)**：记录特定过去的对话
4. **语义记忆 (Semantic Memory)**：随着时间构建一般知识

### 基本操作

#### 添加记忆

```python
memory.add(
    text="用户最近购买了MacBook Pro",
    user_id="user_123",
    metadata={"timestamp": "2024-01-15", "category": "purchase"}
)
```

#### 搜索记忆

```python
results = memory.search(
    query="用户购买了什么电子产品？",
    user_id="user_123",
    limit=5
)
```

#### 更新记忆

```python
memory.update(
    memory_id="mem_123",
    text="用户更新了邮箱地址为 new_email@example.com"
)
```

#### 删除记忆

```python
memory.delete(memory_id="mem_123")
```

## 高级功能

### 自定义存储后端

Mem0 支持多种存储后端：

```python
from mem0 import Memory

# 使用 Redis 作为存储
config = {
    "vector_store": {
        "provider": "redis",
        "config": {
            "host": "localhost",
            "port": 6379,
            "password": "your_password"
        }
    }
}

memory = Memory.from_config(config)
```

支持的后端包括：Redis、Pinecone、Qdrant、Weaviate、Elasticsearch、Postgres 等。

### 与 LLM 集成

```python
from mem0 import Memory
from openai import OpenAI

# 初始化
memory = Memory()
client = OpenAI()

def chat_with_memory(user_input, user_id):
    # 检索相关记忆
    memories = memory.search(user_input, user_id=user_id)
    
    # 构建上下文
    context = "\n".join([mem["text"] for mem in memories])
    
    # 生成响应
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"用户上下文：{context}"},
            {"role": "user", "content": user_input}
        ]
    )
    
    # 保存新记忆
    memory.add(user_input, user_id=user_id, metadata={"type": "conversation"})
    memory.add(response.choices[0].message.content, user_id=user_id, metadata={"type": "response"})
    
    return response.choices[0].message.content
```

### REST API 使用

Mem0 提供 REST API 服务：

```bash
# 启动 REST API 服务器
mem0 server

# 或者使用 Docker
docker run -p 8000:8000 mem0ai/mem0
```

API 端点示例：

```bash
# 添加记忆
curl -X POST "http://localhost:8000/memories/" \
     -H "Content-Type: application/json" \
     -d '{
       "text": "用户喜欢咖啡",
       "user_id": "user_123"
     }'

# 搜索记忆
curl "http://localhost:8000/memories/search/?query=用户喜欢什么饮料&user_id=user_123"
```

## 实际应用示例

### 构建有记忆的聊天机器人

```python
class MemoryChatbot:
    def __init__(self):
        self.memory = Memory()
        self.client = OpenAI()
    
    def chat(self, user_input, user_id):
        # 检索记忆
        memories = self.memory.search(user_input, user_id=user_id, limit=3)
        
        # 构建提示
        context = "用户历史信息：\n" + "\n".join([m["text"] for m in memories])
        prompt = f"{context}\n\n用户：{user_input}\n助手："
        
        # 生成响应
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}]
        )
        
        reply = response.choices[0].message.content
        
        # 保存对话到记忆
        self.memory.add(f"用户：{user_input}", user_id=user_id, metadata={"type": "user_input"})
        self.memory.add(f"助手：{reply}", user_id=user_id, metadata={"type": "assistant_response"})
        
        return reply

# 使用示例
bot = MemoryChatbot()
response = bot.chat("我喜欢科幻小说", "user_123")
print(response)
```

## 最佳实践

1. **用户隔离**：始终使用 `user_id` 参数确保记忆隔离
2. **元数据丰富**：添加有意义的元数据以提高检索准确性
3. **定期清理**：删除过时的或不相关的记忆
4. **性能监控**：监控记忆检索的延迟和准确性
5. **隐私保护**：确保用户数据的安全存储和合规

## 故障排除

### 常见问题

1. **API 密钥错误**
   - 确保正确设置 `MEM0_API_KEY` 环境变量
   - 检查密钥是否有效

2. **连接超时**
   - 检查网络连接
   - 考虑使用本地部署的 Mem0

3. **记忆检索不准确**
   - 尝试调整搜索查询
   - 添加更多元数据
   - 考虑使用不同的向量存储

### 获取帮助

- [官方文档](https://docs.mem0.ai/)
- [GitHub 仓库](https://github.com/mem0ai/mem0)
- [Discord 社区](https://discord.gg/mem0)

## 结论

Mem0 提供了强大的记忆管理能力，使AI Agent能够提供更加个性化和连贯的交互。通过这个教程，你应该能够开始使用 Mem0 为你的AI应用添加记忆功能。

记住，记忆是AI Agent从"无状态"到"有状态"的关键一步，它可以显著提升用户体验和AI的实用性。