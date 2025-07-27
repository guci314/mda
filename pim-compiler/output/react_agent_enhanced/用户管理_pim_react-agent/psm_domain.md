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