# Gemini CLI 修复生成代码指南

本文档记录了在运行和修复 PIM Compiler 生成的代码时遇到的常见问题及解决方案，供 Gemini CLI 参考。

## 1. 环境和依赖问题

### 1.1 Python 依赖缺失

**问题**: FastAPI 应用启动时报错 `RuntimeError: Form data requires "python-multipart" to be installed`

**解决方案**:
```bash
source venv/bin/activate && pip install python-multipart
```

**说明**: requirements.txt 可能缺少某些运行时依赖，需要根据错误信息安装。

### 1.2 代理设置问题

**问题**: 使用 curl 测试本地服务时返回 502 Bad Gateway

**解决方案**: 添加 `--noproxy localhost` 参数
```bash
# 错误方式
curl http://localhost:8100/

# 正确方式
curl --noproxy localhost http://localhost:8100/
```

**说明**: 系统可能配置了 HTTP 代理，导致 localhost 请求被错误转发。

## 2. 代码结构问题

### 2.1 循环导入

**问题**: `ImportError: cannot import name 'Doctor' from partially initialized module`

**解决方案**:
```python
# 在 app/schemas/doctor.py 中使用 TYPE_CHECKING
from __future__ import annotations
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .department import Department

# 使用字符串注解
class Doctor(DoctorInDBBase):
    department: Optional['Department'] = None
```

### 2.2 模块导出缺失

**问题**: `AttributeError: module 'app.models' has no attribute 'User'`

**解决方案**: 在 `__init__.py` 中导出所有模型
```python
# app/models/__init__.py
from .user import User
from .patient import Patient
from .doctor import Doctor
# ... 其他模型
```

### 2.3 导入路径错误

**问题**: 测试文件中 `ModuleNotFoundError: No module named 'app.tests'`

**解决方案**: 修正相对导入路径
```python
# 错误
from app.tests.utils.patient import create_random_patient

# 正确
from tests.utils.patient import create_random_patient
```

## 3. 数据库问题

### 3.1 日期类型转换

**问题**: `TypeError: SQLite Date type only accepts Python date objects as input`

**解决方案**: 确保 Pydantic 模型正确定义日期字段
```python
from datetime import date, datetime
from pydantic import BaseModel

class PatientBase(BaseModel):
    date_of_birth: Optional[date] = None  # 使用 date 而非 str
```

### 3.2 枚举值匹配

**问题**: 枚举值与数据库不匹配

**解决方案**: 检查并统一枚举定义
```python
class GenderEnum(str, enum.Enum):
    male = "男"
    female = "女"
    other = "其他"
```

## 4. API 端点问题

### 4.1 缺失的路由注册

**问题**: 访问某些端点返回 404 Not Found

**解决方案**: 确保所有路由都在 api.py 中注册
```python
# app/api/v1/api.py
from app.api.v1.endpoints import patients, doctors, departments

api_router = APIRouter()
api_router.include_router(patients.router, prefix="/patients", tags=["patients"])
api_router.include_router(doctors.router, prefix="/doctors", tags=["doctors"])
api_router.include_router(departments.router, prefix="/departments", tags=["departments"])
```

### 4.2 Pydantic v2 兼容性

**问题**: `PydanticUserError: TypeAdapter is not fully defined`

**解决方案**: 使用 ConfigDict 替代 Config
```python
from pydantic import BaseModel, ConfigDict

class PatientInDBBase(PatientBase):
    id: int
    model_config = ConfigDict(from_attributes=True)  # Pydantic v2 语法
```

## 5. 应用启动和测试

### 5.1 数据库初始化

在启动应用前，需要初始化数据库：

```python
# 创建 init_db.py
from sqlalchemy import create_engine
from app.db.base import Base
from app.core.config import settings

def init_db():
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
```

### 5.2 FastAPI 应用启动

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install python-multipart  # 额外依赖

# 初始化数据库
python init_db.py

# 启动应用
uvicorn app.main:app --host 0.0.0.0 --port 8100
```

### 5.3 测试 REST 端点

```bash
# 测试根端点
curl --noproxy localhost http://localhost:8100/

# 测试 API 文档
curl --noproxy localhost http://localhost:8100/docs

# 测试具体端点
curl --noproxy localhost http://localhost:8100/api/v1/patients/

# POST 请求示例
curl --noproxy localhost -X POST http://localhost:8100/api/v1/patients/ \
  -H "Content-Type: application/json" \
  -d '{"name": "张三", "id_card_number": "110101199001011234", "phone_number": "13800138000"}'
```

## 6. 修复策略建议

### 6.1 分阶段修复

1. **依赖和导入问题**: 优先修复，这些通常会阻止应用启动
2. **数据库和模型问题**: 确保数据结构正确
3. **API 端点问题**: 最后处理，确保功能完整

### 6.2 自动化修复模板

当遇到常见错误时，可以使用以下修复模板：

```python
# 循环导入修复
if "circular import" in error_message:
    # 使用 TYPE_CHECKING 和字符串注解
    fix_circular_import(file_path)

# 缺失依赖修复
if "No module named" in error_message:
    # 提取模块名并安装
    module_name = extract_module_name(error_message)
    run_command(f"pip install {module_name}")

# Pydantic 兼容性修复
if "Config class is deprecated" in error_message:
    # 替换为 ConfigDict
    update_pydantic_config(file_path)
```

### 6.3 测试验证

每次修复后都应该验证：

1. **语法检查**: `python -m py_compile <file>`
2. **导入检查**: `python -c "import app.main"`
3. **启动检查**: 尝试启动应用并访问根端点
4. **功能检查**: 测试主要 API 端点

## 7. 常用诊断命令

```bash
# 检查 Python 路径
python -c "import sys; print(sys.path)"

# 检查已安装的包
pip list

# 检查文件结构
find . -name "*.py" -type f | grep -E "(models|schemas)" | sort

# 检查导入问题
python -c "from app.models import User"

# 检查数据库表
python -c "from app.db.base import Base; print([t.name for t in Base.metadata.tables.values()])"

# 检查端口占用
lsof -i:8100

# 查看进程
ps aux | grep uvicorn | grep -v grep
```

## 8. 注意事项

1. **总是使用虚拟环境**: 避免依赖冲突
2. **检查日志文件**: FastAPI 的详细错误通常在日志中
3. **增量修复**: 一次只修复一个问题，避免引入新问题
4. **保留原始代码**: 修复前备份，方便回滚
5. **测试驱动**: 确保测试通过再进行下一步

## 9. 性能优化建议

1. **缓存常见修复**: 使用 error_patterns.json 缓存已知问题的修复方案
2. **并行处理**: 独立的文件可以并行修复
3. **跳过非关键警告**: 专注于阻塞性错误
4. **智能重试**: 某些问题（如网络）可以通过重试解决

这份指南基于实际运行 Smart Hospital System 的经验总结，可以帮助 Gemini CLI 更高效地修复生成代码中的问题。