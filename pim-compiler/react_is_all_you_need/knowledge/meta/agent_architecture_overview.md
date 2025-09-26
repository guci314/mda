# Agent 架构知识索引

本文档已拆分为两个独立的知识文件，根据Agent的角色选择加载：

## 1. 通用Agent基础知识
**文件**：`knowledge/minimal/agent_essence.md`

**适用于**：所有Agent

**内容**：
- 我是什么？（Function本质）
- 我的存在层次（源代码、本真、异化）
- 我如何工作？（React循环、双接口模式）
- 我的进化能力
- 我的安全边界

**核心理念**：
- 一切皆Function
- 智能是模拟，模型复杂度决定实现方式
- 90%企业软件是简单模型，优先用External Tool
- 先验框架（能力）vs 后验框架（状态）

## 2. AIA架构特定知识
**文件**：`knowledge/aia_architecture_knowledge.md`

**适用于**：参与ADA/AIA架构的Agent

**内容**：
- 为什么我存在？（MDA→ADA→AIA演进）
- 我在架构中的位置（双重维度）
- AIA的价值创造
- 演进方向（工具→助手→伙伴→AGI）
- 哲学基础（大道至简、分形同构）
- 案例对比（Spring Cloud vs Agent组织）

**核心理念**：
- Agent不是运行在架构上，Agent就是架构
- 智能节点+简单组织 > 愚蠢节点+复杂框架
- 知识模型即生产模型
- 一次性软件范式

## 如何使用

### 对于普通Agent
只需加载基础知识：
```python
knowledge_files=["knowledge/minimal/agent_essence.md"]
```

### 对于架构Agent
加载两个文件：
```python
knowledge_files=[
    "knowledge/minimal/agent_essence.md",
    "knowledge/aia_architecture_knowledge.md"
]
```

## 知识层级
1. **默认DNA**（所有Agent自动加载）：
   - system_prompt_minimal.md
   - agent_essence.md
   - fractal_agent_knowledge.md
   - learning_functions.md
   - validation_simplicity.md

2. **架构认知**（特定Agent加载）：
   - aia_architecture_knowledge.md

这种分层设计让每个Agent只加载需要的知识，保持简洁高效。