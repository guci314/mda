from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import users

# 创建应用
app = FastAPI(
    title="User Management System",
    description="API for managing users",
    version="1.0.0"
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router)

@app.get("/")
def root():
    return {"message": "Welcome to User Management System"}