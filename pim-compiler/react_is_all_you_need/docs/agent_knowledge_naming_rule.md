# Agent知识文件命名规则

## 核心规则

**创建子Agent时，知识文件必须命名为 `agent_knowledge.md`**

## 为什么？

根据三层知识体系架构：

1. **共享知识**（knowledge/*.md）- 所有Agent共享的标准库
2. **个体DNA**（`agent_knowledge.md`）- 每个Agent的独特能力定义 ⭐
3. **个体经验**（`experience.md`）- 运行时积累的经验

`agent_knowledge.md` 是Agent的DNA，定义了它的独特能力和行为模式。

## 正确示例

✅ **正确的做法**：
```python
# 步骤1：创建agent_knowledge.md
write_file("agent_knowledge.md", """
# 电商订单处理专家

## 我的身份
我是电商订单处理专家...

## 核心能力
- 处理订单
- 计算折扣
...
""")

# 步骤2：传递给create_agent
create_agent(
    agent_type="order_processor",
    description="电商订单处理专家",
    knowledge_files=["agent_knowledge.md"]  # 必须是这个名字！
)
```

## 错误示例

❌ **错误的做法**：
```python
# 错误1：使用特定领域名称
write_file("order_knowledge.md", "...")  # ❌ 错误
write_file("book_manager_knowledge.md", "...")  # ❌ 错误

# 错误2：使用多个特定文件
knowledge_files=["accounting.md", "investment.md"]  # ❌ 错误

# 错误3：不传递knowledge_files
create_agent(
    agent_type="complex_agent",
    description="复杂业务Agent"
    # 忘记传递knowledge_files，Agent不会有专属知识！
)
```

## 文件位置流转

1. **创建时**：在工作目录创建 `agent_knowledge.md`
2. **传递时**：通过 `knowledge_files=["agent_knowledge.md"]` 传递
3. **最终位置**：子Agent会将其保存到 `~/.agent/[agent名]/agent_knowledge.md`

## 常见问题

### Q: 为什么不能用 order_knowledge.md 这样的名字？
A: 因为 `agent_knowledge.md` 是Agent DNA的标准名称，系统会特殊处理这个文件。

### Q: 如果需要多个领域的知识怎么办？
A: 将所有知识整合到一个 `agent_knowledge.md` 文件中。

### Q: 简单的Agent需要创建agent_knowledge.md吗？
A: 不需要。简单Agent可以只依赖系统默认知识。

## 记住

- 文件名必须是 `agent_knowledge.md`
- 这是Agent的DNA
- 不要使用其他名称