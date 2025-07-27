# FastAPI UserService 实现

下面是一个基于 FastAPI 的 UserService 服务层实现，包含 CRUD 操作、错误处理、async/await 模式以及类型注解。

```python
from typing import List, Optional
from fastapi import HTTPException, status
from pydantic import BaseModel
from uuid import UUID, uuid4


# 数据模型
class User(BaseModel):
    id: UUID
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False


class UserCreate(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None
    disabled: bool = False


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


# 模拟数据库
class Database:
    def __init__(self):
        self.users: dict[UUID, User] = {}

    async def get_user(self, user_id: UUID) -> Optional[User]:
        return self.users.get(user_id)

    async def get_users(self) -> List[User]:
        return list(self.users.values())

    async def create_user(self, user: User) -> User:
        self.users[user.id] = user
        return user

    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> Optional[User]:
        if user_id not in self.users:
            return None
        
        user = self.users[user_id]
        update_data = user_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(user, field, value)
        
        self.users[user_id] = user
        return user

    async def delete_user(self, user_id: UUID) -> bool:
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False


# 服务层
class UserService:
    def __init__(self, db: Database):
        self.db = db

    async def get_user(self, user_id: UUID) -> User:
        user = await self.db.get_user(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def get_users(self) -> List[User]:
        return await self.db.get_users()

    async def create_user(self, user_create: UserCreate) -> User:
        user = User(
            id=uuid4(),
            **user_create.dict()
        )
        return await self.db.create_user(user)

    async def update_user(self, user_id: UUID, user_update: UserUpdate) -> User:
        user = await self.db.update_user(user_id, user_update)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user

    async def delete_user(self, user_id: UUID) -> None:
        success = await self.db.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )


# 使用示例
if __name__ == "__main__":
    import asyncio
    
    async def main():
        db = Database()
        service = UserService(db)
        
        # 创建用户
        new_user = await service.create_user(UserCreate(
            username="johndoe",
            email="john@example.com",
            full_name="John Doe"
        ))
        print(f"Created user: {new_user}")
        
        # 获取用户
        user = await service.get_user(new_user.id)
        print(f"Retrieved user: {user}")
        
        # 更新用户
        updated_user = await service.update_user(
            user.id,
            UserUpdate(email="john.doe@example.com", disabled=True)
        )
        print(f"Updated user: {updated_user}")
        
        # 获取所有用户
        users = await service.get_users()
        print(f"All users: {users}")
        
        # 删除用户
        await service.delete_user(user.id)
        print("User deleted")
        
        try:
            await service.get_user(user.id)
        except HTTPException as e:
            print(f"Error as expected: {e.detail}")
    
    asyncio.run(main())
```

## 代码说明

1. **数据模型**:
   - `User`: 用户数据模型
   - `UserCreate`: 创建用户时的输入模型
   - `UserUpdate`: 更新用户时的输入模型

2. **数据库模拟**:
   - `Database` 类模拟了一个简单的内存数据库，提供了基本的 CRUD 操作

3. **服务层**:
   - `UserService` 实现了完整的用户服务逻辑
   - 包含错误处理，当用户不存在时返回 404 错误
   - 所有方法都使用 async/await 模式
   - 包含完整的类型注解

4. **特点**:
   - 使用 Pydantic 模型进行数据验证
   - 使用 UUID 作为用户 ID
   - 包含适当的错误处理
   - 支持部分更新 (PATCH 语义)

你可以将此服务层集成到 FastAPI 路由中，例如:

```python
from fastapi import APIRouter

router = APIRouter()
db = Database()
user_service = UserService(db)

@router.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    return await user_service.create_user(user)

@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: UUID):
    return await user_service.get_user(user_id)

# 其他路由...
```