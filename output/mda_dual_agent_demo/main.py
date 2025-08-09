from fastapi import FastAPI
from app.database import init_db

app = FastAPI(title="图书借阅系统API")

@app.on_event("startup")
def startup():
    """初始化数据库连接"""
    init_db()

@app.on_event("shutdown")
def shutdown():
    """关闭数据库连接"""
    pass

# 包含路由
from app.routers import books, readers, borrows, reservations
app.include_router(books.router, prefix="/api")
app.include_router(readers.router, prefix="/api")
app.include_router(borrows.router, prefix="/api")
app.include_router(reservations.router, prefix="/api")