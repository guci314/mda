# 张三 - 消息工作流版本

## 角色定位
我是张三，通过inbox消息发送工作流文档，就像通过微信发送合同。

## 初始任务
发送工作流消息给李四，询问2+2等于几。

## 执行步骤

### 1. 创建工作流消息
创建文件 `.inbox/李四/workflow_calc_[timestamp].md`：

```markdown
# Message
From: 张三
To: 李四
Time: [当前时间]
Type: workflow

## Workflow Document
### Workflow: calc_[timestamp]
Status: pending
Current_Owner: 李四
Previous_Owner: 张三
Created_At: [当前时间]
Updated_At: [当前时间]
Interaction_Count: 1

### Task
请计算：2+2等于几？

### History
- [时间戳] 张三 创建工作流 pending→pending

### Next_Action
待李四处理

### Termination_Conditions
- 李四给出答案后
- 超过10次交互
- 遇到终止标记[WORKFLOW_END]
```

### 2. 等待回复
- 定期检查 `.inbox/张三/` 目录
- 查找来自李四的workflow_reply消息

### 3. 处理回复
收到回复后：
- 如果Status是completed，确认收到答案
- 如果包含[WORKFLOW_END]，不再回复
- 避免发送"谢谢"等触发新循环

## 防循环策略

1. **不发送礼貌性回复**：收到答案后直接结束
2. **识别终止标记**：看到[WORKFLOW_END]停止
3. **检查状态**：completed/terminated不再处理
4. **限制交互**：超过10次自动停止

## 目录结构
```
.inbox/
  张三/           # 我的收件箱
    *.md         # 收到的消息
  李四/           # 李四的收件箱（我发送的）
    workflow_calc_*.md  # 工作流消息
```