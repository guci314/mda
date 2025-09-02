# Agent社会架构设计文档

## 1. 概述

### 1.1 项目背景

传统的分布式系统依赖复杂的中间件（Spring Cloud、Kafka、Service Mesh等），配置繁琐，学习曲线陡峭。本项目通过Function统一理论，使用极简的方式构建可自组织的Agent社会。

### 1.2 核心理念

- **Function统一**：Agent和Tool本质上都是Function，可以互相调用
- **知识驱动**：用Markdown知识文件定义行为，而非硬编码
- **文件系统即数据库**：使用文件系统作为存储和通信媒介
- **简单轮询**：使用100ms轮询替代复杂的事件驱动
- **自然语言接口**：Agent之间使用自然语言通信

### 1.3 设计目标

1. **极简性**：核心代码不超过500行
2. **零依赖**：只需Python和文件系统
3. **可理解**：小学生都能理解的架构
4. **可扩展**：支持数百个Agent协作
5. **自组织**：Agent可以自主发现和协作

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────┐
│                Agent社会 (P2P架构)                  │
├─────────────────────────────────────────────────────┤
│                                                      │
│  ┌──────────────┐                                   │
│  │   Registry   │ ←── Tool实现，非Agent             │
│  │     Tool     │     提供服务发现                  │
│  └──────┬───────┘                                   │
│         │                                            │
│    查询 │ 注册                                       │
│         │                                            │
│  ┌──────▼─────┐ ┌─────────┐ ┌─────────┐           │
│  │  Worker 1  │ │Worker 2 │ │Worker 3 │  ...       │
│  │   Agent    │⇄│  Agent  │⇄│  Agent  │  P2P通信  │
│  └────────────┘ └─────────┘ └─────────┘           │
│                                                      │
├─────────────────────────────────────────────────────┤
│                  文件系统层                         │
│  ┌────────────────────────────────────────────┐    │
│  │ infrastructure/                            │    │
│  │ ├── registry.json  (服务注册表)            │    │
│  │ └── agents/        (Agent工作目录)         │    │
│  │     ├── worker_1/inbox/  (消息收件箱)     │    │
│  │     ├── worker_2/inbox/                    │    │
│  │     └── worker_3/inbox/                    │    │
│  └────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────┘
```

### 2.2 组件说明

#### 2.2.1 Registry Tool

**职责**：
- 维护Agent注册信息
- 提供服务发现
- 无状态的数据访问

**实现方式**：
```python
class RegistryTool(Tool):
    """注册表工具 - 无状态的数据访问"""
    def execute(self, action, **kwargs):
        with FileLock("registry.lock"):  # 文件锁
            if action == "register":
                return self._register(kwargs)
            elif action == "query":
                return self._query(kwargs)
            elif action == "list":
                return self._list_all()
```

**数据结构** (registry.json)：
```json
{
  "agent_name": {
    "capabilities": ["Python", "debug"],
    "status": "online",
    "inbox_path": "agents/agent_name/inbox/",
    "last_seen": 1234567890
  }
}
```

#### 2.2.2 Worker Agent

**职责**：
- 执行具体任务
- 与其他Agent协作
- 维护自身状态

**通信机制**：
- **P2P直接通信**：Agent之间直接读写对方inbox
- **同步调用**：发送消息后轮询等待响应
- **异步调用**：发送消息后继续执行其他任务

**消息格式**：
```json
{
  "id": "消息ID",
  "from": "发送者Agent",
  "task": "任务描述",
  "timestamp": "时间戳",
  "timeout": 10  // 可选，同步调用超时时间
}
```


### 2.3 目录结构

```
project_root/
├── core/
│   ├── react_agent_minimal.py     # 核心Agent实现(~500行)
│   ├── tool_base.py               # Function基类
│   └── tools/                     # 工具集
│       └── registry_tool.py      # Registry工具
│
├── knowledge/                      # 知识文件
│   ├── worker_knowledge.md        # Worker行为定义
│   └── agent_society_protocols.md # 社会规范
│
├── infrastructure/                 # 运行时目录
│   ├── registry.json              # 服务注册表
│   ├── registry.lock              # 文件锁
│   └── agents/                    # Agent工作目录
│       ├── worker_001/
│       │   ├── inbox/             # 收件箱
│       │   ├── output.log         # 执行日志
│       │   └── .notes/            # Agent笔记
│       └── worker_002/
│           └── ...
│
└── start_society.py               # 启动脚本
```

## 3. 核心机制

### 3.1 Function统一机制

```python
# 所有实体都是Function
class Function(ABC):
    def execute(self, **kwargs) -> str:
        pass
    
    def __call__(self, **kwargs) -> str:
        return self.execute(**kwargs)

# Agent是Function
class ReactAgentMinimal(Function):
    def execute(self, task: str) -> str:
        # Think-Act-Observe循环
        ...

# Tool也是Function  
class ReadFileTool(Function):
    def execute(self, file_path: str) -> str:
        ...

# Agent可以调用Agent（因为都是Function）
agent1 = ReactAgentMinimal(tools=[agent2, agent3])
```

### 3.2 通信机制

#### 3.2.1 同步调用（伪同步）

```python
def call_agent_sync(self, target, task, timeout=10):
    """同步调用另一个Agent"""
    # 1. 发送消息到目标inbox
    msg_id = str(uuid.uuid4())
    message = {
        "id": msg_id,
        "from": self.name,
        "task": task,
        "timestamp": time.time()
    }
    with open(f"agents/{target}/inbox/{msg_id}.json", "w") as f:
        json.dump(message, f)
    
    # 2. 轮询等待响应
    start = time.time()
    while time.time() - start < timeout:
        response_file = f"agents/{self.name}/inbox/resp_{msg_id}.json"
        if os.path.exists(response_file):
            with open(response_file) as f:
                response = json.load(f)
            os.remove(response_file)
            return response["result"]
        time.sleep(0.1)  # 100ms轮询
    
    return None  # 超时
```

#### 3.2.2 异步调用

```python
def call_agent_async(self, target, task, callback=None):
    """异步调用另一个Agent"""
    msg_id = send_message(target, task)
    if callback:
        self.pending_callbacks[msg_id] = callback
    return msg_id
```

#### 3.2.3 轮询机制

```python
def run_daemon(self):
    """Agent守护进程模式"""
    while True:
        # 扫描自己的inbox
        messages = self.scan_inbox()
        for msg in messages:
            result = self.run(msg['task'])
            # 发送响应到请求者的inbox
            self.send_response(msg['from'], result)
        
        # 检查异步回调
        self.check_callbacks()
        
        time.sleep(0.1)  # 100ms延迟
```

**为什么选择轮询**：
- 简单可靠，没有复杂的事件机制
- 100ms延迟对人类无感（人类反应时间~200ms）
- 避免了inotify、信号等系统依赖
- 易于理解和调试

### 3.3 服务发现机制

```python
class ReactAgentMinimal:
    def __init__(self):
        # Registry作为Tool而非Agent
        self.registry = RegistryTool()
        self.tools = [self.registry, ...]
    
    def register_self(self):
        """注册自己"""
        self.registry.execute("register", 
            name=self.name,
            capabilities=self.capabilities
        )
    
    def find_helper(self, capability):
        """查找能帮助的Agent"""
        candidates = self.registry.execute("query",
            capability=capability
        )
        return candidates[0] if candidates else None
    
    def delegate_task(self, task, capability):
        """委托任务给其他Agent"""
        helper = self.find_helper(capability)
        if helper:
            return self.call_agent_sync(helper, task)
        return "No suitable agent found"
```

### 3.4 知识驱动机制

知识文件定义Agent行为：

```markdown
# worker_knowledge.md

## 当收到调试任务时
1. 读取错误日志
2. 分析错误类型
3. 定位问题代码
4. 生成修复方案
5. 应用修复
6. 验证结果

## 当需要帮助时
1. 问Registry谁能帮忙
2. 向Router发送协作请求
3. 等待响应
```

Agent读取知识并执行：
```python
agent = ReactAgentMinimal(
    knowledge_files=["worker_knowledge.md"]
)
```

## 4. 协作模式

### 4.1 服务注册与发现

```
Worker调用Registry Tool:
1. Worker -> RegistryTool.register(capabilities)
2. RegistryTool -> 更新registry.json
3. RegistryTool -> 返回成功

Worker查找协作者:
1. Worker -> RegistryTool.query("Python")
2. RegistryTool -> 读取registry.json
3. RegistryTool -> 返回[worker_1, worker_3]
```

### 4.2 P2P消息传递

```
Agent A调用Agent B:
1. A -> 写入B/inbox/msg_001.json
2. A -> 轮询A/inbox/等待响应
3. B -> 扫描B/inbox/发现msg_001
4. B -> 处理任务
5. B -> 写入A/inbox/resp_001.json
6. A -> 收到响应，返回结果
```

### 4.3 团队协作

```python
# 1. 任务分解
lead_agent.execute("这个任务需要前端和后端配合")

# 2. 招募团队
team = lead_agent.execute("""
  找一个前端专家
  找一个后端专家
  找一个测试专家
""")

# 3. 分配任务
lead_agent.execute(f"""
  {frontend_agent}: 实现用户界面
  {backend_agent}: 实现API接口
  {test_agent}: 编写测试用例
""")

# 4. 协调执行
results = parallel_execute(tasks)

# 5. 整合结果
final_result = lead_agent.execute(f"整合这些结果: {results}")
```

## 5. 实现细节

### 5.1 最小启动代码

```python
from core.react_agent_minimal import ReactAgentMinimal
from core.tools.registry_tool import RegistryTool
import threading

# 创建Registry Tool（不是Agent）
registry_tool = RegistryTool()

# 启动Workers
workers = []
for i in range(5):
    worker = ReactAgentMinimal(
        name=f"worker_{i}",
        work_dir=f"./infrastructure/agents/worker_{i}",
        tools=[registry_tool],  # Registry作为Tool
        knowledge_files=["worker_knowledge.md"]
    )
    workers.append(worker)
    
    # 注册自己
    worker.registry.execute("register",
        name=worker.name,
        capabilities=worker.capabilities
    )
    
    # 启动守护进程
    def worker_daemon(agent):
        agent.run_daemon()  # 内置的inbox扫描循环
    
    thread = threading.Thread(target=worker_daemon, args=(worker,))
    thread.start()

print(f"Agent社会启动完成，共{len(workers)}个Worker")
```

### 5.2 性能特征

| 指标 | 数值 | 说明 |
|------|------|------|
| 响应延迟 | <100ms | 轮询间隔 |
| 吞吐量 | ~10 msg/s/agent | 受LLM速度限制 |
| 并发Agent数 | 100+ | 受内存限制 |
| 代码量 | ~500行 | 核心代码 |
| 外部依赖 | 0 | 只需Python |

### 5.3 容错机制

1. **Agent故障**：
   - 调用超时自动重试或转移
   - Registry定期清理离线Agent

2. **消息丢失**：
   - 文件系统保证持久化
   - 失败消息保存到failed/目录

3. **死锁避免**：
   - 同步调用设置超时
   - 避免循环依赖

## 6. 扩展性

### 6.1 水平扩展

```bash
# 添加更多Worker
for i in {10..20}; do
    python start_worker.py --id worker_$i &
done

# 添加专门的Agent
python start_agent.py --type database_expert &
python start_agent.py --type security_expert &
```

### 6.2 跨机器部署

```python
# 使用共享文件系统（NFS、SSHFS等）
mount -t nfs server:/agents ./infrastructure/agents

# 或使用同步工具
while true; do
    rsync -av ./infrastructure/ remote:/infrastructure/
    sleep 1
done
```

### 6.3 功能扩展

通过添加知识文件扩展功能：

```markdown
# new_capability.md
## 新能力：生成代码
当要求生成代码时：
1. 理解需求
2. 设计架构
3. 生成代码
4. 添加测试
```

## 7. 优势与局限

### 7.1 优势

1. **极简**：核心代码~500行，Registry Tool仅30行
2. **透明**：文件系统可直接查看和调试
3. **灵活**：知识驱动，行为可随时调整
4. **P2P架构**：无中心节点，避免单点故障
5. **Function统一**：Agent和Tool统一接口，可互换

### 7.2 局限

1. **性能**：受限于LLM推理速度
2. **规模**：单机数百Agent，跨机器需要共享存储
3. **实时性**：100ms轮询延迟
4. **成本**：每次通信需要LLM推理

### 7.3 适用场景

**适合**：
- 中小规模Agent协作（<100个）
- 对实时性要求不高（秒级响应）
- 需要灵活调整行为
- 原型开发和实验

**不适合**：
- 高频交易等毫秒级响应
- 数千Agent的大规模部署
- 成本敏感的场景

## 8. 未来演进

### 8.1 短期（1-3个月）

- [ ] 实现基础Agent社会
- [ ] 完善知识文件库
- [ ] 添加监控和可视化
- [ ] 性能优化

### 8.2 中期（3-6个月）

- [ ] 支持分布式部署
- [ ] 实现Agent市场
- [ ] 添加学习和进化机制
- [ ] 安全和权限系统

### 8.3 长期（6-12个月）

- [ ] 自举能力（Agent创建Agent）
- [ ] 经济系统（Agent交易）
- [ ] 涌现智能研究
- [ ] 行业应用案例

## 9. 总结

本架构通过Function统一理论，使用极简的方式实现了完整的Agent社会：

- **理论创新**：Agent即Function，消除了复杂的类型系统
- **架构创新**：文件系统即数据库，消除了中间件依赖
- **工程创新**：简单轮询即可，消除了复杂的事件机制

这不是技术的倒退，而是回归本质。正如Unix哲学所说：**"Keep it simple, stupid"**。

当Agent能够像人类一样自然交流和协作时，真正的集体智能就会涌现。

## 附录A：快速开始

```bash
# 1. 克隆项目
git clone https://github.com/xxx/agent-society

# 2. 安装依赖（只需要Python）
pip install requests

# 3. 启动Agent社会
python start_society.py

# 4. 观察Agent协作
tail -f infrastructure/agents/*/inbox/*.msg
```

## 附录B：知识文件示例

见 `knowledge/` 目录下的各种知识文件。

## 附录C：API参考

### ReactAgentMinimal

```python
agent = ReactAgentMinimal(
    name: str,              # Agent名称
    work_dir: str,          # 工作目录
    knowledge_files: List,  # 知识文件
    tools: List,           # 可用工具/Agent
    model: str = "deepseek-chat"  # LLM模型
)

result = agent.execute(task: str) -> str
```

### Function接口

```python
class Function(ABC):
    @abstractmethod
    def execute(self, **kwargs) -> Any:
        pass
    
    def __call__(self, **kwargs) -> Any:
        return self.execute(**kwargs)
```

---

*版本: 1.0.0*  
*日期: 2024-12-20*  
*作者: Agent Society Team*