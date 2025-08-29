# 路由包初始化
from .articles import router as articles_router
from .categories import router as categories_router
from .comments import router as comments_router

__all__ = ["articles_router", "categories_router", "comments_router"]