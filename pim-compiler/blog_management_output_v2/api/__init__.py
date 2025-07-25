"""
API路由模块

包含博客管理系统的所有CRUD端点
"""

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1")

# 导入各子路由模块
# from . import posts, users, comments, categories