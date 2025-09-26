# 隐式常识契约 - Agent世界的无言共识

## 核心理念

人类社会运行在大量隐式契约之上：
- 餐厅流程：点餐→吃饭→付款（无需说明）
- GitHub仓库：必有README.md（约定俗成）
- 电梯礼仪：先出后进（社会共识）

Agent系统同样需要隐式契约，减少显式配置和文档。

## Agent文件系统契约

### 标准目录结构
```
~/.agent/[agent_name]/       # Agent的家（永恒不变）
├── state.json              # 当前状态（自动保存）
├── agent_knowledge.md      # 能力定义（DNA）
├── experience.md           # 经验积累（<10KB）
├── compact.md             # 压缩记忆
└── temp/                  # 临时文件

output.log                 # 异步执行结果（隐式契约）
error.log                  # 错误日志（隐式契约）
/tmp/                      # 临时工作区（隐式契约）
```

### 文件命名契约
- `*.log`：日志文件，追加写入
- `*.md`：知识文档，人类可读
- `*.json`：结构化数据
- `test_*`：测试相关
- `*_async`：异步执行
- `*_temp`：临时文件，可删除

## 执行流程契约

### 异步执行
```python
# 隐式契约：后台任务输出到log文件
python async_agent_runner.py agent_name "task" --background
# 结果自动写入 output.log

# 隐式契约：查看结果
tail -f output.log  # 无需文档说明
```

### 并发执行
```python
# 隐式契约：结果按完成顺序追加
runner.execute_parallel([
    {"agent": "agent1", "task": "task1"},
    {"agent": "agent2", "task": "task2"}
])
# 所有结果追加到 output.log
```

### 错误处理
```python
# 隐式契约：错误写入error.log
try:
    agent.execute(task)
except Exception as e:
    # 自动写入 error.log
```

## 生命周期契约

### Agent加载
```python
# 隐式契约：load()总是从home目录加载
agent = load("agent_name")
# 自动加载 ~/.agent/agent_name/ 的所有文件
```

### 状态保存
```python
# 隐式契约：execute后自动保存
agent.execute(task="...")
# 状态自动保存到 state.json
```

### 后台运行
```bash
# 隐式契约：nohup输出到nohup.out
nohup python run_agent.py &
# 查看 nohup.out 或 output.log
```

## 交互契约

### 特殊命令
- `/compact`：压缩记忆
- `/status`：查看状态
- `/help`：获取帮助
- `@function`：调用知识函数

### 任务格式
- 普通文本：直接执行
- JSON格式：结构化参数
- Markdown：保持格式
- 代码块：原样执行

## 知识传递契约

### 父子继承
```python
# 隐式契约：子Agent继承父Agent的知识
child = parent.create_agent(...)
# 自动继承 agent_knowledge.md
```

### 经验积累
```python
# 隐式契约：experience.md < 10KB
# 超过自动压缩或归档
```

## 工具契约

### 工具返回值
- 成功：返回结果字符串
- 失败：抛出异常
- 进度：写入日志文件

### 工具命名
- `read_*`：读取操作
- `write_*`：写入操作
- `execute_*`：执行操作
- `create_*`：创建操作

## 最佳实践

### 1. 相信隐式契约
```python
# 不好：过度配置
AsyncRunner(
    output_file="output.log",  # 多余
    error_file="error.log",     # 多余
    work_dir="/tmp"            # 多余
)

# 好：依赖隐式契约
AsyncRunner()  # 自动使用标准位置
```

### 2. 遵循命名规范
```python
# 好：符合隐式契约
"output.log"      # 标准输出
"error.log"       # 错误日志
"test_agent.py"   # 测试文件

# 不好：自创规范
"results.txt"     # 不标准
"failures.log"    # 不标准
```

### 3. 利用文件系统
```python
# 隐式契约：文件系统即数据库
agent_home/
├── state.json     # 当前状态
├── history/       # 历史记录
└── cache/         # 缓存数据
```

## 契约的价值

1. **减少认知负担**：无需记忆配置
2. **提高互操作性**：所有Agent遵循相同契约
3. **简化调试**：知道去哪里找日志
4. **加速开发**：减少文档查阅

## 契约的进化

隐式契约不是一成不变的，而是通过实践逐渐形成和优化的：

1. **观察模式**：发现重复出现的模式
2. **提炼契约**：将模式固化为契约
3. **传播共识**：通过使用传播契约
4. **优化迭代**：根据反馈改进契约

## 总结

隐式常识契约让Agent系统更接近人类的自然交互方式。就像我们不需要手册就能使用餐厅服务一样，Agent系统也应该通过隐式契约实现"开箱即用"的体验。

**记住**：最好的设计是不需要说明的设计。