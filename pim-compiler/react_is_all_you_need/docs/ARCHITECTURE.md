# NLPL认知记忆系统架构文档

## 目录
1. [系统概述](#系统概述)
2. [架构理念](#架构理念)
3. [核心组件](#核心组件)
4. [数据流](#数据流)
5. [技术栈](#技术栈)
6. [部署架构](#部署架构)
7. [接口规范](#接口规范)
8. [扩展机制](#扩展机制)

## 系统概述

### 项目定位
NLPL认知记忆系统是一个基于认知心理学原理的AI记忆架构，通过模拟人类记忆机制，实现了从"存储"到"理解"的跨越。系统采用分层架构，将技术需求（消息管理）与认知需求（知识构建）清晰分离。

### 核心特性
- 🧠 **认知真实**：基于Atkinson-Shiffrin记忆模型
- 📝 **NLPL统一**：所有记忆用自然语言表达
- 📁 **纯文件系统**：无需数据库，易于部署
- 🔍 **原生检索**：基于grep的高效搜索
- ⏰ **时间衰减**：模拟人类遗忘曲线
- 🎯 **知识驱动**：Agent行为由NLPL知识文件定义

### 设计原则
1. **简单优于复杂**：使用文件系统而非数据库
2. **可读优于高效**：NLPL文本而非二进制
3. **认知优于存储**：理解而非记录
4. **演化优于设计**：知识自然涌现

## 架构理念

### 双层分离
```
┌─────────────────────────────────────┐
│         应用层（Applications）        │
│         ReactAgent, Tools            │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│        认知层（Cognitive Layer）      │
│  NLPLMemorySystem + 4-Layer Agents   │
│  理解、学习、记忆、反思              │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│       技术层（Technical Layer）       │
│      SimpleMemoryManager              │
│      消息缓冲、上下文窗口            │
└─────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────┐
│       存储层（Storage Layer）         │
│      File System + NLPL Files         │
└─────────────────────────────────────┘
```

### 认知模型映射

| 认知心理学概念 | 系统实现 | 技术实现 |
|--------------|---------|---------|
| 感觉记忆 | 消息流入 | SimpleMemoryManager |
| 工作记忆 | 当前上下文 | working/*.nlpl |
| 短期记忆 | 观察筛选 | L2 Observer Agent |
| 长期记忆-情景 | 事件记录 | episodic/*.nlpl |
| 长期记忆-语义 | 概念知识 | semantic/*.nlpl |
| 长期记忆-程序 | 技能程序 | procedural/*.nlpl |
| 元记忆 | 系统反思 | L4 Metacognition |

## 核心组件

### 1. SimpleMemoryManager（技术层）
```python
class SimpleMemoryManager:
    """纯滑动窗口实现"""
    - window_size: int          # 窗口大小
    - messages: deque           # 消息队列
    
    方法:
    - add_message()            # 添加消息
    - get_context()            # 获取上下文
    - get_stats()              # 获取统计
```

**职责**：
- ✅ 管理消息窗口
- ✅ 自动丢弃旧消息
- ✅ 提供LLM上下文
- ❌ 不做任何智能处理

### 2. NLPLMemorySystem（认知层）
```python
class NLPLMemorySystem:
    """认知记忆系统"""
    - memory_dir: Path          # 记忆目录
    
    方法:
    - create_episodic_memory()  # 创建情景记忆
    - create_semantic_concept() # 创建语义概念
    - create_procedural_skill() # 创建程序技能
    - search_memories()         # 搜索记忆
    - apply_temporal_decay()    # 时间衰减
```

**职责**：
- ✅ 生成三层清晰度记忆
- ✅ 提取知识和模式
- ✅ 实现遗忘机制
- ✅ 支持语义检索

### 3. CognitiveMemoryIntegration（集成层）
```python
class CognitiveMemoryIntegration:
    """集成协调器"""
    - message_manager: SimpleMemoryManager
    - memory_system: NLPLMemorySystem
    - agents: Dict[str, ReactAgent]
    
    触发机制:
    - 每10条消息 → 观察Agent
    - 每50个事件 → 海马体Agent
    - 每100轮 → 元认知Agent
```

### 4. 四层Agent体系

#### L1 工作Agent（Work Agent）
- **角色**：任务执行者
- **记忆模式**：BASIC
- **知识文件**：work_agent.nlpl
- **输出**：执行轨迹

#### L2 观察Agent（Observer Agent）
- **角色**：执行观察者
- **记忆模式**：FULL_ASYNC
- **知识文件**：observer_agent.nlpl
- **输出**：三层清晰度的情景记忆

#### L3 海马体Agent（Hippocampus Agent）
- **角色**：记忆巩固器
- **记忆模式**：HYBRID
- **知识文件**：hippocampus_agent.nlpl
- **输出**：语义概念、程序技能

#### L4 元认知Agent（Metacognition Agent）
- **角色**：系统监控者
- **记忆模式**：FULL_ASYNC
- **知识文件**：metacognition_agent.nlpl
- **输出**：系统评估、优化策略

## 数据流

### 1. 消息流入路径
```
用户输入
    ↓
SimpleMemoryManager.add_message()
    ↓
滑动窗口更新
    ↓
触发计数检查
    ↓
[达到阈值?]
    ↓ Yes
触发认知处理
```

### 2. 记忆生成流程
```
消息历史（Messages）
    ↓
事件提取（Event Extraction）
    ↓
MemoryEvent对象
    ↓
三层记忆生成
    ├── detailed.nlpl（完整信息）
    ├── summary.nlpl（关键信息）
    └── gist.nlpl（核心要点）
```

### 3. 知识萃取流程
```
情景记忆积累
    ↓
模式识别（L3 海马体）
    ↓
知识提取
    ├── 重复模式 → semantic/patterns/
    ├── 概念定义 → semantic/concepts/
    └── 技能步骤 → procedural/skills/
```

### 4. 时间衰减流程
```
记忆文件
    ↓
年龄检查
    ├── 7天后 → 删除detailed版本
    ├── 30天后 → 删除summary版本
    └── 90天后 → 归档或删除gist版本
```

## 技术栈

### 核心依赖
```python
# requirements.txt
python>=3.10
requests        # API调用
pathlib        # 路径处理
dataclasses    # 数据结构
typing         # 类型注解
```

### 文件系统结构
```
.memory/
├── episodic/                    # 情景记忆
│   ├── YYYY-MM-DD/             # 按日期组织
│   │   ├── HH-MM-SS_*_detailed.nlpl
│   │   ├── HH-MM-SS_*_summary.nlpl
│   │   └── HH-MM-SS_*_gist.nlpl
│   └── index.nlpl              # 时间索引
│
├── semantic/                    # 语义记忆
│   ├── concepts/               # 概念定义
│   │   └── *.nlpl
│   ├── patterns/               # 执行模式
│   │   └── *.nlpl
│   └── relations.nlpl          # 概念关系
│
├── procedural/                  # 程序记忆
│   ├── skills/                 # 技能程序
│   │   └── *.nlpl
│   ├── habits/                 # 习惯模式
│   │   └── *.nlpl
│   └── proficiency.nlpl        # 熟练度
│
├── working/                     # 工作记忆
│   ├── current_context.nlpl
│   └── active_goals.nlpl
│
├── metacognitive/              # 元认知
│   ├── self_knowledge.nlpl
│   ├── strategy_effectiveness.nlpl
│   └── assessment.nlpl
│
└── archive/                    # 归档
    └── YYYY-MM-DD/
```

### NLPL文件格式
```markdown
# 标准NLPL记忆格式

## 元信息
- **时间戳**：ISO格式
- **类型**：记忆类型
- **重要性**：0-1浮点数

## 内容
自然语言描述，支持Markdown语法

## 关联
- 相关记忆链接
- 概念引用
```

## 部署架构

### 单机部署
```yaml
# docker-compose.yml
version: '3'
services:
  nlpl-memory:
    build: .
    volumes:
      - ./memory:/app/.memory
      - ./knowledge:/app/knowledge
    environment:
      - MEMORY_DIR=/app/.memory
      - WINDOW_SIZE=50
```

### 分布式部署
```
┌──────────────┐     ┌──────────────┐
│   Agent-1    │     │   Agent-2    │
│  (Worker)    │     │  (Observer)  │
└──────────────┘     └──────────────┘
        ↓                    ↓
    ┌─────────────────────────┐
    │   Shared File System    │
    │     (NFS/GlusterFS)     │
    └─────────────────────────┘
```

### 资源需求
- **CPU**：1-2核心（LLM调用为主要瓶颈）
- **内存**：2GB（滑动窗口 + 文件缓存）
- **存储**：10GB起（随记忆增长）
- **网络**：需要访问LLM API

## 接口规范

### Python API
```python
# 初始化
from core.cognitive_memory_integration import CognitiveMemoryIntegration

memory = CognitiveMemoryIntegration(
    work_dir="./workspace",
    window_size=50,
    memory_dir=".memory"
)

# 添加消息
memory.add_message(role="user", content="创建计算器")

# 处理任务完成
paths = memory.process_task_completion(
    task_name="创建计算器",
    success=True,
    rounds=10
)

# 搜索记忆
results = memory.search_memory("计算器")

# 获取统计
stats = memory.get_stats()
```

### REST API（计划中）
```http
POST /api/memory/message
{
  "role": "user",
  "content": "消息内容"
}

GET /api/memory/search?q=关键词

GET /api/memory/stats

POST /api/memory/decay
```

### CLI接口（计划中）
```bash
# 添加记忆
nlpl-memory add "任务完成"

# 搜索记忆
nlpl-memory search "关键词"

# 显示统计
nlpl-memory stats

# 手动触发衰减
nlpl-memory decay
```

## 扩展机制

### 1. 自定义Agent
```python
# 创建自定义Agent知识文件
# knowledge/custom_agent.nlpl

# 自定义Agent知识

## 角色
我是专门处理XX任务的Agent

## 执行策略
...
```

### 2. 自定义记忆类型
```python
class CustomMemoryType:
    def create_memory(self, data):
        # 实现自定义记忆生成
        pass
    
    def search_memory(self, query):
        # 实现自定义搜索
        pass
```

### 3. 插件系统（计划中）
```python
# plugins/emotion_tagger.py
class EmotionTaggerPlugin:
    def on_message(self, message):
        # 添加情绪标记
        return tagged_message
    
    def on_memory_create(self, memory):
        # 增强记忆的情绪维度
        return enhanced_memory
```

### 4. 外部集成
- **向量数据库**：可选集成FAISS/Pinecone
- **知识图谱**：可选导出到Neo4j
- **LLM适配**：支持OpenRouter兼容的所有模型

## 性能优化

### 内存优化
- 滑动窗口限制消息数量
- 文件延迟加载
- 热点记忆缓存

### I/O优化
- 批量文件操作
- 异步记忆生成
- 索引文件加速检索

### 计算优化
- Agent懒加载
- 触发器阈值调优
- 并行记忆处理

## 监控指标

### 系统健康
- 消息窗口使用率
- 记忆文件总数
- 存储空间占用
- API调用频率

### 认知效能
- 任务成功率
- 平均执行轮数
- 知识复用率
- 记忆检索命中率

### 性能指标
- 消息处理延迟
- 记忆生成时间
- 检索响应时间
- 系统吞吐量

## 故障处理

### 常见问题
1. **记忆文件过多**
   - 定期运行时间衰减
   - 调整触发阈值
   - 归档旧记忆

2. **检索性能下降**
   - 重建索引文件
   - 优化目录结构
   - 使用更精确的搜索词

3. **Agent触发失败**
   - 检查API密钥
   - 验证知识文件路径
   - 查看错误日志

### 备份策略
```bash
# 定期备份记忆
tar -czf memory_backup_$(date +%Y%m%d).tar.gz .memory/

# 增量同步
rsync -av --delete .memory/ backup_server:.memory/
```

## 未来规划

### 短期（1-3个月）
- [ ] REST API实现
- [ ] CLI工具开发
- [ ] 向量检索集成
- [ ] 情绪标记增强

### 中期（3-6个月）
- [ ] 分布式部署支持
- [ ] 插件系统框架
- [ ] 知识图谱导出
- [ ] 多语言支持

### 长期（6-12个月）
- [ ] 自主学习优化
- [ ] 跨Agent记忆共享
- [ ] 记忆可视化界面
- [ ] 认知度量标准

## 参考文献

### 认知心理学
- Atkinson, R. C., & Shiffrin, R. M. (1968). Human memory: A proposed system
- Baddeley, A. (2000). The episodic buffer: a new component of working memory?
- Tulving, E. (1985). Memory and consciousness

### 相关项目
- LangChain Memory Systems
- Semantic Kernel Memory
- MemGPT

### 技术文档
- [NLPL语言规范](./nlpl_language_specification.md)
- [记忆系统设计](./nlpl_memory_pragmatic_design.md)
- [认知心理学评审](./nlpl_memory_cognitive_review.md)

---

*版本：1.0.0*  
*更新日期：2024-08-24*  
*作者：NLPL认知记忆系统团队*