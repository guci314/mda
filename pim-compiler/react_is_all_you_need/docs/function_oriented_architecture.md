# Function-Oriented Architecture: Agent即Function

## 核心洞察

**不需要写新的Python代码！** ReactAgentMinimal本身就是一个完美的Function：

```python
ReactAgentMinimal: (task, knowledge_files) -> result
```

我们需要的只是**不同的知识组合**来创建不同的Function实例。

## 架构本质

### 传统思维（错误）
```
需要新类 -> 写Python代码 -> 继承/组合 -> 复杂架构
```

### Function思维（正确）
```
需要新行为 -> 写知识文件 -> 组合Function -> 简单架构
```

## 实现方案：纯知识驱动

### 1. OSAgent = ReactAgentMinimal + 系统知识

```python
# 不需要新类！直接用ReactAgentMinimal
os_agent = ReactAgentMinimal(
    work_dir="project",
    name="os_agent",
    knowledge_files=[
        "knowledge/os_agent_knowledge.md",      # OS行为定义
        "knowledge/structured_notes.md",        # 笔记架构
        "knowledge/mandatory_protocol.md"       # 强制协议
    ]
)

# 执行OS任务
os_agent.execute(task="""
收到用户任务：生成博客系统
任务类型：generate
知识文件：["generation_knowledge.md", "blog_psm.md"]

请按照OS-Agent协议执行任务。
""")
```

### 2. ProgramAgent = ReactAgentMinimal + 任务知识

```python
# ProgramAgent也不需要新类！
program_agent = ReactAgentMinimal(
    work_dir="project",
    name="program_agent",
    knowledge_files=[
        "knowledge/generation_knowledge.md",    # 任务知识
        "blog_psm.md"                           # 具体规范
        # 注意：没有structured_notes.md！
    ]
)

# 执行程序任务
result = program_agent.execute(task="根据PSM生成代码")
```

### 3. OSAgent如何调用ProgramAgent

在`os_agent_knowledge.md`中定义的行为：

```markdown
## 执行任务时

我需要创建一个ProgramAgent来执行任务：

1. 使用execute_command运行Python代码：
```python
execute_command("""
python -c "
from core.react_agent_minimal import ReactAgentMinimal

# 创建ProgramAgent（只有任务知识）
agent = ReactAgentMinimal(
    work_dir='.',
    name='program_agent',
    knowledge_files=['generation_knowledge.md']
)

# 执行任务
result = agent.execute(task='生成代码')

# 保存结果供OSAgent读取
with open('.temp_result.txt', 'w') as f:
    f.write(result)
"
""")
```

2. 读取结果：
```python
result = read_file(".temp_result.txt")
```

3. 创建笔记（我的职责）：
```python
write_file(".sessions/xxx.md", session_content)
```
```

## 更优雅的方案：使用脚本

### 创建执行脚本

`scripts/run_program_agent.py`:
```python
#!/usr/bin/env python3
import sys
import json
from core.react_agent_minimal import ReactAgentMinimal

# 从参数读取配置
config = json.loads(sys.argv[1])

# 创建纯执行Agent
agent = ReactAgentMinimal(
    work_dir=config['work_dir'],
    name=config['name'],
    knowledge_files=config['knowledge_files']
)

# 执行任务
result = agent.execute(task=config['task'])

# 输出结果
print(json.dumps({
    'result': result,
    'rounds': agent.round_num
}))
```

### OSAgent调用脚本

```python
# 在os_agent_knowledge.md中
config = {
    'work_dir': '.',
    'name': 'program_agent',
    'knowledge_files': ['generation_knowledge.md'],
    'task': '生成代码'
}

result_json = execute_command(f"""
python scripts/run_program_agent.py '{json.dumps(config)}'
""")

result = json.loads(result_json)
```

## 架构优势

### 1. 零新增代码
- ✅ 不需要ProgramAgentTool类
- ✅ 不需要OSAgent类
- ✅ 不需要修改ReactAgentMinimal
- ✅ 只需要知识文件！

### 2. 完美的Function组合
```
OSFunction = ReactAgentMinimal + 系统知识
ProgramFunction = ReactAgentMinimal + 任务知识
DebugFunction = ReactAgentMinimal + 调试知识
...
```

### 3. 知识即程序
- 行为定义在Markdown中
- 知识文件就是程序
- 修改知识就是修改程序

## 实际执行流程

### 用户接口
```python
# 用户只需要这样
from core.react_agent_minimal import ReactAgentMinimal

# 创建OS-Agent
os = ReactAgentMinimal(
    work_dir="my_project",
    name="os",
    knowledge_files=["knowledge/os_agent_knowledge.md"]
)

# 执行管理任务
os.execute("""
用户任务：生成博客系统代码
PSM文件：blog_psm.md
请创建ProgramAgent执行任务，并管理笔记。
""")
```

### OSAgent执行过程
```
1. 读取os_agent_knowledge.md，理解自己的职责
2. 创建目录结构（.sessions/, .notes/）
3. 使用execute_command创建ProgramAgent执行任务
4. 读取执行结果
5. 创建session记录（强制）
6. 更新knowledge文件（强制）
7. 更新world_state（强制）
8. 返回结果给用户
```

## 与Python类设计的对比

| 方面 | 类设计方案 | Function方案 |
|------|------------|--------------|
| 代码量 | 需要写200+行Python | 0行Python |
| 复杂度 | 类继承、方法覆盖 | 只是Function调用 |
| 维护性 | 改代码需要测试 | 改知识立即生效 |
| 灵活性 | 编译时固定 | 运行时动态 |
| 学习曲线 | 需要懂OOP | 只需要懂Markdown |

## 哲学意义

### Agent即Function
```haskell
-- Haskell风格的类型签名
type Agent = Task -> Knowledge -> Result

-- 具体实例
osAgent :: Agent
osAgent task knowledge = executeWithManagement task knowledge

programAgent :: Agent  
programAgent task knowledge = executePure task knowledge
```

### 知识即程序
```lisp
;; Lisp风格的代码即数据
(define os-agent
  '(knowledge (structured-notes mandatory-protocol)))

(define program-agent
  '(knowledge (task-specific domain-patterns)))

(execute os-agent user-task)
```

## 实施计划

### 第一步：创建知识文件
- [x] os_agent_knowledge.md - OS层行为
- [ ] program_executor.md - 纯执行行为
- [ ] task_router.md - 任务路由知识

### 第二步：创建辅助脚本
- [ ] scripts/run_program_agent.py - 执行ProgramAgent
- [ ] scripts/run_os_agent.py - 执行OSAgent

### 第三步：测试Function组合
```python
# 测试OS管理
os = ReactAgentMinimal(knowledge_files=["os_agent_knowledge.md"])
result = os.execute("管理任务执行")
assert ".sessions/" 中有新文件
assert "agent_knowledge.md" 被更新
```

## 结论

**我们不需要写新的Python代码！**

ReactAgentMinimal已经是完美的Function容器。通过不同的知识组合，我们可以创建任意复杂的Agent系统：

- OSAgent = ReactAgentMinimal + 管理知识
- ProgramAgent = ReactAgentMinimal + 执行知识
- DebugAgent = ReactAgentMinimal + 调试知识
- ...

这才是真正的"React is All You Need"：
1. React提供执行机制
2. Knowledge提供行为定义
3. Function组合创造一切

> "程序 = 数据结构 + 算法"
> 
> 在我们的架构中：
> "Agent = ReactFunction + Knowledge"

知识就是新的算法，而ReactAgentMinimal就是通用的执行器。我们通过编写知识而不是代码来编程。这是向着真正的AGI迈出的关键一步：**用自然语言编程**。