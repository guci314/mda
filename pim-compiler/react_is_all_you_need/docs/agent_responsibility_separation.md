# Agent职责分离原则

## 核心原则

**一个功能只能由一个Agent负责**（Single Responsibility Principle for Agents）

当父Agent创建子Agent后，必须将相关的业务职责完全委托给子Agent，自己不再保留这些业务函数。这是Agent系统架构的基本原则。

## 为什么要职责分离？

### 1. 避免决策冲突
如果父Agent和子Agent都有`@addBook`函数，当收到"添加图书"任务时：
- 父Agent可能自己执行
- 也可能委托给子Agent
- 导致行为不确定性

### 2. 保持知识简洁
- 父Agent不需要维护所有业务细节
- 每个Agent只关注自己的专业领域
- 知识文件更加精简和聚焦

### 3. 明确的责任边界
- 出问题时容易定位是哪个Agent的责任
- 便于独立测试和调试
- 易于维护和升级

### 4. 角色的自然演进
父Agent创建子Agent后，角色自然转变为：
- **协调器（Orchestrator）**：负责任务分发
- **聚合器（Aggregator）**：整合多个子Agent的结果
- **流程管理器（Process Manager）**：管理跨领域流程

## 职责分离的执行步骤

### 步骤1：创建子Agent
```python
# 使用@创建子智能体契约函数创建子Agent
result = @创建子智能体(
    agent_type="book_management_agent",
    domain="图书管理",
    requirements="管理图书的增删改查、库存、分类等",
    model="x-ai/grok-code-fast-1"
)
```

### 步骤2：识别需要委托的函数
```python
# 根据domain识别所有相关的业务函数
delegated_functions = [
    "@addBook", "@updateBook", "@deleteBook",
    "@searchBooks", "@getBookById", "@getAvailableBooks",
    "@updateInventory", "@addCategory", "@updateCategory",
    "@deleteCategory", "@getCategories", "@getBooksByCategory"
]
```

### 步骤3：删除已委托的业务函数
```python
# 从父Agent的knowledge.md中删除这些函数
parent_knowledge = read_file(self.knowledge_path)

for func_name in delegated_functions:
    # 删除函数定义（从### @函数名到下一个###或##）
    pattern = f"### {func_name}.*?(?=###|##|$)"
    parent_knowledge = re.sub(pattern, "", parent_knowledge, flags=re.DOTALL)

write_file(self.knowledge_path, parent_knowledge)
```

### 步骤4：添加任务委托机制
```python
# 在父Agent的knowledge.md中添加任务委托章节
delegation_content = """
## 任务委托 - 子Agent分工

### book_management_agent
- **领域**: 图书管理
- **委托规则**: 当任务包含图书相关关键词时委托
- **调用方式**: result = book_management_agent(task="...")
"""
```

## 函数保留策略

创建子Agent后，父Agent应该：

### ✅ 保留的函数
1. **契约函数**
   - `@创建子智能体` - 创建子Agent的能力
   - `@自我实现` - 自我进化能力
   - 其他系统级契约函数

2. **工具函数**
   - `@generateUUID` - 通用工具
   - `@getCurrentDate` - 时间工具
   - `@formatDate` - 格式化工具
   - 其他通用工具函数

3. **共享数据访问函数**（可选）
   - `@loadBooks` - 如果多个子Agent都需要访问
   - `@saveBooks` - 共享的数据持久化
   - 注：如果只有一个子Agent需要，应该移交给它

### ❌ 删除的函数
1. **业务逻辑函数**
   - 所有领域特定的操作函数
   - 已委托给子Agent的功能
   - 不应该在父Agent中重复存在

2. **领域专属函数**
   - 只有特定子Agent才需要的函数
   - 特定领域的验证逻辑
   - 特定领域的计算逻辑

## 实践案例

### 案例1：图书管理系统

**初始状态**：book_agent拥有所有功能
```
book_agent/knowledge.md
├── 图书管理函数（20个）
├── 客户管理函数（15个）
├── 借阅管理函数（12个）
└── 工具函数（5个）
```

**创建子Agent后**：职责清晰分离
```
book_agent/knowledge.md（协调器）
├── 任务委托章节
├── 契约函数（2个）
└── 工具函数（5个）

book_management_agent/knowledge.md
└── 图书管理函数（20个）

customer_management_agent/knowledge.md
└── 客户管理函数（15个）

borrow_management_agent/knowledge.md
└── 借阅管理函数（12个）
```

### 案例2：任务执行流程

**委托前**：父Agent直接执行
```python
# 用户：添加新图书《深度学习》
book_agent.@addBook(title="深度学习", ...)  # 父Agent直接执行
```

**委托后**：父Agent分发任务
```python
# 用户：添加新图书《深度学习》
book_agent识别任务类型
  ↓
委托给book_management_agent
  ↓
book_management_agent.@addBook(title="深度学习", ...)  # 子Agent执行
  ↓
返回结果给父Agent
```

## 职责分离的好处

### 1. 系统架构清晰
```
         book_agent
         (协调器)
            ↓
     ／     ｜     ＼
    ／      ｜      ＼
图书管理  客户管理  借阅管理
 Agent    Agent    Agent
```

### 2. 可扩展性
- 添加新领域只需创建新的子Agent
- 不影响现有Agent的功能
- 系统可以无限扩展

### 3. 可维护性
- 修改图书管理逻辑只需要修改book_management_agent
- 不会影响其他Agent
- 降低系统复杂度

### 4. 并行处理
- 多个子Agent可以并行执行任务
- 提高系统效率
- 充分利用资源

## 注意事项

### 1. 完全委托
一旦创建子Agent并委托某个领域，就要完全委托，不要保留部分函数。

### 2. 避免循环依赖
子Agent不应该反过来调用父Agent的业务函数。

### 3. 保持独立性
每个子Agent应该能独立完成自己领域的任务，不依赖父Agent的业务逻辑。

### 4. 文档更新
职责分离后要更新description，明确声明自己的新角色。

## 检查清单

父Agent创建子Agent后，请确认：

- [ ] 识别了所有需要委托的业务函数
- [ ] 从knowledge.md中删除了这些函数
- [ ] 添加了任务委托章节
- [ ] 子Agent已注册为可调用的工具
- [ ] 更新了自己的角色描述
- [ ] 测试委托机制是否正常工作

## 总结

职责分离是Agent系统架构的核心原则。通过明确的职责边界：
- 父Agent专注于协调和管理
- 子Agent专注于具体业务执行
- 系统变得更加清晰、可维护和可扩展

记住：**创建子Agent不只是添加帮手，而是职责的完全转移**。