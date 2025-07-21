#!/usr/bin/env python3
"""实验：让 Gemini CLI 根据 PSM 文件生成代码"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

print("\n实验：Gemini CLI 从 PSM 生成代码")
print("=" * 60)

# 创建实验目录
exp_dir = Path("./experiment_psm_to_code")
if exp_dir.exists():
    shutil.rmtree(exp_dir)
exp_dir.mkdir()

psm_dir = exp_dir / "psm"
psm_dir.mkdir()
code_dir = exp_dir / "generated"
code_dir.mkdir()

print(f"\n1. 创建目录结构:")
print(f"   - PSM 目录: {psm_dir}")
print(f"   - 代码目录: {code_dir}")

# 创建 PSM 文件
psm_content = """# 用户管理系统 PSM - FastAPI 平台

## 1. 技术架构
- **框架**: FastAPI
- **数据库**: PostgreSQL + SQLAlchemy
- **验证**: Pydantic
- **API文档**: 自动生成的 OpenAPI/Swagger

## 2. 数据模型实现

### User 实体
```python
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Pydantic Schemas
```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50, pattern="^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)

class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
```

## 3. API 实现

### 路由定义
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    # 检查邮箱是否已存在
    # 检查用户名是否已存在
    # 创建新用户
    # 返回用户信息
    pass

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: str, db: Session = Depends(get_db)):
    # 查询用户
    # 如果不存在抛出 404
    # 返回用户信息
    pass
```

## 4. 业务逻辑实现

### UserService
```python
from typing import Optional
import bcrypt
from uuid import uuid4

class UserService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> User:
        # 验证邮箱唯一性
        # 验证用户名唯一性
        # 哈希密码
        # 创建用户记录
        # 发送验证邮件（异步）
        pass
    
    def verify_email(self, token: str) -> bool:
        # 验证令牌
        # 更新用户状态
        pass
```

## 5. 项目结构
```
src/
├── models/
│   └── user.py          # SQLAlchemy 模型
├── schemas/
│   └── user.py          # Pydantic schemas
├── api/
│   └── v1/
│       └── users.py     # API 路由
├── services/
│   └── user_service.py  # 业务逻辑
├── core/
│   ├── config.py        # 配置
│   └── database.py      # 数据库连接
└── main.py              # FastAPI 应用入口
```

## 6. 依赖项
```
fastapi==0.104.1
uvicorn==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic[email]==2.5.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
```
"""

psm_file = psm_dir / "user_management_psm.md"
with open(psm_file, 'w', encoding='utf-8') as f:
    f.write(psm_content)

print(f"\n2. 创建 PSM 文件: {psm_file}")

# 准备 Gemini CLI 命令
print("\n3. 准备 Gemini CLI 调用...")

# 构建提示
prompt = f"""你是一个专业的 FastAPI 开发工程师。

我有一个平台特定模型（PSM）文件，位于：psm/user_management_psm.md

请你根据这个 PSM 文件生成完整的 FastAPI 代码实现。

要求：
1. 读取 PSM 文件了解需求
2. 在 generated/ 目录下创建完整的项目结构
3. 实现所有的模型、API、服务和配置
4. 生成 requirements.txt 文件
5. 确保代码可以直接运行

注意：
- 使用 Pydantic v2 语法（pattern 而不是 regex）
- 使用 SQLAlchemy 2.0 语法
- 包含完整的错误处理
- 添加适当的日志记录
- 实现基本的密码哈希功能

请开始实现。
"""

# 准备环境变量
env = os.environ.copy()
if "GOOGLE_API_KEY" in env and "GEMINI_API_KEY" in env:
    del env["GOOGLE_API_KEY"]

# Gemini CLI 路径
gemini_cli_path = "/home/guci/.nvm/versions/node/v22.17.0/bin/gemini"
if not os.path.exists(gemini_cli_path):
    gemini_cli_path = "gemini"

model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")

print(f"\n4. 调用 Gemini CLI...")
print(f"   - 模型: {model}")
print(f"   - 工作目录: {exp_dir}")

# 调用 Gemini CLI
result = subprocess.run(
    [gemini_cli_path, "-m", model, "-p", prompt, "-y"],
    capture_output=True,
    text=True,
    env=env,
    cwd=exp_dir,  # 在实验目录中执行
    timeout=600   # 10分钟超时
)

print(f"\n5. Gemini CLI 执行结果:")
print(f"   - 返回码: {result.returncode}")

if result.returncode == 0:
    print("   - ✓ 执行成功")
else:
    print("   - ✗ 执行失败")
    if result.stderr:
        print(f"\n错误信息:")
        print("-" * 60)
        print(result.stderr)
        print("-" * 60)

# 检查生成的文件
print(f"\n6. 检查生成的文件...")

# 列出 generated 目录中的所有文件
if code_dir.exists():
    all_files = []
    for root, dirs, files in os.walk(code_dir):
        for file in files:
            file_path = Path(root) / file
            relative_path = file_path.relative_to(code_dir)
            all_files.append(str(relative_path))
    
    if all_files:
        print(f"\n✓ 成功生成 {len(all_files)} 个文件:")
        for f in sorted(all_files):
            print(f"   - {f}")
    else:
        print("\n✗ generated 目录为空")
else:
    print("\n✗ generated 目录不存在")

# 检查关键文件
key_files = [
    "src/main.py",
    "src/models/user.py",
    "src/schemas/user.py",
    "src/api/v1/users.py",
    "src/services/user_service.py",
    "requirements.txt"
]

print(f"\n7. 检查关键文件:")
for key_file in key_files:
    file_path = code_dir / key_file
    if file_path.exists():
        print(f"   ✓ {key_file}")
        # 显示文件大小
        size = file_path.stat().st_size
        print(f"     大小: {size} 字节")
    else:
        print(f"   ✗ {key_file} 未找到")

# 如果有 main.py，显示其内容的前几行
main_file = code_dir / "src" / "main.py"
if main_file.exists():
    print(f"\n8. main.py 内容预览:")
    print("-" * 60)
    with open(main_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()[:20]  # 前20行
        for i, line in enumerate(lines, 1):
            print(f"{i:3d} | {line.rstrip()}")
    if len(lines) == 20:
        print("... (文件内容已截断)")
    print("-" * 60)

# 检查 requirements.txt
req_file = code_dir / "requirements.txt"
if req_file.exists():
    print(f"\n9. requirements.txt 内容:")
    print("-" * 60)
    with open(req_file, 'r', encoding='utf-8') as f:
        print(f.read())
    print("-" * 60)

print(f"\n实验完成！")
print(f"实验目录: {exp_dir}")
print(f"\n提示：你可以查看生成的代码:")
print(f"  cd {exp_dir}/generated")
print(f"  tree -I '__pycache__'")