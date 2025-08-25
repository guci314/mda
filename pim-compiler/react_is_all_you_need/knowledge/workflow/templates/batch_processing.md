# 批处理工作流模板（展示循环模式）

## 模板元信息
```yaml
template_id: batch_processing_v1
version: 1.0.0
type: batch_processing
author: system
created_at: 2024-01-15
tags: [batch, loop, iteration, processing]
description: 展示工作流中各种循环模式的批处理模板
```

## 参数定义
```yaml
parameters:
  data_source:
    type: string
    required: true
    description: 数据源路径或标识
    
  batch_size:
    type: integer
    required: false
    default: 100
    description: 每批处理的记录数
    
  max_retries:
    type: integer
    required: false
    default: 3
    description: 失败重试次数
    
  retry_delay_seconds:
    type: integer
    required: false
    default: 5
    description: 重试间隔（秒）
    
  max_error_rate:
    type: float
    required: false
    default: 0.1
    description: 最大容错率
```

## 工作流步骤

### 1. 数据准备 [action]
**描述**: 准备待处理数据
**执行内容**:
- 连接数据源
- 获取总记录数
- 计算批次数量

**输出变量**:
- `variables.total_records`: 总记录数
- `variables.batch_count`: 批次数量 = ceil(total_records / batch_size)
- `variables.current_batch`: 0（初始化）

### 2. 批次处理循环 [loop: foreach]
**描述**: 对每个批次执行处理
**循环定义**:
```
循环类型: foreach
循环对象: 批次列表 [1, 2, ..., batch_count]
循环变量: current_batch
循环体: 步骤3-6

终止条件:
- 所有批次处理完成
- 或错误率超过max_error_rate
```

**循环控制**:
- 每次迭代: `variables.current_batch += 1`
- 继续条件: `current_batch <= batch_count && error_rate < max_error_rate`

### 3. 提取批次数据 [action] (循环体内)
**描述**: 提取当前批次的数据
**执行内容**:
- 计算偏移量: `offset = (current_batch - 1) * batch_size`
- 提取记录: 从offset开始，最多batch_size条
- 验证数据完整性

**成功条件**:
- 成功提取数据
- 记录 `variables.batch_${current_batch}_size` = 实际提取数

### 4. 数据验证与重试循环 [loop: while] (循环体内)
**描述**: 验证数据质量，失败则重试
**循环定义**:
```
循环类型: while
循环条件: 验证未通过 AND 重试次数 < max_retries
循环变量: retry_count
循环体: 数据验证逻辑

具体逻辑:
while (validation_failed && retry_count < max_retries):
    retry_count += 1
    等待 retry_delay_seconds 秒
    重新验证数据
    if 验证通过:
        break
```

**重试策略**:
- 指数退避: 延迟时间 = retry_delay_seconds * (2 ^ retry_count)
- 记录每次重试的原因

### 5. 处理数据 [action] (循环体内)
**描述**: 对验证通过的数据执行业务处理
**执行内容**:
- 数据转换
- 业务逻辑计算
- 结果存储

**错误处理**:
- 单条记录失败不影响整批
- 记录失败记录到 `variables.failed_records`

### 6. 批次完成检查 [condition] (循环体内)
**描述**: 检查是否继续处理下一批
**判断逻辑**:
```
计算当前错误率: error_rate = failed_count / processed_count

if error_rate > max_error_rate:
    记录错误 → 跳出循环（步骤7）
    设置 variables.abort_reason = "错误率过高"
elif current_batch >= batch_count:
    正常完成 → 跳出循环（步骤8）
    设置 variables.completion_status = "success"
else:
    继续下一批 → 返回步骤2
```

### 7. 错误恢复循环 [loop: until]
**描述**: 尝试恢复失败的记录
**循环定义**:
```
循环类型: until
循环条件: 直到(所有失败记录处理完成 OR 放弃恢复)
循环体: 错误恢复逻辑

具体逻辑:
repeat:
    选择一批失败记录
    尝试修复并重新处理
    更新失败列表
until (failed_records.empty() || recovery_attempts > 3)
```

**恢复策略**:
- 每次最多处理10条失败记录
- 使用不同的处理策略
- 3次恢复尝试后放弃

### 8. 结果聚合 [action]
**描述**: 汇总所有批次的处理结果
**执行内容**:
- 统计成功/失败数量
- 计算处理速率
- 生成处理报告

### 9. 通知循环 [loop: for]
**描述**: 向多个接收者发送通知
**循环定义**:
```
循环类型: for
循环范围: for i in range(len(notification_recipients))
循环变量: recipient_index
循环体: 发送通知

具体逻辑:
for recipient_index in range(len(recipients)):
    recipient = recipients[recipient_index]
    发送通知(recipient, 处理结果)
    记录发送状态
```

## 循环模式总结

### 1. ForEach循环（遍历集合）
```yaml
loop_type: foreach
items: ${collection}
variable: current_item
body: [处理步骤]
```

### 2. While循环（条件循环）
```yaml
loop_type: while
condition: ${继续条件}
body: [处理步骤]
max_iterations: 100  # 防止无限循环
```

### 3. Until循环（直到条件满足）
```yaml
loop_type: until
condition: ${终止条件}
body: [处理步骤]
min_iterations: 1  # 至少执行一次
```

### 4. For循环（计数循环）
```yaml
loop_type: for
start: 0
end: ${count}
step: 1
variable: index
body: [处理步骤]
```

### 5. 嵌套循环
```yaml
outer_loop:
  type: foreach
  items: ${batches}
  body:
    inner_loop:
      type: while
      condition: ${需要重试}
      body: [重试逻辑]
```

## 循环控制语句

### Break（跳出循环）
在循环体内，当满足特定条件时：
```
if 错误率 > 阈值:
    设置 variables.break_loop = true
    跳出当前循环
```

### Continue（跳过本次迭代）
在循环体内，跳过当前迭代：
```
if 记录无效:
    设置 variables.skip_current = true
    继续下一次迭代
```

### 循环状态追踪
```json
{
  "loop_states": {
    "batch_loop": {
      "current_iteration": 5,
      "total_iterations": 10,
      "status": "running"
    },
    "retry_loop": {
      "retry_count": 2,
      "max_retries": 3,
      "last_error": "timeout"
    }
  }
}
```

## 成功判定条件

工作流成功的标准：
- ✅ 所有批次处理完成或主动终止
- ✅ 错误率在可接受范围内
- ✅ 关键数据处理成功
- ✅ 生成完整报告

## 使用示例

### 基础批处理
```
执行 batch_processing.md 模板
参数:
- data_source: "customer_data"
- batch_size: 100
- max_retries: 3
```

### 大数据处理
```
执行 batch_processing.md 模板
参数:
- data_source: "big_data_lake"
- batch_size: 10000
- max_error_rate: 0.01
```

## 监控指标

循环相关的关键指标：
- `loop.iteration_count`: 迭代次数
- `loop.average_duration`: 平均迭代时长
- `loop.success_rate`: 循环成功率
- `loop.break_count`: 提前退出次数
- `loop.retry_total`: 总重试次数