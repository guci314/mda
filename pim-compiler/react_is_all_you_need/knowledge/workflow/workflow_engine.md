# 工作流引擎完整知识

## 概述

工作流引擎是一个通用的流程自动化执行系统，通过维护workflow_state.json文件来管理复杂的工作流程。它支持顺序执行、条件分支、并行处理、审批流程等企业级功能。

## 核心概念

### 1. 工作流（Workflow）

工作流是一系列有序或并行的步骤，用于完成特定的业务流程：
- **步骤（Steps）**：工作流的基本执行单元
- **转换（Transitions）**：步骤之间的流转规则
- **状态（State）**：工作流的执行状态

### 2. 有向无环图（DAG）

工作流本质上是一个DAG：
- 节点代表步骤
- 边代表依赖关系
- 无环保证不会死循环

## JSON结构规范

### 完整结构
```json
{
  "workflow_id": "唯一标识",
  "name": "工作流名称",
  "type": "工作流类型",
  "version": "1.0.0",
  "created_at": "创建时间",
  "started_at": "开始时间",
  "completed_at": "完成时间",
  "status": "pending|running|completed|failed|paused|cancelled",
  "current_step": "当前执行步骤ID",
  "variables": {},      // 全局变量
  "steps": [],         // 步骤定义
  "parallel_groups": {}, // 并行组
  "conditions": {},     // 条件定义
  "approvals": {},      // 审批配置
  "hooks": {},         // 钩子函数
  "logs": [],          // 执行日志
  "metrics": {}        // 性能指标
}
```

### 步骤结构
```json
{
  "id": "step_unique_id",
  "name": "步骤名称",
  "description": "步骤描述",
  "type": "action|condition|parallel|approval|loop|subprocess",
  "status": "pending|running|completed|failed|skipped",
  "started_at": "开始时间",
  "completed_at": "完成时间",
  "duration_ms": 1000,
  "retry_count": 0,
  "max_retries": 3,
  "timeout_seconds": 300,
  "dependencies": ["step_id1", "step_id2"],
  "next_steps": ["step_id3"],
  "result": {},
  "error": null,
  "metadata": {}
}
```

## 步骤类型详解

### 1. Action（动作步骤）
执行具体的操作任务：
```json
{
  "type": "action",
  "action_config": {
    "action_type": "http_request|shell_command|database_query|file_operation",
    "parameters": {
      "url": "https://api.example.com",
      "method": "POST",
      "headers": {},
      "body": {}
    }
  }
}
```

### 2. Condition（条件步骤）
根据条件选择执行路径：
```json
{
  "type": "condition",
  "condition_config": {
    "expression": "${variables.status} == 'success' && ${metrics.error_rate} < 0.05",
    "true_branch": ["step_success_path"],
    "false_branch": ["step_failure_path"],
    "evaluation_result": null
  }
}
```

### 3. Parallel（并行步骤）
同时执行多个任务：
```json
{
  "type": "parallel",
  "parallel_config": {
    "group_id": "deploy_group",
    "wait_strategy": "all|any|threshold",
    "threshold": 2,
    "fail_strategy": "fail_fast|continue|compensate"
  }
}
```

### 4. Approval（审批步骤）
需要人工审批的节点：
```json
{
  "type": "approval",
  "approval_config": {
    "approval_id": "manager_approval",
    "approvers": ["user1@example.com", "user2@example.com"],
    "approval_type": "single|multiple|unanimous",
    "timeout_hours": 24,
    "auto_approve": false,
    "escalation_path": ["supervisor@example.com"]
  }
}
```

### 5. Loop（循环步骤）
重复执行一组步骤：
```json
{
  "type": "loop",
  "loop_config": {
    "loop_type": "for|while|foreach|until",
    "condition": "${index} < ${items.length}",
    "max_iterations": 100,
    "loop_steps": ["step_in_loop"],
    "break_condition": "${error_count} > 3",
    "loop_variable": "current_item",
    "items": "${variables.data_batches}"
  }
}
```

#### 循环类型详解

**ForEach循环** - 遍历集合：
```json
{
  "loop_type": "foreach",
  "items": "${variables.batches}",
  "loop_variable": "current_batch",
  "loop_body": {
    "steps": ["process_batch", "validate_batch"]
  }
}
```

**While循环** - 条件循环：
```json
{
  "loop_type": "while", 
  "condition": "${retry_count} < ${max_retries} && ${status} != 'success'",
  "loop_body": {
    "steps": ["attempt_operation", "check_result"]
  },
  "max_iterations": 10
}
```

**Until循环** - 直到满足条件：
```json
{
  "loop_type": "until",
  "condition": "${all_processed} == true || ${timeout_reached} == true",
  "loop_body": {
    "steps": ["process_next", "update_status"]
  },
  "min_iterations": 1
}
```

**For循环** - 计数循环：
```json
{
  "loop_type": "for",
  "start": 0,
  "end": "${batch_count}",
  "step": 1,
  "loop_variable": "batch_index",
  "loop_body": {
    "steps": ["load_batch", "process_batch", "save_results"]
  }
}
```

#### 循环控制

**循环状态管理**：
```json
{
  "loop_state": {
    "current_iteration": 5,
    "total_iterations": 10,
    "loop_variable_value": "batch_5",
    "accumulated_results": [],
    "break_requested": false,
    "continue_requested": false
  }
}
```

**Break和Continue**：
- Break: 设置 `loop_state.break_requested = true` 跳出循环
- Continue: 设置 `loop_state.continue_requested = true` 跳过当前迭代

### 6. Subprocess（子流程）
调用另一个工作流：
```json
{
  "type": "subprocess",
  "subprocess_config": {
    "workflow_id": "sub_workflow_123",
    "input_mapping": {
      "sub_var1": "${variables.main_var1}"
    },
    "output_mapping": {
      "variables.result": "${subprocess.output}"
    },
    "async": false
  }
}
```

## 高级特性

### 1. 变量系统

#### 变量作用域
- **全局变量**：整个工作流可访问
- **步骤变量**：仅当前步骤可访问
- **临时变量**：执行期间的中间变量

#### 变量引用
```javascript
${variables.global_var}           // 全局变量
${steps.step_1.result.data}      // 步骤结果
${env.API_KEY}                   // 环境变量
${functions.now()}               // 内置函数
```

### 2. 条件表达式

支持复杂的条件判断：
```javascript
// 基础比较
${status} == "success"
${count} > 100
${name} != null

// 逻辑运算
${a} && ${b}
${x} || ${y}
!${flag}

// 复合条件
(${env} == "prod" && ${approval} == true) || ${override} == true

// 函数调用
${functions.contains(list, item)}
${functions.regex_match(text, pattern)}
```

### 3. 并行执行策略

#### Wait策略
- **all**: 等待所有任务完成
- **any**: 任一完成即继续
- **threshold**: 达到指定数量即继续

#### 失败策略
- **fail_fast**: 任一失败立即终止
- **continue**: 继续执行其他任务
- **compensate**: 执行补偿逻辑

### 4. 错误处理

#### 重试机制
```json
{
  "retry_policy": {
    "max_attempts": 3,
    "initial_delay_ms": 1000,
    "max_delay_ms": 30000,
    "backoff_multiplier": 2,
    "retry_on": ["timeout", "network_error"],
    "dont_retry_on": ["validation_error"]
  }
}
```

#### 错误补偿
```json
{
  "compensation": {
    "on_failure": ["rollback_step_1", "cleanup_step"],
    "on_timeout": ["notify_admin"],
    "on_cancel": ["save_checkpoint"]
  }
}
```

### 5. 钩子系统

在特定时机执行额外逻辑：
```json
{
  "hooks": {
    "before_workflow": ["validate_input"],
    "after_workflow": ["cleanup_resources"],
    "before_step": ["log_start"],
    "after_step": ["update_metrics"],
    "on_error": ["send_alert"]
  }
}
```

## 执行策略

### 1. 状态机模型

```
         ┌─────────┐
         │ PENDING │
         └────┬────┘
              ↓
         ┌─────────┐
    ┌────┤ RUNNING ├────┐
    ↓    └────┬────┘    ↓
┌────────┐    ↓    ┌────────┐
│ PAUSED │    ↓    │ FAILED │
└────────┘    ↓    └────────┘
         ┌──────────┐
         │COMPLETED │
         └──────────┘
```

### 2. 执行算法

```python
def execute_workflow():
    while workflow.status == "running":
        # 1. 获取可执行步骤
        ready_steps = get_ready_steps()
        
        # 2. 并发执行
        for step in ready_steps:
            execute_step_async(step)
        
        # 3. 等待步骤完成
        wait_for_completion()
        
        # 4. 更新依赖图
        update_dependencies()
        
        # 5. 检查终止条件
        if is_workflow_complete():
            finalize_workflow()
            break
```

### 3. 依赖解析

使用拓扑排序确定执行顺序：
```python
def topological_sort(steps):
    in_degree = calculate_in_degrees(steps)
    queue = [s for s in steps if in_degree[s] == 0]
    result = []
    
    while queue:
        step = queue.pop(0)
        result.append(step)
        
        for next_step in step.next_steps:
            in_degree[next_step] -= 1
            if in_degree[next_step] == 0:
                queue.append(next_step)
    
    return result
```

## 实施模板

### 1. CI/CD部署流程
```json
{
  "type": "deployment",
  "steps": [
    {"type": "action", "name": "代码检查"},
    {"type": "action", "name": "单元测试"},
    {"type": "action", "name": "构建镜像"},
    {"type": "condition", "name": "环境判断"},
    {"type": "approval", "name": "生产审批"},
    {"type": "parallel", "name": "多节点部署"},
    {"type": "action", "name": "健康检查"},
    {"type": "action", "name": "通知"}
  ]
}
```

### 2. 数据ETL管道
```json
{
  "type": "data_pipeline",
  "steps": [
    {"type": "parallel", "name": "数据提取"},
    {"type": "action", "name": "数据验证"},
    {"type": "loop", "name": "批量转换"},
    {"type": "action", "name": "数据加载"},
    {"type": "condition", "name": "质量检查"},
    {"type": "action", "name": "报告生成"}
  ]
}
```

### 3. 事件响应流程
```json
{
  "type": "incident_response",
  "steps": [
    {"type": "action", "name": "事件检测"},
    {"type": "condition", "name": "严重性评估"},
    {"type": "parallel", "name": "立即响应"},
    {"type": "action", "name": "根因分析"},
    {"type": "approval", "name": "修复审批"},
    {"type": "action", "name": "修复执行"},
    {"type": "action", "name": "验证"},
    {"type": "action", "name": "事后总结"}
  ]
}
```

## 监控与可观测性

### 1. 关键指标

```json
{
  "metrics": {
    "total_duration_ms": 45000,
    "steps_completed": 15,
    "steps_failed": 2,
    "steps_skipped": 3,
    "retry_count": 5,
    "parallel_efficiency": 0.85,
    "approval_wait_time_ms": 120000
  }
}
```

### 2. 日志级别

- **DEBUG**: 详细的调试信息
- **INFO**: 正常的执行信息
- **WARNING**: 警告但不影响执行
- **ERROR**: 错误但可恢复
- **CRITICAL**: 严重错误需要终止

### 3. 追踪链路

每个执行都有唯一的trace_id：
```json
{
  "trace_id": "wf-123-abc",
  "span_id": "step-456-def",
  "parent_span_id": "wf-123-abc",
  "tags": {
    "workflow.type": "deployment",
    "environment": "production"
  }
}
```

## 最佳实践

### 1. 设计原则
- **原子性**：每个步骤应该是原子操作
- **幂等性**：重复执行产生相同结果
- **无状态**：步骤之间通过变量传递状态
- **容错性**：考虑各种失败场景

### 2. 性能优化
- 合理使用并行减少总执行时间
- 避免不必要的等待和阻塞
- 使用缓存减少重复计算
- 设置合理的超时时间

### 3. 安全考虑
- 敏感信息使用变量引用
- 审批步骤增加权限验证
- 日志脱敏处理
- 限制最大执行时间

### 4. 可维护性
- 使用清晰的命名规范
- 添加详细的步骤描述
- 记录关键决策理由
- 版本化工作流定义

## 故障排查

### 常见问题

#### 1. 步骤一直处于running状态
- 检查是否有超时设置
- 查看是否有死锁
- 确认依赖是否满足

#### 2. 并行任务执行串行
- 检查并行组配置
- 确认资源是否充足
- 查看是否有互斥锁

#### 3. 条件判断不符合预期
- 打印变量值调试
- 检查表达式语法
- 确认变量作用域

## 扩展能力

### 1. 插件系统
支持自定义步骤类型：
```python
class CustomStep:
    def execute(self, context):
        # 自定义执行逻辑
        return result
```

### 2. 事件驱动
支持事件触发工作流：
```json
{
  "triggers": {
    "webhook": "https://api.example.com/webhook",
    "schedule": "0 0 * * *",
    "event": "file_uploaded"
  }
}
```

### 3. 分布式执行
支持跨节点执行：
```json
{
  "execution": {
    "mode": "distributed",
    "coordinator": "node1",
    "workers": ["node2", "node3"]
  }
}
```

## 工作流模板系统

### 模板加载与实例化

工作流引擎支持从模板文件加载预定义的工作流：

#### 1. 模板存储位置
```
knowledge/workflow/templates/
├── deployment.md       # 部署流程模板
├── data_pipeline.md    # ETL管道模板
└── incident_response.md # 事件响应模板
```

#### 2. 模板引用方式

在任务描述中引用模板（使用绝对路径）：
```
执行 /home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/workflow/templates/deployment.md 模板
参数:
- environment: production
- servers: [srv1, srv2]
- version: v1.2.3
```

或使用相对路径（相对于工作目录）：
```
执行 knowledge/workflow/templates/deployment.md 模板
参数:
- environment: production
- servers: [srv1, srv2]
- version: v1.2.3
```

#### 3. JSON状态中的模板引用

workflow_state.json 应包含模板引用（推荐使用绝对路径）：
```json
{
  "template_ref": "/home/guci/aiProjects/mda/pim-compiler/react_is_all_you_need/knowledge/workflow/templates/deployment.md",
  "template_id": "deployment_workflow_v1",
  "parameters": {
    "environment": "production",
    "servers": ["srv1", "srv2"],
    "version": "v1.2.3"
  },
  "instance_id": "deploy_20240115_001",
  ...
}
```

#### 4. 模板加载执行流程

当任务提到"执行xxx模板"时：
1. 使用 `read_file` 读取模板文件
2. 解析模板中的元信息和参数定义
3. 用提供的参数值替换模板参数
4. 在 workflow_state.json 中记录 `template_ref` 和 `template_id`
5. 根据模板定义的步骤创建实例化的工作流
6. 按照模板逻辑执行工作流

#### 5. 模板覆盖机制

支持在执行时覆盖模板的部分内容：
```
基于 deployment.md 模板
但修改:
- 跳过步骤1（代码检查）
- 步骤8增加额外验证
```

处理覆盖时：
1. 先加载基础模板
2. 应用覆盖规则
3. 记录覆盖内容到 `variables.overrides`

#### 6. 参数验证

执行前验证参数：
- 检查必需参数是否提供
- 验证参数类型是否匹配
- 检查枚举值是否有效
- 应用默认值

### 模板与实例的关系

#### 类型层（模板）- 显式表达
- **格式**: Markdown + YAML
- **位置**: knowledge/workflow/templates/
- **内容**: 步骤定义、条件逻辑、成功条件
- **特点**: 人类可读、版本控制、可重用

#### 实例层（状态）- 显式表达  
- **格式**: JSON
- **位置**: workflow_state.json
- **内容**: 执行状态、变量值、日志
- **特点**: 机器可处理、实时更新、可追踪

#### 关联机制
- 通过 `template_ref` 字段关联模板文件
- 通过 `template_id` 标识模板版本
- 通过 `parameters` 记录实例化参数
- 通过 `instance_id` 唯一标识执行实例

### 最佳实践

1. **模板设计**
   - 保持模板通用性，通过参数实现定制
   - 明确定义参数的类型和约束
   - 提供清晰的步骤描述和成功条件

2. **版本管理**
   - 模板文件纳入版本控制
   - 更新模板时递增版本号
   - 保持向后兼容性

3. **执行追踪**
   - 始终记录使用的模板和版本
   - 保存完整的参数值
   - 记录任何运行时覆盖

## 总结

工作流引擎通过JSON笔记本实现了：
- ✅ 复杂的流程编排
- ✅ 灵活的执行控制
- ✅ 完整的错误处理
- ✅ 丰富的监控能力
- ✅ 模板化的工作流定义
- ✅ 类型与实例的清晰分离

这是企业级自动化的基础设施。