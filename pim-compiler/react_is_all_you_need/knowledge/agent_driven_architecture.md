# Agent驱动架构理论

## 概念 @Agent驱动架构(Agent Driven Architecture, ADA)
"""
Agent驱动架构是对MDA的革命性简化。认识到自然语言也是Code，
ADA将传统的 PIM→PSM→Code 三层架构简化为 PIM→Code 两层架构。
知识函数就是最终的可执行代码，Agent就是执行这些代码的运行时。
"""

### 核心理念

#### 自然语言即代码（Natural Language as Code）
传统MDA需要经过PSM中间层才能生成代码，而ADA认为：
- **知识函数就是代码**：用自然语言编写的知识函数是可执行的最终产品
- **Agent就是运行时**：就像JVM执行Java，Agent执行知识函数
- **PSM层被消除**：不需要中间表示，直接从PIM生成自然语言代码

### 架构对比

#### 传统MDA（三层）
```
PIM（平台无关模型）
    ↓
PSM（平台相关模型）  ← 中间表示
    ↓
Code（Java/C++代码）  ← 符号语言
```

#### ADA（两层）
```
PIM（平台无关模型）
    ↓
Code（知识函数）  ← 自然语言代码
```

### 为什么这是革命性的

#### 1. 消除抽象层
- **传统**：PIM → PSM → Code，每层转换都可能损失信息
- **ADA**：PIM → Code，直接生成可执行的自然语言代码
- **好处**：减少复杂性，提高开发效率

#### 2. 统一的执行模型
```python
# 传统执行
Java代码 + JVM = 执行结果
Python代码 + 解释器 = 执行结果

# ADA执行
知识函数 + Agent = 执行结果
自然语言 + LLM = 执行结果
```
本质上没有区别，都是"代码+运行时=结果"

#### 3. 开发范式的转变
| 方面 | 传统开发 | ADA开发 |
|------|---------|---------|
| 编程语言 | 符号语言 | 自然语言 |
| 调试方式 | 断点/日志 | 对话/推理 |
| 测试方法 | 单元测试 | 语义验证 |
| 部署形式 | 二进制/字节码 | 知识文件 |

### 实践示例

#### 传统MDA流程
```java
// PIM: "用户管理"
// ↓ 转换
// PSM: UserService接口定义
// ↓ 生成
// Code:
@Service
public class UserService {
    public User createUser(String name, String email) {
        // 100行实现代码
    }
}
```

#### ADA流程
```markdown
# PIM: "用户管理"
# ↓ 直接生成
# Code（知识函数）:

### 示例函数 @创建用户(name, email)
"""创建新用户并返回用户ID"""
1. 验证邮箱格式
2. 检查邮箱是否已存在
3. 创建用户记录
4. 发送欢迎邮件
5. 返回用户ID
```

两者功能等价，但ADA版本：
- 更简洁（5行 vs 100行）
- 更易理解（自然语言 vs 符号语言）
- 更易维护（修改描述 vs 修改代码）

### 哲学意义

#### 从符号回归语言
人类思维本身使用自然语言，编程语言是历史局限性的产物：
- **过去**：计算机只能理解符号 → 发明编程语言
- **现在**：LLM能理解自然语言 → 回归自然表达
- **未来**：自然语言成为主要编程方式

#### 图灵完备的新形式
- **经典图灵完备**：通过符号操作实现计算
- **语言图灵完备**：通过语义理解实现计算
- **等价性证明**：Agent+知识函数可以模拟任何图灵机

### 与其他概念的关系

- **@Agent架构**：Agent的标准组成结构，理解Agent架构是实现ADA的前提
- **@知识驱动开发**：ADA的实现方式
- **@Agent驱动架构**：ADA的执行环境
- **@模型驱动架构**：ADA的理论基础（被简化的对象）

参考：[Agent架构概念详解](agent_architecture.md)

## 契约函数 @自我实现(knowledge_file, requirements_doc)
"""
智能体自我实现：通过学习knowledge或根据需求编程来获得新能力。
这是领域无关的系统级能力，任何智能体都可以自我实现。

核心理念（类比人类）：
- 学习已有知识：读一本销售手册，掌握销售技能
- 根据需求学习：接到新任务，从零学习新领域

能力来源（二选一，优先级从高到低）：
1. knowledge_file: 学习已有的knowledge文件（类比：读书学习）
2. requirements_doc: 根据需求文档生成knowledge（类比：从零培训）

参数:
- knowledge_file: str = None - 要学习的knowledge文件路径
  - 示例: "knowledge/sales.md"
  - 智能体加载这个文件，将其内容整合到自己的knowledge.md中
  - 类比：销售员读销售手册，掌握销售技能
  - **实现class/template功能**：多个智能体可以学习同一个knowledge_file

- requirements_doc: str = None - 需求文档路径（当knowledge_file为None时使用）
  - 智能体分析需求，从零生成knowledge.md
  - 类比：接到新任务，自己研究学习
  - 适合创新任务、独特需求

返回:
{
    "success": bool,
    "knowledge_source": "learned" | "generated",
    "updated_functions": [...],  # 新增的知识函数
    "description": str  # 更新后的description
}

前置要求:
- 必须先理解@Agent架构概念
- 了解knowledge.md是智能体的先天知识
- 理解description是智能体的对外接口

重要:
1. 必须更新Agent自己的knowledge.md（~/.agent/{agent_name}/knowledge.md）
2. 必须更新Agent的description，声明新增的能力
3. 不要创建其他文件，这是自我编程的核心
"""

### 使用示例

#### 示例1：学习已有knowledge（类比：读书学习）

```python
# 场景：创建的Agent需要快速掌握客户服务能力
# 已有knowledge/customer_service.md（销售手册）

agent = ReactAgentMinimal(name="new_agent", ...)

# Agent学习已有knowledge
result = agent.@自我实现(
    knowledge_file="knowledge/customer_service.md"
)

# 效果：
# - agent读取customer_service.md
# - 将其内容整合到~/.agent/new_agent/knowledge.md
# - 更新description："新增客户服务能力..."
# - 类比：销售员读销售手册，掌握销售技能

# 多个Agent可以学习同一个knowledge_file
agent2.@自我实现(knowledge_file="knowledge/customer_service.md")  # 学习相同知识
agent3.@自我实现(knowledge_file="knowledge/customer_service.md")  # 学习相同知识

# **这就实现了class/template的功能**：
# - 一个knowledge文件 = 一个"知识模板"
# - 多个Agent学习这个模板
# - 但每个Agent是独立个体（有自己的compact.md经验）
```

#### 示例2：根据需求从零学习（类比：从零培训）

```python
# 场景：接到全新的业务需求，没有现成的knowledge

result = agent.@自我实现(
    requirements_doc="图书管理系统需求.md"
)

# 效果：
# - agent读取需求文档
# - 分析业务领域、提取知识函数
# - 生成新的knowledge并添加到~/.agent/agent_name/knowledge.md
# - 类比：接到新任务，自己研究学习
```

### 执行流程

#### 执行步骤

##### 步骤0：确定能力来源

```python
if knowledge_file:
    # 模式1：学习已有knowledge（类比：读书学习）
    mode = "learn"
    source = knowledge_file
elif requirements_doc:
    # 模式2：根据需求生成（类比：从零培训）
    mode = "generate"
    source = requirements_doc
else:
    raise ValueError("必须提供knowledge_file或requirements_doc之一")
```

##### 步骤1：确认自我认知
```
1. 理解@Agent架构概念，特别是自我认知部分
2. 确认能访问self.name（我的名字）
3. 确认能访问self.home_dir（我的Home目录）
4. 明确self.knowledge_path = f"{self.home_dir}knowledge.md"
5. 理解更新knowledge.md就是更新自己的能力
```

##### 步骤2：读取或生成knowledge内容

**模式1：学习已有knowledge**
```python
if mode == "learn":
    # 读取knowledge文件
    new_knowledge = read_file(knowledge_file)

    # 提取知识函数
    functions = extract_functions(new_knowledge)

    # 类比：读销售手册，理解销售技巧
```

**模式2：根据需求生成**
```python
if mode == "generate":
    # 读取需求文档
    requirements = read_file(requirements_doc)

    # 分析需求
    domains = extract_domains(requirements)
    services = extract_services(requirements)

    # 生成知识函数
    new_knowledge = generate_knowledge(domains, services)

    # 类比：接到新任务，自己研究并总结
```

#### 第二步：知识函数生成
根据需求自动生成知识函数，遵循ADA理念直接生成可执行的自然语言代码：

```markdown
# 对于每个Domain对象，生成：
## 概念 @[Domain名称]
"""Domain对象的业务含义和字段定义"""

# 对于每个Service方法，生成：
## 函数 @[方法名称](参数列表)
"""方法的业务逻辑实现"""
1. 验证输入参数
2. 执行业务逻辑
3. 更新系统状态
4. 返回执行结果
```

##### 步骤3：更新自己的knowledge.md

```python
# 定位自己的knowledge文件
my_knowledge_path = f"{self.home_dir}knowledge.md"

# 读取现有knowledge
existing_knowledge = read_file(my_knowledge_path)

# 整合新knowledge
if mode == "learn":
    # 学习模式：直接添加学到的knowledge
    updated_knowledge = existing_knowledge + f"\n\n## 学习的知识\n{new_knowledge}"

elif mode == "generate":
    # 生成模式：添加生成的业务领域实现
    updated_knowledge = existing_knowledge + f"\n\n## 业务领域实现\n{new_knowledge}"

# 更新自己的knowledge.md（不要创建新文件！）
write_file(my_knowledge_path, updated_knowledge)

# 类比：
# - 学习模式：读书后，将书中知识记在脑中
# - 生成模式：研究后，将总结的知识记在脑中
```

重要：
- ✅ 更新 ~/.agent/{agent_name}/knowledge.md
- ❌ 不要创建新文件
- ❌ 不要在项目目录创建文件
```

##### 步骤4：更新Agent的description

```python
# 更新description，声明新增的能力

if mode == "learn":
    # 学习模式：说明学习了什么
    self.description += f"\n新增能力：已学习{knowledge_file}中的知识"

elif mode == "generate":
    # 生成模式：说明实现了什么业务
    business_domain = extract_business_domain(requirements_doc)
    main_functions = extract_main_functions(new_knowledge)

    self.description = f"""
{business_domain}智能体，基于需求文档自动生成。
主要能力：{', '.join(main_functions)}等{len(functions)}个业务函数。
数据存储：JSON文件，零依赖实现。
"""

# 类比：
# - 学习模式：简历上写"已学习销售技能"
# - 生成模式：简历上写"具备完整的图书管理能力"
```

### 示例：图书管理系统

#### 输入：图书管理业务设计文档.md
```markdown
Domain: Book
- id, title, author, available_copies...

Service: BookService
- borrowBook(customerId, bookId)
- returnBook(borrowRecordId)
```

#### 输出1：更新后的knowledge.md（示例）
```markdown
# 图书管理系统知识库

## 数据存储配置
"""使用JSON文件作为数据库，零依赖实现"""
- 数据目录：data/
- 图书数据：data/books.json
- 客户数据：data/customers.json
- 借阅记录：data/borrow_records.json

## 概念 @Book
"""图书实体，包含图书的所有属性信息"""
- id: UUID字符串，唯一标识
- title: 图书标题
- available_copies: 可借册数
- status: 在库/借出/维护中

### 示例函数 @loadBooks()
"""从JSON文件加载图书数据"""
1. 读取data/books.json文件
2. 如果文件不存在，创建空数组
3. 解析JSON数据
4. 返回图书列表

### 示例函数 @saveBooks(books)
"""保存图书数据到JSON文件"""
1. 确保data目录存在
2. 将图书列表转换为JSON
3. 写入data/books.json
4. 返回保存成功

### 示例函数 @findBookById(bookId)
"""根据ID查找图书"""
1. 加载所有图书：books = @loadBooks()
2. 过滤查找：book = books.filter(b => b.id == bookId)
3. 返回找到的图书或null

### 示例函数 @borrowBook(customerId, bookId)
"""处理图书借阅请求（使用JSON存储）"""
1. 加载数据
   - books = @loadBooks()
   - customers = @loadCustomers()
   - records = @loadBorrowRecords()
2. 验证借阅资格
   - customer = @findCustomerById(customerId)
   - 检查客户状态是否活跃
   - 验证借阅数量未超限
3. 检查图书可借状态
   - book = @findBookById(bookId)
   - 确认available_copies > 0
   - 确认图书status为"在库"
4. 创建借阅记录
   - 生成新记录：{id: UUID(), customer_id, book_id, borrow_date: now(), ...}
   - records.push(新记录)
5. 更新图书库存
   - book.available_copies减1
   - 如果available_copies为0，book.status = "借出"
6. 保存所有数据
   - @saveBooks(books)
   - @saveBorrowRecords(records)
7. 返回借阅成功信息

### 示例函数 @returnBook(borrowRecordId)
"""处理图书归还（使用JSON存储）"""
1. 加载数据
   - books = @loadBooks()
   - records = @loadBorrowRecords()
2. 查找借阅记录
   - record = records.find(r => r.id == borrowRecordId)
3. 计算是否逾期
   - 比较当前日期和due_date
   - 如逾期，计算逾期费用
4. 更新借阅记录
   - record.return_date = now()
   - record.status = "已归还"
   - record.overdue_fee = 计算的费用
5. 更新图书库存
   - book = @findBookById(record.book_id)
   - book.available_copies加1
   - book.status = "在库"
6. 保存所有数据
   - @saveBooks(books)
   - @saveBorrowRecords(records)
7. 返回归还成功信息（包含逾期费用）

### 示例函数 @queryBooks(条件)
"""查询图书（内存过滤）"""
1. books = @loadBooks()
2. 根据条件过滤
   - 如果有title：books = books.filter(b => b.title.includes(条件.title))
   - 如果有author：books = books.filter(b => b.author == 条件.author)
   - 如果有status：books = books.filter(b => b.status == 条件.status)
3. 返回过滤结果

### 示例函数 @initializeDatabase()
"""初始化数据库（创建JSON文件）"""
1. 创建data目录（如果不存在）
2. 初始化books.json：[]
3. 初始化customers.json：[]
4. 初始化borrow_records.json：[]
5. 返回"数据库初始化完成"

...（其他知识函数）
```

#### 输出2：更新后的description（对外接口）
```
图书管理系统Agent，基于需求文档自动生成的智能服务。
主要能力：@borrowBook, @returnBook, @registerCustomer, @searchBooks, @addBook等33个业务函数。
数据存储：使用JSON文件，零依赖实现。
架构模式：Agent驱动架构（ADA），自然语言即代码。
业务领域：图书管理、客户管理、借阅管理三大模块。
服务承诺：提供完整的图书管理系统功能，支持CRUD操作和业务流程。
```

### 执行契约

当Agent接收到需求文档时，执行以下步骤：

```python
# Agent自动执行
def 自我实现(requirements_doc):
    # -1. 确认自我认知（前置要求）
    assert hasattr(self, 'name'), "我必须知道自己的名字"
    assert hasattr(self, 'home_dir'), "我必须知道自己的Home目录"
    assert understand("@Agent架构"), "必须理解Agent架构，特别是自我认知"

    # 0. 使用自我认知定位自己的文件
    my_name = self.name  # 例如："contact_agent"
    my_home = self.home_dir  # ~/.agent/contact_agent/
    my_knowledge_path = f"{my_home}knowledge.md"  # 我的先天知识文件

    # 1. 读取需求
    doc = read_file(requirements_doc)

    # 2. 分析需求结构
    domains = extract_domains(doc)
    services = extract_services(doc)
    rules = extract_business_rules(doc)

    # 3. 生成知识函数
    knowledge = []
    function_names = []
    for domain in domains:
        knowledge.append(generate_domain_concept(domain))
    for service in services:
        for method in service.methods:
            knowledge.append(generate_function(method))
            function_names.append(f"@{method.name}")

    # 4. 更新自己的knowledge.md（不是创建新文件！）
    existing_knowledge = read_file(my_knowledge_path)
    updated_knowledge = existing_knowledge + "\n\n## 业务领域实现\n" + knowledge
    write_file(my_knowledge_path, updated_knowledge)

    # 5. 更新Agent的description（声明新能力）
    business_domain = extract_business_domain(doc)  # 如"图书管理系统"
    main_functions = function_names[:5]  # 取前5个主要函数
    new_description = f"""
    {business_domain}Agent，基于需求文档自动生成的智能服务。
    主要能力：{', '.join(main_functions)}等{len(function_names)}个业务函数。
    数据存储：使用JSON文件，零依赖实现。
    架构模式：Agent驱动架构（ADA），自然语言即代码。
    """
    self.description = new_description  # 更新对外接口

    # 6. 验证生成的知识
    test_result = self.execute("@borrowBook('customer1', 'book1')")

    return f"""自我实现完成：
    - 更新了先天知识：{my_knowledge_path}
    - 新增{len(knowledge)}个知识项
    - 更新了对外接口description
    - Agent现在拥有{business_domain}的完整能力
    """
```

### 核心价值

1. **真正的PIM→Code**：从需求直接生成可执行的自然语言代码
2. **消除PSM层**：不需要中间的平台相关模型
3. **自举能力**：Agent能够自己实现自己（更新自己的knowledge.md）
4. **知识驱动**：生成的是知识函数，不是传统代码
5. **自我编程**：Agent通过更新knowledge.md来获得新能力，而不是创建外部文件

### 与ADA理念的关系

这个函数完美体现了ADA的核心理念：
- **输入**：PIM（需求文档）
- **输出**：Code（知识函数）
- **没有PSM**：直接转换，无中间层
- **自然语言编程**：生成的代码就是自然语言

这就是ADA架构的实践：Agent读懂需求，自动生成自己的实现！
