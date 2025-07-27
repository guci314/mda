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
    email: EmailStr
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")  # E.164 电话格式
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: constr(min_length=1, max_length=50) = None
    email: EmailStr = None
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$") = None

class UserInDB(UserBase):
    id: str  # UUID格式的唯一标识符
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
```

## 2. API 端点设计 (RESTful)

### 用户管理 API

| 端点 | 方法 | 描述 | 认证要求 |
|------|------|------|----------|
| `/api/users/register` | POST | 用户注册 | 无 |
| `/api/users` | POST | 创建用户 | 管理员 |
| `/api/users` | GET | 查询用户列表 | 管理员 |
| `/api/users/{user_id}` | GET | 获取用户详情 | 用户自己或管理员 |
| `/api/users/{user_id}` | PUT | 更新用户信息 | 用户自己或管理员 |
| `/api/users/{user_id}` | DELETE | 删除/停用用户 | 管理员 |

### 详细端点定义

```python
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate, user_service: UserService = Depends()):
    """
    用户注册
    - 验证信息完整性
    - 验证邮箱和电话格式
    - 检查邮箱唯一性
    - 生成唯一标识符
    - 设置默认状态为活跃
    - 记录创建时间
    """
    return await user_service.register_user(user_create)

@router.post("", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(user_create: UserCreate, 
                     user_service: UserService = Depends(),
                     current_user: UserInDB = Depends(get_current_admin_user)):
    """创建用户 (管理员权限)"""
    return await user_service.create_user(user_create)

@router.get("", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[UserStatus] = None,
    user_service: UserService = Depends(),
    current_user: UserInDB = Depends(get_current_admin_user)
):
    """查询用户列表 (分页, 支持条件过滤)"""
    return await user_service.list_users(skip=skip, limit=limit, name=name, email=email, status=status)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str,
    user_service: UserService = Depends(),
    current_user: UserInDB = Depends(get_current_user_or_admin)
):
    """获取用户详情"""
    user = await user_service.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    user_service: UserService = Depends(),
    current_user: UserInDB = Depends(get_current_user_or_admin)
):
    """更新用户信息"""
    return await user_service.update_user(user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    user_service: UserService = Depends(),
    current_user: UserInDB = Depends(get_current_admin_user)
):
    """删除/停用用户"""
    await user_service.delete_user(user_id)
    return None
```

## 3. 服务层方法定义

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from . import models, schemas

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    async def register_user(self, user_create: schemas.UserCreate) -> models.User:
        # 验证邮箱唯一性
        if self.db.query(models.User).filter(models.User.email == user_create.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered"
            )
        
        # 创建用户记录
        db_user = models.User(
            id=str(uuid.uuid4()),
            name=user_create.name,
            email=user_create.email,
            phone=user_create.phone,
            status=user_create.status,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        try:
            self.db.commit()
            self.db.refresh(db_user)
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail="Failed to create user"
            )
        
        return db_user
    
    async def create_user(self, user_create: schemas.UserCreate) -> models.User:
        return await self.register_user(user_create)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[schemas.UserStatus] = None
    ) -> List[models.User]:
        query = self.db.query(models.User)
        
        if name:
            query = query.filter(models.User.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(models.User.email == email)
        if status:
            query = query.filter(models.User.status == status)
            
        return query.offset(skip).limit(limit).all()
    
    async def get_user(self, user_id: str) -> Optional[models.User]:
        return self.db.query(models.User).filter(models.User.id == user_id).first()
    
    async def update_user(self, user_id: str, user_update: schemas.UserUpdate) -> models.User:
        db_user = await self.get_user(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        update_data = user_update.dict(exclude_unset=True)
        if "email" in update_data and update_data["email"] != db_user.email:
            if self.db.query(models.User).filter(models.User.email == update_data["email"]).first():
                raise HTTPException(
                    status_code=400,
                    detail="Email already registered"
                )
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    async def delete_user(self, user_id: str) -> None:
        db_user = await self.get_user(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.status = schemas.UserStatus.INACTIVE
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
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

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
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
    
    user = await UserService(db).get_user(user_id)
    if user is None:
        raise credentials_exception
    return user

async def get_current_admin_user(current_user: UserInDB = Depends(get_current_user)):
    if not current_user.is_admin:  # 假设用户模型中有is_admin字段
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

async def get_current_user_or_admin(
    user_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return current_user
```

## 5. 数据库设计

### SQLAlchemy 模型

```python
from sqlalchemy import Column, String, DateTime, Enum
from .database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)  # UUID
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    status = Column(Enum("active", "inactive"), default="active", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # 如果实现认证系统
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)
```

### 数据库迁移脚本 (Alembic)

```python
# 迁移脚本示例
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('phone', sa.String(20), nullable=False),
        sa.Column('status', sa.Enum('active', 'inactive', name='user_status'), 
               server_default='active', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), 
               onupdate=sa.text('now()'), nullable=False),
        sa.Column('hashed_password', sa.String(255)),
        sa.Column('is_admin', sa.Boolean(), server_default='false')
    )

def downgrade():
    op.drop_table('users')
```

## 6. 非功能需求实现

### 性能优化
- 数据库查询添加索引
- 使用分页查询避免大数据量返回
- 实现缓存层 (Redis) 用于频繁访问的用户数据

### 可靠性保证
- 数据库操作使用事务
- 实现错误处理和回滚机制
- 添加日志记录关键操作

### 安全措施
- 密码哈希存储
- JWT 认证
- 输入验证
- 敏感数据保护

## 7. 部署建议

1. **数据库**：PostgreSQL 或 MySQL
2. **缓存**：Redis 用于会话和频繁访问数据
3. **API 网关**：Nginx 或 Traefik
4. **监控**：Prometheus + Grafana
5. **日志**：ELK Stack 或 Loki

## 8. 扩展点

1. **审计日志**：记录用户关键操作
2. **通知系统**：用户注册/更新时发送邮件通知
3. **导入/导出**：批量用户数据处理
4. **多因素认证**：增强安全性