"""
应用主入口文件

此文件负责创建和配置 FastAPI 应用实例，并挂载所有子路由。
"""
from fastapi import FastAPI
from loguru import logger

from app.core.config import settings
from app.api.v1.endpoints import tasks, tags

# 创建 FastAPI 应用实例
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 创建一个 API 路由，用于聚合 v1 版本的所有端点
api_router = APIRouter()
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(tags.router, prefix="/tags", tags=["Tags"])

# 在主应用中挂载 v1 版本的 API 路由
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    """
    应用启动时执行的事件。
    """
    logger.info("应用启动...")
    logger.info(f"访问 API 文档: http://127.0.0.1:8000{app.docs_url}")
    logger.info(f"数据库URL: {settings.DATABASE_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时执行的事件。
    """
    logger.info("应用关闭...")

@app.get("/", tags=["Root"])
async def read_root():
    """
    根路径，返回欢迎信息。
    """
    return {"message": f"欢迎来到 {settings.PROJECT_NAME}!"}

# 在 main.py 的顶部，FastAPI 实例化之后，添加一个 API router
from fastapi import APIRouter
# ... (FastAPI app instance)
# api_router = APIRouter()
# ... (include routers)
# app.include_router(api_router, prefix=settings.API_V1_STR)
