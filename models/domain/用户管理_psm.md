# 用户管理领域模型 (PSM - FastAPI)

> 此模型从 [用户管理_pim.md](./用户管理_pim.md) 转换生成
> 生成时间：2024-01-20
> 目标平台：FastAPI + PostgreSQL

## 业务描述

用户管理系统负责维护系统中的用户信息，提供用户的创建、查询、更新和删除功能。基于PIM分析，这是一个标准的CRUD系统，采用FastAPI + PostgreSQL的轻量级技术架构。

## 技术架构决策

### 技术选型
- **Web框架**：FastAPI（高性能、自动API文档）
- **数据库**：PostgreSQL（可靠性、ACID事务）
- **ORM**：SQLAlchemy（成熟稳定）
- **数据验证**：Pydantic（FastAPI原生集成）

### 简化设计原则
- 无需认证系统（纯CRUD服务）
- 无需缓存层（数据量不大）
- 单体服务架构（功能简单）

## 实体模型

```mermaid
classDiagram
    class User {
        +UUID id
        +String name
        +String email
        +String phone
        +UserStatus status
        +DateTime created_at
        +DateTime updated_at
    }
    
    class UserService {
        +create_user(UserCreate) User
        +get_user(UUID) User
        +get_users(skip, limit) List~User~
        +update_user(UUID, UserUpdate) User
        +delete_user(UUID) bool
    }
    
    UserService ..> User : manages
```

## 枚举类型

```python
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
```

## 技术规格

### 数据库设计

#### 表结构
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE UNIQUE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status);
CREATE INDEX idx_users_created_at ON users(created_at DESC);

-- 更新时间触发器
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### Pydantic模型

#### 基础模型
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    
class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, pattern=r'^\+?1?\d{9,15}$')
    status: Optional[UserStatus] = None

class UserInDB(UserBase):
    id: UUID
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class User(UserInDB):
    pass
```

### SQLAlchemy模型

```python
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20), nullable=True)
    status = Column(Enum(UserStatus), nullable=False, default=UserStatus.ACTIVE)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
```

## API设计

### RESTful端点

#### 用户管理
- `POST /api/v1/users` - 创建用户
- `GET /api/v1/users` - 获取用户列表（分页）
- `GET /api/v1/users/{user_id}` - 获取用户详情
- `PUT /api/v1/users/{user_id}` - 更新用户信息
- `DELETE /api/v1/users/{user_id}` - 删除用户（软删除）

### 请求/响应示例

#### 创建用户
```json
POST /api/v1/users
Content-Type: application/json

{
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "+8613812345678"
}

Response 201:
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "张三",
    "email": "zhangsan@example.com",
    "phone": "+8613812345678",
    "status": "active",
    "created_at": "2024-01-20T10:00:00Z",
    "updated_at": "2024-01-20T10:00:00Z"
}
```

#### 查询用户列表
```json
GET /api/v1/users?skip=0&limit=10

Response 200:
{
    "items": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name": "张三",
            "email": "zhangsan@example.com",
            "phone": "+8613812345678",
            "status": "active",
            "created_at": "2024-01-20T10:00:00Z",
            "updated_at": "2024-01-20T10:00:00Z"
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

#### 更新用户
```json
PUT /api/v1/users/550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
    "name": "张三丰",
    "phone": "+8613987654321"
}

Response 200:
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "张三丰",
    "email": "zhangsan@example.com",
    "phone": "+8613987654321",
    "status": "active",
    "created_at": "2024-01-20T10:00:00Z",
    "updated_at": "2024-01-20T11:00:00Z"
}
```

#### 删除用户（软删除）
```json
DELETE /api/v1/users/550e8400-e29b-41d4-a716-446655440000

Response 204: No Content
```

## 业务规则实现

### 唯一性验证
```python
async def check_email_exists(db: Session, email: str, exclude_id: UUID = None) -> bool:
    query = db.query(User).filter(User.email == email)
    if exclude_id:
        query = query.filter(User.id != exclude_id)
    return query.first() is not None
```

### 数据验证
- **姓名**：必填，1-100字符
- **邮箱**：必填，有效邮箱格式，全局唯一
- **电话**：可选，符合电话格式（支持国际格式）

### 状态管理
- 新用户默认状态：`ACTIVE`
- 删除操作：将状态改为`INACTIVE`（软删除）

## 错误处理

### 标准错误响应
```json
{
    "detail": "错误描述",
    "type": "error_type",
    "loc": ["field", "name"]
}
```

### 常见错误码
- `400` - 请求参数错误
- `404` - 用户不存在
- `409` - 邮箱已存在
- `422` - 数据验证失败
- `500` - 服务器内部错误

## 性能优化

### 数据库优化
1. **连接池配置**
   ```python
   SQLALCHEMY_DATABASE_URL = "postgresql://user:pass@localhost/dbname"
   engine = create_engine(
       SQLALCHEMY_DATABASE_URL,
       pool_size=5,
       max_overflow=10,
       pool_pre_ping=True
   )
   ```

2. **查询优化**
   - 使用索引优化邮箱查询
   - 分页查询避免全表扫描
   - 软删除避免物理删除开销

### API优化
1. **分页默认值**
   - 默认页大小：20
   - 最大页大小：100

2. **响应优化**
   - 使用响应模型减少数据传输
   - 排除不必要的字段

## 部署配置

### 环境变量
```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/userdb

# API配置
API_V1_STR=/api/v1
PROJECT_NAME=用户管理服务

# 分页
DEFAULT_SKIP=0
DEFAULT_LIMIT=20
MAX_LIMIT=100
```

### Docker配置
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 依赖清单
```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic[email]==2.5.0
```

## 监控和日志

### 健康检查
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0"
    }
```

### 日志配置
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
```

## 测试策略

### 单元测试
- 测试数据验证逻辑
- 测试业务规则
- 测试错误处理

### 集成测试
- 测试API端点
- 测试数据库操作
- 测试完整的CRUD流程

## 未来扩展

1. **功能扩展**
   - 批量导入/导出
   - 用户搜索（全文搜索）
   - 操作审计日志

2. **性能扩展**
   - 添加Redis缓存
   - 读写分离
   - 水平分片

3. **安全扩展**
   - 添加API认证
   - 数据加密
   - 访问控制