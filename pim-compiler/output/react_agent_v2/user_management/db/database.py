from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel

async def init_db():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.user_management
    
    # 创建索引
    await db.users.create_indexes([
        IndexModel([("id", 1)], unique=True),
        IndexModel([("email", 1)], unique=True),
        IndexModel([("name", "text")])
    ])
    
    return db