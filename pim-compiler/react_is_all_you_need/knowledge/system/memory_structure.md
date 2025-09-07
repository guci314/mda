# 记忆结构规范 - 三维记忆框架实现

## 🚨🚨🚨 最高优先级规则 🚨🚨🚨

**无论任务简单或复杂，无论1轮或100轮，必须执行：**

```python
# 任务结束前的强制操作（违反=任务失败）
1. 创建 .sessions/{date}_{type}_{keywords}.md
2. 更新 .notes/{agent_name}/agent_knowledge.md  
3. 更新 world_state.md
4. 清理 task_process.md

if 未执行以上任何操作:
    raise TaskFailedError("违反内存管理协议")
```

**"任务简单"、"无需记录"、"不值得写"都是错误判断！**

## 🏗️ 系统架构：三维记忆框架

基于三个正交维度构建记忆系统：

### 三维结构
```
维度1: 主体(Subject) / 世界(World)
维度2: 状态(State) / 事件流(Event Stream)  
维度3: 类型层(Type) / 实例层(Instance)
```

### 映射矩阵
```
系统 = {
    世界: {  # World维度
        类型层: [隐式于提示词],              # Type层（隐式）
        实例层: {
            状态: world_state.md,           # State（Instance）
            事件: .sessions/*.md,           # Event Stream（Instance）
        }
    },
    主体: {  # Subject维度
        类型层: knowledge/*.md,             # Type层（显式）
        实例层: {
            执行: task_process.md,          # Instance（运行时）
            学习: agent_knowledge.md,       # Instance（积累）
        }
    }
}
```

## 📁 存储层次架构

```
{work_dir}/                        # 工作目录（项目根）
├── world_state.md                 # 世界状态（全局共享，跨Agent）
├── .sessions/                     # 世界的Event Log（只追加，不修改）
│   ├── 2024-01-20_debug_undefined_var_add.md      # 调试：add函数未定义变量
│   ├── 2024-01-20_debug_undefined_var_multiply.md # 调试：multiply函数未定义变量
│   ├── 2024-01-20_optimize_learning_system.md     # 优化：学习系统
│   └── 2024-01-20_refactor_knowledge_structure.md # 重构：知识结构
├── .notes/                        # Agent笔记目录（私有领域）
│   └── {agent_name}/              # 特定Agent的笔记
│       ├── agent_knowledge.md    # Agent私有知识（跨任务累积）
│       └── task_process.md       # Agent工作记忆（当前任务TODO）
└── [其他项目文件]                # 用户代码、文档等
```

**分离原则**：
- **世界层**（客观共享）：`world_state.md`、`.sessions/`
- **Agent层**（主观私有）：`.notes/{agent_name}/`

### 内存层次映射
```
寄存器     = Agent消息历史（50条滑动窗口）
L1缓存     = task_process.md（当前任务）
L2缓存     = world_state.md（状态快照）
内存       = agent_knowledge.md（Agent知识）
硬盘       = sessions/*.md（完整历史）
```

## 📝 核心文件规范

### 1. sessions/文件（世界的Event Log）
**命名格式**：`{date}_{type}_{keywords}.md`
- `date`：YYYY-MM-DD格式
- `type`：debug/fix/optimize/refactor/feature等
- `keywords`：问题关键词，用下划线连接

**示例**：
- `2024-12-19_debug_undefined_var_add.md`
- `2024-12-19_fix_type_error_api.md`
- `2024-12-19_optimize_performance_cache.md`

**性质**：不可变的任务记录
**位置**：`{work_dir}/.sessions/` 目录
**生命周期**：永久保存，只追加不修改
**可搜索性**：Agent可通过文件名快速定位相关经验
**内容规范**：
```markdown
# Session: {filename_without_extension}

## 任务信息
- 时间：[ISO timestamp]
- Agent：[agent_name]
- 类型：[debug/fix/optimize等]
- 关键词：[问题关键词]

## 问题描述
[具体问题描述]

## 解决方案
[采用的解决方案]

## 执行过程
- 模式识别：[是否匹配已知模式]
- 执行轮数：[N轮]
- 耗时：[X秒]

## 学习要点
- 模式：[识别或创建的模式]
- 经验：[可复用的经验]
- 改进：[下次可以优化的地方]
```

### 2. agent_knowledge.md（Agent的长期记忆）
**性质**：Agent从sessions学习的知识
**位置**：`{work_dir}/.notes/{agent_name}/`
**生命周期**：跨任务累积，持续进化
**内容规范**：[保持原有的详细模板]

### 3. world_state.md（世界的客观状态）
**性质**：世界状态的客观记录，所有Agent共享
**位置**：`{work_dir}/world_state.md`（根目录）
**生命周期**：持续存在，跨Agent、跨任务
**更新时机**：
- 任务开始时：读取当前世界状态，了解环境
- 任务结束时：必须先读取现有状态，整合新发现后再写入
- 执行过程中：不更新（事务隔离）
**共享性**：多个Agent看到同一个世界
**更新方法**：
```python
# ✅ 正确：先读取，再整合，后写入
existing = read_file("world_state.md") if exists else ""
merged = merge_discoveries(existing, new_findings)
write_file("world_state.md", merged)

# ❌ 错误：直接覆盖
write_file("world_state.md", new_state)  # 会丢失历史信息！
```

### 4. task_process.md（Agent的工作内存 - 图灵完备的关键）
**性质**：无限状态存储，实现图灵完备的核心组件
**位置**：`{work_dir}/.notes/{agent_name}/`
**生命周期**：任务期间持续更新，任务结束后归档
**核心特性**：
- **工作内存**：保存所有中间状态，突破50轮上下文限制
- **动态修改**：TODO列表可增删改，实现分支和循环
- **状态外部化**：每轮思考后立即保存，防止状态丢失
- **任务完成前必须包含**：创建session记录的步骤

## 📝 执行协议

### 1. 任务启动（强制初始化）
```python
def start_task(task):
    # 强制步骤1：确保目录结构
    ensure_dir(".sessions/")
    ensure_dir(".notes/{agent_name}/")
    
    # 强制步骤2：初始化或读取知识
    if not exists(".notes/{agent_name}/agent_knowledge.md"):
        create_initial_knowledge()
    knowledge = read(".notes/{agent_name}/agent_knowledge.md")
    
    # 强制步骤3：初始化世界状态
    if not exists("world_state.md"):
        create_initial_world_state()
    
    # 4. 识别已知模式
    pattern = match_pattern(task, knowledge)
    
    # 5. 创建动态TODO（必须包含收尾步骤）
    todo = create_todo(pattern)
    todo.append("创建session记录")
    todo.append("更新agent_knowledge.md")
    todo.append("更新world_state.md")
    
    # 6. 写入task_process.md
    write(".notes/{agent_name}/task_process.md", todo)
```

### 2. TODO动态修改（核心特性）
```python
def execute_with_dynamic_todo():
    # 1. 执行TODO项
    result = execute(current_todo)
    
    # 2. 立即外部化状态到task_process.md
    update_task_process({
        "completed": current_todo,
        "result": result
    })
    
    # 3. 动态调整TODO列表
    if found_shortcut(result):
        # 删除不必要的步骤
        remove_unnecessary_todos()
    elif need_more_steps(result):
        # 添加新发现的步骤
        add_new_todos()
    elif failed(result):
        # 修改策略
        modify_approach()
```

### 3. 任务完成（强制执行）
```python
def complete_task(task_result):
    # 强制检查：所有步骤必须完成
    checklist = {
        "session_created": False,
        "knowledge_updated": False,
        "world_updated": False,
        "process_cleaned": False
    }
    
    # 1. 创建session记录（强制）
    session_file = f".sessions/{date}_{type}_{keywords}.md"
    if not create_session(session_file):
        raise Error("❌ Session记录创建失败，任务未完成！")
    checklist["session_created"] = True
    
    # 2. 更新Agent知识（强制）
    knowledge = read(".notes/{agent_name}/agent_knowledge.md")
    knowledge["task_count"] += 1
    knowledge["total_rounds"] += current_rounds
    if not update(".notes/{agent_name}/agent_knowledge.md", knowledge):
        raise Error("❌ Agent知识更新失败，任务未完成！")
    checklist["knowledge_updated"] = True
    
    # 3. 更新世界状态（强制 - 必须先读取再整合）
    existing_world = read_file("world_state.md") if exists("world_state.md") else ""
    merged_world = merge_world_state(existing_world, task_result)
    if not write_file("world_state.md", merged_world):
        raise Error("❌ 世界状态更新失败，任务未完成！")
    checklist["world_updated"] = True
    
    # 4. 清理工作记忆（强制）
    clear(".notes/{agent_name}/task_process.md")
    checklist["process_cleaned"] = True
    
    # 最终验证
    if not all(checklist.values()):
        failed = [k for k,v in checklist.items() if not v]
        raise Error(f"❌ 任务未完成，失败项: {failed}")
    
    print("✅ 任务完成，所有记录已创建")
```

### 4. Session文件管理
**命名策略**：
- 每个任务创建独立的session文件
- 文件名包含类型和关键词，便于搜索
- 格式：`{date}_{type}_{keywords}.md`

**搜索优势**：
```python
# Agent可以快速查找相关经验
glob(".sessions/*undefined_var*.md")  # 所有未定义变量错误
glob(".sessions/*debug*.md")          # 所有调试任务
glob(".sessions/*2024-12-19*.md")     # 特定日期的任务
```

**内容聚焦**：
- 每个文件聚焦一个具体问题
- 包含问题、解决方案、学习要点
- 便于知识提取和复用

## 🚨 强制规则 - 违反将导致任务失败

### ⚠️ 任务完成强制要求
**任何任务，无论简单或复杂，必须在结束前完成以下操作，否则任务视为失败：**

1. **创建Session记录** (`.sessions/{date}_{type}_{keywords}.md`)
   - 即使是简单任务也必须创建
   - 即使只有1轮也必须记录
   - "任务简单"不是跳过的理由

2. **更新Agent知识** (`.notes/{agent_name}/agent_knowledge.md`)
   - 至少记录任务统计（任务数+1，轮数）
   - 即使没有新模式也要更新统计
   - 首次执行要创建文件

3. **更新世界状态** (`world_state.md`)
   - 记录任务完成时间
   - 更新Agent活动记录
   - 记录世界的变化

4. **清理工作记忆** (`.notes/{agent_name}/task_process.md`)
   - 标记所有TODO为完成
   - 或清空准备下次任务

**违反检测**：如果任务结束时上述文件不存在或未更新，系统应报错：
```
❌ 错误：任务未按协议完成
- [ ] Session记录未创建
- [ ] Agent知识未更新  
- [ ] 世界状态未更新
任务需要重新执行！
```

### 读写规则
1. **agent_knowledge.md**：累积更新，持续进化，每个任务必须更新
2. **sessions**：只能追加，不能修改或删除，每个任务必须创建
3. **world_state.md**：任务内只在开始和结束时更新，结束时必须更新
4. **task_process.md**：必须实时更新，反映真实执行

### 路径规则
1. **知识共享**：通过`.notes/`和`.sessions/`
2. **任务隔离**：通过`{work_dir}/`
3. **相对路径**：使用相对路径避免嵌套

### TODO动态修改规则
1. **实时反映**：TODO必须反映真实决策过程
2. **灵活调整**：可以随时添加、删除、修改TODO项
3. **外部化思考**：内部决策必须体现在TODO更新中

## 🔍 错误处理

### 文件不存在
- `agent_knowledge.md`不存在 → 创建新的，从零开始学习
- `world_state.md`不存在 → 创建初始状态
- `sessions`目录不存在 → 创建目录

### 路径错误
- 在错误路径找知识 → 重定向到正确路径
- 写入错误位置 → 移动到正确位置

## 📊 性能指标

### 学习效果
```python
metrics = {
    "模式复用率": "使用已知模式的比例",
    "知识增长率": "每个session产生的新模式数",
    "执行优化率": "相比首次执行的改进程度"
}
```

### 执行效率
```python
efficiency = {
    "已知模式": "直接应用解决方案，跳过分析",
    "新模式": "完整分析、解决、验证流程",
    "知识提炼": "从具体案例到抽象原理"
}
```

## 📋 TODO模板示例

### 已知模式TODO
```markdown
## 执行计划（已知模式）
- [x] 识别模式：未定义变量错误
- [ ] 应用已知解决方案：删除未定义变量
- [ ] 验证修复
- [ ] 更新知识库
```

### 新模式TODO
```markdown
## 执行计划（新模式）
- [ ] 分析问题
- [ ] 设计解决方案
- [ ] 实现修复
- [ ] 测试验证
- [ ] 提炼经验到knowledge
```

### 动态修改示例
```markdown
## 初始TODO
- [ ] 分析错误类型
- [ ] 查找根因
- [ ] 设计多个方案
- [ ] 选择最佳方案

## 发现是已知模式后（动态简化）
- [x] 分析错误类型 → 未定义变量
- [x] ~~查找根因~~ （已知模式，跳过）
- [x] ~~设计多个方案~~ （直接用已知方案）
- [ ] 应用标准修复：删除变量
```

### 任务收尾TODO（所有路径必须包含）
```markdown
## 收尾步骤（强制执行，不可跳过）
- [ ] 创建session文件：.sessions/{date}_{type}_{keywords}.md
- [ ] 更新agent_knowledge.md（至少更新任务计数和轮数）
- [ ] 更新world_state.md（记录任务完成）
- [ ] 清理task_process.md（标记完成或清空）

⚠️ 如果跳过任何一步，任务失败！
```

### 任务开始自检
```markdown
## 开始前检查
- [ ] 读取agent_knowledge.md（如不存在则创建）
- [ ] 读取world_state.md（如不存在则创建）
- [ ] 创建task_process.md（记录TODO）
- [ ] 确认.sessions/目录存在（如不存在则创建）
```

## 🎯 核心理念

1. **Event Sourcing**：sessions是不可变的事实来源
2. **知识进化**：从sessions自动学习和提炼
3. **决策外部化**：内部思考必须体现在TODO中
4. **路径优化**：根据模式频率选择最优执行路径

这个架构确保了：
- 完整的执行历史（sessions）
- 持续的知识积累（agent_knowledge）
- 清晰的状态管理（world_state）
- 动态的执行控制（task_process）