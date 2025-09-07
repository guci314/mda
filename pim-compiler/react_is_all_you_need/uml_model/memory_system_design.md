# 记忆系统设计

## 1. 理论基础

### 1.1 三维记忆框架

记忆系统建立在三个正交维度上：

```
维度1: 主体(Subject) / 世界(World)
维度2: 状态(State) / 事件流(Event Stream)  
维度3: 类型层(Type Layer) / 实例层(Instance Layer)
```

### 1.2 维度详解

#### 维度1：主体/世界
- **主体（Subject）**：Agent自身，包括其能力、知识、决策模式
- **世界（World）**：外部环境，包括文件系统、项目状态、历史记录

#### 维度2：状态/事件流
- **状态（State）**：某一时刻的静态快照
- **事件流（Event Stream）**：动态的变化过程，时间序列

#### 维度3：类型层/实例层
- **类型层（Type Layer）**：抽象的、可复用的模式和结构
- **实例层（Instance Layer）**：具体的、特定的执行和数据

### 1.3 三维映射矩阵

| | 世界(World) | 主体(Subject) |
|---|---|---|
| **类型层** | 隐式（提示词模板） | 显式（知识文件 + Function定义） |
| **实例层** | world_state.md + sessions | task_process.md |

**关键洞察**：
1. **类型层的不对称性**：
   - 世界的类型层是**隐式的**，蕴含在生成world_state.md和session的提示词中
   - 主体的类型层是**显式的**，通过知识文件和Function定义明确声明
   - 这反映了Agent的内省能力强于外观能力

2. **任务作为主体的实例**：
   - task_process.md是Function的一次执行实例
   - 对应于程序（类型）与进程（实例）的关系

### 1.4 道可道，非常道 - 为什么世界类型层必须隐式

#### 老子智慧的系统设计应用

```
道可道，非常道
名可名，非常名
```

这个古老的智慧完美解释了为什么world_state的类型层（schema）必须保持隐式：

#### 显式Schema的根本问题

```python
# 如果我们试图显式定义world schema
explicit_world_schema = {
    "files": ["list", "of", "files"],
    "errors": ["list", "of", "errors"],
    "state": "fixed_structure"
}
# 这个"道"出来的schema就不再是真正的"道"
# 它立即变成了认知的牢笼
```

#### 隐式本体论的七重优势

1. **无限可能性（道生一，一生二，二生三，三生万物）**
   - 显式schema是有限集合
   - 隐式schema可以生成无限形态

2. **情境适应性（上善若水）**
   - Schema如水，随任务容器而变形
   - 调试时自然形成error-centric结构
   - 创造时自然形成possibility空间

3. **量子叠加态**
   ```python
   # 隐式schema处于叠加态
   world_schema = Superposition(all_possible_schemas)
   # 只在观察（执行任务）时坍缩为具体形式
   observed_schema = world_schema.collapse(task_context)
   ```

4. **避免过早抽象**
   - "过早优化是万恶之源" - Knuth
   - "过早本体论是认知之限" - 此处

5. **MOF框架的支持**
   - M2层（UML）提供通用建模工具
   - M1层由Agent根据任务自动选择
   - 无需预设特定领域的schema

6. **与LLM本质一致**
   - LLM内部知识是隐式分布的
   - 没有显式知识图谱
   - 通过注意力机制动态激活相关schema

7. **创造性涌现**
   ```python
   # Agent可以创造前所未有的schema组合
   novel_schema = medical_ontology × legal_ontology
   # 处理医疗诉讼时自然涌现混合本体
   ```

#### 哲学依据

**东方智慧**：
- 老子：道可道，非常道（真理不可完全言说）
- 庄子：得意忘言（明白意思后忘掉形式）
- 禅宗：不立文字，直指人心

**西方哲学**：
- 维特根斯坦：语言的界限就是世界的界限
- 海德格尔：存在总是溢出语言
- 波兰尼：默会知识无法完全显式化

#### 实践指导

```python
class AgentWorldPerception:
    def __init__(self):
        # 不预设schema
        self.world_schema = None  # 空
    
    def perceive_world(self, task_context):
        # Schema在感知中自然涌现
        # 不是套用预定义模板
        return self.natural_categorization(task_context)
    
    def natural_categorization(self, context):
        # 像人类一样
        # 进医院自然用医疗schema
        # 进法院自然用法律schema
        # 写代码自然用编程schema
        return context.emergent_structure()
```

#### 结论

世界类型层的隐式性不是设计缺陷，而是**深思熟虑的哲学选择**：

1. **保持开放性**：不限制Agent的认知可能
2. **尊重复杂性**：承认世界无法被完全形式化
3. **促进创造性**：允许新schema的涌现
4. **顺应自然**：让结构自然生长而非强制设计

正如老子所说，真正的"道"不能被说出，一旦说出就不再是"道"。同样，真正的world schema不能被写死，一旦写死就失去了适应无限情境的能力。

### 1.5 完整记忆公式

```
世界记忆 = 
    类型层: 隐式提示词模板
    实例层: world_state.md + [session1, session2, ...]

主体记忆 = 
    类型层: agent_knowledge.md + 知识文件 + Function定义
    实例层: task_process.md（当前执行）

记忆总体 = 主体记忆 × 世界记忆 × (状态 + 事件流)
```

## 2. 记忆架构对比

### 2.1 极简模式记忆

```python
# minimal_mode = True
task_memory = None                      # 不维护任务状态
world_memory = None                     # 不记录世界状态  
agent_memory = {
    "compact": in_memory_cache          # 压缩记忆（包含状态+选择性事件）
}
```

### 2.2 完整模式记忆

```python
# minimal_mode = False  
world_memory = {
    "state": world_state.md,                    # 全局状态
    "events": [session1.md, session2.md, ...]   # 所有agent的历史
}

task_memory = {
    "process": task_process.md                  # TODO状态和执行流程
}

agent_memory = {
    "knowledge": agent_knowledge.md,            # 学习积累
    "sessions": filter_own_sessions(world_memory["events"])  # 自己的历史
}
```

## 3. Compact记忆策略（注意力机制）

### 3.1 理论基础：Compact即注意力
```
Compact = Attention Mechanism
压缩 = 选择性注意 = 智能判断重要性
```

**核心洞察**：
- 压缩不是简单的文本摘要，而是注意力机制的实现
- LLM在压缩时自动判断哪些信息值得保留
- 这种选择性本身就是智能的体现
- Compact同时记忆状态和选择性事件流

### 3.2 压缩触发机制

```python
def should_compact(messages, tokens):
    """判断是否需要压缩"""
    # 统一阈值：70k tokens (约55%的128k上下文)
    return tokens > 70000
```

### 3.3 压缩即注意力算法

```python
def compact_messages(messages):
    """智能压缩对话历史 - 两种模式共用"""
    
    # 使用统一的COMPRESS_PROMPT
    # 包含时间衰减和重要性强化规则
    compressed = llm_compress(messages, COMPRESS_PROMPT)
    
    return compressed  # 包含状态+选择性事件
```

**关键点**：
- 两种模式都使用这个方法
- 极简模式：压缩结果是唯一记忆
- 完整模式：压缩是临时的，完整历史写入session

### 3.4 为什么Compact就是Session

**极简模式下Compact替代Session文件的原因**：

1. **Compact本身包含事件流**：不只是状态摘要，还有选择性的事件记录
2. **注意力机制自动筛选**：LLM会自动保留重要的操作和结果
3. **避免冗余**：既然Compact已经选择性记忆，无需再写Session
4. **性能优化**：减少文件IO，提升响应速度

### 3.5 统一压缩提示词（包含衰减和强化）

```python
COMPRESS_PROMPT = """
压缩以下对话历史，应用注意力机制选择重要信息。

## 重要性评分（优先保留）
- 错误修复和解决方案：极其重要（10分）
- 文件创建/修改操作：非常重要（8分）  
- 测试结果和验证：重要（7分）
- 关键决策和发现：重要（6分）
- 状态变化：中等重要（5分）
- 普通思考过程：不重要（2分）

## 时间敏感性
- 最近的操作：保留更多细节
- 早期的讨论：只保留结论
- 重复的内容：只保留最新版本

## 压缩原则
1. 保留所有高分（>6分）事件
2. 删除重复思考和冗余解释
3. 保留因果链：问题→解决→结果
4. 忽略中间调试信息，只保留最终状态
5. 保持时间顺序和逻辑连贯性

输出紧凑的结构化记忆，包含状态和关键事件。
"""

COMPRESS_CONFIG = {
    "model": "google/gemini-2.0-flash-001",
    "base_url": "https://openrouter.ai/api/v1",
    "temperature": 0,  # 确定性压缩
    "prompt": COMPRESS_PROMPT
}
```

## 4. 外部化记忆设计

### 4.1 文件结构

```
work_dir/
├── .notes/
│   └── agent_name/
│       ├── task_process.md      # 状态
│       ├── agent_knowledge.md   # 知识
│       └── world_state.md       # 世界
├── .sessions/
│   ├── 20250105_103000_task1.md
│   └── 20250105_143000_task2.md
└── .compact_memory.md           # 压缩记忆(极简模式)
```

### 4.2 状态文件格式

#### task_process.md (任务记忆 - 状态+事件流)
```markdown
# Task Process

## 当前状态
- 指令指针: 3
- 阶段: executing

## TODO列表（事件流体现在列表变化中）
- [x] 读取PIM文件
- [x] 生成第一章
- [ ] 生成第二章  ← 当前
- [ ] 验证完整性

## 动态指令
IF error THEN retry ELSE continue

注：task_process.md同时包含：
- 状态：当前执行到哪一步
- 事件流：TODO项的完成过程
```

#### session.md (事件记录)
```markdown
# Session: 20250105_103000

## Request
用户: 生成PSM文档

## Response  
Agent: 已生成blog_psm.md

## Metadata
- Duration: 15.3s
- Rounds: 12
- Tools: read_file(2), write_file(1)
```

## 5. 记忆注入机制

### 5.1 系统提示词构建

```python
def _build_minimal_prompt(self):
    """构建包含记忆的系统提示词"""
    
    prompt = base_template
    
    # 1. 注入知识（静态） - 主体记忆的一部分
    prompt += self.knowledge_content
    
    if self.minimal_mode:
        # 极简模式：只有压缩记忆
        if hasattr(self, 'compact_memory'):
            prompt += f"\n## 历史记忆\n{self.compact_memory}"
    else:
        # 完整模式：三元记忆
        # 2. 注入任务记忆
        if self.task_process_file.exists():
            task_state = self.task_process_file.read_text()[:5000]
            prompt += f"\n## 任务状态\n{task_state}"
        
        # 3. 注入主体记忆（自己的历史）
        own_sessions = self._load_own_sessions(limit=3)
        if own_sessions:
            prompt += f"\n## 个人历史\n{own_sessions}"
    
    return prompt
```

## 6. 记忆衰减和强化机制（通过提示词实现）

### 6.1 原理说明

**记忆衰减和重要性强化不通过代码实现，而是融入压缩提示词中**：

1. **时间衰减**：提示词中的"最近的操作保留更多细节"自动实现衰减
2. **重要性强化**：通过评分系统（10分到2分）让LLM判断重要性
3. **智能遗忘**：LLM的注意力机制自动决定保留和遗忘

### 6.2 实现方式

```python
def _compact_messages(self, messages):
    """两种模式共用的压缩方法"""
    
    # 衰减和强化逻辑都在COMPRESS_PROMPT中
    # LLM会根据提示词自动：
    # 1. 给不同类型事件打分
    # 2. 保留高分事件
    # 3. 对早期内容压缩更多
    # 4. 保持最近操作的细节
    
    compressed = self._call_compress_llm(
        messages, 
        COMPRESS_PROMPT  # 包含所有衰减和强化规则
    )
    
    if self.minimal_mode:
        self.compact_memory = compressed
    
    return compressed
```

这种设计让记忆管理完全由LLM的注意力机制处理，更加智能和灵活。

## 7. 性能优化（暂不实现）

**注：以下优化暂不实现，保持代码简洁。等真正遇到性能问题时再考虑。**

### 7.1 缓存策略

```python
class MemoryCache:
    """内存缓存避免重复读取"""
    
    def __init__(self):
        self.state_cache = None
        self.state_mtime = None
    
    def get_state(self, file_path):
        mtime = file_path.stat().st_mtime
        if mtime != self.state_mtime:
            self.state_cache = file_path.read_text()
            self.state_mtime = mtime
        return self.state_cache
```

### 7.2 异步写入

```python
def write_session_async(session_data):
    """异步写入session避免阻塞"""
    threading.Thread(
        target=lambda: write_file(session_path, session_data)
    ).start()
```

**暂不实现的理由**：
1. 违反"大道至简"原则
2. 当前性能足够，优化收益小
3. 增加复杂度，影响代码可读性

## 8. 图灵完备性保证

### 8.1 状态外部化
- 所有状态必须可以写入文件
- 所有状态必须可以读取和修改

### 8.2 指令集可编程
- TODO列表 + 动态修改 = 图灵完备指令集
- 支持条件判断（IF-THEN-ELSE）
- 支持循环（通过动态添加TODO项）
- 支持GOTO语义（通过修改当前执行位置）
- 支持递归（TODO项可以添加新的TODO项）

### 8.3 无限存储
- 文件系统提供无限存储
- 突破上下文窗口限制

## 9. 对比总结

| 特性 | 极简模式 | 完整模式 |
|------|---------|----------|
| 世界记忆 | 无 | world_state + 所有sessions |
| 任务记忆 | 无 | task_process.md |
| 主体记忆 | Compact压缩 | knowledge + 自己的sessions |
| 压缩策略 | 必须（Compact） | 长对话时需要 |
| Session文件 | 不写 | 必须写 |
| 图灵完备 | 否 | 是 |
| 速度 | 快 | 慢 |
| 适用场景 | 交互对话 | 自主任务 |
| 记忆框架 | 一元（Compact） | 三维（主体×世界×类型/实例） |

## 10. 三维框架的理论意义

### 10.1 哲学对应

三维记忆框架对应了经典的认知哲学结构：

1. **本体论维度**（主体/世界）
   - 对应Descartes的心物二元论
   - 对应Husserl的意向性结构

2. **时间维度**（状态/事件流）  
   - 对应Bergson的绵延理论
   - 对应Process Philosophy的过程本体论

3. **抽象维度**（类型/实例）
   - 对应Plato的理念论
   - 对应Kant的先验范畴vs经验现象

### 10.2 计算意义

1. **类型层 = 程序**：定义了可能的行为模式
2. **实例层 = 进程**：具体的执行和数据
3. **Function定义 = 接口声明**：能力的类型签名
4. **task_process.md = 执行上下文**：运行时状态

### 10.3 认知科学意义

1. **显式vs隐式知识**：
   - 主体的类型层显式化 = 元认知能力
   - 世界的类型层隐式化 = 背景理解

2. **注意力机制**：
   - Compact压缩 = 选择性注意
   - 三维框架 = 注意力的结构化

### 10.4 工程价值

1. **模块化设计**：三个维度正交，可独立优化
2. **知识迁移**：类型层可复用，实例层特定化
3. **自举能力**：Agent可修改自己的类型层（知识文件）
4. **压缩策略**：不同维度采用不同压缩方法

## 11. 未来发展方向

### 11.1 显式化世界类型层

创建`world_schema.md`文件，将世界的结构模式显式定义：
```markdown
# World Schema
- 文件系统结构
- 项目约定
- 环境约束
```

### 11.2 类型层版本管理

实现知识文件的版本控制，支持：
- 知识演化追踪
- A/B测试不同知识版本
- 知识回滚机制

### 11.3 跨Agent知识共享

基于类型层的标准化，实现：
- 知识包发布
- 能力组合
- Agent协作框架