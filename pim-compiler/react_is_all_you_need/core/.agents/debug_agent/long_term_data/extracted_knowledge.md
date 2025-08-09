# 知识库

## 元知识
- **ImportError 调试流程**：先确认导入路径 → 检查目标文件是否存在 → 验证类名是否匹配 → 检查包级 `__init__.py` 是否正确导出 → 检查是否存在命名冲突（如两套模型定义）
- **命名一致性检查**：当多个文件互相导入时，类名必须完全一致（包括大小写和后缀），特别注意避免重复后缀（如 `BookDBDB`）
- **目录结构验证**：使用 `list_directory` 和 `search_files` 快速定位文件位置，避免路径假设错误
- **关系映射修复**：修改模型类名后，必须同步更新所有 `relationship()` 中的类名引用
- **测试环境隔离**：测试文件可能位于子目录，需要切换到正确目录运行测试
- **全局搜索替换风险**：批量替换类名时需谨慎，避免过度替换导致重复后缀
- **异步测试调试流程**：遇到 `'async_generator' object has no attribute 'post'` 错误时，检查 fixture 是否正确使用 `async with` 语法和 `yield` 返回客户端实例
- **pytest fixture 验证**：使用 `pytest --fixtures` 查看 fixture 定义，确认返回类型和作用域
- **任务执行坚持原则**：用户要求完成整个调试流程时，必须实际执行修复操作，不能只停留在初始化或准备阶段
- **pytest 异步错误诊断**：当出现 `async_generator` 错误时，按顺序检查：pytest.ini 配置 → conftest.py 的 fixture 定义 → pytest-asyncio 装饰器 → AsyncClient 实例化语法
- **调试状态管理**：使用调试笔记跟踪修复进度，记录每次尝试的结果和下一步计划
- **pytest 配置优先级**：pytest.ini 文件的 `asyncio_mode = auto` 配置是解决异步 fixture 问题的关键，优先检查此配置
- **测试错误分类**：区分配置错误（如 async_generator 问题）和业务逻辑错误（如 400 vs 200 状态码），采用不同修复策略
- **渐进式调试**：先修复基础配置问题（如 pytest 异步支持），再处理具体业务逻辑错误，避免被表面错误掩盖根本问题

## 原理与设计
- **模型命名约定**：项目采用 `*DB` 后缀命名数据库模型类（如 `BookDB`、`ReaderDB`），以区分 Pydantic 模式类
- **分层架构**：`models/` 目录存放 SQLAlchemy 实体，`schemas/` 目录存放 Pydantic 模式，职责分离
- **包导出规范**：每个包的 `__init__.py` 应显式导出公共接口，使用 `__all__` 列表控制
- **架构一致性**：所有层（repository/service/router）必须使用统一的模型命名约定
- **异步测试设计**：测试 fixture 应使用异步上下文管理器确保资源正确创建和清理
- **测试隔离原则**：每个测试应使用独立的数据库实例，避免测试间相互影响
- **pytest 异步模式**：现代 pytest-asyncio 推荐使用 `asyncio_mode = auto` 配置，自动处理异步测试和 fixture
- **测试配置分离**：pytest.ini 控制测试运行行为，conftest.py 定义测试 fixture，两者配合实现完整的测试环境

## 接口与API
- **SQLAlchemy 关系定义**：使用 `relationship("<ClassName>", back_populates="<attribute>")` 建立双向关系
- **包导入语法**：`from .module import Class` 用于相对导入，`from package.module import Class` 用于绝对导入
- **测试配置**：`conftest.py` 中定义测试数据库和客户端，使用内存 SQLite 进行隔离测试
- **find_symbol 工具**：用于快速定位类定义和引用位置
- **异步客户端 fixture**：正确语法为 `async with AsyncClient(...) as ac: yield ac`，确保返回 AsyncClient 实例而非生成器
- **pytest 异步支持**：需要 `pytest-asyncio` 插件，fixture 使用 `@pytest_asyncio.fixture` 装饰器
- **fix_python_syntax_errors 工具**：专门用于修复 Python 语法错误，会自动重写整个文件避免逐行修复问题
- **pytest 运行**：使用 `pytest` 命令运行测试，可添加 `-v` 参数查看详细输出
- **AsyncClient 配置**：需要传入 `app` 参数和 `base_url` 参数，通常使用 `http://test` 作为测试基础URL
- **pytest.ini 配置**：使用 `asyncio_mode = auto` 启用自动异步模式，避免手动标记每个异步测试
- **调试笔记工具**：使用 `create_file` 创建调试日志文件，跟踪修复进度和问题状态
- **pytest.ini 关键配置**：`[tool:pytest]` 或 `[pytest]` 段落，`asyncio_mode = auto` 是解决异步测试问题的核心配置
- **pytest 输出分析**：测试结果显示格式为 `X passed, Y failed`，通过对比前后结果判断修复效果

## 实现细节（需验证）
- **模型位置**：`app/models/` 目录下每个模型单独文件（book.py、reader.py 等）
- **数据库连接**：`app/database/connection.py` 定义 `Base` 和 `get_db()`，需通过 `__init__.py` 导出
- **类名映射**：实际模型类名使用 `BookDB`、`ReaderDB`、`BorrowRecordDB`、`ReservationRecordDB`
- **关系引用**：所有外键关系和 back_populates 参数已同步更新为带 DB 后缀的类名
- **服务层导入**：服务文件应从具体模型文件导入（如 `from app.models.book import BookDB`）
- **仓库层导入**：仓库文件同样应从具体模型文件导入（如 `from app.models.reader import ReaderDB`）
- **测试配置文件**：`tests/conftest.py` 包含数据库和客户端 fixture，client fixture 应返回 AsyncClient 实例
- **测试文件结构**：测试文件位于 `tests/` 目录，包含多个测试模块（如 `test_books.py`）
- **FastAPI 应用入口**：通常在 `app/main.py` 或类似位置定义 FastAPI 应用实例
- **pytest 配置文件**：项目根目录的 `pytest.ini` 文件控制测试行为，必须包含 `asyncio_mode = auto` 配置
- **测试规模**：项目包含94个测试，分布在多个测试文件中
- **API 端点结构**：包含 `/borrows/process/overdue` 等业务端点，可能存在参数验证或业务逻辑错误

## 用户偏好与项目特点
- **严格命名**：要求模型类统一使用 `*DB` 后缀，避免命名冲突
- **测试驱动**：测试文件期望从 `app.models.domain` 导入，但实际模型分散在 `app.models.*` 文件中
- **目录扁平化**：模型文件直接位于 `models/` 下，而非 `models/domain.py`（与测试预期不一致）
- **避免重复**：注意避免在类名替换时产生重复后缀（如 `BookDBDB`）
- **完整调试要求**：用户要求完成整个调试流程，不接受只初始化就返回的行为，必须实际执行修复操作
- **异步测试环境**：项目使用 FastAPI + pytest-asyncio 进行异步测试
- **测试覆盖率要求**：项目包含大量测试（94个测试），要求全部通过
- **立即执行偏好**：用户强调立即开始修复，不要停留在准备阶段
- **零容忍错误**：用户要求所有测试必须100%通过，不接受部分修复
- **调试透明度**：用户希望看到完整的修复过程，包括每个步骤的执行结果
- **配置优先原则**：用户认识到基础配置问题（如 pytest 异步支持）必须优先解决，再处理业务逻辑错误
- **渐进式修复接受度**：用户接受分步骤修复，先解决配置问题（如从0个测试通过到34个），再处理剩余的业务逻辑错误