from fastapi import FastAPI
from .database import engine, Base
from .api.routes import users

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 创建 FastAPI 应用
app = FastAPI(title="User Management System")

# 注册路由
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "User Management System API"}