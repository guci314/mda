# 动态记忆系统设计

## 核心理念

**静态记忆 ≠ 知识**  
**动态验证 + 可更新记忆 = 活知识**

记忆不应该是死的存储，而应该是活的能力。Agent 需要的不是记住所有细节，而是记住如何获取和验证细节。

## 四层记忆架构

### 1. 元知识层（Meta-Knowledge Layer）
**特征**：极少变化，指导如何学习和验证  
**更新频率**：几乎不更新  
**存储位置**：`long_term_data/meta_knowledge.md`

```yaml
示例:
  - 查找功能实现: "使用 grep + read 定位代码"
  - 验证配置项: "在 Config 类中查找默认值"
  - 理解架构: "从 __init__ 方法追踪初始化流程"
```

### 2. 原理层（Principles Layer）
**特征**：设计理念、架构决策、核心概念  
**更新频率**：仅在重大重构时  
**存储位置**：`long_term_data/principles.md`

```yaml
示例:
  - world_overview目的: "帮助 Agent 快速理解工作环境"
  - 记忆系统设计: "三级记忆对应不同场景需求"
  - React范式: "通过观察-思考-行动循环解决问题"
```

### 3. 接口层（Interfaces Layer）
**特征**：API、配置项、公共方法  
**更新频率**：版本更新时验证  
**存储位置**：`long_term_data/interfaces.md`

```yaml
示例:
  - 配置项:
      name: "enable_world_overview"
      type: "bool"
      default: "True"
      purpose: "控制是否自动生成环境概览"
      version: "1.0.0+"
```

### 4. 实现层（Implementation Layer）
**特征**：具体代码位置、内部实现  
**更新频率**：每次使用前验证  
**存储位置**：`long_term_data/implementations/`

```yaml
示例:
  - 功能: "world_overview 初始化检查"
    search_pattern: "_check_world_overview"
    expected_class: "GenericReactAgent"
    cached_location:
      file: "react_agent.py"
      line: 502
      git_hash: "606701fe"
    last_verified: "2024-12-14"
    confidence: 0.9
```

## 记忆项数据结构

```python
@dataclass
class MemoryItem:
    # 核心内容
    content: str                    # 记忆内容
    category: str                   # 所属层级
    keywords: List[str]             # 关键词用于检索
    
    # 验证信息
    verification_method: str        # 如何验证这个记忆
    expected_pattern: Optional[str] # 预期的代码模式
    dependencies: List[str]         # 依赖的其他记忆项
    
    # 版本控制
    source: SourceInfo             # 来源信息
    created_at: datetime           # 创建时间
    last_verified: datetime        # 最后验证时间
    version_range: str             # 适用版本范围
    
    # 可信度
    confidence: float              # 0-1 置信度
    decay_rate: float              # 置信度衰减率
    verification_count: int        # 被验证次数
```

## 记忆使用策略

### 1. 分层查询
```python
def answer_question(self, question):
    # 优先级：元知识 > 原理 > 接口 > 实现
    answers = []
    
    # 1. 从元知识获取方法
    method = self.meta_knowledge.get_method(question)
    
    # 2. 从原理层获取概念
    concept = self.principles.get_concept(question)
    answers.append(concept)
    
    # 3. 需要具体信息时
    if needs_details(question):
        # 从接口层获取API信息
        api_info = self.interfaces.get_api(question)
        
        # 从实现层获取代码位置（需验证）
        impl = self.implementations.get_impl(question)
        if impl.needs_verification():
            impl = self.verify_and_update(impl, method)
        
        answers.extend([api_info, impl])
    
    return synthesize_answer(answers)
```

### 2. 验证机制
```python
def verify_memory(self, memory: MemoryItem) -> MemoryItem:
    if memory.category == "implementation":
        # 使用元知识中的方法验证
        actual = self.execute_verification(memory.verification_method)
        
        if not matches(actual, memory.expected_pattern):
            # 搜索新位置
            new_location = self.search_pattern(memory.expected_pattern)
            memory.cached_location = new_location
            memory.confidence *= 0.7  # 降低置信度
            
    memory.last_verified = datetime.now()
    return memory
```

### 3. 主动更新
```python
def proactive_update(self):
    # 启动时检查
    for memory in self.get_stale_memories():
        if memory.confidence < threshold:
            self.schedule_verification(memory)
    
    # 检测文件变更
    for file in self.watched_files:
        if file.is_modified():
            self.invalidate_related_memories(file)
```

## 记忆组织示例

```
long_term_data/
├── meta_knowledge.md          # 如何学习和验证
├── principles.md              # 核心设计理念
├── interfaces.md              # API 和配置
├── implementations/
│   ├── current.md            # 当前版本实现细节
│   ├── archive/              # 历史版本
│   │   ├── v1.0.0.md
│   │   └── v1.1.0.md
│   └── verification_log.json # 验证历史
└── index.yaml                # 记忆索引和元数据
```

## 实施步骤

### Phase 1: 元数据增强（立即实施）
1. 为现有记忆添加来源、时间戳、置信度
2. 区分不同层级的知识
3. 添加验证方法描述

### Phase 2: 验证器实现
1. 实现 MemoryValidator 类
2. 在使用记忆前进行验证
3. 记录验证结果

### Phase 3: 分层存储
1. 重组现有知识到四层架构
2. 实现分层查询机制
3. 建立更新策略

### Phase 4: 主动演化
1. 文件监控和变更检测
2. 自动触发相关记忆更新
3. 用户反馈学习机制

## 设计原则

1. **稳定优于精确**：宁可给出稳定的原理，不给出可能过时的细节
2. **方法优于结果**：记住如何找到答案，而不是记住答案本身
3. **验证优于信任**：使用前验证，特别是实现层的细节
4. **演化优于静态**：记忆系统本身也要能够进化

## 期望效果

- ✅ Agent 不再给出过时的代码行号
- ✅ 知识随代码更新自动演化
- ✅ 保持核心理念的稳定性
- ✅ 提高回答的可靠性
- ✅ 减少"自信但错误"的情况

这个系统让 Agent 的记忆从"死记硬背"进化为"活学活用"。