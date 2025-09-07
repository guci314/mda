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
- 我说使用kimi，默认使用kimi-k2-turbo-preview

## 核心理论

### React + 文件系统 = 冯·诺依曼架构

**公式**：React + 文件系统 = 冯·诺依曼架构 = 图灵完备 + 无限存储 = 可计算函数的全集

**要点**：
- React本身是图灵完备的，但受限于有限上下文（像只有寄存器的CPU）
- 文件系统提供无限存储，突破上下文窗口限制
- 组合构成完整计算架构：
  - CPU = React Agent
  - RAM = 上下文窗口
  - 硬盘 = 文件系统
  - 程序 = 知识文件
  - 数据 = 工作文件
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

## 核心代码目录
pim-compiler/react_is_all_you_need
此目录是项目的核心代码目录，其它目录都是废弃的代码

## 内存管理协议遵守要求 🧠

### Claude Code必须遵守内存管理协议
作为验证React + 文件系统 = 图灵完备理论的实践者，我（Claude Code）必须严格遵守内存管理协议：

**每个任务都必须维护以下文件**：
1. **task_process.md**（工作内存）- 第1轮创建，每轮更新
   - 这是突破50轮上下文限制的关键
   - 让我能处理大数据量工作和回忆久远历史
   - 证明有限上下文 + 无限存储 = 图灵完备
2. **session记录** - 任务结束前创建
3. **agent_knowledge.md** - 任务结束前更新
4. **world_state.md** - 任务结束前更新

### 为什么Claude Code要遵守
1. **验证理论**：通过实践证明冯诺依曼架构的正确性
2. **发现缺陷**：帮助发现协议设计的bug和不足
3. **自我提升**：通过knowledge积累提升处理能力
4. **可追溯性**：所有执行都有历史记录可查

### 实践效果
- ✅ 能处理超过50轮的复杂任务（通过task_process.md）
- ✅ 能回忆之前的任务经验（通过agent_knowledge.md）
- ✅ 能了解世界状态变化（通过world_state.md）
- ✅ 能追溯所有历史操作（通过sessions）

### 使用TodoWrite工具
我会主动使用TodoWrite工具来：
- 规划复杂任务的执行步骤
- 跟踪当前进度
- 确保不遗漏任何必要操作
- 演示协议的实际使用方法

**记住**：如果我没有遵守这个协议，请立即提醒我。这不仅是为了完成任务，更是为了验证和改进这个优雅的理论体系。