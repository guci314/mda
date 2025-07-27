from typing import List, Optional
from uuid import uuid4
from datetime import datetime

from fastapi import HTTPException, status

from ..models.user import UserCreate, UserInDB, UserUpdate, UserStatus

class UserService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def register_user(self, user_create: UserCreate) -> UserInDB:
        # 验证邮箱唯一性
        if await self._check_email_exists(user_create.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        
        # 创建用户记录
        user_id = str(uuid4())
        now = datetime.utcnow()
        user_data = {
            **user_create.dict(),
            "id": user_id,
            "status": UserStatus.ACTIVE,
            "created_at": now,
            "updated_at": now
        }
        
        try:
            user = await self.db.users.insert_one(user_data)
            return UserInDB(**user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
    
    async def create_user(self, user_create: UserCreate) -> UserInDB:
        # 与register_user类似，但可能有不同的权限检查
        pass
    
    async def get_user(self, user_id: str) -> UserInDB:
        user = await self.db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return UserInDB(**user)
    
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        name: Optional[str] = None,
        email: Optional[str] = None,
        status: Optional[UserStatus] = None
    ) -> List[UserInDB]:
        query = {}
        if name:
            query["name"] = {"$regex": name, "$options": "i"}
        if email:
            query["email"] = email
        if status:
            query["status"] = status
        
        users = await self.db.users.find(query).skip(skip).limit(limit).to_list(limit)
        return [UserInDB(**user) for user in users]
    
    async def update_user(self, user_id: str, user_update: UserUpdate) -> UserInDB:
        # 检查用户是否存在
        existing_user = await self.get_user(user_id)
        
        # 检查邮箱唯一性（如果更新了邮箱）
        if user_update.email and user_update.email != existing_user.email:
            if await self._check_email_exists(user_update.email):
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Email already registered"
                )
        
        update_data = user_update.dict(exclude_unset=True)
        if not update_data:
            return existing_user
        
        update_data["updated_at"] = datetime.utcnow()
        
        try:
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": update_data}
            )
            return await self.get_user(user_id)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update user"
            )
    
    async def delete_user(self, user_id: str) -> None:
        try:
            await self.db.users.update_one(
                {"id": user_id},
                {"$set": {"status": UserStatus.INACTIVE, "updated_at": datetime.utcnow()}}
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete user"
            )
    
    async def _check_email_exists(self, email: str) -> bool:
        existing_user = await self.db.users.find_one({"email": email})
        return existing_user is not None