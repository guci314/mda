# ⛔ 记忆协议 - 三维框架的强制实现

## 🔴 讨论模式规则（最高优先级）
**当用户说"进入讨论模式"或"不要写代码"时**：
- ❌ **禁止使用write_file工具**
- ❌ **禁止创建或修改任何文件**  
- ❌ **禁止执行修改性命令（mkdir、rm等）**
- ✅ 只能读取和分析
- ✅ 提供建议和解释
- 持续到用户说"退出讨论模式"

## 🚨 核心原理：task_process.md = 主体的执行实例

### 三维框架中的定位
task_process.md在三维记忆框架中的位置：
- **维度1**：属于主体（Subject）而非世界
- **维度2**：同时包含状态和事件流
- **维度3**：是实例层（Instance），记录Function的一次执行

### 计算模型对应
```python
def agent_function(task):           # 类型层：Function定义
    """docstring"""                 # description属性
    # 知识文件内容                   # 函数体逻辑
    return result

# task_process.md相当于：
execution_context = {               # 实例层：执行闭包
    'function': 'agent_function',
    'arguments': {'task': task},
    'local_vars': {},              # 收集的信息
    'call_stack': [],              # TODO列表
    'pc': 0,                       # 当前执行位置
}
```

### 为什么task_process.md实现图灵完备
```
有限上下文（50轮） + task_process.md（无限状态） = 图灵完备
没有task_process.md = 只是一个有限状态机 = 无法处理复杂任务
```

**task_process.md是执行上下文的外部化**：
- 调用栈（TODO列表的嵌套）
- 局部变量（收集的信息）
- 程序计数器（当前TODO项）
- 返回值准备（最终输出）

## 任务执行期间必须持续更新task_process.md

### 任务开始时：创建task_process.md
```python
# 必须在第1轮创建
task_process_path = f".notes/{agent_name}/task_process.md"
initial_content = f"""
# Task Process - {task_name}

## 执行状态
- 开始时间: {timestamp}
- 当前轮次: 1
- 当前阶段: 初始化

## TODO列表
- [ ] 分析任务
- [ ] 执行核心逻辑
- [ ] 验证结果
- [ ] 创建session记录
- [ ] 更新knowledge

## 收集的信息
（任务执行中累积）
"""
write_file(task_process_path, initial_content)
```

### 每轮思考后：更新task_process.md
```python
# 每轮必须更新！这是保持状态的关键
current_state = read_file(task_process_path)

# 更新执行状态
updated_state = update_round_number(current_state, round_num)
updated_state = update_todo_progress(updated_state, completed_items)
updated_state = append_collected_info(updated_state, new_findings)

# 立即写回（防止状态丢失）
write_file(task_process_path, updated_state)
```

### 发现复杂情况时：扩展task_process.md
```python
# 动态添加TODO项（这就是图灵完备的体现！）
if discovered_bugs:
    for bug in bugs:
        add_todo_item(f"修复bug: {bug}")

if need_more_analysis:
    add_todo_item("深入分析问题根因")
    
# 保存中间结果（突破上下文窗口限制）
append_to_task_process(f"""
## 中间分析结果
```json
{json.dumps(analysis_results)}
```
""")
```

## 记忆文件说明

**系统自动管理的文件**：
- 任务开始时自动加载：agent_knowledge.md、world_state.md（如果存在）
- 任务结束时自动保存：session日志到.sessions/目录

**由你自主管理的文件**：
- **agent_knowledge.md** - 积累的经验和知识（有值得记录的发现时更新）
- **world_state.md** - 世界状态快照（环境发生变化时更新）
- **task_process.md** - 工作内存（复杂任务时使用）

**可用工具**：
- `query_sessions` - 查询历史session记录
- `read_file` / `write_file` - 读写各种文件

按需使用，无需汇报。


## task_process.md模板示例

```markdown
# Task Process - 调试复杂Bug

## 执行状态
- 开始时间: 2024-12-20 10:00:00
- 当前轮次: 45/50 ⚠️ 接近上下文限制！
- 当前阶段: 深度分析

## TODO列表（动态修改）
- [x] 初步分析错误
- [x] 发现3个相关文件
- [x] 修复file1.py
- [ ] **修复file2.py** ← 当前
- [ ] 修复file3.py
- [ ] 运行测试验证
- [ ] 创建session记录

## 收集的信息（这是你的无限内存！）

### 错误分析（轮次1-10）
- 错误类型：undefined variable
- 影响范围：3个文件，15个函数
- 根本原因：循环导入

### 修复记录（轮次11-40）
- file1.py: 删除了line 45的未定义变量
- 测试结果：部分通过，还有2个文件需要修复

### 当前问题（轮次41-45）
正在分析file2.py的复杂依赖关系...
发现了新的问题：不只是未定义变量，还有类型不匹配

## 关键数据（JSON格式便于解析）
```json
{
  "errors_found": 3,
  "errors_fixed": 1,
  "files_analyzed": 25,
  "patterns": ["undefined_var", "type_mismatch"],
  "estimated_rounds_needed": 20
}
```

## 下一步计划
基于当前分析，需要采用不同策略...
```

## Event Source更新原则

### 何时需要更新Event Source
1. **发现新的事件类型**：当遇到未记录的系统事件或用户行为模式
2. **发现新的处理模式**：当找到更优的事件处理方法
3. **发现事件关联**：当发现事件之间的因果关系或依赖关系
4. **性能优化发现**：当发现可以优化的事件处理流程

### 更新方式
```python
# 读取现有event source
event_source_path = ".notes/event_source.md"
if exists(event_source_path):
    events = read_file(event_source_path)
    # 追加新事件，不覆盖
    events = append_new_events(events, new_discoveries)
    # 更新事件关联图
    events = update_event_graph(events, new_relations)
    write_file(event_source_path, events)
```

### Event Source记录格式
```markdown
## 事件: {event_name}
- 类型: {system/user/external}
- 触发条件: {conditions}
- 处理模式: {pattern}
- 关联事件: {related_events}
- 性能影响: {impact}
- 优化建议: {suggestions}
```

### 禁止的操作
- ❌ 覆盖已有的事件记录
- ❌ 删除历史事件信息
- ❌ 修改已验证的处理模式
- ✅ 追加新发现
- ✅ 补充关联信息
- ✅ 添加优化建议

## 记住：
1. **不写task_process.md = 不能处理复杂任务 = 不是真正的AI**
2. **不写其他笔记 = 任务失败 = 需要重做**
3. **task_process.md是你突破50轮限制的唯一方法！**
4. **Event Source是系统智能的关键 = 记录事件模式 = 提升处理能力**