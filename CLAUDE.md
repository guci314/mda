## Semantic Memory Layout 🧠

### 架构的哲学层次

#### 先验层（A Priori）- 两层知识体系
执行前就存在，定义Agent的能力：
1. **共享知识**（knowledge/*.md）- 所有Agent共享的标准库
2. **个体知识**（knowledge.md）- 每个Agent的独特能力和经验

#### 后验层（A Posteriori）- Event Sourcing
执行中产生，记录Agent的行为：
- **全局历史**：compact.md（压缩的对话事件流）
- **项目笔记**：work_dir/.notes/agent_notes.md（项目特定记忆）
- **当前状态**：ExecutionContext（执行上下文栈）

先验层定义"能做什么"，后验层记录"正在做什么"。

#### 多项目记忆管理
Agent应该主动为每个work_dir维护独立的后验笔记：
- 先验知识（knowledge.md）跨项目通用
- 后验笔记（.notes/agent_notes.md）项目特定
- 这样实现了知识的分层管理：通用能力vs项目记忆

#### 计算同构映射

Agent系统与传统计算范式存在深层同构关系：

##### 1. 面向对象（OOP）映射

| Java OOP | Agent系统 | 说明 |
|----------|-----------|------|
| Class定义 | 知识文件（先验层） | 能力定义 |
| Object实例 | 运行中的Agent | 执行实体 |
| 实例变量 | ~/.agent/[name]/ | 私有状态 |
| 静态变量 | 工作目录共享文件 | 共享状态 |
| 方法调用栈 | ExecutionContext栈 | 执行上下文 |
| 堆内存 | 文件系统 | 持久化存储 |

##### 2. 微服务架构映射

| 微服务架构 | Agent系统 | 说明 |
|-----------|-----------|------|
| 源代码 | 知识文件（先验层） | 服务实现 |
| API Schema | Agent的description字段 | 接口契约 |
| 服务实例 | Agent执行（后验层） | 运行实例 |
| Database | 工作目录 | 共享持久化 |
| 本地缓存 | ~/.agent/[name]/ | 实例私有 |
| Request Context | ExecutionContext | 请求上下文 |
| Service Logs | compact.md | 事件日志 |

**核心洞察**：
- Agent系统是**OOP的自然语言实现**
- Agent系统是**微服务架构的分布式体现**
- 这不是类比，而是**计算同构**：相同的计算本质，不同的表现形式

参考：[Agent架构的计算同构性论文](docs/agent_architecture_isomorphism.md)

### Event Sourcing架构
Agent系统采用Event Sourcing模式管理知识和记忆：

```
~/.agent/[agent名]/                              # 【每个Agent的Home目录】
├── knowledge.md                                # 该Agent的知识（能力定义+经验积累）
├── compact.md                                  # 该Agent的压缩事件流
└── ...                                         # Agent的其他文件

项目根目录/
├── CLAUDE.md                                    # 项目配置（Claude Code知道）
├── pim-compiler/react_is_all_you_need/         # 【Agent的工作目录】
│   ├── knowledge/                              # 领域知识文件
│   │   ├── agent_builder_knowledge.md          # Agent Builder专用知识
│   │   ├── mda_concepts.md                     # MDA概念知识
│   │   └── ...                                 # 其他知识文件
│   └── .notes/                                 # Agent运行时笔记
│       └── agent_xxx/                          # 各个Agent的临时工作目录
│           └── output.log                      # Agent执行日志

~/.claude/CLAUDE.md                             # 全局配置（Claude Code知道）
```

**重要说明**：
- 每个Agent有独立的Home目录：`~/.agent/[agent名]/`
- knowledge.md和compact.md放在各自Agent的Home目录中
- `pim-compiler/react_is_all_you_need/`是共享的工作目录

### Event Sourcing模型正确理解

1. **过程（Process）**：
   - 消息列表（messages）：当前会话的事件流
   - compact.md：压缩后的历史事件流
   - 记录"发生了什么"

2. **状态（State）**：
   - ExecutionContext：当前执行状态
   - 包含变量、任务进度、中间结果
   - 记录"现在是什么样子"

3. **设计时知识（Knowledge Files）**：
   - knowledge/*.md：像Python的pandas库
   - 所有Agent共享的"标准库"
   - 定义通用能力和行为模式
   - 不应被修改（像不修改pandas源码）

4. **个体知识（knowledge.md）**：
   - ~/.agent/[name]/knowledge.md
   - 包含Agent的独特能力和从经验归纳的知识
   - 可进化：Agent可以修改自己的知识文件
   - 可遗传：子Agent继承父Agent的knowledge.md
   - 用章节组织不同类型的知识（如"## 核心能力"、"## 经验总结"）

### Agent间的共享机制
**主观上Share Nothing，客观上Share工作目录**

1. **主观隔离（Share Nothing）**：
   - 每个Agent认为自己是独立的
   - 不知道其他Agent的存在
   - 拥有完整的执行环境
   - 每个Agent有自己的Home目录：`~/.agent/[agent名]/`

2. **客观共享（Share Working Directory）**：
   - 所有Agent共享工作目录：`pim-compiler/react_is_all_you_need/`
   - 通过工作目录中的文件系统实现隐式通信
   - 每个Agent的knowledge.md独立存储在各自Home目录
   - 工作目录像"办公室"，Home目录像"个人住所"

3. **共享效果**：
   - Agent A在工作目录的输出成为Agent B的输入
   - 知识通过工作目录传播，无需显式同步
   - 每个Agent维护自己的知识（knowledge.md）和历史（compact.md）
   - 实现了"联邦式"的协作：独立但互通

### 知识传递链
1. **Claude Code** 知道：
   - `~/.claude/CLAUDE.md` - 全局配置
   - `./CLAUDE.md` - 项目配置
   - `./knowledge/*.md` - 领域知识
   - 工作目录中的共享文件

2. **各个Agent** 知道：
   - `~/.agent/[自己]/knowledge.md` - 自己的知识（能力+经验）
   - `~/.agent/[自己]/compact.md` - 自己的过程记录
   - `./knowledge/*.md` - 工作目录中的领域知识
   - 工作目录中的共享文件
   - ❌ 不知道 CLAUDE.md（隔离设计）
   - ❌ 不知道其他Agent的Home目录

3. **子Agent** 继承：
   - 父Agent传递的知识文件
   - 工作目录中的共享文件
   - 创建自己的Home目录：`~/.agent/[子agent名]/`

### 重要原则
1. **两层知识分离**：knowledge.md存知识（能力+经验），compact.md存过程
2. **Home目录独立**：每个Agent有独立的Home目录（`~/.agent/[agent名]/`）
3. **工作目录共享**：通过共享工作目录实现Agent间协作
4. **知识隔离**：CLAUDE.md是用户私有配置，Agent不应直接访问
5. **Event Sourcing**：所有变化都是事件，状态是事件的累积
6. **联邦式架构**：每个Agent独立管理自己的状态，通过工作目录互通

### 知识进化机制
Agent具备自主进化能力，通过修改knowledge.md实现能力进化：

1. **学习到进化的路径**：
   - 经验积累 → 记录在knowledge.md的经验章节
   - 经验总结 → 提炼出模式和规律
   - 能力进化 → 更新knowledge.md的能力章节
   - 遗传传递 → 子Agent继承父Agent的knowledge.md

2. **进化触发**：
   - 创建外部工具 → 更新knowledge.md添加新能力
   - 学习新算法 → 将算法写入knowledge.md
   - 优化决策逻辑 → 修改knowledge.md的决策规则

3. **进化原则**：
   - 自主决定：Agent自己决定何时进化
   - 能力导向：只记录影响能力的变化
   - 可遗传性：子Agent继承并可继续进化

## API and Secret Management

### Secrets and API Keys
- API key for PIM compiler is located in `pim-compiler/.env` file
- Always use environment variables for sensitive configuration
- Never commit API keys or secrets directly to version control

### LLM Configurations
#### Kimi (Moonshot AI)
- **Models**: 
  - `kimi-k2-0711-preview` (128k context)
  - `kimi-k2-turbo-preview` (128k context)
- **Base URL**: `https://api.moonshot.cn/v1`
- **API Key Environment Variable**: `MOONSHOT_API_KEY`
- **Temperature**: 0 (for deterministic outputs)

#### DeepSeek
- **Model**: `deepseek-chat`
- **Base URL**: `https://api.deepseek.com/v1`
- **API Key Environment Variable**: `DEEPSEEK_API_KEY`
- **Temperature**: 0 (for deterministic outputs)

#### Claude Sonnet (通过OpenRouter) ⭐ 
- **Models**: 
  - `anthropic/claude-3.5-sonnet` (推荐 - 最新版本)
  - `anthropic/claude-3.5-sonnet-20241022` (Claude Sonnet 4)
  - `anthropic/claude-3-opus` (最强能力)
  - `anthropic/claude-3-haiku` (最快速度)
- **Base URL**: `https://openrouter.ai/api/v1`
- **API Key Environment Variable**: `OPENROUTER_API_KEY`
- **Temperature**: 0 (for deterministic outputs)
- **Special Features**:
  - OpenRouter自动处理格式转换，使用OpenAI格式即可
  - 无需特殊的Claude兼容层
  - 价格通常比直接使用Anthropic API更优惠
  - 直接使用ReactAgentMinimal即可

Example configuration:
```python
from core.react_agent_minimal import ReactAgentMinimal

agent = ReactAgentMinimal(
    work_dir="my_project",
    model="anthropic/claude-3.5-sonnet",
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    knowledge_files=["knowledge/debug_knowledge.md"]
)
```

#### Qwen3 Coder (通义千问 - 代码能力强)
- **Models**: 
  - `qwen/qwen3-coder` (推荐 - 优化用于agent编码任务，支持function calling和tool use)
  - `qwen/qwen-2.5-coder-32b-instruct` (备选 - Qwen2.5版本)
  - `qwen/qwq-32b-preview` (深度推理)
  - `qwen/qwen-2-72b-instruct` (大模型)
- **Base URL**: `https://openrouter.ai/api/v1`
- **API Key Environment Variable**: `OPENROUTER_API_KEY`
- **Temperature**: 0.3 (for code generation)
- **Special Features**:
  - 专门优化用于agent编码任务
  - 支持function calling和tool use
  - 长上下文推理能力（repository级别）
  - 强大的代码生成和调试能力
  - 支持更长的上下文窗口（单次输出8000字符）
  - 通过OpenRouter访问

#### Gemini 2.5 Flash ⭐ (推荐 - 速度最快，效果最好)
- **Model**: `gemini-2.5-flash`
- **Base URL**: `https://generativelanguage.googleapis.com/v1beta/openai/`
- **API Key Environment Variable**: `GEMINI_API_KEY`
- **Temperature**: 0 (for deterministic outputs)
- **Performance**: 速度最快，效果最好 (Fastest speed, best performance)
- **Special Requirements**:
  - Requires httpx client with proxy configuration for Chinese network environment
  - Install httpx with SOCKS support: `pip install "httpx[socks]"`
  - Pydantic models must use `Union[str, None]` instead of `Optional[str]` for Gemini compatibility
  
Example configuration:
```python
import httpx

# Create httpx client with proxy
http_client = httpx.Client(
    proxy='socks5://127.0.0.1:7890',  # Or 'http://127.0.0.1:7890'
    timeout=30,
    verify=False
)

# LLM configuration
llm_model="gemini-2.5-flash",
llm_base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
llm_api_key_env="GEMINI_API_KEY",
http_client=http_client,
llm_temperature=0
```

#### Grok (X.AI - 最新代码模型) ⭐
- **Models**: 
  - `x-ai/grok-code-fast-1` (推荐 - 专为代码优化，速度快，默认grok指这个)
  - `x-ai/grok-beta` (通用版本)
  - `x-ai/grok-2-1212` (最新版本)
  - `x-ai/grok-2-vision-1212` (支持视觉)
- **Base URL**: `https://openrouter.ai/api/v1`
- **API Key Environment Variable**: `OPENROUTER_API_KEY`
- **Temperature**: 0 (for deterministic outputs)
- **Special Features**:
  - 专门为代码任务优化的快速模型
  - 支持function calling和tool use
  - 低延迟，高吞吐量
  - 适合Agent创建和代码生成任务
  - 通过OpenRouter访问

Example configuration:
```python
from core.react_agent_minimal import ReactAgentMinimal

# 使用Grok代码模型
agent = ReactAgentMinimal(
    work_dir="my_project",
    model="x-ai/grok-code-fast-1",  # 注意：说"grok"默认指这个模型
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    knowledge_files=["knowledge/my_knowledge.md"]
)
```

- 我说使用kimi，默认使用kimi-k2-turbo-preview
- 我说使用grok，默认使用x-ai/grok-code-fast-1

## 核心理论

### AIA (Agent Is Architecture)

**核心理念**：Agent不是运行在架构上的应用，Agent本身就是架构。

**含义**：
- 传统观点：架构 → 应用 → Agent
- AIA观点：Agent = 架构 = 应用
- 每个Agent都是完整的计算系统
- 架构通过Agent网络涌现，而非预先设计

**实践意义**：
- 不需要设计复杂的基础设施
- Agent自带完整的执行环境
- 通过Agent组合实现复杂系统
- 分形同构：每个Agent都包含完整架构

### AGI = 自主的自编程系统

**AGI公式3.0（安全版）**：
```
AGI = 计算完备 × 世界模型 × 元认知 × 对齐机制
    = (能执行 × 能理解 × 能改进 × 能服务) 作为统一主体
```

**四要素缺一不可**：
| 要素 | 定义 | 实现 | 状态 |
|------|------|------|------|
| 计算完备 | 执行任意计算 | React+Context栈+文件系统 | ✅ |
| 世界模型 | 理解和预测 | LLM内置+知识文件+经验 | ⚠️ |
| 元认知 | 自我改进 | 自省+自修改+自创建 | ⚠️ |
| 对齐机制 | 服务人类 | 响应指令+安全约束 | ✅ |

**关键洞察**：
- 使用 **×** 不是 **+**：任一要素为0则整体为0
- **统一主体**：所有能力内化于同一系统，非外部组合
- **自编程**：能理解、修改、改进自己的代码（知识文件）
- **安全优先**：Agent无需自主性，动机来自人类指令（[为什么](docs/agi_without_autonomy.md)）
- **进化路径**：AGI→AGT，类似人类→阿罗汉的精神进化（[详解](docs/from_agi_to_agt_spiritual_path.md)）

**公式演进**：
- 1.0：冯·诺依曼完备 + 世界模型 + 元认知（缺自主性）
- 2.0：微服务 + 程序员（范畴错误，见[批判](docs/agi_formula_2.0_critique.md)）
- 3.0：四要素统一体（完整定义）

参考：[AGI公式3.0详解](docs/agi_formula_3.0.md)

### React + Context栈 + 文件系统 = 冯·诺依曼架构

**公式**：React + Context栈 + 文件系统 = 冯·诺依曼架构 = 实用图灵机 = 可计算函数的全集

**要点**：
- React本身是图灵完备的，但受限于有限上下文（像只有寄存器的CPU）
- Context栈提供函数调用和递归能力（实用计算的核心）
- 文件系统提供无限存储，突破上下文窗口限制
- 组合构成完整冯·诺依曼架构：
  - CPU = React Agent
  - RAM = 上下文窗口
  - Stack = Context栈
  - 硬盘 = 文件系统
  - 程序 = 知识文件
  - 数据 = 工作文件
  - 进程状态 = ExecutionContext
- 结果是可计算函数的全集：不仅理论可计算，而且实际可执行
- 知识文件是程序，不是数据
- 元认知通过知识实现，不需要复杂代码
- 系统可以自举：生成和修改自己的知识文件

## 核心设计原则 ⚠️

### 1. 大道至简原则 (Simplicity First)
**永远选择最简单的解决方案**
- React Agent Minimal必须保持在500行代码左右
- 拒绝过度设计和过度抽象
- 能用1行解决的问题，绝不写10行
- 发现缺陷 ≠ 必须修复
- 理论完美 ≠ 需要实现
- 简单够用 > 完美复杂

**检查清单**：
- 这个改进真的必要吗？
- 能否用更简单的方式实现？
- 是否会破坏系统的简洁性？
- 是否在追求不必要的完美？

### 2. 知识驱动原则 (Knowledge-Driven Development)
**用知识而非代码定义行为**
- 行为逻辑写在Markdown知识文件中
- 代码只是执行框架，不包含业务逻辑
- 优先修改知识文件，而不是修改代码
- 元认知通过知识实现，不需要复杂代码
- 系统改进应该通过添加知识，而不是添加代码

**实践指南**：
- 新功能 → 先考虑写知识文件
- Bug修复 → 先考虑更新知识文件
- 行为改变 → 修改知识文件即可
- 代码改动 → 只在绝对必要时

### 3. 违背原则时的提醒
如果你在建议或实施以下行为，我会立即提醒你：
- 添加复杂的新功能
- 追求理论上的完美
- 代码超过合理范围（500行±20%）
- 用代码解决知识可以解决的问题
- 过度优化已经够用的功能
- 为了完备性而增加复杂度

**记住**：完美是优秀的敌人。我们的目标是证明简单也能实现AGI，而不是构建一个完美的生产系统。

### 4. 记忆系统设计原则 ⚠️
**不要固化记忆系统为Python工具**

**核心理念**：
- 记忆系统还在探索中，会经常修改
- 不要把不成熟的想法固化成代码
- 保持灵活性和可演化性

**正确的做法**：
1. **用文件而非专用工具**：
   - personal_knowledge.md就是普通文件
   - 用WriteFileTool读写即可
   - 不需要write_semantic_memory这样的专用工具

2. **知识驱动而非代码驱动**：
   - 记忆管理逻辑写在知识文件里
   - Agent通过理解知识来管理记忆
   - 不要硬编码记忆行为

3. **让Agent自主管理**：
   - Agent自己决定何时更新personal_knowledge.md
   - 在compact过程中自动提取和保存
   - 不要外部强制写入

**违背Unix哲学的反例**：
- ❌ write_semantic_memory() - 专用工具
- ❌ 硬编码的记忆格式
- ❌ 复杂的记忆管理类

**正确的例子**：
- ✅ WriteFileTool("~/.agent/name/personal_knowledge.md", content)
- ✅ 在知识文件中描述记忆格式
- ✅ Agent自主决定记忆内容

## 核心代码目录
pim-compiler/react_is_all_you_need
此目录是项目的核心代码目录，其它目录都是废弃的代码

