# 工作流文档流转协议

## 核心概念

工作流文档是Agent之间协作的状态控制机制，通过显式的状态转换来防止死循环。

## 工作流文档结构

每个工作流文档包含：
```markdown
# Workflow: [工作流ID]
Status: [pending|in_progress|completed|terminated]
Current_Owner: [当前负责的Agent]
Previous_Owner: [上一个处理的Agent]
Created_At: [创建时间]
Updated_At: [更新时间]

## Task
[任务描述]

## History
- [时间戳] [Agent] [动作] [状态转换]

## Next_Action
[下一步应该做什么]

## Termination_Conditions
- 任务完成
- 超过最大交互次数(默认10次)
- 遇到终止标记
```

## 状态转换规则

1. **pending** → **in_progress**: Agent接受任务
2. **in_progress** → **completed**: Agent完成任务
3. **in_progress** → **pending**: Agent转交给其他Agent
4. **任何状态** → **terminated**: 达到终止条件

## 防止死循环机制

### 1. 交互次数限制
- 每个工作流最多允许10次Agent交互
- 超过次数自动终止

### 2. 重复检测
- 如果连续两次相同的Agent处理，检查是否有实质进展
- 如果没有进展，终止工作流

### 3. 礼貌性回复识别
以下被识别为礼貌性回复，不应触发新的交互：
- "谢谢" / "感谢" / "Thanks"
- "不客气" / "不用谢" / "You're welcome"
- "好的" / "OK" / "收到" / "明白" / "了解"
- "再见" / "拜拜" / "Goodbye"

### 4. 显式终止标记
Agent可以在消息中添加 `[WORKFLOW_END]` 标记来显式终止工作流。

## Agent行为准则

### 检查工作流状态
```python
1. 检查 .workflows/ 目录
2. 找到assigned给自己的pending或in_progress工作流
3. 读取工作流文档
4. 根据状态决定行动
```

### 更新工作流
```python
1. 更新Status字段
2. 添加History记录
3. 更新Current_Owner和Previous_Owner
4. 写入Next_Action
```

### 终止判断
```python
if any([
    interaction_count >= 10,
    message in COURTESY_PHRASES,
    "[WORKFLOW_END]" in message,
    current_owner == previous_owner and no_progress
]):
    status = "terminated"
```

## 示例工作流

### 询问计算问题
```markdown
# Workflow: calc_2plus2_001
Status: pending
Current_Owner: 李四
Previous_Owner: 张三
Created_At: 2024-01-01 10:00:00
Updated_At: 2024-01-01 10:00:01

## Task
计算 2+2 等于几

## History
- 2024-01-01 10:00:00 张三 创建工作流 pending→pending
- 2024-01-01 10:00:01 张三 分配给李四 pending→pending

## Next_Action
李四需要计算并回复结果

## Termination_Conditions
- 李四给出答案后
- 超过10次交互
```

### 代码测试流程
```markdown
# Workflow: code_test_001
Status: in_progress
Current_Owner: 测试员
Previous_Owner: 程序员
Created_At: 2024-01-01 10:00:00
Updated_At: 2024-01-01 10:05:00

## Task
测试calculator.py中的add函数

## History
- 2024-01-01 10:00:00 秘书 创建工作流 pending→pending
- 2024-01-01 10:01:00 程序员 接受任务 pending→in_progress
- 2024-01-01 10:05:00 程序员 完成编码 in_progress→pending
- 2024-01-01 10:05:00 程序员 分配给测试员 pending→in_progress

## Next_Action
测试员执行测试并报告结果

## Termination_Conditions
- 测试完成并报告结果
- 超过10次交互
```

## 实现要点

1. **工作流目录**: `.workflows/` 存放所有工作流文档
2. **命名规范**: `workflow_[类型]_[时间戳].md`
3. **状态检查**: Agent首先检查工作流，而不是inbox
4. **原子操作**: 使用文件锁确保工作流更新的原子性
5. **清理机制**: 定期清理terminated状态的旧工作流