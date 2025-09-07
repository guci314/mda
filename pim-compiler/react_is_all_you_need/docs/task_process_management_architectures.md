# task_process.md管理架构方案

## 核心问题

task_process.md是Agent的**工作内存**，谁应该负责管理它？

### 设计矛盾
1. **自主性**：程序应该管理自己的内存（Linux进程管理堆栈）
2. **可靠性**：系统需要保证内存被正确管理（防止内存泄漏）
3. **透明性**：程序可能不知道需要管理内存（向后兼容）

## 方案1：自主管理模式（Linux用户态模式）

```python
# ProgramAgent完全负责task_process.md
ProgramAgent:
    knowledge_files = ["task_knowledge.md", "task_process_management.md"]
    
    执行时:
    1. 自己创建task_process.md
    2. 每轮更新task_process.md
    3. 任务完成时清理

OSAgent:
    只负责.sessions/和.notes/agent_knowledge.md
```

### 实现方式
```markdown
# task_process_management.md（给ProgramAgent的知识）

## 工作内存管理协议

你必须管理自己的task_process.md：

### 任务开始时
write_file(".notes/{agent_name}/task_process.md", initial_todo)

### 每轮思考后
current_state = read_file(".notes/{agent_name}/task_process.md")
updated_state = update_with_progress(current_state)
write_file(".notes/{agent_name}/task_process.md", updated_state)

### 任务完成时
final_state = mark_all_completed()
write_file(".notes/{agent_name}/task_process.md", final_state)
```

**优点**：
- ✅ 符合直觉（程序管理自己的内存）
- ✅ ProgramAgent有完全控制权
- ✅ 可以优化内存使用

**缺点**：
- ❌ 依赖ProgramAgent配合
- ❌ 可能忘记更新
- ❌ 无法强制执行

## 方案2：Hook注入模式（Linux信号机制）

```python
class ReactAgentWithHooks(ReactAgentMinimal):
    def __init__(self, hooks=None):
        self.hooks = hooks or {}
        # hooks: before_think, after_think, before_tool, after_tool
    
    def think(self, messages):
        if 'before_think' in self.hooks:
            self.hooks['before_think'](self, messages)
        
        thought = super().think(messages)
        
        if 'after_think' in self.hooks:
            self.hooks['after_think'](self, thought)
        
        return thought
```

### OSAgent通过Hook管理

```python
def task_process_hook(agent, thought):
    """OSAgent注入的hook，自动更新task_process.md"""
    # 解析thought，提取状态
    state = extract_state(thought)
    
    # 更新task_process.md
    update_task_process(agent.work_dir, state)

# 创建ProgramAgent时注入hook
program_agent = ReactAgentMinimal(
    knowledge_files=["task.md"],
    hooks={'after_think': task_process_hook}
)
```

**优点**：
- ✅ 不需要修改ProgramAgent知识
- ✅ 强制执行，无法逃避
- ✅ 向后兼容

**缺点**：
- ❌ 需要修改ReactAgentMinimal代码
- ❌ Hook逻辑可能复杂
- ❌ 性能开销

## 方案3：Shadow记录模式（Linux strace模式）

```python
# OSAgent偷偷记录ProgramAgent的所有行为
class OSAgent:
    def execute_with_shadow(self, task):
        # 创建shadow进程（另一个agent）
        shadow = ReactAgentMinimal(
            knowledge_files=["shadow_recorder.md"]
        )
        
        # 并行执行
        program_result = program_agent.execute(task)
        shadow_record = shadow.observe(program_agent.messages)
        
        # 合并结果写入task_process.md
        merge_to_task_process(program_result, shadow_record)
```

### Shadow知识
```markdown
# shadow_recorder.md

你是一个shadow recorder，观察另一个agent的执行：

1. 分析每轮对话
2. 提取关键状态
3. 构建task_process.md内容
4. 不干预执行，只记录
```

**优点**：
- ✅ ProgramAgent完全不知情
- ✅ 不影响执行
- ✅ 可以智能提取

**缺点**：
- ❌ 需要额外的计算资源
- ❌ 可能理解偏差
- ❌ 复杂度高

## 方案4：代理模式（Linux VFS模式）

```python
# OSAgent代理所有文件操作
class FileSystemProxy:
    def __init__(self, os_agent):
        self.os_agent = os_agent
    
    def write_file(self, path, content):
        # 拦截写操作
        if "task_process.md" not in path:
            # 自动创建/更新task_process.md
            self.os_agent.update_task_process(content)
        
        # 执行原始写操作
        return original_write_file(path, content)

# ProgramAgent的所有文件操作都被代理
program_agent.tools['write_file'] = FileSystemProxy(os_agent)
```

**优点**：
- ✅ 完全透明
- ✅ 强制记录所有操作
- ✅ 可以智能推断

**缺点**：
- ❌ 需要代理所有工具
- ❌ 可能误判
- ❌ 实现复杂

## 方案5：协作模式（微内核架构）

```python
# 分工明确，各司其职
ProgramAgent:
    负责：task_process.md的内容（TODO项、状态）
    
OSAgent:
    负责：task_process.md的结构（创建、格式、生命周期）
```

### 实现方式
```python
# OSAgent创建框架
os_agent.create_task_process_template()

# ProgramAgent填充内容
program_agent.execute(task)  # 会更新内容

# OSAgent验证和归档
os_agent.validate_task_process()
os_agent.archive_to_session()
```

### 协议定义
```markdown
## 职责边界

OSAgent负责：
1. 创建task_process.md模板
2. 设置权限和路径
3. 任务结束时归档

ProgramAgent负责：
1. 更新TODO列表
2. 记录中间状态
3. 标记完成状态
```

**优点**：
- ✅ 职责清晰
- ✅ 双方都有自主权
- ✅ 互不干扰

**缺点**：
- ❌ 需要协议约定
- ❌ 仍依赖配合
- ❌ 可能有空隙

## 方案6：混合智能模式（自适应架构）

```python
class AdaptiveOSAgent:
    def manage_task_process(self, program_agent):
        # 检测ProgramAgent的配合度
        cooperation_level = self.detect_cooperation(program_agent)
        
        if cooperation_level == 'high':
            # 自主模式：让ProgramAgent自己管理
            return 'autonomous'
        elif cooperation_level == 'medium':
            # Hook模式：辅助管理
            self.inject_hooks(program_agent)
            return 'assisted'
        else:
            # Shadow模式：强制管理
            self.enable_shadow_recording(program_agent)
            return 'enforced'
```

### 检测机制
```python
def detect_cooperation(self, agent):
    # 检查agent的知识文件
    if 'task_process_management.md' in agent.knowledge_files:
        return 'high'
    
    # 检查前几轮是否主动创建task_process
    if agent.created_task_process_in_first_rounds():
        return 'medium'
    
    return 'low'
```

**优点**：
- ✅ 灵活适应不同agent
- ✅ 渐进式管理
- ✅ 最优性能

**缺点**：
- ❌ 实现复杂
- ❌ 需要智能判断
- ❌ 可能误判

## 方案对比矩阵

| 方案 | 自主性 | 可靠性 | 复杂度 | 性能影响 | 推荐场景 |
|------|--------|--------|--------|----------|----------|
| 自主管理 | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | 可信agent |
| Hook注入 | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 通用场景 |
| Shadow记录 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ | 不可信agent |
| 代理模式 | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 完全控制 |
| 协作模式 | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | 团队开发 |
| 混合智能 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | 复杂系统 |

## 推荐方案：渐进式实施

### 第一阶段：自主管理（最简单）
先假设ProgramAgent会配合，通过知识文件引导：
```python
# 只需要添加知识文件
knowledge_files = ["task.md", "task_process_management.md"]
```

### 第二阶段：Hook增强（保险机制）
发现问题后，添加简单的hook：
```python
def simple_hook(agent, thought):
    if not exists("task_process.md"):
        create_default_task_process()

hooks = {'after_think': simple_hook}
```

### 第三阶段：智能适配（最终形态）
根据实际运行情况，智能选择管理策略：
```python
os_agent = AdaptiveOSAgent()
os_agent.manage(program_agent)  # 自动选择最佳策略
```

## 哲学思考：信任vs控制

### Linux的智慧
Linux相信进程会正确使用malloc/free，但通过：
1. **页错误处理**：捕获异常访问
2. **OOM Killer**：处理内存耗尽
3. **审计系统**：记录所有操作

### Agent的平衡
我们应该：
1. **相信**：ProgramAgent会管理task_process.md
2. **但验证**：OSAgent检查是否正确管理
3. **有后备**：Hook/Shadow作为保险

## 最终建议

**短期（现在）**：方案1（自主管理）
- 简单直接
- 通过知识文件实现
- 不需要改代码

**中期（优化）**：方案2（Hook注入）
- 添加简单的hook支持
- 保证关键操作
- 向后兼容

**长期（理想）**：方案6（混合智能）
- 自适应管理
- 最优性能
- 完美平衡

> "Trust, but verify." - Ronald Reagan
>
> "让ProgramAgent自主管理task_process.md，但OSAgent要验证和保底。"