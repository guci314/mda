# 动态记忆格式示例

## 现有格式的问题

```markdown
# 现在的格式（静态、扁平）
| 触发时机 | 触发条件 | 代码位置 | 执行顺序 |
|----------|----------|----------|----------|
| Agent初始化时 | world_overview.md不存在 | react_agent.py:502 | 第1步 |
```

问题：
- ❌ 硬编码的行号容易过时
- ❌ 没有验证方法
- ❌ 缺少置信度和时效性

## 改进后的格式

### 1. 元知识记录

```yaml
# META_KNOWLEDGE: 如何理解 world_overview 机制
learning_methods:
  find_trigger_mechanism:
    description: "查找 world_overview 触发机制的方法"
    steps:
      - "grep -n 'world_overview' *.py 找到相关代码"
      - "找到 _check_world_overview 方法"
      - "追踪调用链：__init__ -> _check_world_overview"
      - "查看 execute_task 中的 _pending_overview_task 处理"
    tools_needed: ["grep", "read_file"]
    
  verify_config_option:
    description: "验证配置项的方法"
    steps:
      - "在 ReactAgentConfig 类中查找属性定义"
      - "搜索默认值设置"
      - "检查 __init__ 参数"
```

### 2. 原理层记录

```yaml
# PRINCIPLES: world_overview 设计原理
world_overview_purpose:
  concept: "环境感知机制"
  description: "让 Agent 快速理解陌生工作目录的结构和内容"
  rationale: "Agent 需要像人类一样，先了解环境再开始工作"
  stability: "high"  # 这个原理很少改变
  
trigger_philosophy:
  concept: "延迟生成策略"
  description: "不在初始化时阻塞，而是在首次执行任务时生成"
  rationale: "避免初始化时间过长，按需生成"
  stability: "high"
```

### 3. 接口层记录

```yaml
# INTERFACES: 公共API和配置
configurations:
  enable_world_overview:
    type: "boolean"
    default: "True"
    location: "ReactAgentConfig"
    purpose: "控制是否自动生成 world_overview.md"
    introduced: "v1.0.0"
    stability: "stable"
    verification:
      method: "grep 'enable_world_overview.*=' react_agent.py"
      
methods:
  execute_task:
    class: "GenericReactAgent"
    signature: "execute_task(self, task: str) -> str"
    behavior: "首次调用时会先执行 pending overview 任务"
    stability: "stable"
```

### 4. 实现层记录

```yaml
# IMPLEMENTATION: 具体实现细节（需要频繁验证）
world_overview_check:
  feature: "初始化时检查"
  search_patterns:
    - pattern: "_check_world_overview"
      context: "method definition"
    - pattern: "WorldOverviewChecker"
      context: "class usage"
  cached_info:
    file: "react_agent.py"
    method: "_check_world_overview"
    approximate_line: 502  # 仅作参考
    git_commit: "606701fe"
    last_verified: "2024-12-14T10:30:00"
  confidence: 0.85
  verification_command: |
    grep -n "_check_world_overview" react_agent.py
    
trigger_execution:
  feature: "延迟执行机制"
  search_patterns:
    - pattern: "_pending_overview_task"
      context: "attribute usage"
  dependencies:
    - "world_overview_check"
  confidence: 0.80
```

## 使用示例

当 Agent 需要回答关于 world_overview 的问题时：

```python
def answer_world_overview_question(question):
    # 1. 先从原理层获取概念
    principle = get_principle("world_overview_purpose")
    # Output: "这是一个环境感知机制..."
    
    # 2. 如果需要具体配置
    if "如何禁用" in question:
        config = get_interface("enable_world_overview")
        # Output: "设置 enable_world_overview=False"
    
    # 3. 如果需要代码位置
    if "代码在哪" in question:
        impl = get_implementation("world_overview_check")
        
        # 验证是否仍然准确
        if impl.confidence < 0.7 or age_days(impl) > 7:
            # 执行验证命令
            result = run_command(impl.verification_command)
            impl = update_cached_info(impl, result)
        
        # Output: "在 _check_world_overview 方法中（经验证）"
```

## 迁移计划

### Step 1: 标注现有知识
为 `extracted_knowledge.md` 中的每项知识添加标签：
- `[META]` - 方法类知识
- `[PRINCIPLE]` - 原理类知识
- `[INTERFACE]` - 接口类知识
- `[IMPL]` - 实现类知识

### Step 2: 添加元数据
```yaml
旧格式: "代码位置：react_agent.py:502"

新格式:
  type: "IMPL"
  content: "初始化检查逻辑"
  location:
    file: "react_agent.py"
    search: "_check_world_overview"
    cached_line: 502
  metadata:
    verified: "2024-12-14"
    confidence: 0.85
    method: "grep + read"
```

### Step 3: 实现验证器
创建 `MemoryValidator` 类，在使用实现层知识前进行验证。

### Step 4: 分层存储
将不同类型的知识分别存储，便于差异化管理。

这种格式让记忆系统更加：
- 🔍 **可验证**：每个记忆都有验证方法
- 📊 **有置信度**：知道哪些信息可能过时
- 🔄 **可更新**：能够自我修正
- 📚 **分层清晰**：稳定的原理和易变的细节分开