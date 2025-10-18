# @创建子智能体 详细实现指南

## 契约函数 @创建子智能体(agent_type, domain, requirements, model, parent_knowledge)

"""
详细说明见: [self_awareness.md](../knowledge/self_awareness.md#契约函数-create_subagent)

本文档提供@创建子智能体契约函数的详细实现步骤和代码示例。
"""

## 详细实现步骤

### 步骤1：检查子Agent是否已存在

避免重复创建，提高效率。

```python
# 检查子Agent是否已注册为工具
for tool in self.function_instances:
    if tool.name == agent_type:
        return {
            "success": True,
            "agent_name": agent_type,
            "home_dir": f"~/.agent/{agent_type}/",
            "message": "子Agent已存在，无需重复创建"
        }

# 检查文件系统中是否已创建
agent_home = f"~/.agent/{agent_type}/"
if os.path.exists(os.path.expanduser(agent_home)):
    # 目录存在但未注册为工具，重新加载
    sub_agent = ReactAgentMinimal(
        name=agent_type,
        work_dir=self.work_dir,
        # 从state.json读取配置...
    )
    self.add_function(sub_agent)
    return {
        "success": True,
        "agent_name": agent_type,
        "home_dir": agent_home,
        "message": "子Agent已存在，已重新加载为工具"
    }
```

### 步骤2：验证输入参数

```python
# 命名规范检查
if not agent_type.endswith("_agent"):
    raise ValueError("agent_type必须以_agent结尾")

# 领域验证
if not domain or len(domain.strip()) == 0:
    raise ValueError("domain不能为空")

# 需求验证
if not requirements or len(requirements.strip()) < 10:
    raise ValueError("requirements必须提供详细的需求描述")
```

### 步骤3：配置LLM模型

使用@获取模型配置函数获取正确的API配置。

```python
# 调用知识函数获取配置
config = @获取模型配置(model)
# config包含：
# - model: 完整的模型名称
# - base_url: 匹配的API地址
# - api_key_env: 环境变量名

# 创建state.json配置
state_config = {
    "name": agent_type,
    "description": f"{domain}专业Agent",
    "model": config["model"],
    "base_url": config["base_url"],
    "api_key_env": config["api_key_env"],
    "work_dir": self.work_dir,
    "has_compact": False,
    "message_count": 0,
    "timestamp": datetime.now().isoformat(),
    "task_count": 0,
    "children": []
}
```

⚠️ **重要**：
- 绝对禁止硬编码API密钥
- 必须使用api_key_env指定环境变量名
- 必须调用@获取模型配置确保配置正确

### 步骤4：创建Home目录结构

```python
import os
from pathlib import Path

# 创建主目录
home_dir = Path.home() / ".agent" / agent_type
home_dir.mkdir(parents=True, exist_ok=True)

# 创建external_tools目录
(home_dir / "external_tools").mkdir(exist_ok=True)

# 初始化state.json
state_file = home_dir / "state.json"
with open(state_file, 'w', encoding='utf-8') as f:
    json.dump(state_config, f, ensure_ascii=False, indent=2)
```

### 步骤5：生成完备的knowledge.md

子Agent的knowledge.md必须完备，包含所有必要的知识。

```python
# 读取父Agent的知识（如果需要继承）
parent_knowledge_content = ""
if parent_knowledge:
    parent_knowledge_content = read_file(self.knowledge_path)
    # 提取需要继承的部分（工具函数、数据访问函数等）
    parent_knowledge_content = extract_inheritable_knowledge(parent_knowledge_content)

# 生成领域特定的知识函数
domain_functions = generate_domain_functions(domain, requirements)

# 组合完整的knowledge.md
knowledge_content = f"""# {agent_type} 知识库

创建时间: {datetime.now().isoformat()}
专业领域: {domain}
父Agent: {self.name}

## 核心能力
{extract_domain_capabilities(requirements)}

## 自我认知
- 我的名字: {agent_type}
- 我的Home目录: ~/.agent/{agent_type}/
- 我的knowledge.md: ~/.agent/{agent_type}/knowledge.md
- 我的工作目录: {self.work_dir}
- 我的专业领域: {domain}

## 继承的知识
{parent_knowledge_content if parent_knowledge else "无"}

## 领域知识函数
{domain_functions}

## 决策逻辑
{generate_decision_logic(domain)}

## 经验总结
（由Agent在执行中积累）
"""

# 写入文件
knowledge_file = home_dir / "knowledge.md"
with open(knowledge_file, 'w', encoding='utf-8') as f:
    f.write(knowledge_content)
```

**知识生成策略**：
- 继承父Agent的通用能力（工具函数、数据访问）
- 生成领域特定的业务函数
- 确保至少100行内容
- 包含必要的章节结构

### 步骤6：生成详细的description

```python
description = f"""{agent_type} - {domain}专业Agent

核心职责：
{extract_responsibilities(requirements)}

能力范围：
{list_capabilities(domain)}

接口契约：
- 输入：{domain}相关的任务描述
- 输出：任务执行结果和状态报告
- 保证：领域内任务的专业处理
"""
```

### 步骤7：验证子Agent的完备性

创建后必须验证子Agent的独立执行能力。

```python
def verify_agent_completeness(agent_name):
    """验证子Agent的完备性"""

    checks = {
        "目录结构": check_directory_structure(agent_name),
        "知识完备": check_knowledge_completeness(agent_name),
        "独立执行": check_independent_execution(agent_name),
        "API配置": check_api_configuration(agent_name),
        "领域能力": check_domain_capabilities(agent_name)
    }

    return all(checks.values()), checks

# 知识完备性检查
def check_knowledge_completeness(agent_name):
    knowledge_path = f"~/.agent/{agent_name}/knowledge.md"

    if not os.path.exists(os.path.expanduser(knowledge_path)):
        return False

    content = read_file(knowledge_path)

    # 检查内容长度（至少100行）
    if len(content.splitlines()) < 100:
        return False

    # 检查必要章节
    required_sections = [
        "## 核心能力",
        "## 自我认知",
        "## 领域知识函数",
        "## 决策逻辑"
    ]

    for section in required_sections:
        if section not in content:
            return False

    # 检查知识函数数量（至少5个）
    if content.count("### @") < 5:
        return False

    return True

# 独立执行测试
def check_independent_execution(agent_name):
    try:
        # 创建Agent实例（只用自己的知识）
        agent = ReactAgentMinimal(
            name=agent_name,
            work_dir=get_work_dir(),
            knowledge_files=[f"~/.agent/{agent_name}/knowledge.md"]
        )

        # 执行测试任务
        test_task = get_domain_test_task(agent_name)
        result = agent.execute(test_task)

        return "成功" in result or "完成" in result
    except Exception:
        return False
```

### 步骤8：注册子Agent为工具

这是关键步骤，确保后续可以直接调用。

```python
# 创建子Agent实例
sub_agent = ReactAgentMinimal(
    name=agent_type,
    work_dir=self.work_dir,
    model=config["model"],
    base_url=config["base_url"],
    api_key=os.getenv(config["api_key_env"]),
    knowledge_files=[str(knowledge_file)]
)

# ⭐ 关键：注册为父Agent的工具
self.add_function(sub_agent)  # 子Agent本身就是Function

# 记录父子关系
if not hasattr(self, 'children'):
    self.children = []
self.children.append(agent_type)

# 持久化父子关系
self._auto_save_state()
```

### 步骤9：更新父Agent的knowledge.md - 职责分离

创建子Agent后，父Agent必须删除已委托的业务函数。

#### 9.1 添加任务委托章节

```python
delegation_content = f"""
## 任务委托 - 子Agent分工

### {agent_type}
- **领域**: {domain}
- **职责**: {responsibilities}
- **委托规则**:
  当任务包含以下关键词时，委托给{agent_type}：
  {delegation_keywords}

- **调用方式**:
  ```python
  result = {agent_type}(task="{example_task}")
  ```

- **典型任务示例**:
  {task_examples}
"""
```

#### 9.2 删除已委托的业务函数

```python
def identify_delegated_functions(domain):
    """识别需要删除的业务函数"""
    delegated_map = {
        "图书管理": [
            "@addBook", "@updateBook", "@deleteBook", "@searchBooks",
            "@getBookById", "@getAvailableBooks", "@updateInventory",
            "@addCategory", "@updateCategory", "@deleteCategory",
            "@getCategories", "@getBooksByCategory"
        ],
        "客户管理": [
            "@registerCustomer", "@updateCustomer", "@deleteCustomer",
            "@searchCustomers", "@getCustomerById", "@validateCustomer",
            "@updateMembership", "@upgradeMembership", "@renewMembership",
            "@getMembershipBenefits", "@validateMembership"
        ],
        "借阅管理": [
            "@borrowBook", "@returnBook", "@renewBook",
            "@getBorrowRecords", "@getOverdueRecords",
            "@calculateOverdueFee", "@validateBorrowEligibility",
            "@getBorrowPolicy", "@updateBorrowPolicy",
            "@calculateDueDate", "@validateBorrowLimit"
        ]
    }
    return delegated_map.get(domain, [])

# 删除函数
delegated_functions = identify_delegated_functions(domain)
parent_knowledge = read_file(self.knowledge_path)

for func_name in delegated_functions:
    # 删除函数定义（从### @函数名到下一个###或##）
    pattern = f"### {func_name}.*?(?=###|##|$)"
    parent_knowledge = re.sub(pattern, "", parent_knowledge, flags=re.DOTALL)
```

#### 9.3 转型为协调器

```python
# 更新角色描述
if "## 核心角色" not in parent_knowledge:
    parent_knowledge = "## 核心角色\n协调器（Orchestrator）- 负责任务分发和结果聚合\n\n" + parent_knowledge

# 添加任务委托章节
if "## 任务委托" not in parent_knowledge:
    parent_knowledge += "\n\n" + delegation_content
else:
    parent_knowledge = insert_delegation(parent_knowledge, delegation_content)

# 保存更新
write_file(self.knowledge_path, parent_knowledge)

print(f"✅ 职责分离完成：")
print(f"   - 删除了 {len(delegated_functions)} 个已委托的业务函数")
print(f"   - 父Agent转型为协调器角色")
print(f"   - 子Agent {agent_type} 负责 {domain} 领域的所有业务")
```

### 步骤10：返回创建结果

```python
return {
    "success": True,
    "agent_name": agent_type,
    "home_dir": str(home_dir),
    "verification": verification_results,
    "delegation_info": {
        "keywords": delegation_keywords,
        "responsibilities": responsibilities
    }
}
```

## 保留函数策略

父Agent删除业务函数后应保留：

### ✅ 保留的函数
1. **契约函数**：@创建子智能体, @自我实现等
2. **工具函数**：@generateUUID, @getCurrentDate等
3. **共享数据访问**：@loadBooks等（如果多个子Agent都需要）

### ❌ 删除的函数
1. **业务逻辑函数**：已委托给子Agent的具体操作
2. **领域专属函数**：只有特定子Agent需要的函数

## 常见问题

### 问题1：子Agent知识不完备
**解决**：确保继承父Agent知识并生成完整的领域知识函数

### 问题2：LLM配置错误
**解决**：必须调用@获取模型配置确保配置匹配

### 问题3：子Agent无法独立执行
**解决**：验证knowledge.md包含所有必要知识，不依赖外部文件

### 问题4：重复创建
**解决**：步骤1检查子Agent是否已存在

## 参考

- [职责分离原则](./agent_responsibility_separation.md)
- [修复子Agent重复创建问题](./fix_agent_recreation_issue.md)