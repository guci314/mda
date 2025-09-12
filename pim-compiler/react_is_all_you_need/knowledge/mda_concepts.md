# OMG MDA核心概念

## 什么是MDA？
MDA（Model-Driven Architecture，模型驱动架构）是OMG（Object Management Group）定义的软件开发方法论。核心理念是**通过模型转换实现软件开发**，而不是直接编写代码。

## MDA的三层模型体系

### 1. CIM（Computation Independent Model）计算无关模型
- **是什么**：业务领域模型，描述业务需求和业务流程
- **特点**：完全不涉及任何计算概念，纯业务视角
- **举例**：订单处理流程图、组织结构图
- **不是**：不是代码、不是技术设计

### 2. PIM（Platform Independent Model）平台无关模型
- **是什么**：系统功能模型，描述系统做什么，不描述怎么做
- **特点**：包含计算概念（如数据、操作），但不涉及具体技术
- **格式**：通常是结构化数据（JSON、YAML、XML）
- **举例**：
  ```yaml
  model:
    name: "UserService"
    entities:
      - name: "User"
        attributes:
          - name: "id"
            type: "identifier"
          - name: "email"
            type: "string"
    operations:
      - name: "createUser"
        input: "UserData"
        output: "User"
  ```
- **不是**：不是代码、不是数据库表、不是API定义

### 3. PSM（Platform Specific Model）平台特定模型
- **是什么**：技术模型，加入了特定平台的技术细节
- **特点**：仍然是模型（数据结构），不是代码
- **格式**：结构化数据，包含平台特定信息
- **举例**（FastAPI平台）：
  ```json
  {
    "platform": "FastAPI",
    "name": "UserService",
    "models": [
      {
        "name": "UserModel",
        "base": "pydantic.BaseModel",
        "fields": [
          {"name": "id", "type": "int", "primary_key": true},
          {"name": "email", "type": "str", "validation": "EmailStr"}
        ]
      }
    ],
    "endpoints": [
      {
        "path": "/users",
        "method": "POST",
        "handler": "create_user",
        "input_model": "UserCreate",
        "output_model": "UserModel",
        "status_code": 201
      }
    ],
    "database": {
      "orm": "SQLAlchemy",
      "table": "users"
    }
  }
  ```
- **不是**：不是Python文件、不是可执行代码

### 4. Code（代码）
- **是什么**：从PSM生成的可执行代码
- **特点**：可以直接运行的程序文件
- **举例**：main.py、models.py、routes.py等
- **生成时机**：只有Code Generator才生成代码

## MDA转换流程

```
CIM（可选）
    ↓ 需求分析
PIM（必需）
    ↓ 模型转换（Model Transformation）
PSM（必需）
    ↓ 代码生成（Code Generation）
Code（最终产物）
```

## 关键概念澄清

### "模型"vs"代码"
- **模型（Model）**：描述系统的结构化数据，是"蓝图"
- **代码（Code）**：可执行的程序，是"建筑物"

### "转换"vs"生成"
- **转换（Transform）**：模型到模型，如PIM→PSM
- **生成（Generate）**：模型到代码，如PSM→Code

### 常见错误理解
❌ **错误**：PIM是伪代码
✅ **正确**：PIM是业务模型的数据结构

❌ **错误**：PSM是框架代码
✅ **正确**：PSM是带技术细节的模型数据

❌ **错误**：转换就是生成代码
✅ **正确**：转换是模型到模型，生成才是模型到代码

## Agent职责映射

根据MDA理论，不同Agent的职责应该是：

### PIM Parser Agent
- **输入**：PIM文件（.pim/.yaml/.json）
- **输出**：PIM数据结构（Dict/JSON）
- **禁止**：生成代码、写文件

### PIM2PSM Transformer Agent  
- **输入**：PIM数据结构
- **输出**：PSM数据结构
- **禁止**：生成代码、写文件

### Code Generator Agent
- **输入**：PSM数据结构
- **输出**：代码文件（.py/.js/.java等）
- **允许**：写文件

### Test Runner Agent
- **输入**：生成的代码文件路径
- **输出**：测试结果
- **允许**：执行代码、读写文件

## 为什么要这样设计？

### 1. 分离关注点
- 业务逻辑（PIM）独立于技术实现（PSM）
- 便于业务变更和技术升级

### 2. 提高复用性
- 同一个PIM可以转换为不同平台的PSM
- 同一个PSM可以生成不同风格的代码

### 3. 保证一致性
- 模型是"单一真相源"
- 代码总是与模型保持同步

### 4. 支持自动化
- 通过工具链自动完成转换和生成
- 减少人工编码错误

## 记住核心原则

**MDA的本质是模型驱动，不是代码驱动**

1. 模型是一等公民，代码是衍生品
2. 先有模型，后有代码
3. 修改模型，重新生成代码
4. 永远不要跳过模型直接写代码

## 自检问题

当你作为MDA系统的Agent时，问自己：

1. 我的输入是模型还是代码？
2. 我的输出是模型还是代码？
3. 我是在转换（模型→模型）还是生成（模型→代码）？
4. 我的职责边界清晰吗？

如果不确定，重读本文档。