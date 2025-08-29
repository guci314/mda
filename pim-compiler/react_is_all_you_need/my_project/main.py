from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import database
from routers import articles_router, categories_router, comments_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    database.init_db()
    yield


# 创建FastAPI应用
app = FastAPI(
    title="博客系统API",
    description="基于FastAPI的博客系统，支持文章、分类和评论管理",
    version="1.0.0",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(categories_router, prefix="/api/v1/categories", tags=["categories"])
app.include_router(articles_router, prefix="/api/v1/articles", tags=["articles"])
app.include_router(comments_router, prefix="/api/v1/comments", tags=["comments"])


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "博客系统API",
        "version": "1.0.0",
        "docs": "/docs"
    }