
# 用户管理系统 PSM - FastAPI

## 平台
- 框架: FastAPI
- 数据库: PostgreSQL with SQLAlchemy
- 认证: JWT

## 实体
### User
- id: UUID
- email: str (unique)
- username: str
- password_hash: str
- created_at: datetime

## 服务
### UserService
- create_user(user_data)
- get_user(user_id)
- update_user(user_id, user_data)
- delete_user(user_id)
- authenticate(email, password)

## API端点
- POST /users - 创建用户
- GET /users/{id} - 获取用户
- PUT /users/{id} - 更新用户
- DELETE /users/{id} - 删除用户
- POST /auth/login - 用户登录
