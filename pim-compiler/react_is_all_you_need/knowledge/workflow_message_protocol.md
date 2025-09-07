# 工作流消息协议

## 核心理念
工作流文档嵌入在inbox消息中传递，就像通过微信发送合同一样。

## 消息格式

### 发送工作流消息
```markdown
# Message
From: 张三
To: 李四
Time: 2025-09-08 10:00:00
Type: workflow

## Workflow Document
### Workflow: calc_001
Status: pending
Current_Owner: 李四
Previous_Owner: 张三
Created_At: 2025-09-08 10:00:00
Updated_At: 2025-09-08 10:00:00
Interaction_Count: 1

### Task
请计算：2+2等于几？

### History
- 2025-09-08 10:00:00 张三 创建工作流 pending→pending

### Next_Action
待李四处理

### Termination_Conditions
- 李四给出答案后
- 超过10次交互
- 遇到终止标记[WORKFLOW_END]
```

### 回复工作流消息
```markdown
# Message
From: 李四
To: 张三
Time: 2025-09-08 10:01:00
Type: workflow_reply

## Workflow Document
### Workflow: calc_001
Status: completed
Current_Owner: 李四
Previous_Owner: 张三
Created_At: 2025-09-08 10:00:00
Updated_At: 2025-09-08 10:01:00
Interaction_Count: 2

### Task
请计算：2+2等于几？

### History
- 2025-09-08 10:00:00 张三 创建工作流 pending→pending
- 2025-09-08 10:01:00 李四 完成计算 pending→completed

### Next_Action
任务已完成，答案是4

### Termination_Conditions
- 李四给出答案后 ✓
- 超过10次交互
- 遇到终止标记[WORKFLOW_END]

## Answer
2+2=4

[WORKFLOW_END]
```

## 防死循环机制

### 1. 消息类型识别
- `workflow`: 新工作流或更新
- `workflow_reply`: 工作流回复
- `normal`: 普通消息（不触发工作流）

### 2. 终止条件
- Status为completed或terminated
- 包含[WORKFLOW_END]标记
- Interaction_Count >= 10
- 礼貌用语自动识别

### 3. 礼貌用语处理
如果消息主体是以下内容，不创建新工作流：
- "谢谢"、"感谢"
- "不客气"、"不用谢"
- "好的"、"收到"、"明白"
- "再见"、"拜拜"

## Agent处理流程

### 张三（发起方）
1. 创建工作流文档
2. 嵌入消息发送到李四的inbox
3. 等待回复
4. 收到completed状态不再回复

### 李四（处理方）
1. 检查inbox中的workflow类型消息
2. 读取嵌入的工作流文档
3. 执行任务
4. 更新工作流状态
5. 将更新后的文档嵌入回复消息
6. 添加[WORKFLOW_END]防止循环

## 实现优势

1. **自然直观**：像发微信一样发送"合同"
2. **状态清晰**：每条消息都包含完整状态
3. **防止循环**：通过状态和标记控制
4. **可追溯**：完整历史在消息中
5. **分布式**：无需中心化工作流目录