# React Agent Core - 极简版本

这个目录包含 React Agent 系统的极简实现，遵循"少即是多"的设计哲学。

## 文件结构

```
core/
├── __init__.py                  # 模块初始化
├── react_agent_minimal.py       # 极简Agent实现
├── memory_with_natural_decay.py # 自然衰减记忆系统
├── tools.py                     # 工具定义
└── README.md                    # 本文档
```

仅需 **4个Python文件，约600行代码**，实现完整的React Agent功能。

## 核心模块

### react_agent_minimal.py
**ReactAgentMinimal** - 极简React Agent实现

核心特性：
- 单一记忆系统（MemoryWithNaturalDecay）
- 单一参数控制（pressure_threshold）
- 自动API服务检测
- 完整的工具系统支持

```python
from core import ReactAgentMinimal

# 创建Agent - 极其简单
agent = ReactAgentMinimal(
    work_dir="output",
    pressure_threshold=50  # 唯一的记忆参数！
)

# 执行任务
result = agent.run("创建一个Python计算器")
```

### memory_with_natural_decay.py
**MemoryWithNaturalDecay** - 基于压缩的自然记忆衰减

核心理念：
- **压缩即认知**：压缩过程就是理解过程
- **压力触发**：消息数超过阈值自动压缩
- **自然分层**：压缩历史形成记忆层次
- **模仿人类**：像人类一样自然遗忘细节，保留要点

```python
from core import MemoryWithNaturalDecay

# 创建记忆系统
memory = MemoryWithNaturalDecay(
    pressure_threshold=50,  # 50条消息后自动压缩
    work_dir=".memory",     # 持久化目录
    enable_persistence=True # 启用持久化
)

# 添加消息
memory.add_message("user", "解释量子计算")
memory.add_message("assistant", "量子计算是...")

# 自动压缩会在压力达到阈值时触发
if memory.should_compact():
    compressed = memory.compact()  # 返回CompressedMemory对象
```

### tools.py
**工具系统** - 定义Agent的能力边界

提供的工具：
- **文件操作**：read_file, write_file, edit_lines
- **搜索功能**：search_files, find_symbol, extract_code
- **命令执行**：execute_command
- **代码操作**：search_replace, apply_diff
- **Web功能**：google_search, read_web_page（可选）

所有工具都使用Pydantic模型进行强类型验证。

## 设计哲学

### 1. 极简主义
- **一个Agent类**：ReactAgentMinimal
- **一个记忆系统**：MemoryWithNaturalDecay
- **一个核心参数**：pressure_threshold
- **零复杂配置**：开箱即用

### 2. 自然智能
- 模仿人类记忆的自然衰减
- 压缩即理解，解压即创造
- 无需复杂的多层记忆架构

### 3. 呼吸理论
基于"智能即呼吸"的理论：
- **吸入（压缩）**：理解和提取本质
- **屏息（保持）**：在压缩空间中思考
- **呼出（解压）**：生成和创造

## 与旧版本对比

| 特性 | 旧版本（已删除） | 极简版本 |
|------|-----------------|----------|
| 代码量 | ~3000行 | ~600行 |
| Agent类 | 5个 | 1个 |
| 记忆系统 | 6个 | 1个 |
| 配置参数 | 20+ | 1个 |
| 依赖 | 复杂 | 最小 |
| 性能 | 一般 | 优秀 |

## 快速开始

```python
from core import ReactAgentMinimal

# 1. 创建Agent
agent = ReactAgentMinimal(
    work_dir="my_project",
    model="deepseek-chat",           # 可选：指定模型
    pressure_threshold=30             # 可选：调整压缩阈值
)

# 2. 执行任务
result = agent.run("""
分析当前目录的Python代码，找出所有的类定义，
并生成一个类关系图。
""")

# 3. 查看结果
print(result["final_answer"])
```

## API支持

自动支持多种API服务：
- **DeepSeek** - 默认选择
- **OpenRouter** - 模型路由
- **Moonshot (Kimi)** - 月之暗面
- **Google Gemini** - 谷歌

环境变量配置：
```bash
export DEEPSEEK_API_KEY="your-key"
# 或
export OPENROUTER_API_KEY="your-key"
# 或
export MOONSHOT_API_KEY="your-key"
```

## 理论基础

核心理论文档：
- [呼吸：智能的本质](../docs/paper_breathing_intelligence.md)
- [人机协同呼吸](../docs/human_ai_collaborative_breathing.md)
- [双重呼吸：生命与智能](../docs/dual_breathing_life_intelligence.md)
- [具身强化学习](../docs/embodied_reinforcement_learning.md)

## 为什么选择极简版本？

1. **更少的代码，更少的bug**
2. **更快的执行，更低的延迟**
3. **更易理解，更易维护**
4. **更自然的记忆管理**
5. **更符合智能的本质**

## 贡献指南

保持极简：
- 不要添加新的Agent类
- 不要添加新的记忆系统
- 不要增加配置参数
- 优先删除而非添加

> "完美不是没有什么可以添加，而是没有什么可以删除。"
> 
> — Antoine de Saint-Exupéry

## 许可证

MIT License

---

*基于"压缩即认知"的极简AI系统*