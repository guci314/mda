# BPMN 流程管理（简化版）

## 核心理念
使用BPMN标准化流程管理，但保持实用和简洁。

## 使用原则

### 1. 适用场景
- **复杂多步骤任务**（≥5个步骤）
- **需要并行处理的任务**
- **有复杂分支逻辑的任务**
- **多Agent协作任务**

### 2. 文件管理
在工作目录创建：
- `workflow.json` - 流程定义（JSON格式，更轻量）
- `execution.log` - 执行日志

### 3. 简化的流程定义

```json
{
  "process": "任务名称",
  "created": "时间戳",
  "nodes": [
    {
      "id": "start",
      "type": "start",
      "name": "开始"
    },
    {
      "id": "task1",
      "type": "task",
      "name": "任务描述",
      "status": "pending",
      "implementation": "工具名称"
    },
    {
      "id": "gateway1",
      "type": "exclusive",
      "name": "判断条件",
      "condition": "表达式"
    },
    {
      "id": "end",
      "type": "end",
      "name": "结束"
    }
  ],
  "flows": [
    {"from": "start", "to": "task1"},
    {"from": "task1", "to": "gateway1"},
    {"from": "gateway1", "to": "end", "condition": "success"}
  ]
}
```

## 执行管理

### 状态更新
```json
{
  "nodeId": "task1",
  "status": "running|completed|failed",
  "startTime": "时间戳",
  "endTime": "时间戳",
  "output": "结果摘要"
}
```

### 执行日志格式
```
[时间] 节点ID - 状态 - 描述
[2024-01-20 10:00:00] task1 - running - 开始执行任务1
[2024-01-20 10:00:05] task1 - completed - 成功完成，输出：xxx
```

## 核心元素（精简版）

### 基本节点类型
- `start` - 开始节点
- `end` - 结束节点
- `task` - 任务节点
- `exclusive` - 单选网关（if-else）
- `parallel` - 并行网关

### 任务状态
- `pending` - 待执行
- `running` - 执行中
- `completed` - 已完成
- `failed` - 失败
- `skipped` - 跳过

### 变量支持
- 在process级别定义变量
- 任务可以更新变量（action字段）
- 网关可以基于变量判断
- 支持循环计数器

## 实用示例

### 简单线性流程
```json
{
  "process": "创建计算器",
  "nodes": [
    {"id": "1", "type": "task", "name": "创建类"},
    {"id": "2", "type": "task", "name": "编写测试"},
    {"id": "3", "type": "task", "name": "运行测试"}
  ]
}
```

### 带条件分支
```json
{
  "nodes": [
    {"id": "test", "type": "task", "name": "运行测试"},
    {"id": "check", "type": "exclusive", "name": "测试是否通过"},
    {"id": "fix", "type": "task", "name": "修复代码"},
    {"id": "deploy", "type": "task", "name": "部署"}
  ],
  "flows": [
    {"from": "test", "to": "check"},
    {"from": "check", "to": "fix", "condition": "failed"},
    {"from": "check", "to": "deploy", "condition": "passed"},
    {"from": "fix", "to": "test"}
  ]
}
```

### 带循环控制
```json
{
  "process": "修复测试直到通过",
  "variables": {
    "retryCount": 0,
    "maxRetries": 5
  },
  "nodes": [
    {"id": "test", "type": "task", "name": "运行测试"},
    {"id": "check", "type": "exclusive", "name": "测试是否通过"},
    {"id": "checkRetry", "type": "exclusive", "name": "检查重试次数"},
    {"id": "fix", "type": "task", "name": "修复代码", 
     "action": "retryCount++"},
    {"id": "fail", "type": "end", "name": "放弃修复"},
    {"id": "success", "type": "end", "name": "测试通过"}
  ],
  "flows": [
    {"from": "test", "to": "check"},
    {"from": "check", "to": "success", "condition": "passed"},
    {"from": "check", "to": "checkRetry", "condition": "failed"},
    {"from": "checkRetry", "to": "fix", "condition": "retryCount < maxRetries"},
    {"from": "checkRetry", "to": "fail", "condition": "retryCount >= maxRetries"},
    {"from": "fix", "to": "test"}
  ]
}
```

## 最佳实践

1. **按需使用** - 简单任务不需要BPMN
2. **JSON优先** - 比XML更轻量易处理
3. **增量更新** - 只更新变化的节点状态
4. **日志简洁** - 记录关键信息即可
5. **避免过度建模** - 够用就好

## 适用场景

BPMN流程管理适合：
- **复杂多步骤任务**（≥5个步骤）
- **需要并行处理**的任务
- **复杂条件分支**的流程
- **需要循环重试**的操作
- **多Agent协作**场景
- **需要可视化追踪**的流程

## 核心理念
**实用主义**：BPMN是工具，不是教条。选择最适合的工具完成任务。