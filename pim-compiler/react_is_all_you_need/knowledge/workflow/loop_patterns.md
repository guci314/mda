# 工作流循环模式知识

## 概述

在工作流模板中，循环是通过自然语言和半结构化的方式表达的。Agent需要理解这些模式并在JSON状态中实现相应的循环控制。

## 循环的自然语言表达

### 1. 隐式循环表达

在模板中，循环经常通过自然语言隐式表达：

```markdown
### 步骤名称
**执行内容**:
- 对每个服务器执行部署
- 重试失败的操作，最多3次
- 循环处理直到所有数据验证通过
- 如果失败，则修复并重新测试，直到成功
```

Agent应该识别这些关键词：
- "对每个" / "for each" → foreach循环
- "重试...次" / "retry...times" → for循环
- "直到" / "until" → until循环
- "循环" / "loop" → 需要循环结构
- "如果...则重复" → while循环

### 2. 显式循环定义

在模板中明确定义循环结构：

```markdown
**循环定义**:
```
循环类型: foreach
循环对象: 服务器列表
循环变量: current_server
循环体: 部署步骤

终止条件:
- 所有服务器部署完成
- 或遇到关键错误
```
```

### 3. 条件重试模式

```markdown
**重试策略**:
- 最大重试次数: 3
- 重试间隔: 5秒（指数退避）
- 重试条件: 状态码非200
- 放弃条件: 连续3次超时
```

## JSON实现映射

### 自然语言到JSON的转换规则

#### "对每个X执行Y"
```json
{
  "type": "loop",
  "loop_config": {
    "loop_type": "foreach",
    "items": "${variables.X_list}",
    "loop_variable": "current_X",
    "loop_steps": ["Y_action"]
  }
}
```

#### "重试N次"
```json
{
  "type": "loop",
  "loop_config": {
    "loop_type": "for",
    "start": 0,
    "end": "N",
    "loop_variable": "retry_count",
    "loop_steps": ["retry_action"],
    "break_condition": "${success} == true"
  }
}
```

#### "直到条件满足"
```json
{
  "type": "loop",
  "loop_config": {
    "loop_type": "until",
    "condition": "${condition}",
    "loop_steps": ["action"],
    "max_iterations": 100
  }
}
```

## 循环执行策略

### 1. 批处理循环

当模板提到批处理时：
1. 计算总批次数
2. 初始化批次计数器
3. 对每批执行：
   - 提取批次数据
   - 处理数据
   - 更新进度
   - 检查是否继续

### 2. 重试循环

当模板提到重试时：
1. 设置重试计数器
2. 执行操作
3. 检查结果
4. 如果失败且未达上限：
   - 等待（可能使用退避策略）
   - 递增计数器
   - 重新执行

### 3. 验证循环

当模板提到"验证直到通过"时：
1. 执行验证
2. 如果失败：
   - 识别失败原因
   - 执行修复
   - 重新验证
3. 记录验证次数
4. 设置最大验证次数防止无限循环

## 循环状态管理

### 在workflow_state.json中跟踪循环

```json
{
  "current_step": "batch_processing_loop",
  "loop_states": {
    "batch_loop": {
      "type": "foreach",
      "current_index": 3,
      "total_items": 10,
      "current_item": "batch_3",
      "processed_items": ["batch_1", "batch_2"],
      "failed_items": [],
      "status": "running"
    }
  },
  "variables": {
    "total_processed": 200,
    "current_batch_size": 100,
    "error_count": 2
  }
}
```

### 循环嵌套处理

```json
{
  "loop_states": {
    "outer_loop": {
      "type": "foreach",
      "current_index": 2,
      "inner_loops": {
        "retry_loop": {
          "type": "while",
          "iteration": 1,
          "condition_met": false
        }
      }
    }
  }
}
```

## 最佳实践

### 1. 防止无限循环
- 始终设置 `max_iterations`
- 定义明确的退出条件
- 记录循环执行次数

### 2. 循环性能优化
- 批处理优于单条处理
- 并行执行独立的循环迭代
- 缓存循环不变量

### 3. 错误处理
- 单次迭代失败不应终止整个循环
- 记录失败的迭代以便后续处理
- 提供循环级别的错误恢复机制

### 4. 进度追踪
```json
{
  "loop_progress": {
    "total": 1000,
    "completed": 750,
    "failed": 10,
    "remaining": 240,
    "percentage": 75,
    "estimated_completion": "2024-01-15T14:30:00"
  }
}
```

## 循环模式识别

### 关键词映射表

| 自然语言 | 循环类型 | JSON实现 |
|---------|---------|----------|
| 对每个/for each | foreach | loop_type: "foreach" |
| 重复N次 | for | loop_type: "for" |
| 直到/until | until | loop_type: "until" |
| 当...时/while | while | loop_type: "while" |
| 批处理 | foreach | 对批次的foreach |
| 重试 | for/while | 带break条件的循环 |
| 轮询 | while | 带延迟的while循环 |

### 复合模式

1. **重试并退避**
   - for循环 + 延迟递增
   - 延迟 = base_delay * (2 ^ retry_count)

2. **批处理并发**
   - foreach循环 + parallel执行
   - 每批并行，批间串行

3. **验证-修复-重试**
   - until循环包含：验证→失败→修复→重验证

## 执行指导

当Agent遇到循环相关的任务描述时：

1. **识别循环模式**
   - 扫描关键词
   - 确定循环类型
   - 识别循环对象和条件

2. **初始化循环状态**
   - 在workflow_state.json中创建loop_states
   - 设置循环变量
   - 初始化计数器

3. **执行循环体**
   - 读取当前循环状态
   - 执行循环步骤
   - 更新循环变量
   - 检查继续/终止条件

4. **完成循环**
   - 记录循环结果
   - 清理循环状态
   - 继续下一步骤

## 示例：识别并执行批处理循环

输入（模板描述）：
```markdown
对每个数据批次执行：
- 验证数据质量
- 转换数据格式
- 存储到数据库
如果任何批次失败，记录错误但继续处理
```

输出（JSON执行）：
```json
{
  "steps": [
    {
      "id": "batch_process_loop",
      "type": "loop",
      "loop_config": {
        "loop_type": "foreach",
        "items": "${variables.data_batches}",
        "loop_variable": "current_batch",
        "loop_body": [
          {
            "name": "validate_quality",
            "type": "action"
          },
          {
            "name": "transform_format",
            "type": "action"
          },
          {
            "name": "store_to_db",
            "type": "action",
            "error_handling": "continue"
          }
        ],
        "continue_on_error": true
      }
    }
  ]
}
```

这样，Agent就能正确理解和执行模板中的循环逻辑。