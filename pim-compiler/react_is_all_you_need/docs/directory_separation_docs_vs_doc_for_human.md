# 文档目录分离：docs vs doc_for_human

## 问题

**docs/目录的职责混淆**：

原本用途：
- 给人类看的文档
- 系统设计说明
- 用户手册

实际用途（本次会话）：
- AI的思考记录（event log）
- 设计决策的完整历史
- Event Sourcing的事件序列

**混淆**：两种用途混在一起

## 解决方案

**创建新目录分离职责**：

```
pim-compiler/react_is_all_you_need/
├── docs/                    # AI的event log（AI自己的记录）
│   ├── fix_xxx.md           # 修复过程
│   ├── remove_xxx.md        # 删除决策
│   └── ...                  # 思考记录
│
└── doc_for_human/           # 人类文档（用户要求写的）
    ├── 用户手册.md
    ├── 系统设计文档.md
    └── API文档.md
```

## 目录职责

### docs/（AI的event log）

**用途**：
- AI的思考过程记录
- 设计决策的完整历史
- Event Sourcing日志

**特点**：
- ✅ 完整详细（保留所有推理）
- ✅ 时间序列（按对话顺序）
- ✅ AI自己参考（保持一致性）
- ❌ 人类可能不看（太详细）

**内容类型**：
- 修复过程（fix_xxx.md）
- 删除决策（remove_xxx.md）
- 重构说明（refactoring_xxx.md）
- 设计洞察（xxx_insight.md）
- 架构演化（session_summary.md）

**类比**：
- Git log（完整的commit历史）
- Debug log（调试过程记录）
- Lab notebook（实验记录）

### doc_for_human/（人类文档）

**用途**：
- 用户要求编写的文档
- 面向人类的说明
- 交付物

**特点**：
- ✅ 精炼易懂（为人类优化）
- ✅ 结构化（章节清晰）
- ✅ 实用导向（怎么用）
- ✅ 用户会看（重要！）

**内容类型**：
- 用户手册
- API文档
- 系统架构文档（高层次）
- 快速开始指南
- FAQ

**类比**：
- README.md（项目说明）
- User Manual（用户手册）
- API Reference（接口文档）

## 使用规则

### AI的行为

**写docs/**（自动，不需要用户要求）：
```
当我做了重要决策时：
→ 自动写docs/fix_xxx.md记录
→ 作为我的event log
→ 用户不用管
```

**写doc_for_human/**（只在用户明确要求时）：
```
用户说："写一个用户手册"
→ 写doc_for_human/用户手册.md
→ 这是交付给用户的
→ 用户会看
```

### 区分标准

| 问题 | 放哪里 |
|------|--------|
| 这是AI的思考记录吗？ | docs/ |
| 用户明确要求写文档吗？ | doc_for_human/ |
| 记录"为什么这样设计"吗？ | docs/ |
| 告诉用户"怎么使用"吗？ | doc_for_human/ |

## 需要的操作

### 1. 创建目录

由于权限限制，请手动执行：

```bash
cd /Users/guci/aiProjects/mda/pim-compiler/react_is_all_you_need
mkdir doc_for_human
```

### 2. 添加README说明

创建两个README：

**docs/README.md**：
```markdown
# AI Event Log

这个目录是AI的思考记录和设计决策日志。

- 记录每次对话的重要决策
- Event Sourcing模式
- 完整的演化历史
- 主要给AI自己参考

人类可以阅读，但可能很详细。
```

**doc_for_human/README.md**：
```markdown
# 人类文档

这个目录是面向人类用户的文档。

- 用户手册
- 系统设计文档
- API参考
- 使用指南

只包含用户明确要求编写的文档。
```

## 类比说明

### 软件开发中的类比

```
docs/          = Git log（完整历史）
doc_for_human/ = README.md（给用户看的）

docs/          = 源代码注释（给开发者）
doc_for_human/ = 用户手册（给用户）

docs/          = 设计文档（why）
doc_for_human/ = 使用文档（how）
```

### Event Sourcing的类比

```
Event Store（事件存储）：
└── docs/（所有事件/决策）

Read Model（读模型）：
└── doc_for_human/（给人类的视图）

类似CQRS模式：
- 写模型：完整历史（docs/）
- 读模型：优化视图（doc_for_human/）
```

## 好处

### 1. 职责清晰

```
docs/：
- AI的工作空间
- 想写多少写多少
- 用户不用管

doc_for_human/：
- 交付物
- 用户明确要求
- 精心编写
```

### 2. 避免混乱

```
之前：
docs/中既有AI的思考记录，又有给用户的文档
→ 混乱，用户不知道该看哪个

现在：
docs/ = AI的（不用看）
doc_for_human/ = 用户的（明确交付）
→ 清晰
```

### 3. 符合惯例

```
开源项目：
docs/ = 详细的技术文档（开发者看）
README = 快速开始（用户看）

类似：
docs/ = AI的详细记录（AI看）
doc_for_human/ = 用户文档（用户看）
```

## 总结

**你的决策**：
- ✅ 分离docs/和doc_for_human/
- ✅ docs/是AI的event log
- ✅ doc_for_human/是交付物
- ✅ 用户不关心docs/有多少内容

**我的理解**：
- 文档是我的工作工具
- 不是你的阅读材料
- 只要帮助我更好地工作就行

**未来的规则**：
- 我的思考记录 → docs/
- 用户要求的文档 → doc_for_human/
- 清晰分离，各司其职

需要我创建doc_for_human/README.md说明这个分离吗？