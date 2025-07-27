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