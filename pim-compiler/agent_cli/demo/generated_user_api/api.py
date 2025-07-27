# FastAPI UserService API 路由代码

下面是一个基于 FastAPI 的 UserService RESTful API 实现，包含了请求/响应模型验证、错误处理和适当的 HTTP 状态码。

## 1. 首先创建基础结构和模型

```python
# app/main.py
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from uuid import UUID, uuid4
from datetime import datetime

app = FastAPI(title="UserService API", version="1.0.0")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 错误处理中间件
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"message": "Validation error", "errors": exc.errors()},
    )

# 数据模型
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class UserInDB(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 模拟数据库
class Database:
    def __init__(self):
        self.users = {}

db = Database()
```

## 2. 实现 API 路由

```python
# app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..main import db, UserCreate, UserInDB, UserUpdate

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)

@router.post(
    "/",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user"
)
async def create_user(user: UserCreate):
    """
    Create a new user with the following information:
    - **username**: must be unique
    - **email**: must be a valid email and unique
    - **full_name**: optional
    - **password**: will be hashed before storage (not implemented in this example)
    """
    # 检查用户名是否已存在
    if any(u.username == user.username for u in db.users.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # 检查邮箱是否已存在
    if any(u.email == user.email for u in db.users.values()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 创建用户
    user_id = uuid4()
    now = datetime.now()
    db_user = UserInDB(
        id=user_id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=True,
        created_at=now,
        updated_at=now
    )
    
    db.users[user_id] = db_user
    return db_user

@router.get(
    "/",
    response_model=List[UserInDB],
    summary="List all users"
)
async def read_users(skip: int = 0, limit: int = 100):
    """
    Retrieve a list of users with pagination support.
    - **skip**: number of records to skip (for pagination)
    - **limit**: maximum number of records to return (for pagination)
    """
    return list(db.users.values())[skip : skip + limit]

@router.get(
    "/{user_id}",
    response_model=UserInDB,
    summary="Get a specific user"
)
async def read_user(user_id: UUID):
    """
    Get a specific user by their unique ID.
    """
    if user_id not in db.users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db.users[user_id]

@router.put(
    "/{user_id}",
    response_model=UserInDB,
    summary="Update a user"
)
async def update_user(user_id: UUID, user_update: UserUpdate):
    """
    Update a user's information.
    - Can update email, full_name, and/or password
    - At least one field must be provided
    """
    if user_id not in db.users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    db_user = db.users[user_id]
    
    # 检查邮箱是否已存在（如果提供了新邮箱）
    if user_update.email and user_update.email != db_user.email:
        if any(u.email == user_update.email for u in db.users.values()):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 更新用户信息
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db_user.updated_at = datetime.now()
    db.users[user_id] = db_user
    
    return db_user

@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user"
)
async def delete_user(user_id: UUID):
    """
    Delete a user by their ID.
    """
    if user_id not in db.users:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    del db.users[user_id]
    return None
```

## 3. 将路由添加到主应用

```python
# 在 app/main.py 最后添加
from .routers import users

app.include_router(users.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

## 4. API 文档

FastAPI 会自动生成交互式 API 文档：
- Swagger UI: `/docs`
- ReDoc: `/redoc`

## 5. 运行应用

```bash
uvicorn app.main:app --reload
```

## 功能说明

1. **RESTful API 设计**:
   - POST /users - 创建用户
   - GET /users - 获取用户列表
   - GET /users/{user_id} - 获取特定用户
   - PUT /users/{user_id} - 更新用户
   - DELETE /users/{user_id} - 删除用户

2. **HTTP 状态码**:
   - 200 OK - 成功请求
   - 201 Created - 资源创建成功
   - 204 No Content - 删除成功
   - 400 Bad Request - 客户端错误
   - 404 Not Found - 资源不存在
   - 422 Unprocessable Entity - 验证错误

3. **请求/响应模型验证**:
   - 使用 Pydantic 模型进行输入输出验证
   - 包含基本验证如邮箱格式、UUID 格式等

4. **错误处理中间件**:
   - 处理 HTTPException
   - 处理请求验证错误
   - 返回结构化的错误响应

这个实现提供了一个完整的 UserService API，可以根据实际需求进一步扩展，例如添加认证、数据库集成等。