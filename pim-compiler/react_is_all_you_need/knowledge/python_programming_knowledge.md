# Python 编程知识

## 命名规范

### 文件命名
- **Python文件**: 使用 `snake_case`（小写字母，下划线分隔）
  - 正确: `user_manager.py`, `data_processor.py`
  - 错误: `UserManager.py`, `dataProcessor.py`

### 代码命名
- **类名**: `PascalCase` - `UserManager`, `DataProcessor`
- **函数名**: `snake_case` - `get_user()`, `process_data()`
- **变量名**: `snake_case` - `user_count`, `file_path`
- **常量**: `UPPER_SNAKE_CASE` - `MAX_RETRIES`, `DEFAULT_TIMEOUT`

### 命名转换
- `PascalCase` → `snake_case`: 在大写字母前加下划线并转小写
  - `UserManager` → `user_manager`
  - `HTTPSConnection` → `https_connection`

## 项目结构

### 标准 Python 项目
```
project/
├── src/                # 源代码
│   ├── __init__.py     # 包标识（必需）
│   ├── models/         # 数据模型
│   ├── services/       # 业务逻辑
│   └── utils/          # 工具函数
├── tests/              # 测试文件
│   └── test_*.py       # 测试文件前缀
├── docs/               # 文档
├── requirements.txt    # 依赖列表
├── setup.py           # 安装配置
├── .gitignore         # Git忽略文件
└── README.md          # 项目说明
```

### 重要规则
- 每个目录需要 `__init__.py` 才能作为包导入
- 测试文件以 `test_` 开头或 `_test.py` 结尾
- 配置文件通常放在项目根目录

## 导入规范

### 导入顺序
1. 标准库导入
2. 第三方库导入
3. 本地应用导入

```python
# 标准库
import os
import sys
from pathlib import Path

# 第三方库
import requests
import pandas as pd

# 本地导入
from .models import User
from .utils import calculate_hash
```

### 导入技巧
- 使用绝对导入避免混淆
- 避免使用 `from module import *`
- 合理使用别名简化长模块名

## 文件搜索策略

### 查找类定义
1. 将类名转换为文件名: `ClassName` → `class_name.py`
2. 在 `src/`, `lib/` 或项目根目录搜索
3. 检查 `__init__.py` 中的导出

### 搜索优先级
1. 当前目录
2. `src/` 目录
3. 项目根目录
4. 父目录（如果合理）

### 搜索技巧
- 使用部分匹配（如搜索 "user" 而非完整的 "user_manager"）
- 尝试不同的命名格式
- 使用 `grep -r` 搜索文件内容

## 常见模式

### 单例模式
```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

### 上下文管理器
```python
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    f = open(filename, mode)
    try:
        yield f
    finally:
        f.close()
```

### 装饰器
```python
def retry(max_attempts=3):
    def decorator(func):
        def wrapper(*args, **kwargs):
            for _ in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
            raise last_error
        return wrapper
    return decorator
```

## 最佳实践

### 代码组织
- 函数应该只做一件事
- 类应该有明确的职责
- 模块应该高内聚低耦合

### 错误处理
- 使用具体的异常类型
- 提供有意义的错误信息
- 适当使用 try-except-finally

### 性能考虑
- 使用生成器处理大数据
- 合理使用缓存
- 避免过早优化

### 代码风格
- 遵循 PEP 8 规范
- 使用类型提示增强可读性
- 编写清晰的文档字符串

## 调试技巧

### 常用方法
- `print()` 调试（简单有效）
- `pdb` 调试器（交互式调试）
- `logging` 模块（生产环境）

### 问题定位
1. 确认错误类型和位置
2. 检查输入数据
3. 验证假设条件
4. 简化重现步骤

## 虚拟环境

### 创建和使用
```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 依赖管理
- 使用 `pip freeze > requirements.txt` 导出依赖
- 定期更新依赖版本
- 使用 `pip-tools` 管理复杂依赖