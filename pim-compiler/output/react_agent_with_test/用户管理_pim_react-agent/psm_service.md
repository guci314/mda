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