from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import init_db
from .services.user import UserService
from .routers.users import router as users_router

app = FastAPI(
    title="User Management API",
    description="API for managing users",
    version="1.0.0",
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据库连接
@app.on_event("startup")
async def startup_db_client():
    app.db = await init_db()
    app.user_service = UserService(app.db)

@app.on_event("shutdown")
async def shutdown_db_client():
    app.db.client.close()

# 包含路由
app.include_router(users_router)