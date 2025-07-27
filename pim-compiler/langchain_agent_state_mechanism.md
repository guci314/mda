# LangChain React Agent 状态维护机制详解

## 核心概念：Agent Scratchpad

React Agent 的状态维护主要通过 **`agent_scratchpad`** 实现，这是一个动态更新的思考过程记录。

## 1. Agent Scratchpad 工作原理

```python
# 在 prompt 模板中
prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")  # 关键！
])
```

### 执行流程
```
用户输入 → Agent 思考 → 调用工具 → 记录结果 → 继续思考
         ↑                                      ↓
         ←←←←←← agent_scratchpad 更新 ←←←←←←←←←
```

## 2. Scratchpad 内容示例

```python
# 第一轮
agent_scratchpad = [
    AIMessage("我需要创建一个用户模型，让我先创建目录结构"),
    ToolMessage(tool="create_directory", content="Created: models/"),
    AIMessage("目录创建成功，现在创建用户模型文件"),
    ToolMessage(tool="write_file", content="Created: models/user.py")
]

# 第二轮（累积）
agent_scratchpad = [
    # ... 之前的内容 ...
    AIMessage("用户模型创建完成，现在需要创建API路由"),
    ToolMessage(tool="create_directory", content="Created: routers/"),
    AIMessage("继续创建路由文件...")
]
```

## 3. AgentExecutor 的状态管理

```python
class AgentExecutor:
    def __init__(self, agent, tools, memory=None, ...):
        self.agent = agent
        self.tools = tools
        self.memory = memory  # 可选的长期记忆
        
    def __call__(self, inputs):
        # 初始化 intermediate_steps
        intermediate_steps = []
        
        # 主循环
        for i in range(max_iterations):
            # 1. 准备输入
            agent_inputs = {
                "input": inputs["input"],
                "agent_scratchpad": format_to_messages(intermediate_steps)
            }
            
            # 2. 如果有记忆，添加历史
            if self.memory:
                agent_inputs["chat_history"] = self.memory.chat_memory.messages
            
            # 3. Agent 决策
            output = self.agent.invoke(agent_inputs)
            
            # 4. 执行工具调用
            if output.tool_calls:
                for tool_call in output.tool_calls:
                    tool_output = self.tools[tool_call["name"]].invoke(
                        tool_call["args"]
                    )
                    # 5. 更新 intermediate_steps
                    intermediate_steps.append((output, tool_output))
            else:
                # 最终答案
                break
                
        # 6. 如果有记忆，保存对话
        if self.memory:
            self.memory.save_context(inputs, {"output": final_output})
```

## 4. 两种状态的区别

### Agent Scratchpad（短期工作记忆）
- **生命周期**：单次任务执行期间
- **内容**：思考过程、工具调用、中间结果
- **用途**：让 Agent 知道已经做了什么，避免重复
- **清空时机**：每次新任务开始

### Memory（长期对话记忆）
- **生命周期**：跨任务持续
- **内容**：完整的对话历史
- **用途**：保持上下文连续性
- **清空时机**：手动清除或会话结束

## 5. 实际例子

```python
# 无记忆模式 - 只有 scratchpad
User: "创建用户管理系统"
Agent: 
  - Scratchpad: [思考→创建文件→测试→完成]  # 任务结束后清空
  
User: "添加认证功能"
Agent: 
  - Scratchpad: []  # 全新开始，不知道之前创建了什么

# 有记忆模式 - scratchpad + memory
User: "创建用户管理系统"
Agent: 
  - Memory: []
  - Scratchpad: [思考→创建文件→测试→完成]
  - Memory: [用户: "创建...", AI: "已创建..."]  # 保存

User: "添加认证功能"
Agent:
  - Memory: [之前的对话]  # 知道已创建用户系统
  - Scratchpad: []  # 新任务的思考过程
```

## 6. 状态格式化

```python
def format_to_messages(intermediate_steps):
    """将中间步骤格式化为消息"""
    messages = []
    for action, observation in intermediate_steps:
        # Agent 的思考
        messages.append(AIMessage(content=action.log))
        # 工具的输出
        messages.append(ToolMessage(
            content=str(observation),
            tool_call_id=action.tool_call_id
        ))
    return messages
```

## 7. 高级特性

### 状态检查点
```python
# 保存当前状态
checkpoint = {
    "intermediate_steps": intermediate_steps,
    "memory": self.memory.chat_memory.messages if self.memory else None,
    "iteration": current_iteration
}

# 恢复状态
intermediate_steps = checkpoint["intermediate_steps"]
```

### 状态压缩
```python
# 当 scratchpad 太长时
if len(intermediate_steps) > max_steps:
    # 只保留最近的 N 步
    intermediate_steps = intermediate_steps[-max_steps:]
    # 或者摘要早期步骤
    summary = summarize_early_steps(intermediate_steps[:-max_steps])
    intermediate_steps = [summary] + intermediate_steps[-max_steps:]
```

## 8. 调试技巧

```python
# 查看 Agent 的思考过程
executor = AgentExecutor(agent, tools, verbose=True)  # verbose=True

# 自定义回调查看状态
class StateLogger(BaseCallbackHandler):
    def on_agent_action(self, action, **kwargs):
        print(f"Agent thinking: {action.log}")
        print(f"Tool to call: {action.tool}")
        
    def on_tool_end(self, output, **kwargs):
        print(f"Tool output: {output}")

executor = AgentExecutor(
    agent, 
    tools, 
    callbacks=[StateLogger()]
)
```

## 9. 性能优化

### Scratchpad 大小控制
```python
# 限制中间步骤数量
max_intermediate_steps = 50

# 在 AgentExecutor 中
if len(intermediate_steps) > max_intermediate_steps:
    # 提前终止或压缩
    pass
```

### Token 优化
```python
# 估算 scratchpad tokens
def estimate_scratchpad_tokens(intermediate_steps):
    total = 0
    for action, obs in intermediate_steps:
        total += llm.get_num_tokens(action.log)
        total += llm.get_num_tokens(str(obs))
    return total
```

## 总结

LangChain React Agent 通过 **双层状态机制** 实现了灵活的状态管理：

1. **Agent Scratchpad**：维护当前任务的思考链，让 Agent 能够连贯地完成复杂任务
2. **Memory**（可选）：保持跨任务的对话历史，实现真正的上下文连续性

这种设计既保证了单次任务的连贯性，又支持了长期的对话记忆，是一个非常优雅的解决方案。