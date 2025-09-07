# Event Sourcing Protocol - 事件溯源架构

## 核心原则

**事件流（Event Stream）**：只追加，不修改，不删除
**状态快照（State Snapshot）**：读取-整合-更新

## 文件分类与更新模式

### 📝 事件流文件（Append-Only）

#### 1. Sessions（会话记录）
- **路径**: `.sessions/*.md`
- **模式**: **纯追加（Append-Only）**
- **原则**: 
  - ✅ 每个任务创建新文件
  - ✅ 文件一旦创建，永不修改
  - ❌ 禁止删除或编辑已有session
- **示例**:
```python
# ✅ 正确：创建新session文件
session_file = f".sessions/{date}_{type}_{keywords}.md"
write_file(session_file, session_content)

# ❌ 错误：修改已有session
existing_session = read_file(old_session)
write_file(old_session, modified_content)  # 违反原则！
```

#### 2. Task Process（任务过程 - 特殊的事件流）
- **路径**: `.notes/{agent_name}/task_process.md`
- **模式**: **事件驱动追加**
- **原则**:
  - ✅ TODO状态变化时追加事件
  - ✅ 发现新信息时追加记录
  - ✅ 完成阶段时追加总结
  - ⚠️ 可以更新TODO状态（标记完成）
- **示例**:
```python
# ✅ 正确：追加新事件
process = read_file("task_process.md")
process += f"\n## 轮次{n}：发现了新问题\n- 问题描述..."
write_file("task_process.md", process)

# ⚠️ 允许：更新TODO状态
process = process.replace("- [ ] 任务1", "- [x] 任务1")
```

### 🔄 状态文件（Read-Merge-Write）

#### 1. Agent Knowledge（知识库）
- **路径**: `.notes/{agent_name}/agent_knowledge.md`
- **模式**: **读取-整合-更新（Merge Update）**
- **原则**:
  - ✅ 必须先读取现有知识
  - ✅ 整合新的模式和经验
  - ✅ 保留有价值的历史知识
  - ❌ 不能直接覆盖
- **示例**:
```python
# ✅ 正确：整合式更新
existing_knowledge = read_file("agent_knowledge.md")
new_patterns = extract_patterns(task_process)
merged_knowledge = merge_knowledge(existing_knowledge, new_patterns)
write_file("agent_knowledge.md", merged_knowledge)

# ❌ 错误：直接覆盖
write_file("agent_knowledge.md", "全新的知识")  # 丢失历史！
```

#### 2. World State（世界状态）
- **路径**: `world_state.md`
- **模式**: **读取-整合-更新（Merge Update）**
- **原则**:
  - ✅ 必须先读取当前世界状态
  - ✅ 整合新的发现和变化
  - ✅ 保持多Agent视角的一致性
  - ❌ 不能部分更新或覆盖
- **示例**:
```python
# ✅ 正确：整合式更新
current_world = read_file("world_state.md")
new_discoveries = analyze_environment()
updated_world = merge_world_state(current_world, new_discoveries)
write_file("world_state.md", updated_world)
```

## 实现模式

### Event Sourcing模式实现
```python
class EventSourcing:
    def append_event(self, event):
        """事件只能追加"""
        with open(self.event_file, 'a') as f:
            f.write(f"\n{timestamp}: {event}")
    
    def rebuild_state(self):
        """从事件流重建状态"""
        events = read_all_events()
        state = initial_state()
        for event in events:
            state = apply_event(state, event)
        return state
```

### State Merge模式实现
```python
class StateMerge:
    def update_state(self, new_data):
        """状态必须整合更新"""
        # 1. 读取现有状态
        current = self.read_state()
        
        # 2. 整合新数据
        merged = self.merge(current, new_data)
        
        # 3. 验证完整性
        if not self.validate(merged):
            raise Error("状态整合失败")
        
        # 4. 原子写入
        self.write_state(merged)
```

## 文件更新决策树

```
需要更新文件？
├── 是Session记录？
│   └── 创建新文件（Append-Only）
├── 是Task Process？
│   └── 追加新事件或更新TODO状态
├── 是Agent Knowledge？
│   └── 读取→整合→写入
└── 是World State？
    └── 读取→整合→写入
```

## 违规检测

### 🔴 严重违规（必须修正）
1. 修改或删除session文件
2. 直接覆盖knowledge或world_state
3. 不读取就更新状态文件

### 🟡 轻微违规（应该避免）
1. task_process.md过度重写（应该以追加为主）
2. 状态文件更新不包含时间戳
3. 整合时丢失重要历史信息

## 最佳实践

### 1. Session文件命名
```python
# 包含时间戳确保唯一性
filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{task_type}_{keywords}.md"
```

### 2. Knowledge整合策略
```python
def merge_knowledge(old, new):
    # 保留统计信息
    stats = update_stats(old.stats, new.stats)
    
    # 合并模式库（去重）
    patterns = merge_patterns(old.patterns, new.patterns)
    
    # 追加新经验
    experiences = old.experiences + new.experiences
    
    # 更新时间戳
    last_updated = datetime.now()
    
    return format_knowledge(stats, patterns, experiences, last_updated)
```

### 3. World State版本控制
```python
def update_world_state(new_discoveries):
    current = read_file("world_state.md")
    
    # 保存历史版本（可选）
    backup = f"world_state_{timestamp}.backup"
    write_file(backup, current)
    
    # 整合更新
    merged = merge_world(current, new_discoveries)
    
    # 添加更新记录
    merged += f"\n## 更新历史\n- {timestamp}: {summary_of_changes}"
    
    write_file("world_state.md", merged)
```

## 记住

1. **Sessions = 历史记录** → 只追加
2. **Task Process = 事件日志** → 追加为主
3. **Knowledge = 经验积累** → 整合更新
4. **World State = 共享快照** → 整合更新

**核心理念**：
- 事件是不可变的历史
- 状态是事件的累积结果
- 整合保留价值，追加保留历史