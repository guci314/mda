# 知识库

## 元知识
- **ImportError 调试流程**：先确认导入路径 → 检查目标文件是否存在 → 验证类名是否匹配 → 检查包级 `__init__.py` 是否正确导出 → 检查是否存在命名冲突（如两套模型定义）
- **命名一致性检查**：当多个文件互相导入时，类名必须完全一致（包括大小写和后缀），特别注意避免重复后缀（如 `BookDBDB`）
- **目录结构验证**：使用 `list_directory` 和 `search_files` 快速定位文件位置，避免路径假设错误
- **关系映射修复**：修改模型类名后，必须同步更新所有 `relationship()` 中的类名引用
- **测试环境隔离**：测试文件可能位于子目录，需要切换到正确目录运行测试
- **全局搜索替换风险**：批量替换类名时需谨慎，避免过度替换导致重复后缀

## 原理与设计
- **模型命名约定**：项目采用 `*DB` 后缀命名数据库模型类（如 `BookDB`、`ReaderDB`），以区分 Pydantic 模式类
- **分层架构**：`models/` 目录存放 SQLAlchemy 实体，`schemas/` 目录存放 Pydantic 模式，职责分离
- **包导出规范**：每个包的 `__init__.py` 应显式导出公共接口，使用 `__all__` 列表控制
- **架构一致性**：所有层（repository/service/router）必须使用统一的模型命名约定

## 接口与API
- **SQLAlchemy 关系定义**：使用 `relationship("<ClassName>", back_populates="<attribute>")` 建立双向关系
- **包导入语法**：`from .module import Class` 用于相对导入，`from package.module import Class` 用于绝对导入
- **测试配置**：`conftest.py` 中定义测试数据库和客户端，使用内存 SQLite 进行隔离测试
- **find_symbol 工具**：用于快速定位类定义和引用位置

## 实现细节（需验证）
- **模型位置**：`app/models/` 目录下每个模型单独文件（book.py、reader.py 等）
- **数据库连接**：`app/database/connection.py` 定义 `Base` 和 `get_db()`，需通过 `__init__.py` 导出
- **类名映射**：实际模型类名使用 `BookDB`、`ReaderDB`、`BorrowRecordDB`、`ReservationRecordDB`
- **关系引用**：所有外键关系和 back_populates 参数已同步更新为带 DB 后缀的类名
- **服务层导入**：服务文件应从具体模型文件导入（如 `from app.models.book import BookDB`）
- **仓库层导入**：仓库文件同样应从具体模型文件导入（如 `from app.models.reader import ReaderDB`）

## 用户偏好与项目特点
- **严格命名**：要求模型类统一使用 `*DB` 后缀，避免命名冲突
- **测试驱动**：测试文件期望从 `app.models.domain` 导入，但实际模型分散在 `app.models.*` 文件中
- **目录扁平化**：模型文件直接位于 `models/` 下，而非 `models/domain.py`（与测试预期不一致）
- **避免重复**：注意避免在类名替换时产生重复后缀（如 `BookDBDB`）