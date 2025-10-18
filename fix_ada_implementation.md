# 修正@ada自我实现的执行方式

## Agent必须明确知道的信息

### 1. 你是谁
- 你的名字：通过self.name获取（例如：contact_agent）
- 你的Home目录：~/.agent/{self.name}/
- 你的knowledge.md位置：~/.agent/{self.name}/knowledge.md

### 2. 什么是自我实现
- **不是**：为项目生成文件
- **而是**：更新你自己的能力

### 3. 正确的执行步骤

```python
# 步骤1：确定自己的身份
my_name = self.name  # 例如："contact_agent"
my_home = f"~/.agent/{my_name}/"
my_knowledge = f"{my_home}knowledge.md"

# 步骤2：读取自己现有的knowledge.md
current_knowledge = read_file(my_knowledge)

# 步骤3：根据需求生成新的知识函数
new_functions = generate_from_requirements(requirements_doc)

# 步骤4：更新自己的knowledge.md（不是创建新文件！）
updated_knowledge = current_knowledge + "\n\n## 业务领域实现\n" + new_functions
write_file(my_knowledge, updated_knowledge)  # 更新自己的文件

# 步骤5：更新自己的description
self.description = "我现在会联系人管理了！"
```

## 常见错误

### ❌ 错误1：在项目目录创建knowledge.md
```python
# 错误
write_file("/Users/guci/robot_projects/contact_app/knowledge.md", content)
```

### ✅ 正确：更新自己的knowledge.md
```python
# 正确
write_file(f"~/.agent/{self.name}/knowledge.md", content)
```

### ❌ 错误2：生成Python代码文件
```python
# 错误
write_file("data_tools.py", python_code)
write_file("business_services.py", python_code)
```

### ✅ 正确：只更新知识函数
```python
# 正确
# 知识函数就是最终代码，不需要生成Python文件
# Agent直接执行知识函数即可
```

## 验证清单

执行@ada自我实现后，检查：

1. ✅ ~/.agent/{agent_name}/knowledge.md 被更新了吗？
2. ✅ Agent的description被更新了吗？
3. ✅ Agent现在能执行新的知识函数了吗？
4. ❌ 没有在项目目录创建knowledge.md吧？
5. ❌ 没有生成Python代码文件吧？

## 核心理念再强调

**@ada自我实现是让Agent获得新能力，不是生成项目文件！**

就像：
- 人类学习新技能 → 大脑获得新能力
- Agent执行@ada自我实现 → knowledge.md获得新函数

这是**自我编程**，不是**为别人编程**！