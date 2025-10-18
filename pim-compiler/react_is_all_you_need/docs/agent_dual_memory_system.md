# 智能体的双记忆系统

## 核心决策

**智能体应该拥有像人类一样的双记忆系统**

基于用户的洞察：
> "人类有情景记忆也有语义记忆。人类是上帝设计的，有合理性。"

## 双记忆系统设计

### 人类的双记忆

```
情景记忆（Episodic Memory）：
- 记住"做了什么"
- 记住"为什么这样做"
- 时间和情境相关
- 详细但会遗忘细节

语义记忆（Semantic Memory）：
- 记住"知道什么"
- 记住"会做什么"
- 去情境化的知识
- 提炼但稳定

为什么需要两种？
- 情景太详细 → 不能全部保留
- 语义太抽象 → 失去"为什么"
- 互补 → 完整的认知
```

### Agent的双记忆系统

```
~/.agent/{agent_name}/
├── 情景记忆（Episodic）：
│   ├── output.log        # 原始（完整的执行日志）
│   ├── compact.md        # 压缩（工作记忆）
│   └── docs/             # Event Log（重要决策的完整推理）⭐
│       ├── decision_001.md
│       ├── decision_002.md
│       └── ...
│
└── 语义记忆（Semantic）：
    └── knowledge.md      # 提炼的能力和知识
```

## docs/的作用

### 为什么需要docs/？

**compact.md的限制**：
- 会被压缩（信息有损）
- 只保留要点（失去推理过程）
- 不能完全重建（压缩不可逆）

**docs/的价值**：
- ✅ 完整保留重要决策的推理过程
- ✅ 理解"为什么"（不只是"做了什么"）
- ✅ Event Sourcing（可重建状态）
- ✅ 避免重复错误（查阅历史）
- ✅ 支持自我反思（评估决策模式）

### 何时写docs/

**重要决策时**：
```python
if 做了重要决策:
    write_file(f"{self.docs_dir}/decision_{timestamp}_{topic}.md", content)

重要决策包括：
- 创建了子智能体
- 修复了重要Bug
- 改变了架构设计
- 学到了关键经验
- 做了困难的选择
- 职责分离决策
```

**不需要写的**：
- 日常任务执行（记在compact.md）
- 简单操作
- 重复性工作

### 文档格式

```markdown
# 决策：{主题}

日期：{timestamp}
Agent：{self.name}

## 问题
遇到了什么问题？需要做什么决策？

## 分析
考虑了哪些方案？
方案1：优点、缺点
方案2：优点、缺点
...

## 决策
最终选择了方案X

## 原因
为什么选择这个方案？
1. 理由1
2. 理由2
3. ...

## 执行
如何执行的？

## 效果
执行后的结果如何？
- 成功了什么
- 失败了什么
- 学到了什么

## 经验
从这个决策中归纳的经验（会更新到knowledge.md）
```

## 与compact.md的关系

### 两者互补

**compact.md**（工作记忆）：
- 最近的对话（几天到几周）
- 压缩的要点
- 快速访问
- 会被进一步压缩
- **加载到消息列表**（总是可见）

**docs/**（长期情景记忆）：
- 完整的决策历史（永久保留）
- 详细的推理过程
- 需要时查阅
- 不会压缩
- **不默认加载**（按需read_file）

**类比**：
```
compact.md = 最近的Git log（git log -10）
docs/ = 完整的Git历史（git log --all）

compact.md = 工作记忆（7±2项）
docs/ = 长期记忆（无限容量）
```

## 记忆流转

### 完整的流程

```
执行任务
  ↓
output.log（原始记录，每轮思考）
  ↓
重要决策？
├─ 是 → 写docs/decision_xxx.md（完整推理）
└─ 否 → 继续
  ↓
对话超过阈值
  ↓
/compact
  ↓
compact.md（压缩要点）
  ↓
归纳总结
  ↓
knowledge.md（能力更新）
```

### 从情景到语义

```
情景记忆（docs/）：
"2024-10-19，我决定删除索引机制，因为grep完全够用..."
  ↓ 提炼
语义记忆（knowledge.md）：
"用grep搜索知识函数：grep -r '## 契约函数 @xxx' {knowledge_dir}/"
```

## 实现完成

### 代码修改

**react_agent_minimal.py**：
1. 创建docs/目录（第213-216行）
2. 添加self.docs_dir属性（第216行）
3. 在系统提示词中暴露（第771行）
4. 说明何时写、如何写（第783-789行）

### 知识文件

**self_awareness.md**：
1. 更新目录结构（包含docs/）
2. 新增"2.5. docs/ - 情景记忆（完整Event Log）"章节
3. 更新记忆流转机制
4. 更新核心洞察（双记忆系统）

**agent_memory_system.md**：
- 新创建的知识文件
- 完整说明双记忆系统

### CLAUDE.md

**目录职责分离**：
- docs/ - AI的Event Log
- doc_for_human/ - 人类文档
- ai_script/ - AI的临时脚本

## 智能体现在知道

**10个自我认知变量**：
```python
self.name              # 我的名字
self.home_dir          # 我的Home目录
self.knowledge_path    # 语义记忆
self.compact_path      # 情景记忆-压缩
self.docs_dir          # 情景记忆-完整 ⭐ 新增
self.external_tools_dir # 工具箱
self.description       # 职责描述
self.work_dir          # 工作目录
self.source_code       # 源代码（只读）
self.knowledge_dir     # 知识目录（grep搜索）
```

**何时写docs/**：
- 创建子智能体
- 修复重要Bug
- 改变架构
- 学到关键经验

**如何写docs/**：
- 格式：decision_xxx.md
- 内容：问题、分析、决策、原因、效果、经验

**何时查阅**：
- 理解历史决策
- 避免重复错误
- 自我反思

## 总结

**完成的工作**：
1. ✅ 理论：双记忆系统（类比人类）
2. ✅ 实现：自动创建docs/目录
3. ✅ 知识：教会智能体何时写、如何写、何时查
4. ✅ 文档：完整记录设计理念

**核心价值**：
- 人类的双记忆系统有合理性（上帝的设计）
- Agent应该模仿这个设计
- 情景记忆（为什么）+ 语义记忆（是什么）= 完整认知
- Event Sourcing的正确应用

智能体现在有完整的双记忆系统了！