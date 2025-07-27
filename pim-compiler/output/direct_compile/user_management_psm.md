# FastAPI 用户管理系统 PSM 文档

## 1. 数据模型定义

### 1.1 SQLAlchemy 模型

```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

# 用户角色关联表（多对多关系）
user_role_association = Table(
    'user_role_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('assigned_at', DateTime, default=datetime.utcnow)
)

# 角色权限关联表（多对多关系）
role_permission_association = Table(
    'role_permission_association',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(20), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(50), nullable=False)
    phone_number = Column(String(20))
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    roles = relationship("Role", secondary=user_role_association, back_populates="users")

class Role(Base):
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    code = Column(String(30), unique=True, nullable=False)
    description = Column(String(255))
    
    users = relationship("User", secondary=user_role_association, back_populates="roles")
    permissions = relationship("Permission", secondary=role_permission_association, back_populates="roles")

class Permission(Base):
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    code = Column(String(50), unique=True, nullable=False)
    resource_type = Column(String(50), nullable=False)
    action = Column(String(20), nullable=False)  # read, create, update, delete
    
    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")
```

### 1.2 Pydantic 模型

```python
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, regex="^[a-zA-Z][a-zA-Z0-9_]*$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @validator('password')
    def password_complexity(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        return v

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=1, max_length=50)
    phone_number: Optional[str] = None

class UserInDB(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class RoleBase(BaseModel):
    name: str = Field(..., max_length=50)
    code: str = Field(..., max_length=30)
    description: Optional[str] = Field(None, max_length=255)

class RoleCreate(RoleBase):
    pass

class RoleInDB(RoleBase):
    id: int
    
    class Config:
        orm_mode = True

class PermissionBase(BaseModel):
    name: str = Field(..., max_length=50)
    code: str = Field(..., max_length=50)
    resource_type: str = Field(..., max_length=50)
    action: str = Field(..., max_length=20)

class PermissionCreate(PermissionBase):
    pass

class PermissionInDB(PermissionBase):
    id: int
    
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
```

## 2. API 端点设计

### 2.1 用户相关端点

| 端点 | 方法 | 描述 | 认证要求 |
|------|------|------|----------|
| `/api/auth/register` | POST | 用户注册 | 无 |
| `/api/auth/login` | POST | 用户登录 | 无 |
| `/api/auth/verify-email` | GET | 验证邮箱 | 无 |
| `/api/users/me` | GET | 获取当前用户信息 | 需要认证 |
| `/api/users/me` | PUT | 更新当前用户信息 | 需要认证 |
| `/api/users/me/password` | PUT | 修改密码 | 需要认证 |
| `/api/users/{user_id}` | GET | 获取用户信息（管理员） | 需要管理员权限 |
| `/api/users/{user_id}/status` | PUT | 启用/禁用用户（管理员） | 需要管理员权限 |

### 2.2 角色相关端点

| 端点 | 方法 | 描述 | 认证要求 |
|------|------|------|----------|
| `/api/roles` | POST | 创建角色 | 需要管理员权限 |
| `/api/roles` | GET | 获取角色列表 | 需要认证 |
| `/api/roles/{role_id}` | GET | 获取角色详情 | 需要认证 |
| `/api/roles/{role_id}` | PUT | 更新角色 | 需要管理员权限 |
| `/api/roles/{role_id}` | DELETE | 删除角色 | 需要管理员权限 |
| `/api/roles/{role_id}/permissions` | POST | 为角色分配权限 | 需要管理员权限 |

### 2.3 权限相关端点

| 端点 | 方法 | 描述 | 认证要求 |
|------|------|------|----------|
| `/api/permissions` | POST | 创建权限 | 需要管理员权限 |
| `/api/permissions` | GET | 获取权限列表 | 需要认证 |
| `/api/permissions/check` | POST | 检查权限 | 需要认证 |

## 3. 服务层方法定义

### 3.1 用户服务

```python
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db_session):
        self.db = db_session
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()
    
    def create_user(self, user_data: UserCreate) -> User:
        hashed_password = pwd_context.hash(user_data.password)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            phone_number=user_data.phone_number if hasattr(user_data, 'phone_number') else None
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.get_user_by_username(username)
        if not user or not pwd_context.verify(password, user.hashed_password):
            return None
        return user
    
    def update_user(self, user: User, update_data: UserUpdate) -> User:
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def change_password(self, user: User, new_password: str) -> User:
        user.hashed_password = pwd_context.hash(new_password)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_last_login(self, user: User) -> None:
        user.last_login = datetime.utcnow()
        self.db.commit()
    
    def set_user_status(self, user: User, is_active: bool) -> User:
        user.is_active = is_active
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def verify_email(self, user: User) -> User:
        user.is_verified = True
        user.is_active = True
        self.db.commit()
        self.db.refresh(user)
        return user
```

### 3.2 认证服务

```python
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

class AuthService:
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str, credentials_exception):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_data = TokenData(username=username)
        except JWTError:
            raise credentials_exception
        return token_data
```

### 3.3 角色服务

```python
class RoleService:
    def __init__(self, db_session):
        self.db = db_session
    
    def create_role(self, role_data: RoleCreate) -> Role:
        db_role = Role(**role_data.dict())
        self.db.add(db_role)
        self.db.commit()
        self.db.refresh(db_role)
        return db_role
    
    def get_role_by_id(self, role_id: int) -> Optional[Role]:
        return self.db.query(Role).filter(Role.id == role_id).first()
    
    def get_role_by_code(self, role_code: str) -> Optional[Role]:
        return self.db.query(Role).filter(Role.code == role_code).first()
    
    def get_all_roles(self) -> List[Role]:
        return self.db.query(Role).all()
    
    def update_role(self, role: Role, update_data: RoleCreate) -> Role:
        for field, value in update_data.dict(exclude_unset=True).items():
            setattr(role, field, value)
        self.db.commit()
        self.db.refresh(role)
        return role
    
    def delete_role(self, role: Role) -> None:
        self.db.delete(role)
        self.db.commit()
    
    def assign_permissions_to_role(self, role: Role, permission_ids: List[int]) -> Role:
        permissions = self.db.query(Permission).filter(Permission.id.in_(permission_ids)).all()
        role.permissions.extend(permissions)
        self.db.commit()
        self.db.refresh(role)
        return role
```

### 3.4 权限服务

```python
class PermissionService:
    def __init__(self, db_session):
        self.db = db_session
    
    def create_permission(self, permission_data: PermissionCreate) -> Permission:
        db_permission = Permission(**permission_data.dict())
        self.db.add(db_permission)
        self.db.commit()
        self.db.refresh(db_permission)
        return db_permission
    
    def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.id == permission_id).first()
    
    def get_permission_by_code(self, permission_code: str) -> Optional[Permission]:
        return self.db.query(Permission).filter(Permission.code == permission_code).first()
    
    def get_all_permissions(self) -> List[Permission]:
        return self.db.query(Permission).all()
    
    def check_user_permission(self, user: User, permission_code: str) -> bool:
        for role in user.roles:
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
        return False
```

## 4. 配置说明

### 4.1 数据库配置

```python
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "postgresql://username:password@localhost/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 4.2 FastAPI 应用配置

```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 依赖项
def get_current_user(token: str = Depends(oauth2_scheme), db = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth_service = AuthService()
    token_data = auth_service.verify_token(token, credentials_exception)
    user_service = UserService(db)
    user = user_service.get_user_by_username(token_data.username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_admin_user(current_user: User = Depends(get_current_user)):
    permission_service = PermissionService(db)
    if not permission_service.check_user_permission(current_user, "admin_access"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user
```

### 4.3 环境变量配置

建议使用 `.env` 文件：

```ini
# .env
DATABASE_URL=postgresql://username:password@localhost/dbname
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
EMAIL_SMTP_SERVER=smtp.example.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=your-email@example.com
EMAIL_PASSWORD=your-email-password
```

### 4.4 路由配置

```python
# 用户认证路由
@app.post("/api/auth/register", response_model=UserInDB)
def register(user_data: UserCreate, db = Depends(get_db)):
    user_service = UserService(db)
    if user_service.get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if user_service.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(user_data)

@app.post("/api/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):
    user_service = UserService(db)
    user = user_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    if not user.is_verified:
        raise HTTPException(status_code=400, detail="Email not verified")
    
    auth_service = AuthService()
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    user_service.update_last_login(user)
    return {"access_token": access_token, "token_type": "bearer"}

# 用户路由
@app.get("/api/users/me", response_model=UserInDB)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.put("/api/users/me", response_model=UserInDB)
def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.update_user(current_user, update_data)

# 角色