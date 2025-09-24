# agent_knowledge.md vs experience.md：为什么记录在不同地方？

## 核心区别

### agent_knowledge.md（DNA层）
- **是什么**：Agent的能力定义和行为模式
- **类比**：程序的源代码、类定义、基因
- **特征**：
  - 相对静态
  - 定义"我能做什么"
  - 会被子Agent继承
  - 改变会影响Agent的本质

### experience.md（经验层）
- **是什么**：Agent的运行时经验和历史
- **类比**：日志文件、工作记录、记忆
- **特征**：
  - 动态累积
  - 记录"我做了什么"
  - 个体私有，不自动继承
  - 改变不影响Agent的本质能力

## 为什么创建子Agent记录在experience.md？

### 正确的理由

1. **事件性质**：
   - 创建子Agent是一个运行时事件
   - 是"我在时间T做了X"的记录
   - 不改变父Agent的固有能力

2. **避免知识污染**：
   ```
   如果写入agent_knowledge.md：
   - 所有未来的子Agent都会继承这个信息
   - 导致无关的历史信息传播
   - 知识文件会越来越臃肿
   ```

3. **能力vs行动**：
   - 能力：我能创建Agent（agent_knowledge.md）
   - 行动：我创建了Agent X（experience.md）

### 类比理解

| 场景 | agent_knowledge.md | experience.md |
|------|-------------------|---------------|
| 程序员学会Python | ✅ 更新简历 | ❌ |
| 程序员写了一个函数 | ❌ | ✅ 工作日志 |
| Agent学会新算法 | ✅ 能力提升 | ❌ |
| Agent创建了子Agent | ❌ | ✅ 行动记录 |

## 潜在的问题

### 问题1：重启后的记忆丢失

**场景**：
```python
# 父Agent创建了子Agent
create_agent("order_processor")
write_to_experience("创建了order_processor")

# 父Agent重启...
# 问题：如何知道自己创建过order_processor？
```

**当前方案的缺陷**：
- experience.md可能不会被完整加载
- 父Agent可能"忘记"自己的创建物
- 协作关系可能丢失

### 问题2：协作关系的持久化

**需要记录的信息**：
1. 创建了哪些子Agent（历史事实）→ experience.md ✅
2. 如何与子Agent协作（能力知识）→ agent_knowledge.md ？

**混淆点**：
- 协作方式似乎是一种"能力"
- 但又依赖于具体创建的Agent
- 边界不清晰

## 更好的设计方案？

### 方案1：混合记录

```markdown
# agent_knowledge.md
## 我的协作网络
- 可以调用order_processor处理订单
- 可以调用data_analyzer分析数据

# experience.md
## 创建历史
- 2024-01-01: 创建order_processor，用于处理电商订单
- 2024-01-02: 创建data_analyzer，用于数据分析
```

### 方案2：引用机制

```markdown
# agent_knowledge.md
## 外部能力
- 参见 ~/.agent/[my_name]/collaborators.md

# collaborators.md（新文件）
## 我创建的Agent
- order_processor: 处理订单
- data_analyzer: 数据分析
```

### 方案3：动态发现

```python
# 不记录，而是动态发现
def find_my_children():
    # 扫描 ~/.agent/ 目录
    # 查找creator == self的Agent
    return discovered_children
```

## 当前设计的合理性分析

### 支持当前设计的理由

1. **简洁性**：
   - 保持agent_knowledge.md专注于能力
   - 避免混淆静态能力和动态状态

2. **独立性**：
   - 每个Agent可以独立运作
   - 不依赖于历史创建记录

3. **灵活性**：
   - 子Agent可能被删除或修改
   - 不硬编码依赖关系

### 反对当前设计的理由

1. **实用性**：
   - 协作关系需要持久化
   - 重启后需要恢复上下文

2. **完整性**：
   - Agent的完整能力包括它的协作网络
   - 这应该是知识的一部分

## 建议的原则

### 判断标准

记录在**agent_knowledge.md**如果：
- 改变了Agent的能力集
- 需要被子Agent继承
- 是Agent身份的一部分

记录在**experience.md**如果：
- 是时间相关的事件
- 是个体特定的经历
- 不影响Agent的本质能力

### 特殊情况

**创建工具** → agent_knowledge.md
```markdown
## 我创建的工具
- calculate_tax.py: 计算税务
```
因为工具扩展了能力

**创建子Agent** → experience.md（当前）
```markdown
## 创建历史
- 创建了order_processor
```
因为是历史事件

但也许应该：
**协作能力** → agent_knowledge.md
```markdown
## 协作网络
- 可调用order_processor处理订单
```
因为这是扩展的能力

## 结论

当前将子Agent创建记录在experience.md有其合理性，主要是为了：
1. 保持知识文件的纯净
2. 避免无关信息的继承
3. 区分能力和历史

但可能需要额外的机制来：
1. 持久化协作关系
2. 支持重启后的上下文恢复
3. 明确什么构成了"能力的改变"

**核心洞察**：
> 创建子Agent是**事件**（记录在experience）
>
> 但拥有可调用的子Agent是**能力**（可能应该在knowledge）
>
> 当前设计选择了简洁性而牺牲了一些实用性。