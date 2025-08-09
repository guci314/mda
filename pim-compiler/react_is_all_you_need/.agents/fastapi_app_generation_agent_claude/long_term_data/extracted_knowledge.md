# 知识库

## 元知识
- 当文件名不匹配时，使用search_files工具查找相关文件
- 先查看目录结构了解项目布局，再进行具体操作
- 基于现有文档（如PIM）推断系统需求，即使目标文档（PSM）不存在
- 创建项目时遵循标准目录结构，便于维护和理解
- 先创建目录结构，再创建文件，确保路径存在
- 当目标文件不存在时，搜索相关文件（如PSM不存在时查找PIM）
- 从PIM文档可以完整推导出系统的数据模型和业务逻辑需求
- 测试失败时，先启动应用进行手动测试，定位具体错误原因
- 使用有效的测试数据（如符合校验规则的身份证号）避免验证错误
- 通过curl测试API端点可以快速验证应用功能
- 分步骤验证：先测试基础功能，再测试复杂业务逻辑

## 原理与设计
- FastAPI项目采用分层架构：models（数据模型）、schemas（API模式）、services（业务逻辑）、routers（路由）
- 数据库使用SQLAlchemy ORM，支持异步操作
- 业务逻辑与数据访问分离，services层处理业务规则
- 使用Pydantic进行数据验证和序列化
- 遵循RESTful API设计原则
- 配置管理使用环境变量，支持不同环境部署
- 领域驱动设计：基于业务实体（图书、读者、借阅记录、预约记录）构建系统
- 服务层封装复杂业务逻辑，如借阅规则验证、信用分计算、罚金处理
- 工具函数层提供可复用的验证器和计算器
- 测试驱动开发：为每个模块创建对应的测试文件
- 数据验证层：使用严格的验证规则（身份证校验码、ISBN格式等）
- 错误处理：API返回详细的错误信息，便于调试

## 接口与API
- `read_file(path)`: 读取文件内容
- `list_directory(path)`: 列出目录内容
- `search_files(pattern, path)`: 搜索匹配文件
- `create_directory(path)`: 创建目录
- `write_file(path, content)`: 写入文件
- `search_replace(file_path, search_text, replace_text)`: 文本替换
- `execute_command(command)`: 执行系统命令
- SQLAlchemy: `declarative_base()`, `Column`, `Integer`, `String`, `DateTime`, `ForeignKey`, `Enum`, `Text`, `Boolean`
- FastAPI: `APIRouter`, `Depends`, `HTTPException`, `status`, `Query`, `Path`
- Pydantic: `BaseModel`, `Field`, `validator`, `ConfigDict`
- 数据库会话依赖: `get_db()` 函数用于依赖注入
- 异步数据库操作: `AsyncSession`, `select()`, `update()`, `delete()`
- 测试工具: `TestClient`, `pytest.fixture`, `conftest.py`
- 应用启动: `uvicorn library_system.main:app --host 0.0.0.0 --port 8000`
- 测试命令: `pytest tests/` 或 `pytest tests/test_specific.py`
- API测试: `curl --noproxy "*" -X POST -H "Content-Type: application/json" -d '{}' URL`

## 实现细节（需验证）
- 项目根目录结构：`library_system/`（主包）、`tests/`（测试）
- 主包内部：`models/`、`schemas/`、`routers/`、`services/`、`utils/`
- 核心文件：`main.py`（应用入口）、`database.py`（数据库配置）、`config.py`（配置管理）
- 每个子包都需要`__init__.py`文件
- 数据模型文件：`book.py`, `reader.py`, `borrow_record.py`, `reservation_record.py`
- 路由文件：`books.py`, `readers.py`, `borrowing.py`, `query.py`, `reservations.py`
- 服务文件：`book_service.py`, `reader_service.py`, `borrowing_service.py`, `query_service.py`, `reservation_service.py`
- 工具函数：`validators.py`（验证器）、`credit_calculator.py`（信用分计算）、`fine_calculator.py`（罚金计算）、`id_generator.py`、`date_utils.py`
- 配置文件：`.env.example`（环境变量模板）、`requirements.txt`（依赖）
- 测试文件：`conftest.py`（pytest配置）、`test_main.py`、`test_books.py`、`test_readers.py`、`test_borrowing.py`、`test_query.py`、`test_utils.py`
- 数据库表关系：Book-BorrowRecord（一对多）、Reader-BorrowRecord（一对多）、Book-ReservationRecord（一对多）、Reader-ReservationRecord（一对多）
- 身份证验证：使用校验码算法验证18位身份证号的有效性
- 测试数据库：使用SQLite内存数据库进行测试隔离
- API端点：`/`（根端点）、`/health`（健康检查）、`/readers/`（读者管理）、`/books/`（图书管理）

## 用户偏好与项目特点
- 偏好完整的项目结构，包含测试和文档
- 需要生成requirements.txt和环境配置文件
- 基于领域模型（如图书、读者、借阅记录）设计系统
- 重视代码组织和模块化设计
- 包含业务规则验证（如借阅期限、库存检查）
- 支持预约功能和逾期处理
- 需要完整的测试覆盖，包括单元测试和集成测试
- 重视业务逻辑的封装，如信用分系统、罚金计算
- 支持复杂查询功能，如按多条件搜索图书和读者
- 使用枚举类型管理状态（图书状态、读者状态、借阅状态等）
- 包含数据验证和业务规则检查（如借阅数量限制、逾期处理）
- 要求严格的数据验证（身份证校验码、ISBN格式验证等）
- 偏好使用真实有效的测试数据而非虚假数据
- 需要应用能够实际运行并通过API测试验证