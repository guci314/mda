# FastAPI 用户管理平台特定模型 (PSM)

## 1. 数据模型定义

### 用户模型 (User)

```python
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional
from enum import Enum

class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)  # 姓名不能为空
    email: EmailStr  # 自动验证邮箱格式
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # E.164电话格式
    status: UserStatus = UserStatus.ACTIVE  # 默认活跃状态

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r"^\+?[1-9]\d{1,14}$")] = None
    status: Optional[UserStatus] = None

class UserInDB(UserBase):
    id: str  # 唯一标识符
    created_at: datetime  # 创建时间
    updated_at: datetime  # 更新时间

    class Config:
        orm_mode = True
```

## 2. API端点设计 (RESTful)

### 用户管理API

| 端点 | 方法 | 描述 | 认证要求 |
|------|------|------|----------|
| `/api/users/register` | POST | 注册新用户 | 公开 |
| `/api/users` | POST | 创建用户 (管理员) | 管理员 |
| `/api/users` | GET | 查询用户列表 | 认证用户 |
| `/api/users/{user_id}` | GET | 获取用户详情 | 认证用户或管理员 |
| `/api/users/{user_id}` | PUT | 更新用户信息 | 用户自己或管理员 |
| `/api/users/{user_id}` | DELETE | 删除/停用用户 | 管理员 |

### 详细端点定义

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate):
    """
    用户注册流程
    - 验证信息完整性
    - 验证邮箱和电话格式
    - 检查邮箱唯一性
    - 生成唯一ID
    - 设置默认状态为活跃
    - 记录创建时间
    """
    pass

@router.post("", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, current_user: UserInDB = Depends(get_current_admin)):
    """
    管理员创建用户
    """
    pass

@router.get("", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[UserStatus] = None,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    分页查询用户列表
    - 支持按姓名、邮箱、状态过滤
    """
    pass

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    获取单个用户详情
    - 普通用户只能查看自己
    - 管理员可以查看所有用户
    """
    pass

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user_or_admin)
):
    """
    更新用户信息
    - 用户只能更新自己的信息
    - 管理员可以更新任何用户
    - 更新邮箱时需要重新验证唯一性
    """
    pass

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: UserInDB = Depends(get_current_admin)
):
    """
    删除用户（实际是设置为停用状态）
    - 仅管理员可操作
    - 记录更新时间
    """
    pass
```

## 3. 服务层方法定义

```python
from typing import Optional, List
from sqlalchemy.orm import Session

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_create: UserCreate) -> UserInDB:
        """
        完整注册流程实现
        """
        # 1. 验证信息完整性 (由Pydantic处理)
        
        # 2. 检查邮箱唯一性
        if self.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # 3. 生成唯一ID (UUID)
        user_id = str(uuid.uuid4())
        
        # 4. 创建用户记录
        db_user = UserModel(
            id=user_id,
            name=user_create.name,
            email=user_create.email,
            phone=user_create.phone,
            status=UserStatus.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # 5. 保存到数据库 (事务处理)
        try:
            self.db.add(db_user)
            self.db.commit()
            self.db.refresh(db_user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        return db_user
    
    def create_user(self, user_create: UserCreate) -> UserInDB:
        """管理员创建用户 (简化版注册流程)"""
        return self.register_user(user_create)
    
    def get_user_by_id(self, user_id: str) -> Optional[UserInDB]:
        """根据ID查询用户"""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserInDB]:
        """根据邮箱查询用户"""
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[UserStatus] = None
    ) -> List[UserInDB]:
        """分页查询用户列表"""
        query = self.db.query(UserModel)
        
        if name:
            query = query.filter(UserModel.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(UserModel.email.ilike(f"%{email}%"))
        if status:
            query = query.filter(UserModel.status == status)
            
        return query.offset(skip).limit(limit).all()
    
    def update_user(self, user_id: str, user_update: UserUpdate) -> UserInDB:
        """更新用户信息"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # 检查邮箱唯一性 (如果修改了邮箱)
        if user_update.email and user_update.email != db_user.email:
            if self.get_user_by_email(user_update.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            self.db.refresh(db_user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
        
        return db_user
    
    def delete_user(self, user_id: str) -> None:
        """删除用户 (设置为停用状态)"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.status = UserStatus.INACTIVE
        db_user.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserInDB:
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
    
    user = UserService(db).get_user_by_id(user_id)
    if user is None:
        raise credentials_exception
    return user

def get_current_admin(
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    # 这里假设有一个is_admin字段或角色系统
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def get_current_user_or_admin(
    user_id: str,
    current_user: UserInDB = Depends(get_current_user)
) -> UserInDB:
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return current_user
```

## 5. 数据库设计 (SQLAlchemy模型)

```python
from sqlalchemy import Column, String, Enum, DateTime
from sqlalchemy.ext.declarative import declarative_base
import enum

Base = declarative_base()

class UserStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    status = Column(Enum(UserStatusEnum), default=UserStatusEnum.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 如果实现认证系统
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
```

## 6. 数据库迁移 (Alembic)

建议使用Alembic进行数据库迁移管理。初始迁移脚本应包含:

```python
# migrations/versions/xxxx_initial.py

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', name='userstatusenum'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
```

## 7. 依赖注入配置

```python
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_service(db: Session = Depends(get_db)) -> UserService:
    return UserService(db)
```

## 8. 错误处理

```python
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers,
    )
```

## 9. 性能优化考虑

1. **数据库索引**:
   - 在email字段上创建唯一索引
   - 在status字段上创建普通索引

2. **缓存策略**:
   - 对频繁访问的用户数据使用Redis缓存
   - 实现缓存失效策略

3. **批量操作**:
   - 实现批量用户创建和更新API
   - 使用数据库批量插入优化性能

## 10. 安全考虑

1. **数据保护**:
   - 敏感字段(如密码)不返回API响应
   - 使用HTTPS传输

2. **速率限制**:
   - 对注册和登录接口实施速率限制
   - 防止暴力破解

3. **输入验证**:
   - 使用Pydantic进行严格输入验证
   - 防止SQL注入

这个PSM文档提供了从PIM到FastAPI平台的完整转换，涵盖了数据模型、API设计、服务实现、认证授权和数据库设计等关键方面。