"""
路由包初始化
"""
from .books import router as books_router
from .readers import router as readers_router
from .borrows import router as borrows_router
from .reservations import router as reservations_router

__all__ = [
    "books_router",
    "readers_router", 
    "borrows_router",
    "reservations_router"
]