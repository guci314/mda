# 极简异步Agent设计文档

## 核心理念：Agent活在文件系统中

### 1. 基本原理
```python
# Agent = Home目录 + 加载器
~/.agent/[agent_name]/  # Agent的永恒家园
    ├── state.json      # 状态
    ├── agent_knowledge.md  # 能力
    ├── experience.md   # 经验
    └── compact.md      # 记忆

# 加载 = 复活
agent = load("agent_name")

# 执行 = 工作
result = agent.execute(task="...")

# 保存 = 休眠（自动）
```

### 2. 极简异步实现
```python
# async_agent_runner.py 核心代码（< 20行）
from core.react_agent_minimal import ReactAgentMinimal
import subprocess

def load(agent_name: str) -> ReactAgentMinimal:
    """从home目录加载Agent"""
    return ReactAgentMinimal(name=agent_name, stateful=True)

def run_async(agent_name: str, task: str):
    """后台运行Agent"""
    cmd = f'''
from async_agent_runner import load
agent = load("{agent_name}")
result = agent.execute(task="{task}")
print(result)
'''
    # 隐式契约：输出到output.log
    with open("output.log", "a") as f:
        subprocess.Popen(["python", "-c", cmd], stdout=f)
```

### 3. 隐式契约系统

#### 文件契约
- `output.log` - 异步执行结果
- `error.log` - 错误信息
- `~/.agent/*/` - Agent家目录

#### 执行契约
- 后台运行 → 输出重定向到log
- 并发执行 → 结果按序追加
- 长任务 → 定期写入进度

### 4. 并发方案对比

| 方案 | 实现复杂度 | 真并发 | 符合原则 |
|------|-----------|--------|----------|
| 后台Python脚本 | ⭐ | ✅ | ✅ |
| ThreadPoolExecutor | ⭐⭐ | ✅ | ✅ |
| ProcessPoolExecutor | ⭐⭐ | ✅ | ✅ |
| 修改ReactAgentMinimal | ⭐⭐⭐⭐⭐ | ✅ | ❌ |

### 5. 使用示例

#### 基础用法
```bash
# 同步执行
python -c "from async_agent_runner import load; load('agent1').execute('task')"

# 异步执行
python async_agent_runner.py agent1 "task" --async

# 后台执行
nohup python -c "..." &

# 并行执行
parallel python -c "load('{}').execute('task')" ::: agent1 agent2 agent3
```

#### 高级用法
```python
# Agent农场 - 批量管理
class AgentFarm:
    def __init__(self, num_workers=4):
        self.pool = ProcessPoolExecutor(num_workers)

    def submit(self, agent_name, task):
        return self.pool.submit(lambda: load(agent_name).execute(task))

# 使用
farm = AgentFarm()
futures = [farm.submit(f"agent_{i}", f"task_{i}") for i in range(10)]
results = [f.result() for f in futures]
```

### 6. 实现要点

#### 必须实现
- [x] load() 函数：从home目录加载Agent
- [x] 隐式契约：output.log自动记录
- [x] 后台运行：subprocess或nohup

#### 可选优化
- [ ] 进度报告：定期写入状态
- [ ] 错误重试：最多3次
- [ ] 资源限制：控制并发数
- [ ] 日志轮转：防止log过大

### 7. 架构优势

1. **极简**：< 100行代码实现完整异步
2. **解耦**：Agent核心保持同步和简单
3. **灵活**：支持多种并发模式
4. **持久**：Agent状态永久保存
5. **符合原则**：不修改ReactAgentMinimal

### 8. 待实现功能

```python
# TODO: 实现这些功能（当需要时）

class AsyncAgentManager:
    """异步Agent管理器"""

    def list_running(self):
        """列出运行中的Agent"""
        pass

    def kill(self, agent_name):
        """终止Agent执行"""
        pass

    def get_status(self, agent_name):
        """获取Agent状态"""
        pass

    def schedule(self, agent_name, task, cron):
        """定时执行任务"""
        pass
```

### 9. 设计哲学

> "Agent不是运行在内存中的对象，而是活在文件系统中的实体"

- Agent的本质是其home目录
- 执行只是临时唤醒
- 并发通过多进程实现
- 隐式契约减少配置

### 10. 实施计划

1. **Phase 1**（已完成）：基础异步执行
2. **Phase 2**：添加进度报告
3. **Phase 3**：实现Agent农场
4. **Phase 4**：添加Web界面

---

**注**：本文档描述了极简异步Agent的设计理念和实现方案。实际实现时应保持简洁，避免过度工程化。记住："最好的异步是不需要异步框架的异步"。