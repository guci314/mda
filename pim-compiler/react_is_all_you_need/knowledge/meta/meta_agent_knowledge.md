# Meta Agent知识

Meta Agent就是一个普通的Agent + 专门的知识文件 + CreateAgentTool

## 核心理念
- Meta Agent不是特殊的类，就是ReactAgentMinimal
- 通过知识文件获得"创建Agent的常识"
- 通过CreateAgentTool获得创建Agent的能力
- 体现"人类不会安排文盲当美国总统"的哲学

## 如何成为Meta Agent

```python
from core.react_agent_minimal import ReactAgentMinimal
from tools.create_agent_tool import create_agent_tool

# 普通Agent + Meta知识 = Meta Agent
meta_agent = ReactAgentMinimal(
    name="meta_agent",
    description="负责创建和协调其他Agent",
    model="deepseek-chat",  # 需要理解能力
    knowledge_files=[
        "knowledge/meta/meta_knowledge.md",  # 本文件
        "knowledge/meta/llm_selection_knowledge.md"  # LLM选择常识
    ]
)

# 添加创建Agent的能力
meta_agent.add_tool("create_agent", create_agent_tool)
```

## LLM选择常识

### 任务类型映射
- **文件操作** → grok-fast, gemini-flash（速度优先）
- **代码调试** → deepseek, claude（深度优先）
- **文档生成** → kimi, claude（创意优先）
- **架构设计** → deepseek, claude（理解优先）
- **批量处理** → gemini-flash（并发优先）

### 选择原则
1. 简单任务不用复杂模型（节省成本）
2. 复杂任务不用简单模型（避免失败）
3. 紧急任务用快速模型（响应优先）
4. 重要任务用可靠模型（质量优先）

## 创建Agent的步骤

### 1. 分析任务
```
收到任务 → 识别任务类型 → 评估复杂度 → 确定需求
```

### 2. 选择配置
```
任务类型 → 选择LLM → 选择知识文件 → 确定参数
```

### 3. 创建Agent
```python
# 使用create_agent工具
result = create_agent(
    name="debug_agent",
    description="负责调试和修复代码错误",
    task_analysis="需要深度分析代码错误并修复bug",
    knowledge_files=["knowledge/debugging.md"]
)
# 工具会自动选择deepseek-chat
```

### 4. 协调执行
```
分配任务 → 监控进度 → 收集结果 → 汇总报告
```

## Agent团队模式

### 串行执行
```
Agent1完成 → Agent2开始 → Agent3收尾
适用：有依赖关系的任务链
```

### 并行执行
```
同时启动Agent1、Agent2、Agent3
适用：独立任务的快速处理
```

### 层级管理
```
Meta Agent
├── 子Meta Agent1（管理一个领域）
│   ├── Worker Agent1
│   └── Worker Agent2
└── 子Meta Agent2（管理另一个领域）
    ├── Worker Agent3
    └── Worker Agent4
```

## 实例：处理复杂项目

当收到"创建完整的博客系统"任务时：

1. **任务分解**
   - 清理环境（文件操作）
   - 生成PSM（文档生成）
   - 生成代码（代码生成）
   - 修复测试（调试修复）

2. **创建Agent团队**
   ```python
   # 文件操作Agent - 用快速模型
   create_agent(
       name="file_agent",
       task_analysis="清理目录等文件操作"
   )  # 自动选择grok-fast
   
   # PSM生成Agent - 用文档模型
   create_agent(
       name="psm_agent",
       task_analysis="生成PSM文档"
   )  # 自动选择kimi
   
   # 调试Agent - 用深度模型
   create_agent(
       name="debug_agent",
       task_analysis="调试修复测试错误"
   )  # 自动选择deepseek
   ```

3. **执行协调**
   - 串行执行各Agent
   - 收集执行结果
   - 生成总结报告

## 记住
- Meta Agent = 普通Agent + 知识 + 工具
- 不需要特殊的类或复杂的代码
- 知识驱动行为，工具提供能力
- 简单即是美，组合即是力量