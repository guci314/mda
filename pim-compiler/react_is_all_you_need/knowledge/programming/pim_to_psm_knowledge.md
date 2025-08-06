# PIM 转 PSM 转换知识

## 概述

本文档包含将 PIM（Platform Independent Model）转换为 PSM（Platform Specific Model）的核心知识和转换规则。

## PIM 和 PSM 的区别

### PIM（平台无关模型）
- **关注点**：业务逻辑和需求
- **语言**：自然语言描述
- **内容**：业务实体、流程、规则
- **特点**：不涉及技术实现细节

### PSM（平台特定模型）
- **关注点**：技术实现方案
- **语言**：技术术语和规范
- **内容**：数据模型、API 设计、技术架构
- **特点**：针对特定技术栈的设计

## 转换规则

### 1. 业务实体转换

#### PIM 示例：
```markdown
### 用户
系统的使用者。

属性：
- 用户名：唯一标识
- 邮箱：用于登录和通知
- 密码：加密存储
- 注册时间：记录创建时间
```

#### PSM 转换（FastAPI）：
```markdown
### User 数据模型

#### SQLAlchemy 模型
- 表名：users
- 字段：
  - id: Integer, Primary Key, 自增
  - username: String(50), Unique, Not Null, Index
  - email: String(100), Unique, Not Null, Index
  - password_hash: String(255), Not Null
  - created_at: DateTime, Default=now()
  - updated_at: DateTime, Default=now(), OnUpdate=now()

#### Pydantic Schema
- UserCreate: username, email, password
- UserResponse: id, username, email, created_at
- UserUpdate: username?, email?
```

### 2. 业务流程转换

#### PIM 示例：
```markdown
### 用户注册流程
1. 用户填写注册信息
2. 系统验证信息有效性
3. 创建用户账号
4. 发送欢迎邮件
```

#### PSM 转换（FastAPI）：
```markdown
### 用户注册 API

#### 端点设计
- POST /api/users/register
- 请求体：UserCreate schema
- 响应：UserResponse schema

#### 实现步骤
1. 验证输入数据（Pydantic 自动验证）
2. 检查用户名/邮箱唯一性
3. 密码加密（bcrypt）
4. 数据库事务：
   - 创建用户记录
   - 记录注册日志
5. 异步任务：发送欢迎邮件
6. 返回用户信息（排除密码）

#### 错误处理
- 400: 验证失败
- 409: 用户名/邮箱已存在
- 500: 服务器错误
```

### 3. 业务规则转换

#### PIM 示例：
```markdown
### 文章发布规则
- 只有注册用户可以发布文章
- 文章标题不能为空
- 文章内容至少 100 字
- 每个用户每天最多发布 10 篇文章
```

#### PSM 转换（FastAPI）：
```markdown
### 文章发布验证

#### 认证中间件
- 使用 JWT Bearer Token
- 依赖注入：get_current_user

#### 数据验证
```python
class ArticleCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=100)
    
    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('标题不能为空')
        return v
```

#### 业务逻辑验证
- 在 Service 层实现发布频率限制
- 使用 Redis 记录用户日发布数
- 键格式：article_count:{user_id}:{date}
- TTL：24小时
```

## 转换模式

### 1. 实体映射模式

| PIM 概念 | PSM 概念（FastAPI） |
|---------|-------------------|
| 业务实体 | SQLAlchemy Model |
| 属性 | 数据库字段 |
| 唯一约束 | Unique Index |
| 关联关系 | Foreign Key |
| 业务标识 | Primary Key |

### 2. 流程映射模式

| PIM 流程 | PSM 实现 |
|---------|---------|
| 用户操作 | API 端点 |
| 系统验证 | Pydantic Schema + Validator |
| 数据处理 | Service 层方法 |
| 状态变更 | 数据库事务 |
| 通知/消息 | 异步任务队列 |

### 3. 规则映射模式

| PIM 规则 | PSM 实现 |
|---------|---------|
| 权限规则 | 认证/授权中间件 |
| 数据规则 | Schema 验证器 |
| 业务规则 | Service 层逻辑 |
| 限制规则 | 速率限制/缓存 |

## 最佳实践

### 1. 命名转换
- PIM 中文名称 → PSM 英文名称
- 使用清晰的英文命名
- 遵循目标平台命名规范

### 2. 关系处理
- 一对多：外键 + relationship
- 多对多：关联表
- 级联操作：明确定义

### 3. 性能考虑
- 为查询字段添加索引
- 使用分页避免大数据查询
- 考虑缓存策略

### 4. 安全考虑
- 敏感数据加密存储
- API 认证授权
- 输入验证和清理
- SQL 注入防护

## 转换示例

### 完整示例：博客系统

#### PIM 输入
```markdown
# 博客系统

## 业务实体

### 文章
- 标题
- 内容
- 作者
- 发布时间
- 分类

### 分类
- 名称（唯一）
- 描述

## 业务流程

### 发布文章
1. 用户撰写文章
2. 选择分类
3. 发布
```

#### PSM 输出
```markdown
# 博客系统 PSM

## 数据模型

### Article 表
- id: Integer, PK
- title: String(200), Not Null
- content: Text, Not Null
- author_id: Integer, FK(users.id)
- category_id: Integer, FK(categories.id)
- published_at: DateTime
- created_at: DateTime
- updated_at: DateTime

### Category 表
- id: Integer, PK
- name: String(50), Unique, Not Null
- description: Text

## API 设计

### 文章管理
- GET /api/articles - 文章列表（分页）
- GET /api/articles/{id} - 文章详情
- POST /api/articles - 创建文章（需认证）
- PUT /api/articles/{id} - 更新文章（需认证+授权）
- DELETE /api/articles/{id} - 删除文章（需认证+授权）

### 分类管理
- GET /api/categories - 分类列表
- POST /api/categories - 创建分类（需管理员权限）
```

## 转换检查清单

- [ ] 所有业务实体都映射为数据模型
- [ ] 所有属性都有合适的数据类型
- [ ] 所有约束都正确实现
- [ ] 所有流程都映射为 API 端点
- [ ] 所有业务规则都有对应实现
- [ ] 考虑了性能优化
- [ ] 考虑了安全性
- [ ] 添加了必要的技术字段（id, timestamps）
- [ ] 定义了合适的索引
- [ ] 设计了恰当的错误处理