```python
# auth.py
"""
极简用户认证系统
仅支持邮箱+密码，提供注册、登录、密码重置、会话管理
"""

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Dict, Optional

# 内存存储（演示用）
_users: Dict[str, Dict] = {}          # email -> user
_sessions: Dict[str, str] = {}        # token -> email


class AuthError(Exception):
    """认证相关异常"""
    pass


def _hash_pwd(pwd: str) -> str:
    """简单哈希（演示用，生产请用 bcrypt/scrypt）"""
    import hashlib
    return hashlib.sha256(pwd.encode()).hexdigest()


def _valid_email(email: str) -> bool:
    return re.fullmatch(r"[^@]+@[^@]+\.[^@]+", email) is not None


def register(email: str, password: str) -> None:
    """注册新用户"""
    if not _valid_email(email):
        raise AuthError("邮箱格式错误")
    if email in _users:
        raise AuthError("用户已存在")
    _users[email] = {
        "pwd_hash": _hash_pwd(password),
        "created": datetime.now(timezone.utc)
    }


def login(email: str, password: str) -> str:
    """登录并返回会话 token"""
    user = _users.get(email)
    if not user or user["pwd_hash"] != _hash_pwd(password):
        raise AuthError("邮箱或密码错误")
    token = str(uuid.uuid4())
    _sessions[token] = email
    return token


def reset_password(email: str, new_password: str) -> None:
    """重置密码"""
    if email not in _users:
        raise AuthError("用户不存在")
    _users[email]["pwd_hash"] = _hash_pwd(new_password)


def session_info(token: str) -> Optional[Dict]:
    """根据 token 返回用户信息"""
    email = _sessions.get(token)
    if not email:
        return None
    return {"email": email, "created": _users[email]["created"]}


def logout(token: str) -> None:
    """登出"""
    _sessions.pop(token, None)
```

以下示例采用 **FastAPI + PostgreSQL + asyncpg + bcrypt + JWT** 作为技术栈，实现“注册 / 登录”核心功能。  
代码保持简洁，单文件即可运行（生产请拆分）。

```python
# main.py
"""
极简 FastAPI 认证服务
GET  /health     探活
POST /register   注册
POST /login      登录
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Annotated

import asyncpg
import bcrypt
from fastapi import FastAPI, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from pydantic import BaseModel, EmailStr

# -------------------- 配置 --------------------
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pwd@localhost:5432/auth")
JWT_SECRET = os.getenv("JWT_SECRET", "change-me")
JWT_ALGO = "HS256"
ACCESS_TTL = timedelta(hours=24)

app = FastAPI()
security = HTTPBearer(auto_error=False)


# -------------------- 模型 --------------------
class AuthRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    token: str


# -------------------- 数据库 --------------------
async def get_db() -> asyncpg.Connection:
    return await asyncpg.connect(DATABASE_URL)


async def init_db() -> None:
    conn = await get_db()
    await conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users(
            email TEXT PRIMARY KEY,
            pwd_hash TEXT NOT NULL,
            created TIMESTAMPTZ DEFAULT now()
        )
        """
    )
    await conn.close()


# -------------------- 工具 --------------------
def hash_pwd(p: str) -> str:
    return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()


def verify_pwd(p: str, hashed: str) -> bool:
    return bcrypt.checkpw(p.encode(), hashed.encode())


def create_token(email: str) -> str:
    payload = {"sub": email, "exp": datetime.now(timezone.utc) + ACCESS_TTL}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


# -------------------- 路由 --------------------
@app.on_event("startup")
async def startup():
    await init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(req: AuthRequest):
    conn = await get_db()
    try:
        await conn.execute(
            "INSERT INTO users(email, pwd_hash) VALUES($1, $2)",
            req.email,
            hash_pwd(req.password),
        )
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail="用户已存在")
    finally:
        await conn.close()
    return Token(token=create_token(req.email))


@app.post("/login", response_model=Token)
async def login(req: AuthRequest):
    conn = await get_db()
    row = await conn.fetchrow("SELECT pwd_hash FROM users WHERE email=$1", req.email)
    await conn.close()
    if not row or not verify_pwd(req.password, row["pwd_hash"]):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    return Token(token=create_token(req.email))


# -------------------- 运行 --------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
```

依赖（`pip install fastapi uvicorn asyncpg bcrypt python-jose[cryptography] pydantic[email]`）。

```python
# models.py
"""
用户认证系统数据模型
实体：User（用户）
属性：email（主键）、pwd_hash、created_at
关系：无（单实体即可满足注册/登录）
"""
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    """持久化用户实体"""
    email: EmailStr = Field(..., description="唯一标识")
    pwd_hash: str = Field(..., description="bcrypt 哈希")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserCreate(BaseModel):
    """注册请求载荷"""
    email: EmailStr
    password: str = Field(..., min_length=6, max_length=128)


class TokenPayload(BaseModel):
    """JWT 载荷"""
    sub: EmailStr
    exp: datetime


class Token(BaseModel):
    """登录成功返回"""
    access_token: str
    token_type: str = "bearer"
```

```python
# endpoints.py
"""
FastAPI 端点：注册 / 登录 / 登出 / 重置密码
"""
from datetime import datetime, timezone
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from jose import JWTError, jwt
from pydantic import BaseModel, EmailStr

from main import JWT_SECRET, JWT_ALGO, ACCESS_TTL, get_db
from models import UserCreate, Token
import bcrypt
import asyncpg

router = APIRouter(prefix="/api/v1", tags=["auth"])


class ResetRequest(BaseModel):
    email: EmailStr
    new_password: str


# ---------- 依赖 ----------
async def _get_user(conn: asyncpg.Connection, email: str) -> Dict:
    row = await conn.fetchrow("SELECT * FROM users WHERE email=$1", email)
    if not row:
        raise HTTPException(status_code=404, detail="用户不存在")
    return dict(row)


# ---------- 端点 ----------
@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(req: UserCreate, conn=Depends(get_db)):
    pwd_hash = bcrypt.hashpw(req.password.encode(), bcrypt.gensalt()).decode()
    try:
        await conn.execute(
            "INSERT INTO users(email, pwd_hash) VALUES($1, $2)",
            req.email,
            pwd_hash,
        )
    except asyncpg.exceptions.UniqueViolationError:
        raise HTTPException(status_code=409, detail="用户已存在")
    token = jwt.encode(
        {"sub": req.email, "exp": datetime.now(timezone.utc) + ACCESS_TTL},
        JWT_SECRET,
        algorithm=JWT_ALGO,
    )
    return Token(access_token=token, token_type="bearer")


@router.post("/login", response_model=Token)
async def login(req: UserCreate, conn=Depends(get_db)):
    user = await _get_user(conn, req.email)
    if not bcrypt.checkpw(req.password.encode(), user["pwd_hash"].encode()):
        raise HTTPException(status_code=401, detail="邮箱或密码错误")
    token = jwt.encode(
        {"sub": req.email, "exp": datetime.now(timezone.utc) + ACCESS_TTL},
        JWT_SECRET,
        algorithm=JWT_ALGO,
    )
    return Token(access_token=token, token_type="bearer")


@router.post("/logout")
async def logout(token: str):
    # 无状态 JWT，直接返回成功；如需黑名单可在此记录
    return {"detail": "已登出"}


@router.post("/reset-password")
async def reset_password(req: ResetRequest, conn=Depends(get_db)):
    user = await _get_user(conn, req.email)
    new_hash = bcrypt.hashpw(req.new_password.encode(), bcrypt.gensalt()).decode()
    await conn.execute(
        "UPDATE users SET pwd_hash=$1 WHERE email=$2", new_hash, req.email
    )
    return {"detail": "密码已重置"}
```