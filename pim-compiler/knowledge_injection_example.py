#!/usr/bin/env python3
"""ReactAgent 知识注入示例"""

# 1. 领域特定知识
DOMAIN_SPECIFIC_KNOWLEDGE = """
## 领域知识库

### 用户管理系统最佳实践
- 密码必须使用 bcrypt 或 argon2 加密
- 邮箱验证使用双重确认机制
- 实现账号锁定机制防止暴力破解
- 使用 JWT 时设置合理的过期时间
- 敏感操作需要二次验证

### FastAPI 最佳实践
- 使用 Pydantic 进行数据验证
- 依赖注入管理数据库会话
- 使用中间件处理跨域请求
- 异步处理长时间运行的任务
- 使用 BackgroundTasks 处理后台任务

### 性能优化知识
- 使用连接池管理数据库连接
- 实现查询结果缓存
- 对频繁查询的字段建立索引
- 使用分页避免大量数据传输
- 实现 API 限流防止滥用
"""

# 2. 错误处理知识
ERROR_HANDLING_KNOWLEDGE = """
## 常见错误及解决方案

### Pydantic v2 兼容性
- 错误: `regex` is removed
- 解决: 使用 `pattern` 替代 `regex`
- 错误: `orm_mode` 
- 解决: 使用 `from_attributes`

### 导入错误
- 错误: ModuleNotFoundError
- 解决: 确保所有目录都有 __init__.py
- 检查 PYTHONPATH 设置
- 使用正确的相对/绝对导入

### 依赖版本冲突
- httpx 0.28+ 与 openai 不兼容
- 解决: 降级到 httpx==0.24.1
- LangChain 需要特定版本的 Pydantic
"""

# 3. 项目模板知识
PROJECT_TEMPLATES = {
    "fastapi": {
        "structure": """
project_name/
├── __init__.py
├── main.py              # FastAPI 应用入口
├── core/                # 核心配置
│   ├── __init__.py
│   ├── config.py        # 设置管理
│   └── security.py      # 安全相关
├── api/                 # API 路由
│   ├── __init__.py
│   ├── deps.py          # 共享依赖
│   └── v1/
│       ├── __init__.py
│       └── endpoints/
├── models/              # 数据模型
│   ├── __init__.py
│   └── domain/          # 领域模型
├── schemas/             # Pydantic schemas
│   ├── __init__.py
│   └── user.py
├── services/            # 业务逻辑
│   ├── __init__.py
│   └── user.py
├── db/                  # 数据库
│   ├── __init__.py
│   ├── base.py
│   └── session.py
└── tests/              # 测试
    ├── __init__.py
    └── conftest.py
""",
        "dependencies": [
            "fastapi>=0.100.0",
            "uvicorn[standard]",
            "pydantic>=2.0",
            "pydantic-settings",
            "sqlalchemy>=2.0",
            "alembic",
            "python-jose[cryptography]",
            "passlib[bcrypt]",
            "python-multipart",
            "email-validator"
        ]
    }
}

# 4. 代码片段库
CODE_SNIPPETS = {
    "auth_middleware": '''
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            if not credentials.scheme == "Bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme.")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token.")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code.")
    
    def verify_jwt(self, jwtoken: str) -> bool:
        # JWT验证逻辑
        pass
''',
    "database_session": '''
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
'''
}

# 5. 测试用例模板
TEST_TEMPLATES = {
    "api_test": '''
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

@pytest.fixture(scope="module")
def test_app():
    from main import app
    client = TestClient(app)
    yield client

def test_create_user(test_app):
    response = test_app.post(
        "/api/v1/users/",
        json={"email": "test@example.com", "password": "secret"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
'''
}

if __name__ == "__main__":
    print("知识注入示例已创建")
    print("\n可用的知识类别：")
    print("1. 领域特定知识")
    print("2. 错误处理知识")
    print("3. 项目模板")
    print("4. 代码片段库")
    print("5. 测试模板")