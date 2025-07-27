# API 设计规范 (FastAPI 实现)

## 1. RESTful 端点设计

### 用户管理 API

#### 1.1 用户注册
```python
@router.post(
    "/users/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="用户注册",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        409: {"model": ErrorResponse, "description": "邮箱已存在"}
    }
)
async def register_user(user: UserCreate):
    """
    注册新用户
    
    参数:
    - user: 用户注册信息，包含姓名、邮箱和电话
    
    返回:
    - 201: 用户注册成功，返回用户信息
    - 400: 请求参数验证失败
    - 409: 邮箱已存在
    """
```

#### 1.2 创建用户 (管理员)
```python
@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="创建用户",
    dependencies=[Depends(admin_required)],
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        409: {"model": ErrorResponse, "description": "邮箱已存在"}
    }
)
async def create_user(user: UserCreate):
    """
    创建新用户 (管理员权限)
    
    参数:
    - user: 用户创建信息
    
    返回:
    - 201: 用户创建成功
    - 400: 请求参数验证失败
    - 401: 未授权
    - 403: 权限不足
    - 409: 邮箱已存在
    """
```

#### 1.3 查询用户列表
```python
@router.get(
    "/users",
    response_model=Page[UserResponse],
    summary="查询用户列表",
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"}
    }
)
async def list_users(
    name: Optional[str] = Query(None, min_length=1, max_length=50),
    email: Optional[str] = Query(None, regex=EMAIL_REGEX),
    status: Optional[UserStatus] = None,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
):
    """
    查询用户列表 (支持分页和过滤)
    
    参数:
    - name: 用户姓名模糊查询
    - email: 邮箱精确查询
    - status: 用户状态过滤
    - page: 页码 (从1开始)
    - size: 每页数量 (1-100)
    
    返回:
    - 200: 用户列表 (分页格式)
    - 401: 未授权
    - 403: 权限不足
    """
```

#### 1.4 查询单个用户
```python
@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="查询用户详情",
    responses={
        404: {"model": ErrorResponse, "description": "用户不存在"},
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"}
    }
)
async def get_user(user_id: UUID):
    """
    根据ID查询用户详情
    
    参数:
    - user_id: 用户唯一标识符
    
    返回:
    - 200: 用户详情
    - 401: 未授权
    - 403: 权限不足
    - 404: 用户不存在
    """
```

#### 1.5 更新用户信息
```python
@router.patch(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="更新用户信息",
    responses={
        400: {"model": ErrorResponse, "description": "请求参数错误"},
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "用户不存在"},
        409: {"model": ErrorResponse, "description": "邮箱已存在"}
    }
)
async def update_user(
    user_id: UUID,
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    更新用户信息
    
    参数:
    - user_id: 要更新的用户ID
    - user_update: 用户更新信息
    - current_user: 当前登录用户
    
    返回:
    - 200: 更新成功，返回更新后的用户信息
    - 400: 请求参数验证失败
    - 401: 未授权
    - 403: 权限不足 (只能更新自己的信息或管理员)
    - 404: 用户不存在
    - 409: 邮箱已存在
    """
```

#### 1.6 删除用户
```python
@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="删除用户",
    responses={
        401: {"model": ErrorResponse, "description": "未授权"},
        403: {"model": ErrorResponse, "description": "权限不足"},
        404: {"model": ErrorResponse, "description": "用户不存在"}
    }
)
async def delete_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user)
):
    """
    删除用户 (实际上是停用)
    
    参数:
    - user_id: 要删除的用户ID
    - current_user: 当前登录用户
    
    返回:
    - 204: 删除成功 (无内容)
    - 401: 未授权
    - 403: 权限不足
    - 404: 用户不存在
    """
```

## 2. 请求验证

### 2.1 参数验证规则

#### 路径参数
```python
user_id: UUID  # 必须为有效的UUID格式
```

#### 查询参数
```python
name: Optional[str] = Query(None, min_length=1, max_length=50)  # 可选，长度1-50
email: Optional[str] = Query(None, regex=EMAIL_REGEX)  # 可选，必须符合邮箱格式
status: Optional[UserStatus]  # 可选，必须是预定义的用户状态枚举值
page: int = Query(1, ge=1)  # 页码，最小1
size: int = Query(20, ge=1, le=100)  # 每页数量，1-100
```

### 2.2 请求体格式

#### 用户创建/注册 (UserCreate)
```python
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, example="张三")
    email: str = Field(..., regex=EMAIL_REGEX, example="user@example.com")
    phone: str = Field(..., regex=PHONE_REGEX, example="13800138000")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "张三",
                "email": "user@example.com",
                "phone": "13800138000"
            }
        }
```

#### 用户更新 (UserUpdate)
```python
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50, example="李四")
    email: Optional[str] = Field(None, regex=EMAIL_REGEX, example="new@example.com")
    phone: Optional[str] = Field(None, regex=PHONE_REGEX, example="13900139000")
    status: Optional[UserStatus] = Field(None, example="active")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "李四",
                "email": "new@example.com",
                "phone": "13900139000",
                "status": "active"
            }
        }
```

## 3. 响应格式

### 3.1 成功响应

#### 用户响应 (UserResponse)
```python
class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name": "张三",
                "email": "user@example.com",
                "phone": "13800138000",
                "status": "active",
                "created_at": "2023-01-01T00:00:00",
                "updated_at": "2023-01-01T00:00:00"
            }
        }
```

### 3.2 错误响应

#### 通用错误响应 (ErrorResponse)
```python
class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "code": 404,
                "message": "用户不存在",
                "detail": "找不到ID为550e8400-e29b-41d4-a716-446655440000的用户"
            }
        }
```

### 3.3 分页格式

#### 分页响应 (Page)
```python
class Page(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        schema_extra = {
            "example": {
                "items": [...],
                "total": 100,
                "page": 1,
                "size": 20,
                "pages": 5
            }
        }
```

## 4. API 版本控制策略

### 4.1 版本控制实现

采用 URL 路径版本控制，所有 API 前缀为 `/v1/`：

```python
# main.py
app = FastAPI(title="用户管理系统", version="1.0.0")

# 添加API路由
app.include_router(router, prefix="/v1")
```

### 4.2 版本升级策略

1. **兼容性变更**：
   - 添加新端点
   - 添加可选请求参数
   - 添加响应字段
   - 这些变更不需要升级版本号

2. **不兼容变更**：
   - 修改现有端点行为
   - 删除或重命名端点
   - 修改必填参数
   - 这些变更需要升级版本号 (如 `/v2/`)

3. **弃用策略**：
   - 旧版本API至少保留6个月
   - 在响应头中添加 `Deprecation: true` 和 `Sunset: <日期>`
   - 文档中明确标注已弃用的API

### 4.3 版本切换实现

```python
# 在API路由中添加版本参数
@router.get("/users", tags=["v1"])
async def list_users_v1():
    ...

# 新版本API
@router.get("/users", tags=["v2"])
async def list_users_v2():
    ...
```

## 5. 类型定义和枚举

### 5.1 用户状态枚举
```python
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
```

### 5.2 正则表达式常量
```python
# 邮箱正则
EMAIL_REGEX = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

# 手机号正则 (中国大陆)
PHONE_REGEX = r"^1[3-9]\d{9}$"
```

## 6. 安全规范

### 6.1 认证方式
- 使用 JWT (JSON Web Token)
- 通过 Authorization 头传递: `Bearer <token>`

### 6.2 权限控制
- 普通用户: 只能查看和修改自己的信息
- 管理员: 可以管理所有用户

### 6.3 速率限制
- 公共API: 100次/分钟/IP
- 认证API: 1000次/分钟/用户

## 7. 最佳实践

1. **使用异步IO**：所有数据库操作使用异步SQLAlchemy
2. **依赖注入**：使用FastAPI的Depends管理依赖
3. **ORM模式**：Pydantic模型配置orm_mode=True
4. **错误处理**：统一错误处理中间件
5. **日志记录**：结构化日志记录所有请求和响应
6. **OpenAPI文档**：自动生成交互式API文档
7. **测试覆盖**：单元测试覆盖核心业务逻辑