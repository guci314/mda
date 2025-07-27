# FastAPI 用户管理 API 设计规范

## 1. RESTful 端点设计

### 用户资源端点

#### 1.1 创建用户
- **HTTP 方法**: POST
- **URL 路径**: `/api/v1/users`
- **请求格式**:
  ```json
  {
    "name": "string, 必填, 用户姓名",
    "email": "string, 必填, 有效邮箱格式",
    "phone": "string, 可选, 有效电话号码格式"
  }
  ```
- **响应格式**:
  - 成功 (201 Created):
    ```json
    {
      "success": true,
      "message": "用户创建成功",
      "data": {
        "id": "string, 用户唯一标识",
        "name": "string",
        "email": "string",
        "phone": "string|null",
        "status": "active|inactive",
        "created_at": "ISO8601 时间戳",
        "updated_at": "ISO8601 时间戳"
      }
    }
    ```
  - 错误 (400 Bad Request/409 Conflict):
    ```json
    {
      "success": false,
      "error": {
        "code": "错误代码",
        "message": "错误描述"
      }
    }
    ```

#### 1.2 查询用户列表
- **HTTP 方法**: GET
- **URL 路径**: `/api/v1/users`
- **查询参数**:
  - `name`: 可选, 按姓名模糊查询
  - `email`: 可选, 按邮箱精确查询
  - `status`: 可选, 按状态过滤 (active/inactive)
  - `page`: 可选, 页码 (默认1)
  - `size`: 可选, 每页数量 (默认10)
- **响应格式**:
  - 成功 (200 OK):
    ```json
    {
      "success": true,
      "data": {
        "items": [
          {
            "id": "string",
            "name": "string",
            "email": "string",
            "status": "string",
            "created_at": "ISO8601"
          }
        ],
        "total": 100,
        "page": 1,
        "size": 10
      }
    }
    ```

#### 1.3 查询单个用户
- **HTTP 方法**: GET
- **URL 路径**: `/api/v1/users/{user_id}`
- **响应格式**:
  - 成功 (200 OK):
    ```json
    {
      "success": true,
      "data": {
        "id": "string",
        "name": "string",
        "email": "string",
        "phone": "string|null",
        "status": "string",
        "created_at": "ISO8601",
        "updated_at": "ISO8601"
      }
    }
    ```
  - 用户不存在 (404 Not Found)

#### 1.4 更新用户
- **HTTP 方法**: PATCH
- **URL 路径**: `/api/v1/users/{user_id}`
- **请求格式**:
  ```json
  {
    "name": "string, 可选",
    "email": "string, 可选, 有效邮箱格式",
    "phone": "string, 可选, 有效电话号码格式"
  }
  ```
- **响应格式**: 同创建用户

#### 1.5 删除用户
- **HTTP 方法**: DELETE
- **URL 路径**: `/api/v1/users/{user_id}`
- **响应格式**:
  - 成功 (200 OK):
    ```json
    {
      "success": true,
      "message": "用户已停用"
    }
    ```

## 2. 请求验证

### 2.1 参数验证规则

使用 Pydantic 模型进行验证:

```python
from pydantic import BaseModel, EmailStr, constr, validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)  # 姓名不能为空
    email: EmailStr  # 自动验证邮箱格式
    phone: Optional[constr(regex=r'^\+?[1-9]\d{1,14}$')]  # E.164 电话格式

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)]
    email: Optional[EmailStr]
    phone: Optional[constr(regex=r'^\+?[1-9]\d{1,14}$')]
```

### 2.2 业务规则验证

在服务层实现:
- 邮箱唯一性检查
- 状态变更验证
- 删除保护等业务规则

## 3. 响应格式

### 3.1 标准响应结构

```python
from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar('T')

class SuccessResponse(GenericModel, Generic[T]):
    success: bool = True
    data: T

class ErrorResponse(BaseModel):
    success: bool = False
    error: dict

class PaginatedResponse(GenericModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    size: int
```

### 3.2 错误代码规范

| 错误代码       | HTTP 状态码 | 描述                  |
|----------------|-------------|-----------------------|
| invalid_input  | 400         | 输入验证失败          |
| email_exists   | 409         | 邮箱已存在            |
| user_not_found | 404         | 用户不存在            |
| system_error   | 500         | 系统内部错误          |

## 4. API 版本控制策略

采用 URL 路径版本控制:
- 所有 API 以 `/api/v1/` 开头
- 重大变更升级到 v2
- 向后兼容至少一个主要版本

## 5. 技术实现示例

### 5.1 路由定义

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter(prefix="/api/v1/users")

@router.post("/", response_model=SuccessResponse[UserResponse], status_code=201)
async def create_user(user: UserCreate):
    """
    创建新用户
    - 验证输入格式
    - 检查邮箱唯一性
    - 生成唯一ID
    - 设置默认状态为active
    - 记录创建时间
    """
    pass

@router.get("/", response_model=SuccessResponse[PaginatedResponse[UserResponse]])
async def list_users(
    name: str = None, 
    email: str = None,
    status: str = None,
    page: int = 1,
    size: int = 10
):
    """
    查询用户列表
    - 支持分页
    - 支持姓名模糊查询
    - 支持邮箱精确查询
    - 支持状态过滤
    """
    pass
```

### 5.2 数据库模型

```python
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.sql import func
from enum import Enum as PyEnum

class UserStatus(str, PyEnum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    phone = Column(String(20))
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### 5.3 服务层实现

```python
class UserService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def create_user(self, user_data: UserCreate) -> User:
        # 检查邮箱唯一性
        if await self.get_user_by_email(user_data.email):
            raise EmailExistsError()
        
        # 创建用户记录
        user = User(
            id=str(uuid.uuid4()),
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            status=UserStatus.ACTIVE
        )
        
        self.db.add(user)
        await self.db.commit()
        return user
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        # 实现邮箱查询
        pass
```

## 6. 最佳实践

1. **依赖注入**:
   - 使用 FastAPI 的 Depends 管理数据库会话
   - 服务层与路由层分离

2. **异步支持**:
   - 所有数据库操作使用 async/await
   - 使用 asyncpg 或 aiomysql 等异步驱动

3. **安全措施**:
   - 生产环境启用 HTTPS
   - 敏感操作需要认证
   - 实现速率限制

4. **文档生成**:
   - 自动生成 OpenAPI 文档
   - 为每个端点添加详细描述

5. **性能优化**:
   - 数据库查询使用索引
   - 列表查询实现分页
   - 考虑缓存高频访问数据