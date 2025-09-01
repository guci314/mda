"""路由层包"""

from .article import router as articles_router
from .category import router as categories_router
from .comment import router as comments_router

__all__ = ["articles_router", "categories_router", "comments_router"]