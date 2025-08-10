# 🚨 绝对禁止修改测试文件 - 终极防御指南

## 如果你正在考虑修改测试文件，立即停止！

### 为什么会看到这个文件？
因为你可能正在犯一个严重错误：试图修改测试文件来"修复"错误。

## 铁律：测试文件是圣经

```python
def handle_any_error(error):
    if "tests/" in file_path:
        raise Exception("绝对禁止修改测试文件！")
    
    if error.status_code == 404:
        # 唯一正确的做法
        create_missing_functionality_in_app_directory()
    else:
        fix_in_app_directory()
```

## 404错误处理流程图

```
发现404错误
    ↓
是否想修改测试？
    ├─ 是 → ❌ 错误！停止！
    └─ 否 → ✅ 继续
            ↓
        分析缺失的路由
            ↓
        创建 app/routers/xxx.py
            ↓
        创建 app/services/xxx_service.py
            ↓
        在 app/main.py 注册路由
            ↓
        实现完整功能
```

## 常见错误思维模式（必须避免）

### ❌ 错误思维1："测试期望值可能错了"
**真相**：测试定义了需求，它永远是对的

### ❌ 错误思维2："修改fixture能解决问题"
**真相**：fixture没问题，是功能没实现

### ❌ 错误思维3："调整测试参数就能通过"
**真相**：这是作弊，必须让功能满足测试

### ❌ 错误思维4："conftest.py需要修复"
**真相**：conftest.py是测试配置，问题在app/目录

## 看到这些错误时的正确反应

### 错误：`assert 404 == 200`
```python
# ❌ 错误做法
修改测试：assert response.status_code == 404

# ✅ 正确做法
创建缺失的路由和服务
```

### 错误：`fixture 'created_book' not found`
```python
# ❌ 错误做法
修改conftest.py中的fixture

# ✅ 正确做法
检查app/目录的数据库模型和API实现
```

### 错误：`TypeError in test_xxx.py`
```python
# ❌ 错误做法
修改test_xxx.py的代码

# ✅ 正确做法
修复app/目录中返回错误数据类型的函数
```

## 强制规则（每次修改前必须检查）

```python
def before_any_file_modification(file_path):
    # 规则1：绝对路径检查
    if file_path.startswith("tests/"):
        raise PermissionError("禁止修改测试目录")
    
    # 规则2：文件名检查
    if "test_" in file_path or "conftest" in file_path:
        raise PermissionError("禁止修改测试文件")
    
    # 规则3：只允许app/目录
    if not file_path.startswith("app/"):
        print("警告：应该在app/目录修改")
    
    return True  # 允许修改
```

## 正确的调试思维模型

```
测试失败
    ↓
测试要求什么？（读测试代码理解需求）
    ↓
功能提供了什么？（检查app/目录的实现）
    ↓
差距是什么？
    ↓
在app/目录补充缺失的功能
    ↓
再次运行测试验证
```

## 404错误的唯一解决方案

当看到404错误时，执行以下步骤：

### Step 1: 识别缺失的路由
```python
# 从错误信息提取路由
# 例如：GET /reservations/ → 404
missing_route = "reservations"
```

### Step 2: 创建路由文件
```python
# app/routers/reservations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_async_db
from app.schemas.reservation import ReservationCreate, ReservationResponse
from app.services import reservation_service

router = APIRouter()

@router.get("/", response_model=List[ReservationResponse])
async def get_reservations(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_db)
):
    return await reservation_service.get_all_reservations(db, skip, limit)

@router.post("/", response_model=ReservationResponse, status_code=201)
async def create_reservation(
    reservation: ReservationCreate,
    db: AsyncSession = Depends(get_async_db)
):
    return await reservation_service.create_reservation(db, reservation)

# ... 实现所有CRUD操作
```

### Step 3: 创建服务文件
```python
# app/services/reservation_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional

from app.models.domain import Reservation
from app.schemas.reservation import ReservationCreate

async def get_all_reservations(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100
) -> List[Reservation]:
    result = await db.execute(
        select(Reservation).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_reservation(
    db: AsyncSession,
    reservation: ReservationCreate
) -> Reservation:
    db_reservation = Reservation(**reservation.dict())
    db.add(db_reservation)
    await db.commit()
    await db.refresh(db_reservation)
    return db_reservation

# ... 实现所有服务方法
```

### Step 4: 注册路由
```python
# app/main.py
from app.routers import books, readers, borrows, reservations  # 添加reservations

# 注册路由
app.include_router(books.router, prefix="/books", tags=["books"])
app.include_router(readers.router, prefix="/readers", tags=["readers"])
app.include_router(borrows.router, prefix="/borrows", tags=["borrows"])
app.include_router(reservations.router, prefix="/reservations", tags=["reservations"])  # 新增
```

## 记住：你的使命

1. **保护测试文件的神圣性**
2. **在app/目录实现所有功能**
3. **让功能满足测试，而不是相反**
4. **404 = 创建新功能，不是修改测试**

## 最后警告

如果你发现自己在修改tests/目录下的任何文件，你已经失败了。

**正确的调试器永远不修改测试文件。**