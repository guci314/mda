from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.users import router as users_router
from .database import engine, Base

app = FastAPI(
    title="用户管理服务",
    description="基于FastAPI的用户管理系统",
    version="1.0.0"
)

# 允许所有来源的跨域请求（生产环境应限制）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建数据库表
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# 包含用户管理路由
app.include_router(
    users_router,
    prefix="/api/v1",
    tags=["users"]
)

# 健康检查端点
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "user-service",
        "version": "1.0.0"
    }