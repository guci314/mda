# 修复 SQLAlchemy "Table already defined" 错误

## 错误特征
```
InvalidRequestError: Table 'books' is already defined for this MetaData instance
```

## 根本原因
这个错误发生在应用代码（app/models/）中，不是测试的问题！

## 正确的修复方法

### 1. 检查 app/models/database.py
确保Base只被定义一次：
```python
# app/models/database.py
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()  # 只应该有一个Base实例
```

### 2. 检查模型导入
在 app/models/ 中避免循环导入：
```python
# app/models/__init__.py
# 不要这样：
from .database import Base
from .book import BookDB
from .reader import ReaderDB

# 应该这样（如果有循环导入问题）：
# 让每个模型文件单独导入Base
```

### 3. 检查模型定义
每个模型类只应该定义一次：
```python
# app/models/book.py
from .database import Base  # 使用相对导入

class BookDB(Base):
    __tablename__ = "books"
    # ... 字段定义
```

### 4. 修复导入路径
统一使用相对导入或绝对导入，不要混用：
```python
# ❌ 错误：混用导入
from app.database import Base  # 绝对导入
from .enums import BookStatus  # 相对导入

# ✅ 正确：统一使用相对导入
from .database import Base
from .enums import BookStatus
```

## 绝对不要做的事

❌ **不要修改 tests/conftest.py**
❌ **不要在测试中添加 extend_existing=True**
❌ **不要修改测试的导入方式**

## 具体步骤

1. 打开 app/models/database.py，确保Base只定义一次
2. 检查所有模型文件（book.py, reader.py等），确保导入路径一致
3. 检查 app/models/__init__.py，避免循环导入
4. 如果有多个Base实例，删除多余的

## 验证修复

修复后运行测试：
```bash
pytest tests/ -xvs
```

如果还有问题，问题一定在app/目录，不在tests/目录！