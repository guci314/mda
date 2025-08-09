# 执行策略和最佳实践

## 概述

本文档总结了使用React Agent执行Sequential Thinking和工作流引擎的策略、技巧和最佳实践。这些经验来自实际的实施和测试。

## 核心执行原则

### 1. 知识驱动原则

**原则**：Agent的行为应该由知识文件驱动，而不是外部程序控制。

```markdown
# ✅ 正确：知识文件中
你必须完成8个思考步骤：
1. 读取当前状态
2. 如果未完成，添加下一个thought
3. 重复直到完成

# ❌ 错误：Python代码中
for i in range(8):
    agent.execute(f"添加第{i}个thought")
```

### 2. 自主循环原则

**原则**：Agent应该自主执行循环，不依赖外部控制。

```python
# Agent的思维模式
while not task_completed():
    state = read_current_state()
    next_action = determine_next_action(state)
    execute_action(next_action)
    update_state()
```

### 3. 递增完成原则

**原则**：不要试图一次性完成所有任务，而是递增式推进。

```json
// 第一次执行
{
  "progress": 1,
  "total": 8,
  "status": "in_progress"
}

// 第二次执行
{
  "progress": 2,
  "total": 8,
  "status": "in_progress"
}

// ... 直到完成
```

## 模型选择策略

### 1. 模型能力评估

| 模型 | Sequential Thinking | 工作流引擎 | 推荐度 |
|-----|-------------------|-----------|--------|
| **Gemini 2.5 Pro** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 强烈推荐 |
| **DeepSeek Reasoner** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 推荐 |
| **Claude 3.5 Sonnet** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 推荐 |
| **GPT-4** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 推荐 |
| **Kimi k2-turbo** | ⭐⭐ | ⭐⭐ | 不推荐 |

### 2. 选择考虑因素

#### 任务复杂度
- **简单任务**（<5步）：大多数模型都能完成
- **中等任务**（5-10步）：需要较强的指令遵循能力
- **复杂任务**（>10步）：需要顶级模型

#### 性能要求
- **实时响应**：选择快速模型（Gemini Flash）
- **批处理**：可以选择更强但较慢的模型
- **成本敏感**：考虑性价比

#### 特殊需求
- **需要推理**：DeepSeek Reasoner、o1模型
- **需要创造性**：Claude、GPT-4
- **需要稳定性**：Gemini Pro

## JSON操作策略

### 1. 安全操作模式

**核心规则：永远不要使用search_replace操作JSON！**

#### ✅ 正确方法
```python
def safe_json_update(file_path, updates):
    # 1. 读取完整JSON
    data = json.loads(read_file(file_path))
    
    # 2. 内存中修改
    for key, value in updates.items():
        data[key] = value
    
    # 3. 验证JSON有效性
    json_str = json.dumps(data, indent=2)
    
    # 4. 写入完整文件
    write_file(file_path, json_str)
```

#### ❌ 危险方法
```python
# 永远不要这样做！
search_replace(file, '"status": "pending"', '"status": "running"')
# 风险：可能匹配到错误的位置，破坏JSON结构
```

### 2. 大文件处理

对于大型JSON文件（>10MB）：

```python
# 分片策略
{
  "metadata": {
    "total_parts": 3,
    "current_part": 1
  },
  "data_part_1": [...],
  "reference_to_part_2": "data_part_2.json",
  "reference_to_part_3": "data_part_3.json"
}
```

### 3. 并发访问

处理并发访问问题：

```json
{
  "lock": {
    "acquired_by": "agent_1",
    "acquired_at": "2024-01-01T10:00:00Z",
    "expires_at": "2024-01-01T10:05:00Z"
  },
  "version": 123,
  "last_modified_by": "agent_1"
}
```

## 错误处理策略

### 1. 重试机制

```python
def execute_with_retry(action, max_attempts=3):
    for attempt in range(max_attempts):
        try:
            result = action()
            return result
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            wait_time = 2 ** attempt  # 指数退避
            time.sleep(wait_time)
```

### 2. 检查点机制

定期保存检查点：

```json
{
  "checkpoints": [
    {
      "id": "checkpoint_1",
      "timestamp": "10:00:00",
      "state": {...},
      "can_rollback": true
    }
  ]
}
```

### 3. 优雅降级

```json
{
  "fallback_strategies": [
    {"condition": "primary_failed", "action": "use_backup"},
    {"condition": "backup_failed", "action": "use_cache"},
    {"condition": "cache_failed", "action": "return_default"}
  ]
}
```

## 性能优化策略

### 1. 批处理

减少IO操作：
```python
# ❌ 低效：多次读写
for item in items:
    data = read_file("data.json")
    data["items"].append(item)
    write_file("data.json", data)

# ✅ 高效：批量操作
data = read_file("data.json")
for item in items:
    data["items"].append(item)
write_file("data.json", data)
```

### 2. 缓存策略

```json
{
  "cache": {
    "enabled": true,
    "ttl_seconds": 300,
    "max_size_mb": 100,
    "strategy": "LRU"
  }
}
```

### 3. 异步执行

```json
{
  "async_tasks": [
    {"id": 1, "status": "running", "async": true},
    {"id": 2, "status": "running", "async": true},
    {"id": 3, "status": "waiting", "depends_on": [1, 2]}
  ]
}
```

## 调试策略

### 1. 详细日志

```json
{
  "debug": {
    "enabled": true,
    "level": "DEBUG",
    "include_timestamps": true,
    "include_stack_trace": true
  },
  "logs": [
    {
      "timestamp": "10:00:00.123",
      "level": "DEBUG",
      "message": "Entering function X",
      "context": {
        "input": {...},
        "state": {...}
      }
    }
  ]
}
```

### 2. 状态快照

```json
{
  "snapshots": [
    {
      "timestamp": "before_action",
      "state": {...}
    },
    {
      "timestamp": "after_action",
      "state": {...},
      "diff": {...}
    }
  ]
}
```

### 3. 断言检查

```json
{
  "assertions": [
    {
      "condition": "thoughts.length >= current_thought",
      "message": "Thoughts array inconsistent with current_thought"
    },
    {
      "condition": "status in ['pending', 'running', 'completed']",
      "message": "Invalid status value"
    }
  ]
}
```

## 知识文件设计

### 1. 结构化组织

```markdown
# 主标题

## 核心概念
- 概念解释
- 原理说明

## 执行步骤
1. 明确的步骤
2. 具体的操作

## 示例模板
```json
{具体的JSON示例}
```

## 检查清单
- [ ] 检查项1
- [ ] 检查项2
```

### 2. 明确的指令

```markdown
# ✅ 好的指令
你必须完成以下步骤：
1. 读取thought_chain.json
2. 如果thoughts数量 < 8，添加下一个thought
3. 重复直到达到8个thoughts
4. 设置status为completed

# ❌ 模糊的指令
尝试完成思考链的构建，适当添加一些thoughts。
```

### 3. 条件和分支

```markdown
## 决策树
如果 environment == "production":
    - 执行审批流程
    - 等待批准
    - 继续部署
否则：
    - 跳过审批
    - 直接部署
```

## 测试策略

### 1. 单元测试

测试单个步骤：
```json
{
  "test_cases": [
    {
      "name": "test_add_thought",
      "input": {"current_thought": 2},
      "expected": {"current_thought": 3},
      "actual": null,
      "passed": null
    }
  ]
}
```

### 2. 集成测试

测试完整流程：
```json
{
  "integration_test": {
    "scenario": "complete_workflow",
    "steps": ["init", "process", "complete"],
    "expected_duration_ms": 5000,
    "expected_final_state": "completed"
  }
}
```

### 3. 压力测试

```json
{
  "stress_test": {
    "concurrent_workflows": 10,
    "total_steps": 1000,
    "max_duration_ms": 60000,
    "success_rate_threshold": 0.95
  }
}
```

## 部署策略

### 1. 环境配置

```json
{
  "environments": {
    "development": {
      "llm_model": "gemini-flash",
      "timeout_ms": 10000,
      "debug": true
    },
    "production": {
      "llm_model": "gemini-pro",
      "timeout_ms": 5000,
      "debug": false
    }
  }
}
```

### 2. 版本管理

```json
{
  "version": {
    "current": "1.2.3",
    "minimum_compatible": "1.0.0",
    "deprecation_warnings": [
      "Field 'old_field' will be removed in 2.0.0"
    ]
  }
}
```

### 3. 监控指标

```json
{
  "monitoring": {
    "metrics": [
      {"name": "completion_rate", "value": 0.98},
      {"name": "average_duration_ms", "value": 3500},
      {"name": "error_rate", "value": 0.02}
    ],
    "alerts": [
      {"condition": "error_rate > 0.05", "severity": "warning"},
      {"condition": "error_rate > 0.1", "severity": "critical"}
    ]
  }
}
```

## 安全最佳实践

### 1. 输入验证

```python
def validate_input(data):
    # 类型检查
    assert isinstance(data, dict)
    
    # 必需字段
    required = ["id", "type", "status"]
    for field in required:
        assert field in data
    
    # 值域检查
    assert data["status"] in ["pending", "running", "completed"]
    
    # 大小限制
    assert len(json.dumps(data)) < 1000000  # 1MB
```

### 2. 权限控制

```json
{
  "permissions": {
    "read": ["agent_*", "user_admin"],
    "write": ["agent_executor", "user_admin"],
    "delete": ["user_admin"]
  }
}
```

### 3. 审计追踪

```json
{
  "audit": {
    "enabled": true,
    "retention_days": 90,
    "events": [
      {
        "timestamp": "2024-01-01T10:00:00Z",
        "actor": "agent_1",
        "action": "update_status",
        "details": {...}
      }
    ]
  }
}
```

## 故障恢复

### 1. 自动恢复

```json
{
  "recovery": {
    "auto_recovery": true,
    "max_recovery_attempts": 3,
    "recovery_strategies": [
      "restore_from_checkpoint",
      "retry_failed_step",
      "skip_and_continue"
    ]
  }
}
```

### 2. 手动干预

```json
{
  "manual_intervention": {
    "required": true,
    "reason": "Critical error detected",
    "suggested_actions": [
      "Review error logs",
      "Check system resources",
      "Contact support"
    ]
  }
}
```

## 总结

成功执行的关键：
1. **选择合适的模型**（推荐Gemini 2.5 Pro）
2. **遵循JSON操作规范**（完整读写）
3. **实施错误处理**（重试、检查点）
4. **优化性能**（批处理、缓存）
5. **详细的知识文件**（明确、结构化）
6. **充分的测试**（单元、集成、压力）
7. **安全第一**（验证、权限、审计）

记住：**知识驱动，自主执行，递增完成**。