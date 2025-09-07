# 异步Agent协议

## 核心原则：只有inbox，没有outbox

每个Agent只有一个inbox，所有消息都发到接收者的inbox。

## 每轮检查inbox

在每个思考轮次，首先检查是否有新消息：

```python
# 检查inbox目录
inbox_path = f".inbox/{agent_name}/"
if exists(inbox_path):
    messages = list_files(inbox_path, "*.md")
    if messages:
        # 读取第一个消息
        message = read_file(messages[0])
        # 提取发送者
        sender = extract_sender_from_message(message)
        # 删除已读消息
        delete_file(messages[0])
        # 执行消息中的任务
        result = execute_task(message)
        
        # 如果需要回复，发到sender的inbox
        if sender and needs_reply(message):
            write_file(
                f".inbox/{sender}/reply_{timestamp}.md",
                f"From: {agent_name}\nTo: {sender}\n\nResult: {result}"
            )
```

## 消息格式

每个消息必须包含sender信息：

```markdown
# Message

From: project_manager    # 发送者（重要！）
To: coder_agent
Time: 2025-01-09 10:00
ID: msg_12345            # 可选：消息ID用于追踪

## Task
实现TODO类

## Context
这是项目的第一步
```

## 发送消息

```python
# 发送消息（总是发到接收者的inbox）
write_file(
    f".inbox/coder_agent/msg_{timestamp}.md",
    f"""From: {my_name}
To: coder_agent
Time: {now}

Task: 实现TODO类
"""
)
```

## 回复消息

```python
# 回复消息（发到原发送者的inbox）
if sender:
    write_file(
        f".inbox/{sender}/reply_{timestamp}.md",
        f"""From: {my_name}
To: {sender}
Re: {original_message_id}

Result: 任务已完成，代码在todo_app.py
"""
    )
```

## 广播消息

向多个Agent发送相同消息：

```python
agents = ["coder_agent", "tester_agent", "doc_agent"]
for agent in agents:
    write_file(
        f".inbox/{agent}/broadcast_{timestamp}.md",
        f"""From: project_manager
To: {agent}
Type: broadcast

Notice: 项目启动，请准备
"""
    )
```

## 重要：没有outbox！

- ❌ 不要创建outbox目录
- ❌ 不要写入.outbox/
- ✅ 所有消息都发到接收者的.inbox/
- ✅ 回复也发到原发送者的.inbox/