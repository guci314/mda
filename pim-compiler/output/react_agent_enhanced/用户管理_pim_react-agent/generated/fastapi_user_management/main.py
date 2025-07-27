from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config.config import settings
from .database.database import Base, engine
from .api.user_api import router as user_router

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=settings.CORS_METHODS,
    allow_headers=settings.CORS_HEADERS,
)

# 包含路由
app.include_router(user_router)

@app.get("/")
def read_root():
    """根端点，返回应用信息"""
    return {
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }