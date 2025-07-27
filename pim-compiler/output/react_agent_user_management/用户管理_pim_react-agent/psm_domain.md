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