```python
# main.py - FastAPI 用户管理平台主应用入口文件

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, constr
from datetime import datetime
from typing import Optional, List
from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Enum as SQLEnum, DateTime, Boolean
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid
import enum

# 应用配置
app = FastAPI(
    title="用户管理平台",
    description="基于FastAPI的用户管理系统",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库配置
SQLALCHEMY_DATABASE_URL = "sqlite:///./users.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# 认证配置
SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token")

# 数据模型定义
class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class UserBase(BaseModel):
    name: constr(min_length=1, max_length=50)
    email: EmailStr
    phone: constr(regex=r"^\+?[1-9]\d{1,14}$")
    status: UserStatus = UserStatus.ACTIVE

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[constr(min_length=1, max_length=50)] = None
    email: Optional[EmailStr] = None
    phone: Optional[constr(regex=r"^\+?[1-9]\d{1,14}$")] = None
    status: Optional[UserStatus] = None

class UserInDB(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# 数据库模型
class UserStatusEnum(str, enum.Enum):
    active = "active"
    inactive = "inactive"

class UserModel(Base):
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    phone = Column(String(20), nullable=False)
    status = Column(SQLEnum(UserStatusEnum), default=UserStatusEnum.active)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    hashed_password = Column(String(255))
    is_admin = Column(Boolean, default=False)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 依赖注入
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 服务层
class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_create: UserCreate) -> UserInDB:
        if self.get_user_by_email(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        user_id = str(uuid.uuid4())
        db_user = UserModel(
            id=user_id,
            name=user_create.name,
            email=user_create.email,
            phone=user_create.phone,
            status=UserStatusEnum.ACTIVE,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
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
        return self.register_user(user_create)
    
    def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()
    
    def get_user_by_email(self, email: str) -> Optional[UserModel]:
        return self.db.query(UserModel).filter(UserModel.email == email).first()
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[UserStatusEnum] = None
    ) -> List[UserModel]:
        query = self.db.query(UserModel)
        
        if name:
            query = query.filter(UserModel.name.ilike(f"%{name}%"))
        if email:
            query = query.filter(UserModel.email.ilike(f"%{email}%"))
        if status:
            query = query.filter(UserModel.status == status)
            
        return query.offset(skip).limit(limit).all()
    
    def update_user(self, user_id: str, user_update: UserUpdate) -> UserModel:
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
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
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.status = UserStatusEnum.INACTIVE
        db_user.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )

# 认证和权限控制
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> UserModel:
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
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user

def get_current_user_or_admin(
    user_id: str,
    current_user: UserModel = Depends(get_current_user)
) -> UserModel:
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this resource"
        )
    return current_user

# API路由
router = APIRouter(prefix="/api/users", tags=["users"])

@router.post("/register", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def register_user(user_create: UserCreate, db: Session = Depends(get_db)):
    return UserService(db).register_user(user_create)

@router.post("", response_model=UserInDB, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_create: UserCreate,
    current_user: UserModel = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    return UserService(db).create_user(user_create)

@router.get("", response_model=List[UserInDB])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    email: Optional[str] = None,
    status: Optional[UserStatus] = None,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return UserService(db).list_users(skip, limit, name, email, status)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(
    user_id: str,
    current_user: UserModel = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = UserService(db).get_user_by_id(user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserModel = Depends(get_current_user_or_admin),
    db: Session = Depends(get_db)
):
    return UserService(db).update_user(user_id, user_update)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: str,
    current_user: UserModel = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    UserService(db).delete_user(user_id)
    return None

# 错误处理
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

# 注册路由
app.include_router(router)

# 启动应用
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```