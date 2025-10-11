# 知识文件索引

本目录包含Agent系统的所有知识文件。

---

## 默认加载（所有Agent自动加载）

### 核心知识
1. **system_prompt_minimal.md** - 系统提示词（Agent本质定义）
2. **validation_adaptive.md** - 自适应验证（客观+主观）
3. **learning_functions.md** - 学习与记忆契约函数
   - @learning() - 从实践学习
   - @memory() - 记住用户教育
   - @learning_from_expert() - 向Claude请教
4. **agent_essence.md** - Agent本质理解
5. **model_mappings.md** - 模型配置
   - @切换模型() - LLM切换
6. **honesty_enforcement.md** - 诚实原则（防虚报、禁借口）

### 个体知识
7. **~/.agent/[name]/knowledge.md** - Agent个体知识（如果存在）

---

## 按需加载（特定Agent手动加载）

### 专用功能
- **test_fixing_function.md** (541行) - 测试修复
  - @修复测试() - 系统化修复流程
  - 诚实验证、禁止借口、完成验证契约
  - 适用：需要修复测试的Agent

- **work_with_expert.md** - 与专家对比学习
  - @work_with_expert() - 自己做→Claude做→对比→学习
  - 适用：需要对比学习的Agent

---

## 文档（不加载，供阅读）

### 理论文档（docs/）
- **agi_formula_3.0.md** - AGI公式3.0
- **externalization_creates_certainty.md** - 外部化创造确定性
- **why_execution_context_enforces_honesty.md** - ExecutionContext为何有强制性
- **heterogeneous_agent_collaboration.md** - 异构Agent协作范式
- **metacognition_triggers.md** - 元认知触发机制设计

### 实践指南（examples/）
- **fast_slow_agent_demo.py** - 快慢Agent协作示例

---

## 知识文件设计原则

### 1. 通用 vs 专用
```
通用（默认加载）：
- 所有Agent都需要的基础能力
- 诚实、学习、验证

专用（按需加载）：
- 特定任务的专业知识
- 测试修复、特殊功能
```

### 2. 大小控制
```
默认加载总量：
- 控制在30K tokens以内
- 避免过度占用上下文

专用知识：
- 可以更大（需要时再加载）
```

### 3. 职责单一
```
每个文件一个主题：
- learning_functions.md → 学习契约函数
- model_mappings.md → 模型配置
- honesty_enforcement.md → 诚实原则

不要混杂
```

---

## 快速查找

### 我需要...

**学习功能**：
- 从实践学习 → learning_functions.md (@learning)
- 记住教育 → learning_functions.md (@memory)
- 向专家请教 → learning_functions.md (@learning_from_expert)

**诚实执行**：
- 防止虚报成功 → honesty_enforcement.md
- 禁止找借口 → honesty_enforcement.md

**验证方法**：
- 自适应验证 → validation_adaptive.md
- 客观验证 → validation_objective.md（不默认加载）
- 程序正义验证 → validation_procedural_justice.md（不默认加载）

**模型配置**：
- 切换模型 → model_mappings.md (@切换模型)

**测试修复**：
- 修复测试 → test_fixing_function.md (@修复测试)

**专家协作**：
- 对比学习 → work_with_expert.md (@work_with_expert)

---

## 添加新知识文件

### 通用知识（考虑默认加载）
```
1. 文件大小 < 100行
2. 所有Agent都需要
3. 核心能力或原则
→ 添加到react_agent_minimal.py的默认加载列表
```

### 专用知识（按需加载）
```
1. 针对特定任务
2. 文件可以较大
3. 少数Agent需要
→ Agent创建时手动指定
```

---

## 当前统计

```
默认加载：7个文件
- system_prompt_minimal.md
- validation_adaptive.md
- learning_functions.md (3个契约函数)
- agent_essence.md
- model_mappings.md (1个契约函数)
- honesty_enforcement.md
- knowledge.md (个体)

按需加载：2个文件
- test_fixing_function.md (1个契约函数)
- work_with_expert.md (1个契约函数)

总契约函数：6个
```

---

## 知识的层次

```
第1层：系统（system_prompt_minimal.md）
  ↓ Agent是什么

第2层：原则（validation_adaptive.md, honesty_enforcement.md）
  ↓ 如何验证、如何诚实

第3层：能力（learning_functions.md, agent_essence.md）
  ↓ 如何学习、如何理解自己

第4层：配置（model_mappings.md）
  ↓ 如何切换模型

第5层：个体（knowledge.md）
  ↓ 这个Agent独特的知识

第6层：专用（test_fixing_function.md等）
  ↓ 特定任务的专业知识
```

**从通用到专用，层层递进。**
