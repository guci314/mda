# ETL数据管道工作流模板

## 模板元信息
```yaml
template_id: data_pipeline_v1
version: 1.0.0
type: etl_pipeline
author: system
created_at: 2024-01-15
tags: [etl, data, pipeline, batch_processing]
description: 通用ETL数据处理管道，支持多数据源和并行处理
```

## 参数定义
```yaml
parameters:
  sources:
    type: array
    required: true
    description: 数据源列表
    example: ["mysql", "mongodb", "redis", "kafka"]
    
  target:
    type: string
    required: true
    description: 目标数据仓库
    example: "data_warehouse"
    
  batch_size:
    type: integer
    required: false
    default: 10000
    description: 批处理大小
    
  error_threshold:
    type: float
    required: false
    default: 0.05
    description: 错误率阈值（0-1）
    
  processing_mode:
    type: string
    required: false
    default: "batch"
    enum: [batch, stream, micro_batch]
    description: 处理模式
    
  schedule:
    type: string
    required: false
    description: 调度时间（cron表达式）
    example: "0 2 * * *"
```

## 工作流步骤

### 1. 数据源连接验证 [parallel]
**描述**: 验证所有数据源的连接性
**并行任务**:
对每个 source 执行:
- 测试数据源连接
- 验证访问权限
- 检查数据源状态
- 获取数据统计信息

**成功条件**: 
- 所有数据源连接成功
- 权限验证通过
- 记录 `variables.source_stats` = {源:记录数}

### 2. 数据提取 [parallel]
**描述**: 从多个数据源并行提取数据
**并行任务**:
根据不同数据源类型执行相应提取逻辑:

**MySQL提取**:
- 执行SQL查询
- 分页读取数据
- 处理大表优化

**MongoDB提取**:
- 执行聚合查询
- 游标批量读取
- 处理嵌套文档

**Redis提取**:
- 扫描键空间
- 批量获取数据
- 处理不同数据类型

**Kafka提取**:
- 消费指定主题
- 处理偏移量
- 批量拉取消息

**成功条件**: 
- 提取记录数 > 0
- 记录 `variables.extracted_count` = 总提取数
- 生成临时文件: `extracted_data_${source}.json`

### 3. 数据质量检查 [action]
**描述**: 验证提取数据的质量
**执行内容**:
- 检查数据完整性（非空字段）
- 验证数据格式（日期、数字格式）
- 检查数据范围（值域验证）
- 识别重复数据
- 统计异常数据

**计算指标**:
- 完整性得分: ${complete_records} / ${total_records}
- 格式正确率: ${valid_format} / ${total_records}
- 重复率: ${duplicate_records} / ${total_records}
- 异常率: ${anomaly_records} / ${total_records}

**成功条件**: 
- 数据质量得分 > 0.95
- 记录 `variables.quality_score` = 质量得分
- 记录 `variables.error_rate` = 错误率

### 4. 错误处理决策 [condition]
**描述**: 根据错误率决定处理策略
**判断逻辑**:
```
error_rate = variables.error_rate

if error_rate > error_threshold:
    if error_rate > 0.2:
        触发告警 → 进入步骤5（数据修复）
        设置 variables.action = "repair"
    else:
        记录警告 → 进入步骤5（数据修复）
        设置 variables.action = "repair_continue"
else:
    正常处理 → 跳过步骤5，进入步骤6
    设置 variables.action = "continue"
```

### 5. 数据修复 [action]
**描述**: 修复识别出的数据问题
**执行内容**:
- 填充缺失值（使用默认值或均值）
- 修正格式错误（日期、数字格式化）
- 去除重复记录
- 标记无法修复的记录

**修复策略**:
- 缺失值: 使用列均值/众数/默认值
- 格式错误: 尝试自动转换，失败则标记
- 重复数据: 保留最新记录
- 异常值: 根据业务规则处理

**成功条件**: 
- 修复后错误率 < error_threshold
- 生成修复报告
- 更新 `variables.repaired_count` = 修复记录数

**跳过条件**: 
- `variables.action` == "continue"

### 6. 数据转换 [parallel]
**描述**: 并行执行数据转换任务
**并行任务**:

**数据清洗**:
- 去除无效字符
- 标准化文本（大小写、空格）
- 处理特殊字符

**格式标准化**:
- 统一日期格式
- 统一数值精度
- 统一编码格式

**业务逻辑转换**:
- 字段映射
- 值转换（代码转名称）
- 单位换算

**衍生指标计算**:
- 计算聚合指标
- 生成时间序列
- 创建分类标签

**成功条件**: 
- 所有转换任务完成
- 生成转换后文件: `transformed_data.json`
- 记录 `variables.transformed_count` = 转换后记录数

### 7. 数据验证 [action]
**描述**: 验证转换后的数据
**执行内容**:
- 对比源和目标记录数
- 验证关键字段完整性
- 检查业务规则符合性
- 抽样对比验证

**验证规则**:
- 记录数一致性: |源-目标| / 源 < 0.01
- 关键字段非空率: > 99%
- 业务规则通过率: > 99%

**成功条件**: 
- 所有验证规则通过
- 生成验证报告

### 8. 数据加载 [action]
**描述**: 将数据加载到目标数据仓库
**执行内容**:
- 建立目标连接
- 创建/更新表结构
- 批量插入数据
- 更新索引

**加载策略**:
- 批量大小: ${batch_size}
- 并发数: 根据目标库性能调整
- 失败重试: 最多3次
- 事务控制: 每批一个事务

**成功条件**: 
- 数据全部加载成功
- 记录 `variables.loaded_count` = 加载记录数
- 无加载错误

### 9. 索引更新 [action]
**描述**: 更新数据仓库索引
**执行内容**:
- 重建必要索引
- 更新统计信息
- 优化表结构
- 刷新物化视图

**成功条件**: 
- 索引更新完成
- 查询性能符合要求

### 10. 报告生成 [action]
**描述**: 生成ETL执行报告
**报告内容**:
- 执行摘要
  - 开始时间: ${start_time}
  - 结束时间: ${end_time}
  - 总耗时: ${duration}
- 数据统计
  - 提取记录数: ${extracted_count}
  - 转换记录数: ${transformed_count}
  - 加载记录数: ${loaded_count}
  - 错误记录数: ${error_count}
- 质量指标
  - 数据质量得分: ${quality_score}
  - 错误率: ${error_rate}
  - 修复率: ${repair_rate}
- 性能指标
  - 提取速率: ${extract_rate} records/s
  - 转换速率: ${transform_rate} records/s
  - 加载速率: ${load_rate} records/s
- 异常记录明细

**输出文件**: 
- `etl_report_${timestamp}.md`
- `error_records_${timestamp}.csv`

## 错误处理策略

### 提取阶段错误
- 连接失败: 重试3次，间隔递增
- 权限错误: 记录并跳过该数据源
- 超时: 分批重试

### 转换阶段错误
- 格式错误: 记录到错误表，继续处理
- 业务规则违反: 根据严重程度决定是否继续

### 加载阶段错误
- 主键冲突: 更新或跳过
- 约束违反: 记录错误，回滚该批次
- 空间不足: 清理后重试

## 成功判定条件

工作流成功的标准:
- ✅ 数据加载完成率 > 99%
- ✅ 错误率 < error_threshold
- ✅ 所有关键步骤执行成功
- ✅ 数据质量验证通过
- ✅ 生成完整报告

## 使用示例

### 基础批处理
```
执行 data_pipeline.md 模板
参数:
- sources: ["mysql", "mongodb"]
- target: "data_warehouse"
- batch_size: 10000
- error_threshold: 0.05
```

### 流式处理
```
执行 data_pipeline.md 模板
参数:
- sources: ["kafka"]
- target: "real_time_db"
- processing_mode: "stream"
- batch_size: 100
```

### 定时调度
```
执行 data_pipeline.md 模板
参数:
- sources: ["mysql", "redis"]
- target: "data_warehouse"
- schedule: "0 2 * * *"  # 每天凌晨2点执行
```

## 监控指标

执行过程中收集的关键指标:
- `pipeline.total_records`: 总处理记录数
- `pipeline.duration`: 总执行时长
- `pipeline.throughput`: 吞吐量（records/s）
- `quality.score`: 数据质量得分
- `quality.error_rate`: 错误率
- `performance.extract_rate`: 提取速率
- `performance.transform_rate`: 转换速率
- `performance.load_rate`: 加载速率