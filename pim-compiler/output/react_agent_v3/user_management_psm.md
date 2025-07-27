# FastAPI 用户管理系统 PSM 文档

## 1. 数据模型定义

### 用户模型 (User)

```python
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, EmailStr, constr

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # E.164格式
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: constr(min_length=1, max_length=50) | None = None
    email: EmailStr | None = None
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$") | None = None
    status: UserStatus | None = None

class UserInDB(UserBase):
    id: str  # UUID格式
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

### 查询参数模型

```python
from typing import Optional

class UserQueryParams(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[UserStatus] = None
    skip: int = 0
    limit: int = 100
```

### 响应模型

```python
class UserResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserInDB] = None

class UsersResponse(BaseModel):
    success: bool
    total: int
    users: list[UserInDB]
```

## 2. API端点设计 (RESTful)

### 用户管理API

| 端点 | 方法 | 描述 | 认证要求 |
|------|------|------|----------|
| `/api/users/register` | POST | 注册新用户 | 无 |
| `/api/users` | POST | 创建新用户 | 需要管理员权限 |
| `/api/users` | GET | 查询用户列表 | 需要认证 |
| `/api/users/{user_id}` | GET | 获取单个用户详情 | 需要认证 |
| `/api/users/{user_id}` | PUT | 更新用户信息 | 需要管理员权限或本人 |
| `/api/users/{user_id}` | DELETE | 删除用户 | 需要管理员权限 |

### 端点实现示例

```python
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/api/users")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    """
    用户注册流程
    """
    # 实现注册逻辑
    pass

@router.post("", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    token: str = Depends(oauth2_scheme)
):
    """
    创建新用户 (管理员)
    """
    # 实现创建逻辑
    pass

@router.get("", response_model=UsersResponse)
async def query_users(
    params: UserQueryParams = Depends(),
    token: str = Depends(oauth2_scheme)
):
    """
    查询用户列表
    """
    # 实现查询逻辑
    pass

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    获取单个用户详情
    """
    # 实现获取逻辑
    pass

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    token: str = Depends(oauth2_scheme)
):
    """
    更新用户信息
    """
    # 实现更新逻辑
    pass

@router.delete("/{user_id}", response_model=UserResponse)
async def delete_user(
    user_id: str,
    token: str = Depends(oauth2_scheme)
):
    """
    删除用户 (实际上是停用)
    """
    # 实现删除逻辑
    pass
```

## 3. 服务层方法定义

### 用户服务实现

```python
from typing import Optional
from uuid import uuid4
from datetime import datetime

class UserService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def register_user(self, user_data: UserCreate) -> dict:
        """
        注册用户流程
        返回: {success: bool, message: str, user: Optional[UserInDB]}
        """
        # 1. 验证信息完整性 (由Pydantic自动处理)
        
        # 2. 检查邮箱唯一性
        if await self._check_email_exists(user_data.email):
            return {
                "success": False,
                "message": "Email already registered",
                "user": None
            }
        
        # 3. 生成唯一标识符
        user_id = str(uuid4())
        
        # 4. 准备用户数据
        user_dict = user_data.dict()
        user_dict.update({
            "id": user_id,
            "status": UserStatus.ACTIVE,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # 5. 保存用户
        try:
            user = await self.db.users.insert_one(user_dict)
            return {
                "success": True,
                "message": "User registered successfully",
                "user": UserInDB(**user_dict)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Registration failed: {str(e)}",
                "user": None
            }
    
    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """创建用户 (管理员)"""
        return await self.register_user(user_data)
    
    async def get_user(self, user_id: str) -> Optional[UserInDB]:
        """获取单个用户"""
        user = await self.db.users.find_one({"id": user_id})
        return UserInDB(**user) if user else None
    
    async def query_users(self, params: UserQueryParams) -> dict:
        """查询用户列表"""
        query = {}
        if params.name:
            query["name"] = {"$regex": params.name, "$options": "i"}
        if params.email:
            query["email"] = params.email
        if params.status:
            query["status"] = params.status
            
        total = await self.db.users.count_documents(query)
        users = await self.db.users.find(query).skip(params.skip).limit(params.limit).to_list(None)
        
        return {
            "success": True,
            "total": total,
            "users": [UserInDB(**user) for user in users]
        }
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserInDB]:
        """更新用户信息"""
        update_data = user_data.dict(exclude_unset=True)
        if not update_data:
            return None
            
        update_data["updated_at"] = datetime.utcnow()
        
        if "email" in update_data and await self._check_email_exists(update_data["email"], exclude_id=user_id):
            raise ValueError("Email already in use")
            
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 1:
            return await self.get_user(user_id)
        return None
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户 (设置为停用)"""
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$set": {"status": UserStatus.INACTIVE, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count == 1
    
    async def _check_email_exists(self, email: str, exclude_id: str = None) -> bool:
        """检查邮箱是否已存在"""
        query = {"email": email}
        if exclude_id:
            query["id"] = {"$ne": exclude_id}
        return await self.db.users.count_documents(query) > 0
```

## 4. 认证和权限控制

### 认证服务

```python
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from datetime import datetime, timedelta

# 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await UserService.get_user(user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_active_user)):
    # 这里需要实现管理员检查逻辑
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return current_user
```

### 在API端点中使用

```python
@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_active_user)):
    return {
        "success": True,
        "message": "Current user info",
        "user": current_user
    }
```

## 5. 数据库设计

### MongoDB 集合设计 (users)

```json
{
  "_id": ObjectId,
  "id": "UUID字符串",
  "name": "用户姓名",
  "email": "user@example.com",
  "phone": "+8613812345678",
  "status": "active|inactive",
  "created_at": ISODate,
  "updated_at": ISODate,
  "password_hash": "加密后的密码",  // 如果使用本地认证
  "is_admin": false,              // 管理员标志
  "last_login": ISODate           // 最后登录时间
}
```

### 索引设计

```python
# 确保唯一性
db.users.create_index([("email", 1)], unique=True)
db.users.create_index([("id", 1)], unique=True)

# 查询优化
db.users.create_index([("name", "text")])
db.users.create_index([("status", 1)])
db.users.create_index([("created_at", -1)])
```

### 数据库初始化脚本

```python
async def init_db():
    # 创建索引
    await db.users.create_index([("email", 1)], unique=True)
    await db.users.create_index([("id", 1)], unique=True)
    await db.users.create_index([("name", "text")])
    await db.users.create_index([("status", 1)])
    await db.users.create_index([("created_at", -1)])
    
    # 创建初始管理员用户
    if not await db.users.find_one({"email": "admin@example.com"}):
        admin_user = UserCreate(
            name="Admin",
            email="admin@example.com",
            phone="+8610000000000"
        )
        admin_data = admin_user.dict()
        admin_data.update({
            "id": str(uuid4()),
            "status": UserStatus.ACTIVE,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_admin": True,
            "password_hash": get_password_hash("admin123")  # 需要实现密码哈希函数
        })
        await db.users.insert_one(admin_data)
```

## 6. 异常处理

```python
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"success": False, "message": "Validation error", "details": exc.errors()},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"success": False, "message": "Internal server error"},
    )
```

## 7. 性能优化

1. **缓存策略**：
   - 对频繁访问的用户数据使用Redis缓存
   - 缓存时间：5分钟

2. **分页优化**：
   - 使用游标分页代替偏移分页处理大数据集
   - 默认每页100条记录，最大不超过1000条

3. **批量操作**：
   - 提供批量创建/更新用户的API
   - 使用批量写入操作减少数据库往返

4. **异步处理**：
   - 所有数据库操作使用异步驱动
   - 耗时操作（如发送欢迎邮件）放入后台任务队列

## 8. 安全考虑

1. **数据保护**：
   - 敏感字段（如密码）不返回API响应
   - 日志中不记录敏感信息

2. **输入验证**：
   - 使用Pydantic模型验证所有输入
   - 对特殊字符进行转义处理

3. **速率限制**：
   - 对认证端点实施速率限制
   - 防止暴力破解攻击

4. **CORS策略**：
   - 严格限制允许的源
   - 仅允许必要的HTTP方法和头部

## 9. 部署建议

1. **容器化**：
   ```dockerfile
   FROM python:3.9
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **水平扩展**：
   - 使用多个FastAPI实例
   - 通过Nginx负载均衡

3. **监控**：
   - 集成Prometheus监控
   - 设置关键指标告警（错误率、响应时间等）

4. **日志**：
   - 结构化日志（JSON格式）
   - 集中式日志收集

## 10. 测试策略

1. **单元测试**：
   - 测试所有服务方法
   - 模拟数据库依赖

2. **集成测试**：
   - 测试API端点
   - 包括认证流程测试

3. **性能测试**：
   - 使用Locust进行负载测试
   - 验证响应时间SLA

4. **E2E测试**：
   - 完整用户流程测试
   - 包括错误场景测试

---

这份PSM文档提供了从PIM到FastAPI平台的详细转换，涵盖了数据模型、API设计、服务实现、安全考虑和部署策略等各个方面。根据实际项目需求，可以进一步调整和扩展特定部分。