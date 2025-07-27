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
    name: constr(min_length=1, max_length=50)  # 姓名不能为空
    email: EmailStr  # 自动验证邮箱格式
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # E.164 电话格式
    status: UserStatus = UserStatus.ACTIVE  # 默认活跃状态

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: constr(min_length=1, max_length=50) | None = None
    email: EmailStr | None = None
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$") | None = None
    status: UserStatus | None = None

class UserInDB(UserBase):
    id: str  # UUID格式的唯一标识符
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

## 2. API 端点设计 (RESTful)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

router = APIRouter(
    prefix="/api/v1/users",
    tags=["users"],
    dependencies=[Depends(get_current_active_user)],  # 默认需要认证
)

# 用户注册 (不需要认证)
@router.post(
    "/register",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    dependencies=[]
)
async def register_user(user_create: UserCreate):
    # 实现注册逻辑
    pass

# 创建用户 (需要管理员权限)
@router.post(
    "/",
    response_model=UserInDB,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(check_admin_permission)]
)
async def create_user(user_create: UserCreate):
    pass

# 查询用户列表
@router.get("/", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[UserStatus] = None
):
    pass

# 查询单个用户
@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: str):
    pass

# 更新用户
@router.patch("/{user_id}", response_model=UserInDB)
async def update_user(user_id: str, user_update: UserUpdate):
    pass

# 删除用户 (实际上是停用)
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: str):
    pass
```

## 3. 服务层方法定义

```python
from typing import List, Optional
from uuid import uuid4
from datetime import datetime

class UserService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def register_user(self, user_create: UserCreate) -> UserInDB:
        # 验证邮箱唯一性
        if await self._check_email_exists(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # 创建用户记录
        user_id = str(uuid4())
        now = datetime.utcnow()
        user_data = {
            **user_create.dict(),
            "id": user_id,
            "status": UserStatus.ACTIVE,
            "created_at": now,
            "updated_at": now
        }
        
        try:
            user = await self.db.users.insert_one(user_data)
            return UserInDB(**user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def create_user(self, user_create: UserCreate) -> UserInDB:
        # 与register_user类似，但可能有不同的权限检查
        pass
    
    async def get_user(self, user_id: str) -> UserInDB:
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserInDB(**user)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[UserStatus] = None
    ) -> List[UserInDB]:
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        if email:
            query["email"] = email
        if status:
            query["status"] = status
        
        users = await self.db.users.find(query).skip(skip).limit(limit).to_list(limit)
        return [UserInDB(**user) for user in users]
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserInDB:
        # 检查用户是否存在
        existing_user = await self.get_user(user_id)
        
        # 检查邮箱唯一性（如果更新了邮箱）
        if user_update.email and user_update.email != existing_user.email:
            if await self._check_email_exists(user_update.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
        
        update_data = user_update.dict(exclude_unset=True)
        if not update_data:
            return existing_user
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": update_data}
            )
            return await self.get_user(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
    
    async def delete_user(self, user_id: str) -> None:
        try:
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": {"status": UserStatus.INACTIVE, "updated_at": datetime.utcnow()}}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
    
    async def _check_email_exists(self, email: str) -> bool:
        existing_user = await self.db.users.find_one({"email": email})
        return existing_user is not None
```

## 4. 认证和权限控制

```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext

# 配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class TokenData(BaseModel):
    username: str | None = None
    scopes: List[str] = []

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)):
    if current_user.status != UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def check_admin_permission(current_user: UserInDB = Depends(get_current_active_user)):
    if "admin" not in current_user.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

## 5. 数据库设计 (MongoDB 示例)

```python
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel

async def init_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.user_management
    
    # 创建索引
    await db.users.create_indexes([
        IndexModel([("id", 1)], unique=True),
        IndexModel([("email", 1)], unique=True),
        IndexModel([("name", "text")])
    ])
    
    return db

# 用户集合文档结构示例
"""
{
    "id": "uuid-string",
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890",
    "status": "active",
    "created_at": ISODate("2023-01-01T00:00:00Z"),
    "updated_at": ISODate("2023-01-01T00:00:00Z"),
    "hashed_password": "...",
    "scopes": ["user"]  # 或 ["admin"] 用于管理员
}
"""
```

## 6. 应用配置和主程序

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="User Management API",
    description="API for managing users",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接
@app.on_event("startup")
async def startup_db_client():
    app.db = await init_db()
    app.user_service = UserService(app.db)

@app.on_event("shutdown")
async def shutdown_db_client():
    app.db.client.close()

# 包含路由
app.include_router(router)
```

## 7. 测试用例示例

```python
from fastapi.testclient import TestClient

def test_register_user():
    client = TestClient(app)
    
    # 测试成功注册
    response = client.post("/api/v1/users/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890"
    })
    assert response.status_code == 201
    assert response.json()["email"] == "test@example.com"
    
    # 测试重复邮箱
    response = client.post("/api/v1/users/register", json={
        "name": "Test User",
        "email": "test@example.com",
        "phone": "+1234567890"
    })
    assert response.status_code == 409
```

## 8. 部署配置 (Docker 示例)

```dockerfile
FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 9. 性能优化建议

1. **缓存层**：对频繁访问的用户数据添加 Redis 缓存
2. **分页优化**：使用游标分页代替偏移量分页
3. **批量操作**：为批量用户操作添加专用端点
4. **异步任务**：将非关键路径操作（如发送欢迎邮件）转为后台任务
5. **索引优化**：确保所有查询条件都有适当的数据库索引

## 10. 安全考虑

1. **敏感数据**：确保密码哈希存储，不记录明文
2. **速率限制**：对认证端点和关键操作添加速率限制
3. **输入验证**：所有输入数据都经过 Pydantic 模型验证
4. **HTTPS**：生产环境必须启用 HTTPS
5. **审计日志**：记录关键操作日志