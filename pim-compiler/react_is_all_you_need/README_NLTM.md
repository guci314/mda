# 🤖 自然语言图灵机 (NLTM)
> Natural Language Turing Machine - 让每个LLM成为图灵完备的计算机

## 🌟 概述

NLTM是一个革命性的计算范式，它让自然语言成为真正的编程语言，让每个大语言模型(LLM)都成为图灵完备的通用计算机。

## 🎯 核心特性

### 图灵完备性验证 ✅
- **顺序执行** - 按步骤顺序执行指令
- **条件分支** - 支持if/else逻辑判断  
- **循环结构** - 实现while/for循环迭代
- **状态存储** - JSON文件提供无限存储
- **子程序调用** - 支持函数调用和递归

### 技术创新
- 🌐 **自然语言即代码** - 用母语直接编程
- 🧠 **LLM即执行引擎** - 无需编译器或解释器
- 💾 **JSON即内存** - 状态持久化和无限存储
- 🔄 **动态适应** - 根据执行结果调整策略
- 🎯 **领域无关** - 适用于任何计算任务

## 📁 项目结构

```
react_is_all_you_need/
├── knowledge/                     # NLTM知识库
│   ├── natural_language_turing_machine.md    # 核心理论
│   ├── nltm_implementation_guide.md          # 实施指南
│   ├── nltm_examples.md                      # 示例集
│   └── kimi_agent_discipline.md              # 执行纪律
├── core/                          # 核心实现
│   ├── kimi_react_agent.py       # Kimi Agent (支持NLTM)
│   └── react_agent.py            # 通用React Agent
├── nltm_demo.py                  # 概念验证Demo
├── test_nltm_with_kimi.py        # LLM集成测试
└── nltm_simple_test.py           # 简单示例

```

## 🚀 快速开始

### 1. 编写NLPL程序

```yaml
程序: 计算斐波那契
  目标: 生成前10个斐波那契数
  
  状态:
    - 序列: [0, 1]
    - 位置: 2
  
  主流程:
    步骤1: 初始化序列
    步骤2: 循环计算
      循环 当"位置 < 10":
        下一个 = 序列[-1] + 序列[-2]
        追加: 下一个到序列
        增加: 位置
    步骤3: 输出结果
```

### 2. 执行程序

```python
# 基础执行
python nltm_demo.py

# 使用Kimi Agent
python test_nltm_with_kimi.py

# 简单示例
python nltm_simple_test.py
```

### 3. 集成到项目

```python
from core import KimiReactAgent

# 创建NLTM Agent
agent = KimiReactAgent(
    work_dir="./work",
    knowledge_files=["knowledge/natural_language_turing_machine.md"]
)

# 执行自然语言程序
result = agent.execute_task("执行NLPL程序...")
```

## 📚 NLPL语言规范

### 基本结构
```yaml
程序: <程序名>
  目标: <目标描述>
  状态: <状态变量>
  主流程: <执行步骤>
  子程序: <函数定义>
```

### 控制结构
- **顺序**: `步骤1 → 步骤2 → 步骤3`
- **条件**: `如果 <条件>: <真分支> 否则: <假分支>`
- **循环**: `循环 当<条件>: <循环体>`
- **调用**: `调用: 子程序(参数)`

### 状态管理
- **读取**: `获取: 状态.变量`
- **写入**: `设置: 状态.变量 = 值`
- **更新**: `更新: 状态.变量`

## 🔬 验证结果

| 特性 | 状态 | 说明 |
|------|------|------|
| 顺序执行 | ✅ | 步骤按顺序执行 |
| 条件分支 | ✅ | if/else逻辑正常 |
| 循环结构 | ✅ | while/for循环实现 |
| 状态存储 | ✅ | JSON持久化成功 |
| 子程序调用 | ✅ | 函数和递归支持 |

## 💡 应用场景

- 📊 **数据处理** - 批量处理、转换、分析
- 🔄 **工作流自动化** - 多步骤任务执行
- 🎮 **游戏逻辑** - 状态机和规则引擎
- 🧮 **数学计算** - 算法实现和优化
- 🔍 **搜索优化** - 启发式搜索和路径规划
- 🤖 **智能决策** - 条件判断和策略选择

## 🌍 支持的LLM

- **Kimi** (Moonshot) - 原生支持，无需LangChain
- **DeepSeek** - 通过LangGraph集成
- **Gemini** - 高速执行，支持并行
- **GPT系列** - 通用兼容
- **Claude** - 完全支持

## 📖 文档

- [核心理论](knowledge/natural_language_turing_machine.md)
- [实施指南](knowledge/nltm_implementation_guide.md)
- [示例集合](knowledge/nltm_examples.md)
- [执行纪律](knowledge/kimi_agent_discipline.md)

## 🎯 未来展望

NLTM开启了计算的新纪元：
- 人人都能用母语编程
- 程序即知识，知识即程序
- 从符号计算到语义计算
- 从代码驱动到知识驱动

## 📄 许可

MIT License

## 🤝 贡献

欢迎提交Issue和Pull Request！

---

**"自然语言是最后的编程语言"** - NLTM Team