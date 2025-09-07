# React Agent Core - 极简版本

这个目录包含 React Agent 系统的极简实现，遵循"少即是多"的设计哲学。

## 文件结构

```
core/
├── __init__.py                  # 模块初始化
├── react_agent_minimal.py       # 极简Agent实现 (801行)
├── tool_base.py                 # 函数基础类 (201行)
├── tools/                       # 工具模块
│   ├── create_agent_tool.py     # 创建Agent工具 (152行)
│   └── search_tool.py           # 搜索工具 (218行)
└── README.md                    # 本文档
```

总计 **5个Python文件，约1372行代码**，实现完整的React Agent功能。

## 核心模块

### react_agent_minimal.py
**ReactAgentMinimal** - 极简React Agent实现

核心特性：
- 单一Agent类，自己做笔记
- 自动API服务检测
- 完整的工具系统集成
- 基于Function基类的统一接口

```python
from core import ReactAgentMinimal

# 创建Agent - 极其简单
agent = ReactAgentMinimal(
    work_dir="output"
)

# 执行任务
result = agent.run("创建一个Python计算器")
```

### tool_base.py
**Function** - 统一的函数抽象基类

核心理念：
- 所有工具都继承自Function基类
- 统一的参数验证和执行接口
- 支持OpenAI函数调用格式
- 强类型Pydantic模型验证

```python
from core import Function

class MyTool(Function):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="我的工具描述",
            parameters={
                "param1": {"type": "string", "description": "参数1"}
            }
        )
    
    def execute(self, **kwargs) -> str:
        # 工具逻辑
        return "执行结果"
```

### tools/create_agent_tool.py
**CreateAgentTool** - 创建子Agent工具

功能：
- 动态创建子Agent
- 支持多种模型配置
- 自动环境变量管理
- 父子Agent协作

### tools/search_tool.py
**SearchTool & NewsSearchTool** - 搜索工具

功能：
- 网络搜索（需要Serper API）
- 新闻搜索
- 结果格式化和过滤

## 设计哲学

### 1. 极简主义
- **一个核心Agent类**：ReactAgentMinimal
- **一个函数基类**：Function
- **零复杂配置**：开箱即用
- **自己做笔记**：Agent通过写笔记实现记忆

### 2. 函数即工具
- 所有工具都是Function的子类
- 统一的参数验证和执行模型
- 支持OpenAI函数调用格式
- 易于扩展和维护

### 3. 智能压缩
Agent本身就是智能压缩器：
- **写入笔记** = 知识压缩
- **读取笔记** = 知识提取
- **更新笔记** = 知识演化

## 快速开始

```python
from core import ReactAgentMinimal

# 1. 创建Agent
agent = ReactAgentMinimal(
    work_dir="my_project"
)

# 2. 执行任务
result = agent.run("""
分析当前目录的Python代码，找出所有的类定义，
并生成一个类关系图。
""")

# 3. 查看结果
print(result)
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

## 工具系统

当前可用的工具：
- **CreateAgentTool**: 创建子Agent
- **SearchTool**: 网络搜索
- **NewsSearchTool**: 新闻搜索

所有工具都通过Function基类提供：
- 统一的参数验证
- 类型安全的执行
- 错误处理机制

## 为什么选择极简版本？

1. **更少的代码，更少的bug**
2. **更快的执行，更低的延迟**
3. **更易理解，更易维护**
4. **更自然的智能实现**
5. **更符合函数式编程思想**

## 贡献指南

保持极简：
- 所有新工具必须继承Function基类
- 优先使用函数式编程风格
- 保持代码简洁明了
- 文档比代码更重要

> "完美不是没有什么可以添加，而是没有什么可以删除。"
> 
> — Antoine de Saint-Exupéry

## 许可证

MIT License

---

*基于"函数即工具"的极简AI系统*
## 架构文档

详细的系统架构设计文档请参考：
- [UML架构文档](../uml_model/architecture.md) - 包含系统架构图、类图和时序图
