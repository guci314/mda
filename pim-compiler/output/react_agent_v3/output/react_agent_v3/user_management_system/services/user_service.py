from typing import Optional
from uuid import uuid4
from datetime import datetime
from ..schemas.user import UserCreate, UserUpdate, UserInDB, UserQueryParams

class UserService:
    def __init__(self, db_session):
        self.db = db_session
    
    async def register_user(self, user_data: UserCreate) -> dict:
        """
        注册用户流程
        返回: {success: bool, message: str, user: Optional[UserInDB]}
        """
        # 1. 验证信息完整性 (由Pydantic自动处理)
        
        # 2. 检查邮箱唯一性
        if await self._check_email_exists(user_data.email):
            return {
                "success": False,
                "message": "Email already registered",
                "user": None
            }
        
        # 3. 生成唯一标识符
        user_id = str(uuid4())
        
        # 4. 准备用户数据
        user_dict = user_data.dict()
        user_dict.update({
            "id": user_id,
            "status": "active",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # 5. 保存用户
        try:
            user = await self.db.users.insert_one(user_dict)
            return {
                "success": True,
                "message": "User registered successfully",
                "user": UserInDB(**user_dict)
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Registration failed: {str(e)}",
                "user": None
            }
    
    async def create_user(self, user_data: UserCreate) -> UserInDB:
        """创建用户 (管理员)"""
        return await self.register_user(user_data)
    
    async def get_user(self, user_id: str) -> Optional[UserInDB]:
        """获取单个用户"""
        user = await self.db.users.find_one({"id": user_id})
        return UserInDB(**user) if user else None
    
    async def query_users(self, params: UserQueryParams) -> dict:
        """查询用户列表"""
        query = {}
        if params.name:
            query["name"] = {"$regex": params.name, "$options": "i"}
        if params.email:
            query["email"] = params.email
        if params.status:
            query["status"] = params.status
            
        total = await self.db.users.count_documents(query)
        users = await self.db.users.find(query).skip(params.skip).limit(params.limit).to_list(None)
        
        return {
            "success": True,
            "total": total,
            "users": [UserInDB(**user) for user in users]
        }
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[UserInDB]:
        """更新用户信息"""
        update_data = user_data.dict(exclude_unset=True)
        if not update_data:
            return None
            
        update_data["updated_at"] = datetime.utcnow()
        
        if "email" in update_data and await self._check_email_exists(update_data["email"], exclude_id=user_id):
            raise ValueError("Email already in use")
            
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 1:
            return await self.get_user(user_id)
        return None
    
    async def delete_user(self, user_id: str) -> bool:
        """删除用户 (设置为停用)"""
        result = await self.db.users.update_one(
            {"id": user_id},
            {"$set": {"status": "inactive", "updated_at": datetime.utcnow()}}
        )
        return result.modified_count == 1
    
    async def _check_email_exists(self, email: str, exclude_id: str = None) -> bool:
        """检查邮箱是否已存在"""
        query = {"email": email}
        if exclude_id:
            query["id"] = {"$ne": exclude_id}
        return await self.db.users.count_documents(query) > 0