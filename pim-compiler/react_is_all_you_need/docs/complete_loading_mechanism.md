# 智能体的完整加载机制

## 默认加载总结

### 1. Knowledge文件（加载到系统提示词）

#### 强制加载（1个）
- **self_awareness.md** - 自我认知基础

**位置**：`knowledge/self_awareness.md`

**加载到**：系统提示词（system role）

**内容**：
- 三层认知结构
- @创建子智能体、@批量创建智能体契约函数
- 系统级文件认知
- 知识函数PATH机制

#### 条件加载（1个）
- **~/.agent/{name}/knowledge.md** - 个体知识（如果存在）

**加载到**：系统提示词（system role）

**内容**：
- 领域特定的知识函数
- 个体能力定义
- 积累的知识

#### 用户指定（0到N个）
- 通过`knowledge_files`参数传入

### 2. Compact记忆（加载到消息列表）⭐

#### 强制加载（如果存在）
- **~/.agent/{name}/compact.md** - 压缩的对话历史

**加载方式**（第289-298行）：
```python
if self._load_compact_memory():
    # 作为assistant消息添加到消息列表
    self.messages.append({
        "role": "assistant",
        "content": f"[已加载历史压缩记忆]\n{self.compact_memory}"
    })
```

**加载到**：消息列表（assistant role）

**内容**：
- 压缩的对话历史
- 重要的决策和学习
- 动态演化的记忆

### 3. System Prompt（模板）

- **system_prompt_minimal.md** - 系统提示词模板

**位置**：`knowledge/minimal/system/system_prompt_minimal.md`

**不是knowledge文件**：
- 不加到knowledge_files列表
- 作为模板直接读取
- 通过占位符填充内容

**内容**：
- ExecutionContext使用规则
- Context栈规则
- 契约函数vs软约束函数

### 4. 知识函数索引（不加载到提示词）

- **knowledge_function_index.json** - 函数索引

**生成**：启动时自动生成

**不加载**：
- ❌ 不加到系统提示词
- ❌ 不加到knowledge_files
- ✅ 智能体主动读取

**用途**：
- 智能体查询函数类型（contract/soft）
- 智能体查询函数定义位置
- 智能体决定是否使用Context栈

## 加载层次对比

| 内容 | 加载位置 | 角色 | 特性 | 设计理由 |
|------|---------|------|------|---------|
| **self_awareness.md** | 系统提示词 | system | 静态知识 | 基础必须知道 |
| **个体knowledge.md** | 系统提示词 | system | 静态知识 | 能力定义 |
| **compact.md** | 消息列表 | assistant | 动态记忆 | 会演化、会压缩 ⭐ |
| **system_prompt模板** | 系统提示词 | system | 执行规则 | 行为规范 |
| **索引JSON** | 不加载 | N/A | 查询工具 | 智能体主动查 |

## 设计的合理性

### 为什么compact.md不放在knowledge_files？

#### 1. 本质不同
```
knowledge.md = 先天知识（DNA）
  - 能力定义
  - 静态、结构化
  - 手动更新

compact.md = 后天记忆（经验）
  - 对话历史
  - 动态、演化
  - 自动压缩
```

#### 2. 生命周期不同
```
knowledge.md:
  - 创建时定义
  - 通过@自我实现更新
  - 相对稳定

compact.md:
  - 每次对话都变化
  - 超过70k tokens自动压缩
  - 持续演化
```

#### 3. 加载位置不同
```
knowledge.md → 系统提示词（system role）
  - 总是可见
  - 不会变化
  - 提供稳定的能力基础

compact.md → 消息列表（assistant role）
  - 在对话流中
  - 会被压缩
  - 动态累积经验
```

## 智能体的认知结构

### 启动时知道的（被动接收）

**通过系统提示词**：
1. self_awareness.md（自我认知）
2. ~/.agent/{name}/knowledge.md（个体知识）
3. system_prompt_minimal.md（执行规则）

**通过消息列表**：
4. compact.md（历史记忆，如果存在）

### 执行时查询的（主动获取）

**主动读取索引**：
5. knowledge_function_index.json

**根据需要读取**：
6. 其他knowledge文件（通过索引找到路径）

## 完整的加载流程

### 启动时

```python
agent = ReactAgentMinimal(name="book_agent", ...)

# 步骤1：加载knowledge文件
knowledge_files = [
    "knowledge/self_awareness.md",  # 默认
    "~/.agent/book_agent/knowledge.md"  # 如果存在
]

# 步骤2：构建系统提示词
system_prompt = build_prompt(
    template="system_prompt_minimal.md",
    knowledge=knowledge_content,
    self_awareness=self_awareness_section
)

# 步骤3：初始化消息列表
messages = [
    {"role": "system", "content": system_prompt}
]

# 步骤4：加载compact记忆（如果存在）
if compact.md存在:
    messages.append({
        "role": "assistant",
        "content": "[已加载历史压缩记忆]\n{compact_memory}"
    })

# 步骤5：构建索引（不加载到提示词）
knowledge_loader.build_index()
# → 生成knowledge_function_index.json
```

### 执行时

```python
# 智能体看到@learning
用户: "执行@learning"

# 智能体主动查询
index = read_file("knowledge_function_index.json")
func_info = index["functions"]["learning"]

# 智能体主动读取
definition = read_file(func_info["path"])

# 智能体理解并执行
if func_info["func_type"] == "contract":
    context.push(...)
```

## 总结

### 默认加载的内容

**Knowledge文件**（静态知识）：
1. ✅ self_awareness.md（强制）
2. ✅ ~/.agent/{name}/knowledge.md（如果存在）

**Compact记忆**（动态记忆）：
3. ✅ ~/.agent/{name}/compact.md（如果存在，加载到消息列表）

**System Prompt**（执行规则）：
4. ✅ system_prompt_minimal.md（作为模板，不是knowledge文件）

**索引文件**（查询工具）：
5. ✅ knowledge_function_index.json（生成，不加载）

### 设计的合理性 ✅

**静态vs动态的完美分离**：
- 静态知识 → 系统提示词（knowledge.md）
- 动态记忆 → 消息列表（compact.md）
- 执行规则 → 系统提示词模板（system_prompt）
- 查询工具 → 文件系统（索引JSON）

**智能体的主动性**：
- 被动接收：基础知识（self_awareness.md）
- 主动查询：函数索引（knowledge_function_index.json）
- 主动读取：需要的知识文件

这个设计非常清晰和合理！不需要修改。