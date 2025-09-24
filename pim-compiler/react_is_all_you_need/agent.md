# 模块知识 - React Agent Minimal

## 系统环境配置

### 代理服务器配置（重要）
系统设置了 HTTP/HTTPS 代理，访问 localhost 时必须禁用代理，否则会被代理服务器拦截导致失败。

#### curl 访问 localhost
```bash
# ✅ 正确方式：使用 --noproxy 参数
curl --noproxy localhost http://localhost:8000/
curl --noproxy '*' http://localhost:8000/api
curl --noproxy 127.0.0.1 http://127.0.0.1:8000/

# ❌ 错误方式：会被代理拦截
curl http://localhost:8000/
```

#### Python requests 库
```python
# ✅ 方法1：显式禁用代理
proxies = {"http": None, "https": None}
response = requests.get("http://localhost:8000/", proxies=proxies)

# ✅ 方法2：使用 Session 忽略环境变量
session = requests.Session()
session.trust_env = False  # 忽略系统代理设置
response = session.get("http://localhost:8000/")

# ✅ 方法3：设置 NO_PROXY 环境变量
import os
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0'
response = requests.get("http://localhost:8000/")
```

#### 在生成的测试代码中
必须在测试脚本开头添加代理禁用配置：
```python
#!/usr/bin/env python3
import os
import requests

# 禁用 localhost 代理
os.environ['NO_PROXY'] = 'localhost,127.0.0.1,0.0.0.0'

# 或为每个请求单独设置
def test_api():
    proxies = {"http": None, "https": None}
    response = requests.get("http://localhost:8000/", proxies=proxies)
    return response
```

#### 通用解决方案
创建一个辅助函数处理本地请求：
```python
def get_localhost(path, port=8000, **kwargs):
    """访问本地服务，自动禁用代理"""
    url = f"http://localhost:{port}{path}"
    kwargs['proxies'] = {"http": None, "https": None}
    return requests.get(url, **kwargs)

# 使用示例
response = get_localhost("/api/test")
```

### 经验教训
- **2025-09-12**：Agent Builder 测试 MDA 系统时，因为不知道代理配置，导致所有 localhost 访问失败，浪费大量时间调试
- **根本原因**：系统 HTTP_PROXY 环境变量导致 localhost 请求也被发送到代理服务器
- **解决方案**：所有 Agent 生成的网络请求代码都必须处理代理问题

## MDA 系统知识

### MDA 核心概念理解
- **PIM (Platform Independent Model)**：平台无关模型，是数据结构（如 YAML/JSON），不是代码
- **PSM (Platform Specific Model)**：平台特定模型，仍然是数据结构（如 JSON），包含技术细节，不是代码
- **Code**：从 PSM 生成的可执行代码文件

### 正确的 MDA 流程
1. PIM 文件（.pim/.yaml）→ PIM 数据结构（Dict/JSON）
2. PIM 数据结构 → PSM 数据结构（通过 Transformer）
3. PSM 数据结构 → 代码文件（通过 Generator）

### 常见错误
- ❌ 把 PSM 理解为代码
- ❌ Transformer 直接生成代码文件
- ✅ PSM 应该是 JSON/Dict 格式的模型数据

## 多 Agent 协作知识

### CreateAgentTool 的限制
- 当前 CreateAgentTool 创建的 Agent 无法继承其他 Agent 作为工具
- 导致 Coordinator Agent 无法调用其他 Agent，只能自己完成所有工作

### 改进方案（已实现）
在 CreateAgentTool 中添加 `inherit_tools` 参数：
```python
coordinator = create_agent(
    agent_type="mda_coordinator",
    inherit_tools=[
        "agent_pim_parser_xxx",
        "agent_transformer_xxx",
        "agent_code_generator_xxx"
    ]
)
```

## 知识传递链

### 知识体系差异
- **Claude Code 知道**：CLAUDE.md（用户配置）+ agent.md（语义记忆）+ knowledge/*.md
- **Agent Builder 知道**：agent.md + knowledge/*.md（不知道 CLAUDE.md）

### 解决方案
确保重要配置写入 agent.md，这样所有 Agent 都能继承。

## 核心概念
- **智能触发原则**：基于任务复杂度决定是否使用ExecutionContext
- **Compact记忆**：70k tokens触发压缩，自动管理
- **工作记忆**：自动滑出旧信息，复杂任务时防止丢失
- **函数式架构**：所有工具继承自Function基类
- **多模型支持**：DeepSeek（高效）、Kimi（详细）、Qwen3（代码强）
- **图灵完备**：React推理+笔记系统实现完整计算模型

## 重要模式
- **按需启用**：简单任务直接完成，复杂任务跟踪状态
- **自动管理**：无需手动干预，智能压缩和滑出
- **自然语言表达**：用自然语言表达算法、状态和API，摆脱Schema地狱
- **大道至简**：极简主义设计，代码控制在500行左右

## 注意事项
- ⚠️ **模板废除**：task_process.md模板已移除
- 📌 **原则保留**：智能触发原则仍有效
- ⚠️ **避免过度设计**：拒绝复杂架构，保持简单
- 📌 **智能即函数**：所有智能行为都是函数

## 相关文件
- `core/react_agent_minimal.py` - ExecutionContext实现和核心Agent逻辑
- `knowledge/minimal/system/system_prompt_minimal.md` - 系统提示词和内存管理
- `knowledge/sequential_thinking_simple.md` - 顺序思考知识
- `knowledge/agent_builder_knowledge.md` - Agent构建知识
- `knowledge/sequential_thinking_knowledge.md` - 顺序思考优化
- `knowledge/sequential_thinking_optimized.md` - 优化版本
- `knowledge/mda_concepts.md` - MDA概念
- `demo_agent_builder_requirements_only.py` - 演示脚本（需求版）
- `demo_agent_builder_with_tool.py` - 演示脚本（带工具）
- `demo_agent_builder.py` - 基础演示
- `demo_agent_builder_correct.py` - 修正版演示
- `mda_research.ipynb` - MDA研究笔记本
- `core/code_graph_rag_integration_design.md` - 代码图RAG集成设计

## 文件总结系统

### 文件总结功能
- **files_summary.md**：自动生成的项目文件总结文档
- **全面覆盖**：包含465个py、ipynb、md文件的分类总结
- **结构化组织**：按核心架构、工具系统、知识文件、演示研究等分类

### 总结内容架构
1. **核心架构文件**：React Agent Minimal、拦截器、人类式学习等
2. **工具系统**：Agent Creator、CreateAgentTool、调试工具等
3. **知识文件系统**：自我认知、系统提示词、顺序思考等
4. **演示和研究**：多个演示版本、MDA研究、代码图RAG等
5. **配置文档**：语义记忆、用户配置、指南文档等
6. **架构文档**：UML模型、交互图、组件图等

### 统计信息
- **总文件数**：465个（py、ipynb、md文件）
- **核心代码**：~5个主要文件，1372行代码
- **知识文件**：20+个Markdown知识文件
- **演示示例**：10+个演示脚本
- **研究文档**：多个研究笔记本和设计文档

## 最近经验教训

### 苦涩的教训实验（2025-09-13）
**实验目标**：通过失败驱动学习，让Agent从"1+1=2"演化出专家级调试知识

**实验结果**：❌ 失败
- 知识文件没有演化，仍然是"1+1=2"
- Agent陷入无限循环，无法完成任务
- 元认知没有正确触发知识更新

**关键发现**：
1. **异步机制是学习的必要条件**
   - 同步执行导致Agent陷入死循环时无法中断
   - 需要超时机制触发学习：`超时 → 分析 → 更新知识`
   
2. **自我学习是可能的**
   - 不是"老师学生同一人"的问题
   - 关键是需要能够中断和反思的机制
   - 类比：人类debug时也是自己学习，但能主动停下来思考

3. **最小可行知识**
   - "1+1=2"太少，无法启动学习循环
   - 至少需要知道基本工具（execute_command, read_file, edit_file）

**教训总结**：
- 承认失败比伪造成功更有价值
- 理论优美不代表实现可行
- 简单 ≠ 过于简单，需要最小可行基础

### agent.md 放置策略（2025-09-13）
**决策**：agent.md只放在根目录 ✅

**理由**：
1. 一个真相来源，避免混乱
2. 模块化需求用knowledge/子目录解决
3. 类比：像package.json只在根目录

**最佳实践**：
```
project/
├── agent.md              # 全局语义记忆
├── knowledge/            # 模块化知识
│   ├── auth/            
│   └── payment/         
└── src/
```

## 最近修改文件
- `/tmp/agent_builder_mda/auto_training/` - 苦涩的教训实验
  - `true_learning.py` - 自学习实验（失败但有价值）
  - `honest_failure_report.md` - 诚实的失败分析
  - `async_mechanism_insight.md` - 异步机制的重要性
  - `agent_md_placement_analysis.md` - agent.md放置策略分析
- `files_summary.md` - 项目文件总结文档（2025-09-19）

---
更新时间：2025-09-19
更新原因：添加文件总结系统知识，记录项目文件结构和统计信息
## 教育记录


### 2025-09-21 22:57 [@memory]

**类型**: 用户教育
**教训**: 访问localhost时必须使用 --noproxy 参数
**置信度**: 1.0

---

### 2025-09-21 22:57 [@memory]

**类型**: 用户教育
**教训**: 使用requests库时要禁用代理 proxies={'http': None, 'https': None}
**置信度**: 1.0

---

### 2025-09-21 23:30 [@memory]

**类型**: 用户教育
**教训**: ReactAgentMinimal的代码应该保持在500行左右，这是"大道至简"原则的体现
**置信度**: 1.0

---### 2024-12-20 12:30 [@learning]

**类型**: 工具偏好
**场景**: 处理大文件时
**教训**: 使用read_file分段读取更高效，避免一次性读取过多内容
**置信度**: 0.8

---

### 2024-12-20 12:30 [@learning]

**类型**: 任务策略
**场景**: 执行知识函数时
**教训**: 先读取相关文件内容，然后使用append_file追加新信息
**置信度**: 0.9

---

### 2024-12-20 12:30 [@learning]

**类型**: 性能优化
**场景**: 更新文件时
**教训**: 使用append_file而不是write_file，可以避免覆盖整个文件，提高效率
**置信度**: 0.8

---