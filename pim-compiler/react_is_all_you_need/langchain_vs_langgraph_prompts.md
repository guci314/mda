# LangChain vs LangGraph 提示词对比

## 1. 传统 LangChain ReAct Agent 的默认提示词

```
Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
```

### 特点：
- **明确的 ReAct 格式**：Thought → Action → Action Input → Observation
- **结构化输出**：强制 Agent 遵循特定的思考和行动模式
- **显式的思考过程**：每一步都要先思考（Thought）
- **循环结构**：可以重复 N 次直到找到答案

## 2. LangGraph create_react_agent 的默认行为

LangGraph 的 `create_react_agent` **没有内置的默认提示词**。

### 行为：
- 当 `prompt=None` 时，不添加任何系统消息
- 完全依赖 LLM 的原生工具调用能力
- 模型直接决定是否调用工具，无需特定格式

### 示例：
```python
# 不使用提示词
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt=None  # 不添加任何系统提示词
)

# 使用自定义提示词
agent = create_react_agent(
    model=llm,
    tools=tools,
    prompt="You are a helpful assistant"  # 作为 SystemMessage 添加
)
```

## 3. 主要区别

| 特性 | LangChain ReAct | LangGraph |
|------|-----------------|-----------|
| 默认提示词 | 有，包含详细的 ReAct 格式 | 无 |
| 思考过程 | 显式要求 "Thought" | 依赖模型自身 |
| 输出格式 | 严格的格式要求 | 灵活，无格式要求 |
| 工具调用 | 通过 Action/Action Input | 原生工具调用 |
| 适用场景 | 需要可解释的推理过程 | 高效的工具使用 |

## 4. 在我们的实现中

当前 `react_agent.py` 的行为：

```python
# 有知识文件时
prompt = system_prompt_template + prior_knowledge
agent = create_react_agent(..., prompt=prompt)  # 覆盖默认（虽然默认是空的）

# 无知识文件时
agent = create_react_agent(..., prompt=None)  # 不添加系统提示词
```

## 5. 建议

如果你想要传统 ReAct 的思考过程，可以：

1. **在自定义提示词中加入 ReAct 格式**：
```python
react_prompt = """You are a helpful assistant. When solving problems:

1. Think step by step about what needs to be done
2. Use the available tools to gather information or take actions
3. Observe the results and think about next steps
4. Continue until you have a complete answer

{prior_knowledge}
"""
```

2. **或者使用传统的 LangChain ReAct Agent**：
```python
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub

prompt = hub.pull('hwchase17/react')
agent = create_react_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools)
```

## 总结

- LangGraph 的设计理念是**更简洁、更灵活**
- 它不强制特定的思考格式，让 LLM 自由发挥
- 如果需要结构化的推理过程，需要自己在提示词中定义