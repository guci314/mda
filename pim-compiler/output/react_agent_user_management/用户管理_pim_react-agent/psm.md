# Platform Specific Model (PSM)

生成时间: 2025-07-27 06:02:35
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
class PhoneNumber:
    """电话号码值对象，不可变且具有验证逻辑"""
    def __init__(self, number: str):
        if not self._validate_phone(number):
            raise ValueError("Invalid phone number format")
        self._number = number
    
    @property
    def number(self) -> str:
        return self._number
    
    @staticmethod
    def _validate_phone(phone: str) -> bool:
        """验证电话号码格式 (简单示例)"""
        return len(phone) >= 10 and phone.isdigit()

# SQLAlchemy 实体模型
class User(Base):
    """用户实体模型"""
    __tablename__ = "users"
    
    # 主键使用UUID，确保全局唯一性
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    
    # 用户名，必填，长度限制2-50字符
    name = Column(String(50), nullable=False)
    
    # 邮箱，必填，唯一索引，长度限制255字符
    email = Column(String(255), unique=True, nullable=False, index=True)
    
    # 电话号码，可选，长度限制20字符
    phone = Column(String(20))
    
    # 用户状态，使用枚举，默认活跃状态
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    
    # 创建时间，自动设置为当前时间
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 更新时间，自动更新
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """将实体转换为字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
```

## Pydantic 模型 (用于请求/响应验证)

```python
from pydantic import BaseModel, Field, validator
from typing import Optional

# 基础用户模型
class UserBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, example="张三")
    email: EmailStr = Field(..., example="user@example.com")
    phone: Optional[str] = Field(
        None, 
        min_length=10, 
        max_length=20, 
        regex=r"^\d+$",
        example="13800138000"
    )

# 创建用户请求模型
class UserCreate(UserBase):
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError("Phone number must contain only digits")
        return v

# 更新用户请求模型
class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50, example="李四")
    email: Optional[EmailStr] = Field(None, example="new@example.com")
    phone: Optional[str] = Field(
        None, 
        min_length=10, 
        max_length=20, 
        regex=r"^\d+$",
        example="13900139000"
    )
    
    @validator('phone')
    def validate_phone(cls, v):
        if v is not None and not v.isdigit():
            raise ValueError("Phone number must contain only digits")
        return v

# 用户响应模型
class UserResponse(UserBase):
    id: str
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        orm_mode = True
```

## 领域服务实现 (FastAPI 路由)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from . import crud, schemas
from .database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户
    
    业务规则:
    1. 邮箱必须唯一
    2. 电话号码格式必须有效
    3. 用户默认状态为活跃
    """
    # 检查邮箱是否已存在
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # 验证电话号码
    if user.phone:
        try:
            PhoneNumber(user.phone)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    # 创建用户
    return crud.create_user(db=db, user=user)

@router.get("/", response_model=List[schemas.UserResponse])
def read_users(
    skip: int = 0,
    limit: int = 100,
    status: Optional[schemas.UserStatus] = None,
    db: Session = Depends(get_db)
):
    """
    查询用户列表
    
    支持分页和状态过滤
    """
    users = crud.get_users(db, skip=skip, limit=limit, status=status)
    return users

@router.get("/{user_id}", response_model=schemas.UserResponse)
def read_user(user_id: str, db: Session = Depends(get_db)):
    """
    根据ID查询单个用户
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.put("/{user_id}", response_model=schemas.UserResponse)
def update_user(
    user_id: str,
    user: schemas.UserUpdate,
    db: Session = Depends(get_db)
):
    """
    更新用户信息
    
    业务规则:
    1. 如果修改邮箱，必须保持唯一性
    2. 更新后自动更新updated_at字段
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # 检查邮箱唯一性
    if user.email and user.email != db_user.email:
        existing_user = crud.get_user_by_email(db, email=user.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # 验证电话号码
    if user.phone:
        try:
            PhoneNumber(user.phone)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    return crud.update_user(db=db, user_id=user_id, user=user)

@router.delete("/{user_id}", response_model=schemas.UserResponse)
def delete_user(user_id: str, db: Session = Depends(get_db)):
    """
    删除用户 (实际上是设置为停用状态)
    
    业务规则:
    1. 不实际删除记录，而是将状态改为停用
    2. 更新updated_at字段
    """
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return crud.deactivate_user(db=db, user_id=user_id)
```

## CRUD 操作实现

```python
from sqlalchemy.orm import Session
import uuid
from typing import Optional

from . import models, schemas

def get_user(db: Session, user_id: str):
    """根据ID查询单个用户"""
    return db.query(models.User).filter(models.User.id == uuid.UUID(user_id)).first()

def get_user_by_email(db: Session, email: str):
    """根据邮箱查询用户"""
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(
    db: Session, 
    skip: int = 0, 
    limit: int = 100,
    status: Optional[schemas.UserStatus] = None
):
    """查询用户列表，支持分页和状态过滤"""
    query = db.query(models.User)
    if status:
        query = query.filter(models.User.status == status)
    return query.offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    """创建新用户"""
    db_user = models.User(
        name=user.name,
        email=user.email,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, user_id: str, user: schemas.UserUpdate):
    """更新用户信息"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_user, key, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def deactivate_user(db: Session, user_id: str):
    """停用用户"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    db_user.status = models.UserStatus.INACTIVE
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
```

## 领域规则实现

1. **唯一性规则**：
   - 通过SQLAlchemy的`unique=True`约束和业务逻辑双重保证
   - 在创建和更新时检查邮箱唯一性

2. **数据完整性规则**：
   - 使用Pydantic模型进行输入验证
   - 姓名：必填，长度2-50字符
   - 邮箱：必填，符合Email格式
   - 电话：可选，但必须符合格式要求

3. **状态规则**：
   - 新用户默认为`ACTIVE`状态
   - 删除操作实际上是设置为`INACTIVE`状态

## 最佳实践说明

1. **分层架构**：
   - 路由层：处理HTTP请求/响应
   - 服务层：实现业务逻辑
   - 数据访问层：处理数据库操作

2. **依赖注入**：
   - 使用FastAPI的Depends注入数据库会话

3. **错误处理**：
   - 使用HTTPException返回适当的HTTP状态码和错误信息

4. **验证**：
   - 使用Pydantic进行输入验证
   - 自定义验证逻辑处理业务规则

5. **类型安全**：
   - 使用Python类型注解
   - 为枚举和值对象创建专用类型

6. **性能考虑**：
   - 为常用查询字段(如email)创建索引
   - 实现分页查询避免大数据集问题

7. **RESTful设计**：
   - 使用适当的HTTP方法和状态码
   - 资源导向的URL设计

---

## 2. Service Layer（服务层）

# 用户管理服务层实现 (PSM)

## 服务接口定义

### 用户服务接口 (UserService)

```python
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, constr
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# 用户状态枚举
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

# 用户输入模型
class UserCreate(BaseModel):
    name: constr(min_length=1, max_length=50)  # 姓名不能为空且长度限制
    email: EmailStr  # 使用Pydantic的EmailStr验证邮箱格式
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # 国际电话号码格式验证
    
# 用户更新模型
class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r"^\+?[1-9]\d{1,14}$")] = None
    status: Optional[UserStatus] = None

# 用户输出模型
class UserOut(BaseModel):
    id: str  # 用户唯一标识符
    name: str
    email: str
    phone: str
    status: UserStatus
    created_at: datetime
    updated_at: datetime

# 查询条件模型
class UserQuery(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    status: Optional[UserStatus] = None
    skip: int = 0  # 分页偏移量
    limit: int = 100  # 每页数量限制

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, user_data: UserCreate) -> UserOut:
        """
        注册新用户
        参数:
            user_data: 包含用户姓名、邮箱、电话的创建数据
        返回:
            注册成功的用户信息
        异常:
            HTTPException 400: 输入数据验证失败
            HTTPException 409: 邮箱已存在
            HTTPException 500: 系统错误
        """
        pass
    
    async def create_user(self, user_data: UserCreate) -> UserOut:
        """
        创建新用户记录
        参数:
            user_data: 包含用户姓名、邮箱、电话的创建数据
        返回:
            创建成功的用户信息
        异常:
            HTTPException 400: 输入数据验证失败
            HTTPException 409: 邮箱已存在
            HTTPException 500: 系统错误
        """
        pass
    
    async def get_users(self, query: UserQuery) -> List[UserOut]:
        """
        查询用户列表
        参数:
            query: 包含查询条件和分页参数
        返回:
            匹配的用户列表
        异常:
            HTTPException 400: 查询参数验证失败
            HTTPException 500: 系统错误
        """
        pass
    
    async def get_user_by_id(self, user_id: str) -> UserOut:
        """
        根据ID获取单个用户
        参数:
            user_id: 用户唯一标识符
        返回:
            用户详细信息
        异常:
            HTTPException 404: 用户不存在
            HTTPException 500: 系统错误
        """
        pass
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> UserOut:
        """
        更新用户信息
        参数:
            user_id: 要更新的用户ID
            update_data: 更新数据
        返回:
            更新后的用户信息
        异常:
            HTTPException 400: 输入数据验证失败
            HTTPException 404: 用户不存在
            HTTPException 409: 邮箱冲突
            HTTPException 500: 系统错误
        """
        pass
    
    async def delete_user(self, user_id: str) -> bool:
        """
        删除用户(实际上是标记为停用)
        参数:
            user_id: 要删除的用户ID
        返回:
            是否成功删除
        异常:
            HTTPException 404: 用户不存在
            HTTPException 500: 系统错误
        """
        pass
```

## 业务流程实现

### 用户服务实现

```python
from uuid import uuid4
from sqlalchemy import and_, or_

class UserServiceImpl(UserService):
    async def register_user(self, user_data: UserCreate) -> UserOut:
        """
        注册用户流程实现
        1. 验证输入数据
        2. 检查邮箱唯一性
        3. 生成唯一ID
        4. 设置默认状态
        5. 记录创建时间
        6. 保存到数据库
        """
        try:
            # 检查邮箱是否已存在
            if self._email_exists(user_data.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
            
            # 创建用户记录
            user_id = str(uuid4())
            now = datetime.utcnow()
            user = User(
                id=user_id,
                name=user_data.name,
                email=user_data.email,
                phone=user_data.phone,
                status=UserStatus.ACTIVE,
                created_at=now,
                updated_at=now
            )
            
            # 保存到数据库
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            
            return UserOut.from_orm(user)
            
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database integrity error"
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def create_user(self, user_data: UserCreate) -> UserOut:
        """创建用户实现(与注册类似但不完全相同)"""
        return await self.register_user(user_data)
    
    async def get_users(self, query: UserQuery) -> List[UserOut]:
        """查询用户列表实现"""
        try:
            # 构建查询条件
            filters = []
            if query.name:
                filters.append(User.name.ilike(f"%{query.name}%"))
            if query.email:
                filters.append(User.email == query.email)
            if query.status:
                filters.append(User.status == query.status)
            
            # 执行查询
            users = self.db.query(User)\
                .filter(and_(*filters))\
                .offset(query.skip)\
                .limit(query.limit)\
                .all()
            
            return [UserOut.from_orm(u) for u in users]
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def get_user_by_id(self, user_id: str) -> UserOut:
        """根据ID获取用户实现"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserOut.from_orm(user)
    
    async def update_user(self, user_id: str, update_data: UserUpdate) -> UserOut:
        """更新用户信息实现"""
        try:
            # 获取现有用户
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # 检查邮箱是否已存在(如果更新了邮箱)
            if update_data.email and update_data.email != user.email:
                if self._email_exists(update_data.email):
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Email already registered"
                    )
            
            # 更新字段
            if update_data.name:
                user.name = update_data.name
            if update_data.email:
                user.email = update_data.email
            if update_data.phone:
                user.phone = update_data.phone
            if update_data.status:
                user.status = update_data.status
            
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(user)
            
            return UserOut.from_orm(user)
            
        except IntegrityError as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database integrity error"
            )
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户实现(标记为停用)"""
        try:
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            user.status = UserStatus.INACTIVE
            user.updated_at = datetime.utcnow()
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    def _email_exists(self, email: str) -> bool:
        """检查邮箱是否已存在"""
        return self.db.query(User)\
            .filter(User.email == email)\
            .first() is not None
```

## 仓储接口 (Repository)

```python
from abc import ABC, abstractmethod
from typing import List, Optional

class UserRepository(ABC):
    """用户仓储抽象接口"""
    
    @abstractmethod
    async def create(self, user: UserCreate) -> UserOut:
        """创建用户"""
        pass
    
    @abstractmethod
    async def get_by_id(self, user_id: str) -> Optional[UserOut]:
        """根据ID获取用户"""
        pass
    
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[UserOut]:
        """根据邮箱获取用户"""
        pass
    
    @abstractmethod
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserOut]:
        """获取所有用户(分页)"""
        pass
    
    @abstractmethod
    async def update(self, user_id: str, update_data: UserUpdate) -> UserOut:
        """更新用户信息"""
        pass
    
    @abstractmethod
    async def delete(self, user_id: str) -> bool:
        """删除用户(标记为停用)"""
        pass
    
    @abstractmethod
    async def search(self, query: UserQuery) -> List[UserOut]:
        """根据条件搜索用户"""
        pass

class SQLAlchemyUserRepository(UserRepository):
    """SQLAlchemy实现的用户仓储"""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create(self, user: UserCreate) -> UserOut:
        """创建用户实现"""
        db_user = User(**user.dict(), id=str(uuid4()))
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserOut.from_orm(db_user)
    
    async def get_by_id(self, user_id: str) -> Optional[UserOut]:
        """根据ID获取用户实现"""
        db_user = self.db.query(User).filter(User.id == user_id).first()
        return UserOut.from_orm(db_user) if db_user else None
    
    async def get_by_email(self, email: str) -> Optional[UserOut]:
        """根据邮箱获取用户实现"""
        db_user = self.db.query(User).filter(User.email == email).first()
        return UserOut.from_orm(db_user) if db_user else None
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[UserOut]:
        """获取所有用户实现"""
        users = self.db.query(User).offset(skip).limit(limit).all()
        return [UserOut.from_orm(u) for u in users]
    
    async def update(self, user_id: str, update_data: UserUpdate) -> UserOut:
        """更新用户信息实现"""
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            raise ValueError("User not found")
        
        update_data_dict = update_data.dict(exclude_unset=True)
        for key, value in update_data_dict.items():
            setattr(db_user, key, value)
        
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(db_user)
        return UserOut.from_orm(db_user)
    
    async def delete(self, user_id: str) -> bool:
        """删除用户实现"""
        db_user = self.db.query(User).filter(User.id == user_id).first()
        if not db_user:
            return False
        
        db_user.status = UserStatus.INACTIVE
        db_user.updated_at = datetime.utcnow()
        self.db.commit()
        return True
    
    async def search(self, query: UserQuery) -> List[UserOut]:
        """搜索用户实现"""
        filters = []
        if query.name:
            filters.append(User.name.ilike(f"%{query.name}%"))
        if query.email:
            filters.append(User.email == query.email)
        if query.status:
            filters.append(User.status == query.status)
        
        users = self.db.query(User)\
            .filter(and_(*filters))\
            .offset(query.skip)\
            .limit(query.limit)\
            .all()
        
        return [UserOut.from_orm(u) for u in users]
```

## 最佳实践说明

1. **事务管理**:
   - 每个服务方法都是一个独立的事务边界
   - 使用SQLAlchemy的commit/rollback机制确保数据一致性
   - 在异常情况下回滚事务

2. **错误处理**:
   - 使用FastAPI的HTTPException返回标准化的错误响应
   - 区分客户端错误(4xx)和服务端错误(5xx)
   - 提供详细的错误信息帮助调试

3. **输入验证**:
   - 使用Pydantic模型进行输入验证
   - 定义严格的字段约束(如邮箱格式、电话格式)
   - 在业务逻辑中执行额外的验证(如邮箱唯一性)

4. **性能考虑**:
   - 查询方法支持分页避免大数据量问题
   - 使用SQLAlchemy的延迟加载优化查询性能
   - 对常用查询条件建立数据库索引

5. **安全考虑**:
   - 不直接暴露数据库模型
   - 使用单独的输入/输出模型
   - 敏感字段(如密码)应单独处理

6. **可测试性**:
   - 依赖注入数据库会话
   - 定义清晰的仓储接口
   - 业务逻辑与持久化分离

---

## 3. API Design（API 设计）

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

---

## 4. Configuration（配置）

# FastAPI 用户管理系统 PSM (Platform Specific Model)

## 1. 应用配置

### 1.1 数据库连接配置

```python
# config/database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseSettings

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/user_management"
    # 服务端口配置
    API_PORT: int = 8000
    # 环境变量
    ENVIRONMENT: str = "development"
    
    class Config:
        env_file = ".env"

settings = Settings()

# SQLAlchemy 配置
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### 1.2 服务端口配置

```python
# main.py
from fastapi import FastAPI
from config.database import settings

app = FastAPI(
    title="用户管理系统",
    description="基于FastAPI的用户管理服务",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
```

## 2. 依赖配置

### 2.1 第三方服务配置

```python
# config/external_services.py
from pydantic import BaseSettings, AnyHttpUrl

class ExternalServicesSettings(BaseSettings):
    # 邮件服务配置
    EMAIL_SERVICE_URL: AnyHttpUrl = "https://api.email-service.com/v1"
    EMAIL_SERVICE_API_KEY: str
    
    # 短信服务配置
    SMS_SERVICE_URL: AnyHttpUrl = "https://api.sms-service.com/v1"
    SMS_SERVICE_API_KEY: str
    
    class Config:
        env_file = ".env"

external_services_settings = ExternalServicesSettings()
```

### 2.2 中间件配置

```python
# main.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

# 仅在生产环境启用HTTPS重定向
if settings.ENVIRONMENT == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.ENVIRONMENT == "development" else [
        "https://your-production-domain.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 3. 安全配置

### 3.1 认证方式

```python
# config/security.py
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseSettings

class SecuritySettings(BaseSettings):
    # JWT配置
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

security_settings = SecuritySettings()

# OAuth2密码认证流程
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
```

### 3.2 授权策略

```python
# utils/security.py
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from config.security import security_settings, oauth2_scheme

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, security_settings.SECRET_KEY, algorithms=[security_settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # 这里可以添加从数据库获取用户的逻辑
    return {"user_id": user_id}

# 基于角色的权限检查
async def check_admin_role(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return current_user
```

### 3.3 CORS 设置

已在中间件配置部分实现

## 4. 部署配置

### 4.1 Docker 配置

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 环境变量
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# 运行应用
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/user_management
      - ENVIRONMENT=production
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=user_management
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 4.2 环境差异配置

```python
# config/environment.py
from enum import Enum
from pydantic import BaseSettings

class Environment(str, Enum):
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"

class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    
    class Config:
        env_file = ".env"

env_settings = EnvironmentSettings()

def get_database_url():
    if env_settings.ENVIRONMENT == Environment.TESTING:
        return "sqlite:///./test.db"
    return settings.DATABASE_URL
```

## 5. 领域模型实现

### 5.1 用户模型 (SQLAlchemy)

```python
# models/user.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from config.database import Base

class UserDB(Base):
    """用户数据库模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False)  # 用户姓名
    email = Column(String(100), unique=True, index=True, nullable=False)  # 用户邮箱
    phone = Column(String(20), nullable=False)  # 用户电话
    is_active = Column(Boolean, default=True)  # 用户状态
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # 创建时间
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  # 更新时间
```

### 5.2 用户模型 (Pydantic)

```python
# schemas/user.py
from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    """用户基础模型"""
    name: str
    email: EmailStr
    phone: str

    @validator('phone')
    def validate_phone(cls, v):
        # 简单的电话号码验证
        if not v.isdigit() or len(v) < 10:
            raise ValueError("电话号码格式不正确")
        return v

class UserCreate(UserBase):
    """创建用户模型"""
    pass

class UserUpdate(BaseModel):
    """更新用户模型"""
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None

    @validator('phone', pre=True, always=True)
    def validate_phone(cls, v):
        if v is not None and (not v.isdigit() or len(v) < 10):
            raise ValueError("电话号码格式不正确")
        return v

class UserInDB(UserBase):
    """数据库用户模型"""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

## 6. 领域服务实现

### 6.1 用户服务实现

```python
# services/user.py
from sqlalchemy.orm import Session
from models.user import UserDB
from schemas.user import UserCreate, UserUpdate, UserInDB
from fastapi import HTTPException, status
from typing import List, Optional

class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserCreate) -> UserInDB:
        """创建用户"""
        # 检查邮箱唯一性
        db_user = self.db.query(UserDB).filter(UserDB.email == user.email).first()
        if db_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已被注册"
            )
        
        # 创建用户
        db_user = UserDB(**user.dict())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserInDB.from_orm(db_user)

    def get_user(self, user_id: int) -> Optional[UserInDB]:
        """根据ID查询用户"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            return None
        return UserInDB.from_orm(db_user)

    def get_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
        """查询用户列表"""
        db_users = self.db.query(UserDB).offset(skip).limit(limit).all()
        return [UserInDB.from_orm(user) for user in db_users]

    def update_user(self, user_id: int, user: UserUpdate) -> Optional[UserInDB]:
        """更新用户信息"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            return None
        
        update_data = user.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_user, key, value)
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserInDB.from_orm(db_user)

    def delete_user(self, user_id: int) -> bool:
        """删除用户（实际上是停用）"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            return False
        
        db_user.is_active = False
        self.db.add(db_user)
        self.db.commit()
        return True
```

## 7. API路由实现

```python
# api/users.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from models.user import UserDB
from schemas.user import UserCreate, UserUpdate, UserInDB
from services.user import UserService
from config.database import SessionLocal

router = APIRouter(prefix="/users", tags=["users"])

# 依赖项 - 获取数据库会话
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    user_service = UserService(db)
    return user_service.create_user(user)

@router.get("/", response_model=List[UserInDB])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """查询用户列表"""
    user_service = UserService(db)
    return user_service.get_users(skip=skip, limit=limit)

@router.get("/{user_id}", response_model=UserInDB)
def read_user(user_id: int, db: Session = Depends(get_db)):
    """根据ID查询用户"""
    user_service = UserService(db)
    db_user = user_service.get_user(user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.put("/{user_id}", response_model=UserInDB)
def update_user(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息"""
    user_service = UserService(db)
    db_user = user_service.update_user(user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    return db_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """删除用户"""
    user_service = UserService(db)
    success = user_service.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="用户不存在")
    return None
```

## 8. 主应用集成

```python
# main.py
from fastapi import FastAPI
from config.database import settings
from api.users import router as users_router

app = FastAPI(
    title="用户管理系统",
    description="基于FastAPI的用户管理服务",
    version="1.0.0",
    docs_url="/docs" if settings.ENVIRONMENT != "production" else None,
    redoc_url="/redoc" if settings.ENVIRONMENT != "production" else None
)

# 添加路由
app.include_router(users_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.API_PORT)
```

## 9. 测试配置

```python
# tests/conftest.py
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from config.database import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
```

## 10. 业务规则实现

### 10.1 唯一性规则实现

```python
# services/user.py 中的 create_user 方法
def create_user(self, user: UserCreate) -> UserInDB:
    """创建用户"""
    # 检查邮箱唯一性
    db_user = self.db.query(UserDB).filter(UserDB.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    ...
```

### 10.2 数据完整性规则实现

```python
# schemas/user.py 中的验证器
@validator('phone')
def validate_phone(cls, v):
    # 简单的电话号码验证
    if not v.isdigit() or len(v) < 10:
        raise ValueError("电话号码格式不正确")
    return v
```

### 10.3 状态规则实现

```python
# services/user.py 中的 delete_user 方法
def delete_user(self, user_id: int) -> bool:
    """删除用户（实际上是停用）"""
    db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
    if not db_user:
        return False
    
    db_user.is_active = False
    self.db.add(db_user)
    self.db.commit()
    return True
```

## 11. 性能优化

```python
# services/user.py
def get_users(self, skip: int = 0, limit: int = 100) -> List[UserInDB]:
    """查询用户列表 - 使用分页优化性能"""
    db_users = self.db.query(UserDB).filter(UserDB.is_active == True).offset(skip).limit(limit).all()
    return [UserInDB.from_orm(user) for user in db_users]

# 添加索引优化查询性能
# models/user.py
from sqlalchemy import Index

# 在UserDB类定义后添加
Index("idx_user_email", UserDB.email)
Index("idx_user_status", UserDB.is_active)
```

## 12. 错误处理

```python
# exceptions.py
from fastapi import HTTPException, status

class UserNotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

class EmailAlreadyRegisteredException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )

class InvalidPhoneNumberException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="

---

