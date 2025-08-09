"""
图书借阅系统主应用
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import create_tables
from app.routers import books_router, readers_router, borrows_router, reservations_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时创建数据库表
    await create_tables()
    print("数据库表创建完成")
    yield
    # 关闭时的清理工作
    print("应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="图书借阅系统API",
    description="基于FastAPI的图书借阅管理系统，提供图书、读者、借阅、预约等功能",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(books_router)
app.include_router(readers_router)
app.include_router(borrows_router)
app.include_router(reservations_router)


@app.get("/", tags=["根路径"])
async def root():
    """根路径"""
    return {
        "message": "欢迎使用图书借阅系统API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health", tags=["健康检查"])
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "message": "图书借阅系统运行正常"
    }


@app.get("/api/info", tags=["系统信息"])
async def api_info():
    """API信息"""
    return {
        "title": "图书借阅系统API",
        "version": "1.0.0",
        "description": "基于FastAPI的图书借阅管理系统",
        "endpoints": {
            "books": "/books",
            "readers": "/readers", 
            "borrows": "/borrows",
            "reservations": "/reservations"
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # 从环境变量获取配置
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )