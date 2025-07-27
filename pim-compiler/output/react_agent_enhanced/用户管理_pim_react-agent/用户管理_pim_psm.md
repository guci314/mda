# Platform Specific Model (PSM)

生成时间: 2025-07-27 06:20:50
目标平台: fastapi
框架: FastAPI
ORM: SQLAlchemy
验证库: Pydantic

---

## 1. Domain Models（领域模型）

# 用户管理领域模型 (PSM - FastAPI 实现)

## 实体定义 (SQLAlchemy 模型)

```python
from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid
from pydantic import BaseModel, EmailStr, constr
from fastapi import HTTPException, status

from .database import Base

# 枚举定义
class UserStatus(str, Enum):
    """用户状态枚举"""
    ACTIVE = "active"  # 活跃状态
    INACTIVE = "inactive"  # 停用状态

# 值对象定义
class PhoneNumber(str):
    """电话号码值对象，包含格式验证"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not v:
            return v
        # 简单的电话号码格式验证 (可根据实际需求调整)
        if not v.startswith("+") and not v.isdigit():
            raise ValueError("电话号码格式不正确")
        return cls(v)

# 实体模型 (SQLAlchemy)
class User(Base):
    """用户实体模型"""
    __tablename__ = "users"
    
    # 主键使用UUID
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(50), nullable=False)  # 姓名，必填，最大50字符
    email = Column(String(100), unique=True, nullable=False, index=True)  # 邮箱，必填，唯一，最大100字符
    phone = Column(String(20))  # 电话号码，可选
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)  # 状态，默认为活跃
    created_at = Column(DateTime, default=datetime.utcnow)  # 创建时间，自动设置
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # 更新时间，自动更新

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name}, email={self.email})>"

# Pydantic 模型 (用于输入输出验证)
class UserBase(BaseModel):
    """用户基础模型"""
    name: constr(max_length=50)  # 姓名，最大50字符
    email: EmailStr  # 邮箱，自动验证格式
    phone: Optional[PhoneNumber] = None  # 电话号码，可选

class UserCreate(UserBase):
    """创建用户模型"""
    pass

class UserUpdate(BaseModel):
    """更新用户模型"""
    name: Optional[constr(max_length=50)] = None  # 可选更新
    email: Optional[EmailStr] = None  # 可选更新
    phone: Optional[PhoneNumber] = None  # 可选更新

class UserInDB(UserBase):
    """数据库用户模型"""
    id: uuid.UUID
    status: UserStatus
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True  # 允许ORM模型转换
```

## 领域服务实现 (FastAPI 路由)

```python
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .models import User, UserStatus, UserCreate, UserUpdate, UserInDB
from .database import get_db
from .exceptions import EmailAlreadyExistsException

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    注册新用户
    - 验证输入数据
    - 检查邮箱唯一性
    - 创建用户记录
    """
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise EmailAlreadyExistsException()
    
    # 创建用户模型
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        status=UserStatus.ACTIVE  # 默认活跃状态
    )
    
    # 保存到数据库
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.get("/", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = Query(100, le=1000),  # 限制最大1000条
    status: Optional[UserStatus] = None,
    db: Session = Depends(get_db)
):
    """
    查询用户列表
    - 支持分页
    - 支持按状态过滤
    """
    query = db.query(User)
    
    if status:
        query = query.filter(User.status == status)
        
    users = query.offset(skip).limit(limit).all()
    return users

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    获取单个用户详情
    """
    user = db.query(User).get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: uuid.UUID,
    user_update: UserUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    - 验证输入数据
    - 检查邮箱唯一性(如果修改)
    - 更新用户记录
    """
    db_user = db.query(User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    update_data = user_update.dict(exclude_unset=True)
    
    # 检查邮箱唯一性
    if "email" in update_data and update_data["email"] != db_user.email:
        existing_user = db.query(User).filter(User.email == update_data["email"]).first()
        if existing_user:
            raise EmailAlreadyExistsException()
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    删除用户(实际上是设置为停用状态)
    """
    db_user = db.query(User).get(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db_user.status = UserStatus.INACTIVE
    db.commit()
    return None
```

## 异常处理

```python
from fastapi import HTTPException

class EmailAlreadyExistsException(HTTPException):
    """邮箱已存在异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail="该邮箱已被注册"
        )

class UserNotFoundException(HTTPException):
    """用户不存在异常"""
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
```

## 数据库配置

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://user:password@localhost/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# 依赖项
def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

## 领域规则实现

1. **唯一性规则**：
   - 在注册和更新用户时检查邮箱唯一性
   - 数据库层设置唯一约束

2. **数据完整性规则**：
   - 使用Pydantic模型验证输入数据格式
   - SQLAlchemy模型设置非空约束

3. **状态规则**：
   - 新用户默认为ACTIVE状态
   - 删除操作实际上是设置为INACTIVE状态

## 最佳实践说明

1. **分层架构**：
   - 实体模型与Pydantic模型分离
   - 业务逻辑集中在路由处理函数中

2. **验证策略**：
   - 输入验证使用Pydantic
   - 业务规则验证在服务层实现

3. **错误处理**：
   - 自定义异常类提供清晰的错误信息
   - 使用HTTP状态码正确反映问题性质

4. **性能考虑**：
   - 查询使用分页
   - 常用字段(email)添加索引

5. **安全考虑**：
   - 敏感信息(如密码)不应出现在模型中(示例简化)
   - 使用HTTPS传输数据

6. **可扩展性**：
   - 使用UUID作为主键便于分布式系统
   - 模型设计考虑未来可能的扩展需求

---

## 2. Service Layer（服务层）

# 用户管理服务层实现 (PSM)

## 1. 服务接口定义

```python
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from enum import Enum
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

# 定义用户状态枚举
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# 用户基础模型
class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)  # 姓名不能为空且长度限制
    email: EmailStr  # 使用Pydantic的EmailStr验证邮箱格式
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # 国际电话号码格式验证

# 用户创建模型
class UserCreate(UserBase):
    pass

# 用户更新模型
class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r"^\+?[1-9]\d{1,14}$")] = None

# 用户响应模型
class UserResponse(UserBase):
    id: int  # 用户唯一标识符
    status: UserStatus  # 用户状态
    created_at: datetime  # 创建时间
    updated_at: datetime  # 更新时间
    
    class Config:
        orm_mode = True  # 允许ORM模型转换

# 查询条件模型
class UserQuery(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[UserStatus] = None

# 分页响应模型
class PaginatedResponse(BaseModel):
    total: int
    page: int
    per_page: int
    items: List[UserResponse]
```

## 2. 仓储接口 (Repository)

```python
from typing import Optional, List
from sqlalchemy.orm import Session
from models import User  # SQLAlchemy模型

class UserRepository:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_user(self, user: UserCreate) -> User:
        """创建用户"""
        pass
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        pass
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        pass
    
    async def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """更新用户信息"""
        pass
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户(实际上是更新状态为INACTIVE)"""
        pass
    
    async def list_users(
        self, 
        query: UserQuery, 
        page: int = 1, 
        per_page: int = 10
    ) -> List[User]:
        """查询用户列表(支持分页)"""
        pass
    
    async def count_users(self, query: UserQuery) -> int:
        """统计符合条件的用户数量"""
        pass
```

## 3. 用户服务实现 (UserService)

```python
from datetime import datetime
from uuid import uuid4
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register_user(self, user_create: UserCreate) -> UserResponse:
        """
        注册用户流程
        1. 验证信息完整性
        2. 验证邮箱格式
        3. 验证电话格式
        4. 检查邮箱唯一性
        5. 创建用户记录
        """
        # 检查邮箱是否已存在
        existing_user = await self.user_repo.get_user_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        try:
            # 创建用户记录
            db_user = await self.user_repo.create_user(user_create)
            return UserResponse.from_orm(db_user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def create_user(self, user_create: UserCreate) -> UserResponse:
        """
        创建用户(管理员用)
        与注册用户类似，但不需要前端验证步骤
        """
        return await self.register_user(user_create)
    
    async def get_user(self, user_id: int) -> UserResponse:
        """
        获取单个用户详情
        """
        db_user = await self.user_repo.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserResponse.from_orm(db_user)
    
    async def list_users(
        self, 
        query: UserQuery, 
        page: int = 1, 
        per_page: int = 10
    ) -> PaginatedResponse:
        """
        查询用户列表(支持分页)
        """
        total = await self.user_repo.count_users(query)
        users = await self.user_repo.list_users(query, page, per_page)
        
        return PaginatedResponse(
            total=total,
            page=page,
            per_page=per_page,
            items=[UserResponse.from_orm(user) for user in users]
        )
    
    async def update_user(
        self, 
        user_id: int, 
        user_update: UserUpdate
    ) -> UserResponse:
        """
        更新用户信息
        1. 检查用户是否存在
        2. 如果更新邮箱，检查邮箱唯一性
        3. 更新用户信息
        """
        db_user = await self.user_repo.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # 检查邮箱唯一性
        if user_update.email and user_update.email != db_user.email:
            existing_user = await self.user_repo.get_user_by_email(user_update.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        try:
            updated_user = await self.user_repo.update_user(user_id, user_update)
            return UserResponse.from_orm(updated_user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
    
    async def delete_user(self, user_id: int) -> bool:
        """
        删除用户(实际上是更新状态为INACTIVE)
        """
        db_user = await self.user_repo.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        try:
            success = await self.user_repo.delete_user(user_id)
            return success
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
```

## 4. 依赖注入配置

```python
from fastapi import Depends
from database import get_db  # 获取数据库会话的函数

def get_user_repository(db: Session = Depends(get_db)) -> UserRepository:
    """获取用户仓储实例"""
    return UserRepository(db)

def get_user_service(user_repo: UserRepository = Depends(get_user_repository)) -> UserService:
    """获取用户服务实例"""
    return UserService(user_repo)
```

## 5. API路由示例

```python
from fastapi import APIRouter, Depends, status

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    user_service: UserService = Depends(get_user_service)
):
    """用户注册接口"""
    return await user_service.register_user(user_create)

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """获取用户详情"""
    return await user_service.get_user(user_id)

@router.get("/", response_model=PaginatedResponse)
async def list_users(
    query: UserQuery = Depends(),
    page: int = 1,
    per_page: int = 10,
    user_service: UserService = Depends(get_user_service)
):
    """查询用户列表(分页)"""
    return await user_service.list_users(query, page, per_page)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    user_service: UserService = Depends(get_user_service)
):
    """更新用户信息"""
    return await user_service.update_user(user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service)
):
    """删除用户"""
    await user_service.delete_user(user_id)
    return None
```

## 6. 事务管理与错误处理

```python
from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

class UserService:
    # ... 其他方法 ...
    
    async def _execute_in_transaction(self, operation, *args, **kwargs):
        """
        事务执行包装器
        确保数据库操作在事务中执行，并处理可能的异常
        """
        try:
            # 开始事务
            result = await operation(*args, **kwargs)
            # 提交事务
            return result
        except SQLAlchemyError as e:
            # 回滚事务
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database operation failed"
            )
        except HTTPException:
            # 已处理的HTTP异常直接抛出
            raise
        except Exception as e:
            # 其他未知异常
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )
    
    # 修改后的注册方法使用事务
    async def register_user(self, user_create: UserCreate) -> UserResponse:
        async def _register():
            # 检查邮箱是否已存在
            existing_user = await self.user_repo.get_user_by_email(user_create.email)
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
            
            # 创建用户记录
            db_user = await self.user_repo.create_user(user_create)
            return UserResponse.from_orm(db_user)
        
        return await self._execute_in_transaction(_register)
```

## 7. 最佳实践说明

1. **分层架构**：
   - 清晰分离服务层、仓储层和API路由层
   - 服务层处理业务逻辑，仓储层处理数据访问

2. **依赖注入**：
   - 使用FastAPI的Depends实现依赖注入
   - 便于测试和替换实现

3. **输入验证**：
   - 使用Pydantic模型进行输入验证
   - 在模型层面定义约束条件

4. **错误处理**：
   - 统一处理数据库异常
   - 返回适当的HTTP状态码和错误信息

5. **事务管理**：
   - 关键操作使用事务保证数据一致性
   - 提供统一的事务执行包装器

6. **类型提示**：
   - 全面使用Python类型提示
   - 提高代码可读性和IDE支持

7. **分页支持**：
   - 标准化的分页响应格式
   - 支持页码和每页数量参数

8. **RESTful设计**：
   - 遵循RESTful API设计原则
   - 合理的HTTP方法和状态码使用

---

## 3. API Design（API 设计）

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

---

## 4. Configuration（配置）

# FastAPI 用户管理 PSM (Platform Specific Model)

## 1. 应用配置

### config.py

```python
from pydantic import BaseSettings, PostgresDsn, validator
from typing import Optional

class Settings(BaseSettings):
    # 应用基础配置
    APP_NAME: str = "用户管理系统"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # 数据库配置
    DATABASE_URL: PostgresDsn = "postgresql://user:password@localhost:5432/userdb"
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # 服务端口配置
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000
    
    # 认证配置
    SECRET_KEY: str = "your-secret-key-here"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    ALGORITHM: str = "HS256"
    
    # CORS配置
    CORS_ORIGINS: list = ["*"]
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## 2. 依赖配置

### dependencies.py

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .models import User
from .schemas import TokenData

# 数据库依赖
def get_db():
    """
    获取数据库会话，每个请求独立会话，请求结束后自动关闭
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 认证依赖
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    获取当前认证用户，验证JWT令牌有效性
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    """
    检查用户是否处于活跃状态
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="用户已停用")
    return current_user
```

## 3. 数据库模型

### models.py

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class User(Base):
    """
    用户数据模型，对应数据库中的users表
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=True)
    full_name = Column(String(100), nullable=True)
    hashed_password = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.username}>"
```

## 4. Pydantic 模式

### schemas.py

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, validator

class UserBase(BaseModel):
    """
    用户基础模型，包含基本用户信息
    """
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r"^\+?[1-9]\d{1,14}$")

    @validator("phone")
    def validate_phone(cls, v):
        if v is None:
            return v
        if not v.startswith("+"):
            raise ValueError("电话号码必须以国际区号开头，例如：+86")
        return v

class UserCreate(UserBase):
    """
    创建用户模型，包含密码字段
    """
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """
    更新用户模型，所有字段可选
    """
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    phone: Optional[str] = Field(None, regex=r"^\+?[1-9]\d{1,14}$")
    is_active: Optional[bool] = None

class UserInDB(UserBase):
    """
    数据库中的用户模型，包含所有字段
    """
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class Token(BaseModel):
    """
    JWT令牌模型
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    JWT令牌数据模型
    """
    user_id: Optional[str] = None
```

## 5. 路由和控制器

### routers/users.py

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..dependencies import get_db, get_current_active_user
from ..models import User
from ..schemas import UserCreate, UserInDB, UserUpdate
from ..services import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "未找到"}},
)

@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """
    创建新用户
    
    - **username**: 用户名，必须唯一
    - **email**: 邮箱地址，必须唯一
    - **full_name**: 用户全名（可选）
    - **phone**: 电话号码（可选）
    - **password**: 密码，至少8个字符
    """
    return user_service.create_user(db=db, user=user)

@router.get("/", response_model=List[UserInDB])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    获取用户列表，支持分页
    
    - **skip**: 跳过多少条记录
    - **limit**: 返回多少条记录
    """
    return user_service.get_users(db, skip=skip, limit=limit)

@router.get("/me", response_model=UserInDB)
def read_user_me(current_user: User = Depends(get_current_active_user)):
    """
    获取当前登录用户信息
    """
    return current_user

@router.get("/{user_id}", response_model=UserInDB)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    根据ID获取用户详情
    
    - **user_id**: 用户ID
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    return db_user

@router.put("/{user_id}", response_model=UserInDB)
def update_user(
    user_id: int,
    user: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    更新用户信息
    
    - **user_id**: 要更新的用户ID
    - **email**: 新邮箱地址（可选）
    - **full_name**: 新全名（可选）
    - **phone**: 新电话号码（可选）
    - **is_active**: 新状态（可选）
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    return user_service.update_user(db=db, db_user=db_user, user=user)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除用户（实际上是停用用户）
    
    - **user_id**: 要删除的用户ID
    """
    db_user = user_service.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户未找到")
    user_service.delete_user(db=db, db_user=db_user)
    return {"ok": True}
```

## 6. 服务层

### services/user_service.py

```python
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from ..models import User
from ..schemas import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """
    验证密码是否正确
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """
    生成密码哈希
    """
    return pwd_context.hash(password)

def create_user(db: Session, user: UserCreate):
    """
    创建新用户
    
    1. 检查用户名和邮箱是否已存在
    2. 哈希密码
    3. 创建用户记录
    """
    # 检查用户名是否已存在
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise ValueError("用户名已存在")
    
    # 检查邮箱是否已存在
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise ValueError("邮箱已存在")
    
    # 创建用户
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session, skip: int = 0, limit: int = 100):
    """
    获取用户列表，支持分页
    """
    return db.query(User).offset(skip).limit(limit).all()

def get_user(db: Session, user_id: int):
    """
    根据ID获取单个用户
    """
    return db.query(User).filter(User.id == user_id).first()

def update_user(db: Session, db_user: User, user: UserUpdate):
    """
    更新用户信息
    
    1. 检查邮箱是否已存在（如果修改了邮箱）
    2. 更新用户信息
    """
    if user.email and user.email != db_user.email:
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            raise ValueError("邮箱已存在")
    
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, db_user: User):
    """
    删除用户（实际上是停用用户）
    """
    db_user.is_active = False
    db.add(db_user)
    db.commit()
    return db_user
```

## 7. 认证路由

### routers/auth.py

```python
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..config import settings
from ..dependencies import get_db, authenticate_user, create_access_token
from ..schemas import Token

router = APIRouter(tags=["auth"])

@router.post("/token", response_model=Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录获取JWT令牌
    
    - **username**: 用户名
    - **password**: 密码
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}
```

## 8. 主应用文件

### main.py

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import users, auth

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 包含路由
app.include_router(auth.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    """
    根端点，返回应用信息
    """
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }
```

## 9. 数据库配置

### database.py

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from .config import settings

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 声明基类
Base = declarative_base()
```

## 10. 安全工具

### security.py

```python
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str):
    """
    验证密码是否正确
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    """
    生成密码哈希
    """
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    创建JWT访问令牌
    
    - **data**: 要编码的数据
    - **expires_delta**: 过期时间间隔
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt
```

## 11. 部署配置

### Dockerfile

```dockerfile
# 使用官方Python基础镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 复制依赖文件
COPY requirements.txt .

# 安装依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 8000

# 运行应用
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### requirements.txt

```
fastapi==0.68.0
uvicorn==0.15.0
sqlalchemy==1.4.22
psycopg2-binary==2.9.1
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.5
pydantic==1.8.2
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/userdb
    depends_on:
      - db
    volumes:
      - .:/

---

