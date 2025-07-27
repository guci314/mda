```markdown
# FastAPI 用户管理平台

基于FastAPI构建的RESTful用户管理系统，提供完整的用户CRUD操作、认证授权和权限控制功能。

## 功能特性

- ✅ 用户注册与账号管理
- ✅ 多角色权限控制（用户/管理员）
- ✅ JWT认证与安全防护
- ✅ 数据验证与错误处理
- ✅ 分页查询与过滤搜索
- ✅ 数据库迁移支持

## 技术栈

- Python 3.8+
- FastAPI
- SQLAlchemy (ORM)
- Pydantic (数据验证)
- Alembic (数据库迁移)
- JWT (认证)

## 数据模型

### 用户字段

| 字段 | 类型 | 必填 | 描述 |
|------|------|------|------|
| id | UUID | 是 | 用户唯一标识 |
| name | String(50) | 是 | 用户姓名 |
| email | EmailStr | 是 | 已验证邮箱 |
| phone | E.164格式 | 是 | 国际电话号码 |
| status | Enum | 否 | active/inactive |
| created_at | DateTime | 是 | 创建时间 |
| updated_at | DateTime | 是 | 更新时间 |

## API文档

### 用户端点

| 端点 | 方法 | 描述 | 权限 |
|------|------|------|------|
| `/api/users/register` | POST | 用户注册 | 公开 |
| `/api/users` | POST | 创建用户 | 管理员 |
| `/api/users` | GET | 用户列表 | 认证用户 |
| `/api/users/{user_id}` | GET | 用户详情 | 用户自己或管理员 |
| `/api/users/{user_id}` | PUT | 更新用户 | 用户自己或管理员 |
| `/api/users/{user_id}` | DELETE | 删除用户 | 管理员 |

### 请求/响应示例

**注册用户 (POST /api/users/register)**
```json
{
  "name": "张三",
  "email": "user@example.com",
  "phone": "+8613812345678"
}
```

**成功响应**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "张三",
  "email": "user@example.com",
  "phone": "+8613812345678",
  "status": "active",
  "created_at": "2023-01-01T00:00:00",
  "updated_at": "2023-01-01T00:00:00"
}
```

## 快速开始

### 安装依赖
```bash
pip install fastapi sqlalchemy pydantic passlib python-jose alembic
```

### 运行服务
```bash
uvicorn main:app --reload
```

### 数据库迁移
```bash
alembic upgrade head
```

## 开发指南

### 环境配置
1. 复制`.env.example`为`.env`
2. 配置数据库连接和JWT密钥

### 测试API
```bash
pytest tests/
```

## 安全建议

1. 生产环境务必修改`SECRET_KEY`
2. 启用HTTPS
3. 实施API速率限制
4. 定期备份数据库

## 许可证

MIT License
```