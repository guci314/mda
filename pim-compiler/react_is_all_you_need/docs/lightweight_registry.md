# 轻量级External Tool注册表

## 为什么不用Spring Cloud？

Spring Cloud提供：
- Eureka服务注册
- Config配置中心
- Gateway网关
- Hystrix熔断器
- ...

**我们只需要**：一个能找到工具的地方。

## 三个递进方案

### 方案1：文件系统（最简单）

```python
# registry.json
{
  "tools": {
    "order_processor": {
      "path": "/external_tools/order_processor.py",
      "agent": "order_agent",
      "version": "a3f2b1c8"
    }
  }
}
```

**优点**：
- 零依赖
- 易理解
- 便于调试

**缺点**：
- 单机限制
- 无法分布式

### 方案2：共享文件系统（NFS/CIFS）

```python
class FileBasedRegistry:
    def __init__(self):
        # 使用共享目录
        self.registry_dir = "/mnt/shared/agent_registry"
        self.lock_file = f"{self.registry_dir}/.lock"

    def register_with_lock(self, tool):
        # 文件锁保证原子性
        with file_lock(self.lock_file):
            self.register(tool)
```

**优点**：
- 支持多机
- 仍然简单
- 不需要额外服务

**缺点**：
- 需要NFS
- 性能受限

### 方案3：极简HTTP服务

```python
# 50行代码的注册中心
from flask import Flask, jsonify

app = Flask(__name__)
registry = {}

@app.route('/register', methods=['POST'])
def register():
    tool = request.json
    registry[tool['name']] = tool
    return jsonify({"status": "ok"})

@app.route('/discover/<capability>')
def discover(capability):
    tools = [t for t in registry.values()
             if capability in t.get('capabilities', [])]
    return jsonify(tools)

@app.route('/call/<tool_name>', methods=['POST'])
def call(tool_name):
    tool = registry[tool_name]
    # 动态加载并执行
    module = load_module(tool['path'])
    result = module.execute(**request.json)
    return jsonify(result)
```

**优点**：
- 真正分布式
- HTTP标准协议
- 可扩展

**缺点**：
- 需要运行服务
- 需要处理高可用

## 推荐架构：渐进式

### Phase 1：开发阶段
使用**文件系统**方案：
```bash
~/.agent/tool_registry/
├── registry.json       # 注册表
├── tools/             # 工具代码
│   ├── order_processor.py
│   └── price_calculator.py
└── logs/              # 调用日志
```

### Phase 2：测试阶段
使用**共享文件系统**：
```bash
/mnt/shared/agent_registry/
├── team_a/
│   └── registry.json
├── team_b/
│   └── registry.json
└── global/
    └── registry.json  # 全局工具
```

### Phase 3：生产阶段
使用**HTTP服务**（但仍然极简）：
```python
# 200行以内的完整注册中心
class LightweightRegistry:
    def __init__(self):
        self.storage = "file"  # 或 redis, etcd
        self.cache = {}        # 内存缓存
        self.health_check()    # 健康检查

    def register(self, tool):
        # 注册逻辑
        pass

    def discover(self, query):
        # 发现逻辑
        pass

    def call_remote(self, tool_id, params):
        # RPC调用
        pass
```

## 与Spring Cloud对比

| 特性 | Spring Cloud | 我们的方案 |
|-----|-------------|-----------|
| 代码量 | 10000+ 行 | < 200 行 |
| 依赖 | 50+ 个jar | 0-2 个pip包 |
| 内存 | 512MB+ | < 50MB |
| 启动时间 | 30秒 | < 1秒 |
| 配置 | XML/YAML地狱 | 1个JSON文件 |
| 学习曲线 | 陡峭 | 10分钟上手 |

## 核心洞察

### 我们不需要的
- 服务网格
- 断路器
- 负载均衡
- 配置中心
- 分布式追踪

### 我们真正需要的
```python
def find_tool(name: str) -> str:
    """找到工具的位置"""
    return registry[name]["path"]

def call_tool(name: str, params: dict) -> any:
    """调用工具"""
    tool_path = find_tool(name)
    module = load_module(tool_path)
    return module.execute(**params)
```

**就这么简单！**

## 实际使用示例

### Agent注册工具
```python
# Agent创建了一个新工具
agent.execute("""
创建external tool: order_validator
功能：验证订单合法性
""")

# Agent自动注册
registry.register_tool(
    name="order_validator",
    path="/tmp/tools/order_validator.py",
    agent="order_agent",
    capabilities=["validation", "order"]
)
```

### 其他Agent发现并使用
```python
# Agent A 发现工具
tools = registry.discover("validation")
# [{"name": "order_validator", "agent": "order_agent", ...}]

# Agent A 使用工具
result = broker.call_tool("order_validator", {
    "order": {"id": "12345", "items": [...]}
})
```

## 最佳实践

1. **从简单开始**：先用文件系统
2. **按需演进**：有分布式需求再升级
3. **保持极简**：能用100行解决，不写1000行
4. **工具自描述**：每个工具包含schema
5. **版本管理**：用文件hash做简单版本控制

## 结论

**不要过度工程化！**

- Spring Cloud是为Netflix规模设计的
- 我们的Agent系统不需要那种复杂度
- 文件系统 + 简单HTTP足够了
- 复杂度是创新的敌人

记住：**最好的注册中心是不需要注册中心**。让Agent之间直接通过文件系统或简单HTTP通信。