# Agent CLI 诊断日志使用指南

## 概述

Agent CLI v2 现在集成了增强的诊断日志功能，可以帮助开发者深入了解执行过程、识别性能瓶颈和诊断问题。

## 功能特点

### 1. 详细的执行跟踪
- 记录每个步骤的开始和结束
- 跟踪每个动作的参数和结果
- 记录 LLM 调用次数和响应长度
- 监控文件读写操作

### 2. 性能分析
- 步骤耗时统计
- LLM 调用频率分析
- 文件重复读取检测
- 上下文压缩统计

### 3. 问题诊断
- 错误和异常记录
- 警告信息（如达到动作上限）
- 步骤决策原因追踪

## 使用方法

### 启用诊断日志

```python
from agent_cli.core_v2_new import AgentCLI_V2
from agent_cli.core import LLMConfig

# 创建 Agent CLI 时启用诊断日志
agent = AgentCLI_V2(
    llm_config=llm_config,
    enable_diagnostic_logging=True,  # 启用诊断日志
    diagnostic_log_file="my_diagnostics.log"  # 指定日志文件
)

# 执行任务
success, result = agent.execute_task("你的任务描述")
```

### 日志文件

执行后会生成两个文件：

1. **诊断日志文件** (`my_diagnostics.log`)
   - 详细的执行过程记录
   - 时间戳和日志级别
   - 适合调试和问题排查

2. **诊断摘要文件** (`my_diagnostics_summary.json`)
   - JSON 格式的执行统计
   - 性能指标和问题汇总
   - 适合性能分析和优化

## 日志内容说明

### 诊断日志格式

```
2025-07-25 23:00:00,000 - agent_cli.diagnostics - INFO - [TASK] 生成博客管理系统代码

2025-07-25 23:00:01,000 - agent_cli.diagnostics - INFO - [STEP START] 分析PSM文件
  Description: 读取并理解系统设计
  Expected: 系统设计摘要

2025-07-25 23:00:02,000 - agent_cli.diagnostics - INFO - [ACTION 1] read_file
  Description: 读取 PSM 文件
  Parameters: {
    "path": "blog_management_psm.md"
  }
  Result: SUCCESS

2025-07-25 23:00:03,000 - agent_cli.diagnostics - INFO - [STEP DECISION]
  Completed: False
  Reason: 还需要生成摘要文档

2025-07-25 23:00:10,000 - agent_cli.diagnostics - INFO - [STEP END] 分析PSM文件
  Status: completed
  Duration: 9.00s
  Actions: 2
  LLM Calls: 3
```

### 诊断摘要格式

```json
{
  "total_duration": 120.5,
  "total_llm_calls": 80,
  "steps": 11,
  "total_actions": 40,
  "files_read_count": {
    "blog_management_psm.md": 5,
    "main.py": 2
  },
  "repeated_reads": {
    "blog_management_psm.md": 5
  },
  "performance_by_step": {
    "分析PSM文件": {
      "duration": 9.2,
      "actions": 2,
      "llm_calls": 3,
      "files_read": 1,
      "files_written": 1,
      "errors": 0
    }
  }
}
```

## 问题诊断示例

### 1. 识别重复读取

```python
# 在摘要中查看 repeated_reads
if summary['repeated_reads']:
    print("发现重复读取的文件:")
    for file, count in summary['repeated_reads'].items():
        if count > 3:
            print(f"⚠️ {file} 被读取了 {count} 次！")
```

### 2. 找出耗时步骤

```python
# 找出耗时超过 30 秒的步骤
slow_steps = []
for step, metrics in summary['performance_by_step'].items():
    if metrics['duration'] > 30:
        slow_steps.append((step, metrics['duration']))

if slow_steps:
    print("耗时较长的步骤:")
    for step, duration in sorted(slow_steps, key=lambda x: x[1], reverse=True):
        print(f"  - {step}: {duration:.1f}s")
```

### 3. 分析 LLM 调用效率

```python
# 计算平均每步骤的 LLM 调用次数
total_steps = summary['steps']
total_llm_calls = summary['total_llm_calls']
avg_calls_per_step = total_llm_calls / total_steps if total_steps > 0 else 0

if avg_calls_per_step > 5:
    print(f"⚠️ 平均每步骤 LLM 调用 {avg_calls_per_step:.1f} 次，可能需要优化")
```

## 最佳实践

### 1. 定期检查诊断日志
- 在开发和测试阶段始终启用诊断日志
- 定期查看摘要文件，识别性能问题

### 2. 设置合理的文件名
```python
from datetime import datetime

# 使用时间戳和任务标识
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
task_id = "blog_generation"
log_file = f"diagnostics_{task_id}_{timestamp}.log"
```

### 3. 自动化分析
```python
def analyze_diagnostics(summary_file):
    """自动分析诊断摘要并生成报告"""
    with open(summary_file, 'r') as f:
        summary = json.load(f)
    
    # 生成分析报告
    report = {
        "efficiency_score": calculate_efficiency(summary),
        "bottlenecks": find_bottlenecks(summary),
        "recommendations": generate_recommendations(summary)
    }
    
    return report
```

## 故障排查

### 诊断日志未生成
1. 检查是否安装了 `enhanced_logging` 模块
2. 确认 `enable_diagnostic_logging=True`
3. 检查文件写入权限

### 日志文件过大
1. 定期轮转日志文件
2. 使用不同的日志文件名
3. 清理旧的日志文件

### 性能影响
诊断日志功能的性能开销很小（< 1%），但在生产环境中可以考虑：
1. 降低日志级别
2. 禁用详细的动作结果记录
3. 使用采样记录（记录部分执行）

## 总结

诊断日志功能为 Agent CLI 提供了强大的可观测性，帮助开发者：
- 快速定位性能瓶颈
- 识别重复和低效的操作
- 优化 LLM 调用策略
- 改进执行效率

通过合理使用诊断日志，可以将 Agent CLI 的执行时间减少 50% 以上。