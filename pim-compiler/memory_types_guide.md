# ReactAgent Memory Types 完整指南

## 可用的 memory_type 选项

### 1. `"buffer"` - 完整缓冲记忆
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="buffer"
)
```
- **特点**：保存所有对话历史，不做任何压缩
- **优点**：信息完整，不丢失任何细节
- **缺点**：Token消耗快速增长，可能超限
- **适用**：短期任务（<10轮对话）
- **存储**：内存

### 2. `"window"` - 滑动窗口记忆
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="window",
    window_size=10  # 保留最近10轮对话
)
```
- **特点**：只保留最近N轮对话
- **优点**：Token使用可控，性能稳定
- **缺点**：丢失早期上下文
- **适用**：中等长度任务
- **存储**：内存

### 3. `"summary"` - 摘要记忆
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="summary"
)
```
- **特点**：将历史对话压缩成摘要
- **优点**：极大减少Token使用
- **缺点**：可能丢失重要细节，生成摘要耗时
- **适用**：超长对话场景
- **存储**：内存

### 4. `"summary_buffer"` - 摘要缓冲混合
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="summary_buffer",
    max_token_limit=2000  # Token阈值
)
```
- **特点**：保留最近对话原文，早期对话转为摘要
- **优点**：平衡细节和效率
- **缺点**：实现复杂，需要调优参数
- **适用**：生产环境的长期项目
- **存储**：内存

### 5. `"file"` - 文件持久化
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="file",
    memory_file="./memory/project_x.json"
)
```
- **特点**：将对话历史保存到JSON文件
- **优点**：持久化存储，可恢复会话
- **缺点**：文件I/O开销，并发需要锁
- **适用**：需要断点续传的项目
- **存储**：文件系统

### 6. `"sqlite"` - SQLite数据库（推荐）
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="sqlite",
    session_id="project_123",
    db_path="./memory.db"
)
```
- **特点**：使用SQLite数据库存储
- **优点**：可靠持久化，支持查询，多会话管理
- **缺点**：需要数据库管理
- **适用**：专业项目，团队协作
- **存储**：SQLite数据库

### 7. `"redis"` - Redis缓存
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="redis",
    redis_url="redis://localhost:6379",
    session_ttl=86400  # 24小时过期
)
```
- **特点**：使用Redis存储，支持分布式
- **优点**：高性能，支持集群，自动过期
- **缺点**：需要Redis服务器
- **适用**：分布式系统，高并发
- **存储**：Redis

### 8. `"vector"` - 向量数据库记忆
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="vector",
    vector_store="chroma",
    embedding_model="text-embedding-ada-002"
)
```
- **特点**：将对话转为向量存储，支持语义搜索
- **优点**：智能检索相关记忆
- **缺点**：实现复杂，需要嵌入模型
- **适用**：需要智能记忆检索的场景
- **存储**：向量数据库

### 9. `"hybrid"` - 混合记忆
```python
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="hybrid",
    short_term="window",      # 短期记忆用窗口
    long_term="sqlite",       # 长期记忆用数据库
    checkpoint="file"         # 检查点用文件
)
```
- **特点**：组合多种记忆类型
- **优点**：灵活配置，最优性能
- **缺点**：配置复杂
- **适用**：复杂的生产环境
- **存储**：混合

### 10. `"none"` 或 `False` - 无记忆
```python
# 方式1
generator = ReactAgentGenerator(
    enable_memory=False
)

# 方式2
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="none"
)
```
- **特点**：不保存任何历史
- **优点**：最简单快速
- **缺点**：无连续性
- **适用**：一次性任务
- **存储**：无

## 配置示例

### 开发环境配置
```python
# 快速原型
config = {
    "enable_memory": True,
    "memory_type": "window",
    "window_size": 5
}

# 调试项目
config = {
    "enable_memory": True,
    "memory_type": "file",
    "memory_file": "./debug_history.json"
}
```

### 生产环境配置
```python
# 标准项目
config = {
    "enable_memory": True,
    "memory_type": "sqlite",
    "db_path": "./project_memory.db",
    "session_id": f"project_{project_id}",
    "max_messages": 1000
}

# 分布式系统
config = {
    "enable_memory": True,
    "memory_type": "redis",
    "redis_url": os.getenv("REDIS_URL"),
    "session_prefix": "react_agent:",
    "session_ttl": 3600 * 24 * 7  # 7天
}
```

### 高级配置
```python
# 智能记忆系统
config = {
    "enable_memory": True,
    "memory_type": "hybrid",
    "config": {
        "short_term": {
            "type": "window",
            "size": 10
        },
        "long_term": {
            "type": "vector",
            "store": "chroma",
            "collection": "project_memory"
        },
        "checkpoint": {
            "type": "sqlite",
            "auto_checkpoint": True,
            "checkpoint_interval": 10  # 每10轮对话
        }
    }
}
```

## 选择决策树

```
需要记忆吗？
├─ 否 → memory_type="none"
└─ 是
   ├─ 需要持久化吗？
   │  ├─ 否
   │  │  ├─ 对话很短？ → "buffer"
   │  │  ├─ 对话中等？ → "window"
   │  │  └─ 对话很长？ → "summary_buffer"
   │  └─ 是
   │     ├─ 单机使用？
   │     │  ├─ 简单需求？ → "file"
   │     │  └─ 专业需求？ → "sqlite" ⭐
   │     └─ 分布式？
   │        ├─ 需要过期？ → "redis"
   │        └─ 需要智能检索？ → "vector"
   └─ 需要多种能力？ → "hybrid"
```

## 性能对比

| 类型 | 启动时间 | Token开销 | 存储需求 | 并发性 | 持久化 |
|------|---------|-----------|----------|--------|--------|
| none | 0ms | 0 | 0 | ⭐⭐⭐⭐⭐ | ❌ |
| buffer | 1ms | 高 | 内存 | ⭐⭐⭐ | ❌ |
| window | 1ms | 中 | 内存 | ⭐⭐⭐ | ❌ |
| summary | 100ms | 低 | 内存 | ⭐⭐⭐ | ❌ |
| summary_buffer | 50ms | 中 | 内存 | ⭐⭐⭐ | ❌ |
| file | 10ms | 高 | 磁盘 | ⭐ | ✅ |
| sqlite | 20ms | 高 | 磁盘 | ⭐⭐ | ✅ |
| redis | 5ms | 高 | 内存 | ⭐⭐⭐⭐ | ✅ |
| vector | 200ms | 中 | 混合 | ⭐⭐⭐ | ✅ |
| hybrid | 100ms | 可配置 | 混合 | ⭐⭐ | ✅ |

## 最佳实践建议

### 对于你的后台异步场景

**推荐配置**：
```python
# 主力配置 - SQLite
generator = ReactAgentGenerator(
    enable_memory=True,
    memory_type="sqlite",
    session_id=task_id,
    db_path="./memory/projects.db",
    # 可选的高级配置
    max_messages=1000,          # 最多保存1000条消息
    compress_after=100,         # 100条后开始压缩
    auto_checkpoint=True,       # 自动创建检查点
    checkpoint_interval=20      # 每20轮创建检查点
)
```

**备选配置**：
1. **快速测试**：`memory_type="window"`
2. **分布式部署**：`memory_type="redis"`
3. **智能系统**：`memory_type="vector"`
4. **极简需求**：`memory_type="none"`

这样可以在不同场景下灵活选择最合适的记忆方案。