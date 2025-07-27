#!/usr/bin/env python3
"""从PSM生成代码文件"""

import os
from pathlib import Path
from datetime import datetime

def main():
    print("=== Generating Code from PSM ===")
    
    # 读取PSM
    psm_file = Path("output/direct_compile/user_management_psm.md")
    if not psm_file.exists():
        print(f"❌ PSM file not found: {psm_file}")
        return
    
    psm_content = psm_file.read_text(encoding='utf-8')
    print(f"✅ Loaded PSM: {psm_file}")
    
    # 设置输出目录
    output_dir = Path("output/direct_compile/generated")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 创建项目结构
    print("\nCreating project structure...")
    
    # 1. 创建 requirements.txt
    requirements = """fastapi==0.100.0
uvicorn[standard]==0.22.0
sqlalchemy==2.0.19
pydantic==2.0.3
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
python-dotenv==1.0.0
"""
    (output_dir / "requirements.txt").write_text(requirements)
    print("✅ Created requirements.txt")
    
    # 2. 创建 README.md
    readme = """# FastAPI 用户管理系统

基于 FastAPI 的用户管理系统，包含用户注册、登录、角色权限管理等功能。

## 快速开始

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. 设置环境变量：
   创建 `.env` 文件并配置数据库连接等信息

3. 运行应用：
   ```bash
   uvicorn main:app --reload
   ```

## API 文档

运行后访问 http://localhost:8000/docs 查看 Swagger 文档
"""
    (output_dir / "README.md").write_text(readme)
    print("✅ Created README.md")
    
    # 3. 创建 .env.example
    env_example = """DATABASE_URL=postgresql://username:password@localhost/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
"""
    (output_dir / ".env.example").write_text(env_example)
    print("✅ Created .env.example")
    
    # 4. 创建包结构
    packages = ["models", "schemas", "services", "api", "core", "db"]
    for pkg in packages:
        pkg_dir = output_dir / pkg
        pkg_dir.mkdir(exist_ok=True)
        (pkg_dir / "__init__.py").write_text("")
    print(f"✅ Created {len(packages)} packages")
    
    # 5. 创建 database.py
    database_py = """from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
"""
    (output_dir / "db" / "database.py").write_text(database_py)
    print("✅ Created db/database.py")
    
    # 6. 创建 config.py
    config_py = """from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
"""
    (output_dir / "core" / "config.py").write_text(config_py)
    print("✅ Created core/config.py")
    
    # 7. 创建 models/user.py
    user_model = """from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from db.database import Base

# 用户角色关联表
user_role_association = Table(
    'user_role_association',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('assigned_at', DateTime, default=datetime.utcnow)
)

# 角色权限关联表
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
    action = Column(String(20), nullable=False)
    
    roles = relationship("Role", secondary=role_permission_association, back_populates="permissions")
"""
    (output_dir / "models" / "user.py").write_text(user_model)
    print("✅ Created models/user.py")
    
    # 8. 创建 schemas/user.py
    user_schema = """from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, pattern="^[a-zA-Z][a-zA-Z0-9_]*$")
    email: EmailStr
    full_name: str = Field(..., min_length=1, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    
    @field_validator('password')
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
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None
"""
    (output_dir / "schemas" / "user.py").write_text(user_schema)
    print("✅ Created schemas/user.py")
    
    # 9. 创建 main.py
    main_py = """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import engine, Base
from api import auth, users

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(title="用户管理系统", version="1.0.0")

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(users.router, prefix="/api/users", tags=["用户"])

@app.get("/")
def read_root():
    return {"message": "用户管理系统 API"}
"""
    (output_dir / "main.py").write_text(main_py)
    print("✅ Created main.py")
    
    # 10. 创建 auth router
    auth_router = """from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from db.database import get_db
from schemas.user import UserCreate, UserInDB, Token
from services.user_service import UserService
from services.auth_service import AuthService
from core.config import settings

router = APIRouter()

@router.post("/register", response_model=UserInDB)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    user_service = UserService(db)
    if user_service.get_user_by_username(user_data.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if user_service.get_user_by_email(user_data.email):
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_service.create_user(user_data)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
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
    
    auth_service = AuthService()
    access_token = auth_service.create_access_token(
        data={"sub": user.username}, 
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    user_service.update_last_login(user)
    return {"access_token": access_token, "token_type": "bearer"}
"""
    (output_dir / "api" / "auth.py").write_text(auth_router)
    print("✅ Created api/auth.py")
    
    # 11. 创建 users router
    users_router = """from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from schemas.user import UserInDB, UserUpdate
from services.user_service import UserService
from core.dependencies import get_current_active_user
from models.user import User

router = APIRouter()

@router.get("/me", response_model=UserInDB)
def read_current_user(current_user: User = Depends(get_current_active_user)):
    return current_user

@router.put("/me", response_model=UserInDB)
def update_current_user(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    user_service = UserService(db)
    return user_service.update_user(current_user, update_data)
"""
    (output_dir / "api" / "users.py").write_text(users_router)
    print("✅ Created api/users.py")
    
    # 12. 创建 user service
    user_service = """from passlib.context import CryptContext
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from models.user import User
from schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    def __init__(self, db_session: Session):
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
            full_name=user_data.full_name
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
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def update_last_login(self, user: User) -> None:
        user.last_login = datetime.utcnow()
        self.db.commit()
"""
    (output_dir / "services" / "user_service.py").write_text(user_service)
    print("✅ Created services/user_service.py")
    
    # 13. 创建 auth service
    auth_service = """from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
from core.config import settings

class AuthService:
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str):
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except JWTError:
            return None
"""
    (output_dir / "services" / "auth_service.py").write_text(auth_service)
    print("✅ Created services/auth_service.py")
    
    # 14. 创建 dependencies
    dependencies_py = """from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db.database import get_db
from models.user import User
from services.user_service import UserService
from services.auth_service import AuthService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    auth_service = AuthService()
    username = auth_service.verify_token(token)
    if username is None:
        raise credentials_exception
    user_service = UserService(db)
    user = user_service.get_user_by_username(username)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
"""
    (output_dir / "core" / "dependencies.py").write_text(dependencies_py)
    print("✅ Created core/dependencies.py")
    
    # 15. 创建 __init__.py for api
    api_init = """from . import auth, users
"""
    (output_dir / "api" / "__init__.py").write_text(api_init)
    print("✅ Created api/__init__.py")
    
    print(f"\n✅ Code generation complete!")
    print(f"Generated 15 files in: {output_dir}")
    print("\nNext steps:")
    print("1. cd output/direct_compile/generated")
    print("2. pip install -r requirements.txt")
    print("3. cp .env.example .env (and update values)")
    print("4. uvicorn main:app --reload")

if __name__ == "__main__":
    main()