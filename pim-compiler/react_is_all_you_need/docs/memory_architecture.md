# React Agent 记忆架构实现对照表

## 概述
React Agent 实现了认知科学中的四类记忆系统，通过极简设计实现了完整的记忆功能。

## 四类记忆对照表

| 记忆类型 | 理论定义 | 当前实现 | 存储位置 | 生命周期 | 触发机制 |
|---------|---------|---------|---------|---------|---------|
| **工作记忆**<br>Working Memory | 当前任务的临时信息存储<br>类似CPU寄存器 | `self.messages`<br>上下文窗口 | 内存中 | 任务期间 | 自动维护 |
| **会话记忆**<br>Conversational Memory | 完整对话历史记录<br>当前会话的所有交互 | `self.messages`<br>消息列表 | 内存中 | 会话期间 | 自动记录 |
| **情景记忆**<br>Episodic Memory | 时空绑定的经历<br>具体事件和上下文 | `compact.md`<br>压缩历史 | 文件系统<br>`.agent/目录/` | 跨会话持久 | 70k tokens<br>自动压缩 |
| **语义记忆**<br>Semantic Memory | 抽象概念和规则<br>结构化知识 | `agent.md`<br>知识文档 | 文件系统<br>工作目录 | 永久保存 | 用户触发<br>Agent建议 |

## 实现细节

### 1. 工作记忆 (Working Memory)
```python
# 位置: react_agent_minimal.py
self.messages  # 当前上下文窗口
```
- **容量限制**: 128k tokens (DeepSeek)
- **更新方式**: 每轮对话自动更新
- **清理机制**: 任务结束后重置
- **类比**: CPU寄存器，RAM

### 2. 会话记忆 (Conversational Memory)
```python
# 位置: react_agent_minimal.py
self.messages = []  # 消息历史列表
```
- **记录内容**: 所有user/assistant消息
- **压缩触发**: 达到70k tokens
- **持久化**: 会话结束不保存
- **类比**: 进程内存空间

### 3. 情景记忆 (Episodic Memory)
```python
# 位置: .agent/项目名/compact.md
_compact_messages()  # 压缩方法
_save_compact_memory()  # 保存方法
_load_compact_memory()  # 加载方法
```
- **压缩策略**: 保留关键信息，压缩到10,000字符
- **时间标记**: 每次压缩记录时间戳
- **加载时机**: Agent初始化时
- **存储格式**: Markdown文档
- **不完美性**: 信息损失，但实用够用

### 4. 语义记忆 (Semantic Memory)
```python
# 位置: 工作目录/agent.md
_load_semantic_memory()  # 加载语义记忆
write_semantic_memory()  # 写入工具
```
- **级联加载**: 当前目录 → 父目录（最多2级）
- **注入时机**: execute()执行任务时动态注入
- **更新触发**: 
  1. 用户命令："写agent.md"
  2. 复杂任务后Agent建议
- **知识格式**: Markdown结构化文档

## 记忆协同机制

```
用户输入
    ↓
[工作记忆] ← 动态注入 ← [语义记忆 agent.md]
    ↓                          ↑
[会话记忆] → 70k触发 → [情景记忆 compact.md]
    ↓
任务执行
```

## 设计哲学

### 大道至简 (Simplicity First)
- 四类记忆，四个实现
- 无复杂依赖
- 文件系统即数据库
- Markdown即知识表示

### 压缩就是认知 (Compression is Cognition)
- compact.md: 通过压缩实现遗忘与记忆
- agent.md: 通过抽象实现知识沉淀
- 重要的保留，冗余的遗忘

### 文件系统即存储 (Filesystem as Storage)
- 无需数据库
- 版本控制友好
- 人类可读可编辑
- 位置即关系

## 使用示例

### 1. 自动情景记忆
```python
# 自动触发，无需干预
agent = ReactAgentMinimal(work_dir="my_project")
# 对话达到70k tokens时自动压缩到compact.md
```

### 2. 手动语义记忆
```python
# 用户触发
"请写agent.md记录这个模块的核心知识"

# Agent建议
"这是一个复杂任务，建议保存到agent.md中..."
```

### 3. 记忆级联
```python
# 在 /project/module/submodule/ 工作时
# 自动加载:
# 1. /project/module/submodule/agent.md (如果存在)
# 2. /project/module/agent.md (如果存在)
```

## 理论验证

这个实现验证了核心理论：
```
React + 文件系统 = 冯·诺依曼架构 = 图灵完备
```

- **CPU**: React Agent（推理引擎）
- **RAM**: 工作记忆（上下文窗口）
- **硬盘**: 文件系统（compact.md, agent.md）
- **程序**: 知识文件（agent.md）
- **数据**: 工作文件和压缩历史

## 未来展望

当前实现已经足够，但可能的改进方向（不追求完美）：
- 向量数据库支持（如需要）
- 多级语义记忆（如需要）
- 自动知识提取（如需要）

**记住**: 完美是优秀的敌人。当前实现已经验证了理论，够用即可。