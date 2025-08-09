# 知识库

## 元知识
- **PSM到代码的映射方法**：先读取PSM文件→提取领域模型→按MVC/分层架构组织→先生成基础结构→再填充业务逻辑
- **FastAPI项目结构验证**：通过`uvicorn main:app --reload`快速验证主应用文件是否正确。
- **常见启动错误排查**：如遇`Address already in use`错误，表明端口被占用，可尝试更换端口（如`--port 8001`）再启动。
- **枚举类设计模式**：使用`str, Enum`组合确保数据库兼容性和API文档可读性
- **Pydantic模型分层**：区分`BaseModel`(请求/响应)和数据库模型(SQLAlchemy)，避免循环引用
- **模型映射策略**：数据库模型继承`SQLAlchemy`的`Base`，请求/响应模型使用`BaseModel`，通过`from_orm`/`dict()`转换
- **异步上下文管理**：使用`async with`确保数据库会话正确关闭，避免连接泄漏
- **完整项目生成流程**：目录结构→依赖文件→枚举→数据模型→DTO模型→数据库连接→仓储层→服务层→路由层→主应用→测试→配置文件
- **项目验证方法**：通过文件计数和Python语法检查验证生成完整性
- **导入问题排查**：相对导入vs绝对导入，检查`__init__.py`文件，验证模块路径
- **测试环境隔离**：使用内存SQLite数据库(`sqlite+aiosqlite:///:memory:`)进行测试，避免影响开发数据库
- **环境变量优先级**：`.env`文件 > 环境变量 > 默认值，注意`.env.example`仅为模板
- **数据库连接调试**：检查DATABASE_URL环境变量，确认数据库类型和连接参数
- **pytest异步配置方法**：使用`pytest.ini`或`pyproject.toml`配置`asyncio_mode = auto`，避免每个测试函数都需要`@pytest.mark.asyncio`装饰器
- **测试fixture依赖管理**：通过`app.dependency_overrides`在测试中替换数据库连接，实现测试隔离
- **项目完整性验证策略**：先运行简单测试验证基础功能，再逐步验证复杂功能，避免一次性运行所有测试导致的错误定位困难

## 原理与设计
- **分层架构**：清晰的repository-service-router三层分离，repository处理数据访问，service封装业务逻辑，router处理HTTP层
- **依赖注入模式**：使用FastAPI的`Depends`实现数据库会话、服务层的依赖注入
- **DTO模式**：请求/响应模型(DTO)与数据库模型分离，避免直接暴露内部数据结构。DTOs集中管理在`models/pydantic.py`中。
- **软删除设计**：通过状态字段(如`BookStatus.REMOVED`)而非物理删除，保持数据完整性
- **事务边界**：在service层控制事务，确保业务操作的原子性
- **RESTful设计**：使用标准HTTP方法(GET/POST/PUT/DELETE)对应CRUD操作，路径设计为复数资源名
- **错误处理**：在service层统一处理业务异常，router层转换为合适的HTTP状态码
- **业务逻辑封装**：复杂业务操作（如借书、还书、预约）在service层实现，包含业务规则验证
- **关联关系处理**：使用SQLAlchemy的`relationship`和`back_populates`建立双向关联
- **异步架构设计**：全栈异步，从数据库连接到API端点，使用`async/await`模式
- **测试依赖覆盖**：通过`app.dependency_overrides`在测试中替换数据库连接，实现测试隔离
- **渐进式测试策略**：先验证基础功能（如应用启动、简单API），再测试复杂业务逻辑，便于问题定位

## 接口与API
- **FastAPI标准模式**：
  - 主应用：`FastAPI(title, description, version)` + `include_router`
  - 路由：`APIRouter(prefix, tags, responses)` + 标准CRUD端点
  - 响应模型：`response_model=List[BookResponse]`确保类型安全
- **SQLAlchemy异步配置**：
  - 异步引擎：`create_async_engine(DATABASE_URL, echo=True)`
  - 会话：`async_sessionmaker(engine, expire_on_commit=False)`
  - 会话管理：`async with async_session() as session:`
- **Alembic迁移**：标准初始化`alembic init alembic` + 配置`alembic.ini`
- **测试工具**：`pytest-asyncio` + `AsyncClient` + `TestClient`组合测试
- **CORS配置**：`app.add_middleware(CORSMiddleware, allow_origins=["*"])`
- **数据库URL格式**：
  - PostgreSQL: `postgresql+asyncpg://user:pass@localhost/dbname`
  - SQLite: `sqlite+aiosqlite:///./database.db`
  - 内存SQLite: `sqlite+aiosqlite:///:memory:`
- **项目依赖管理**：生成`requirements.txt`文件，包含`fastapi`, `uvicorn`, `sqlalchemy[asyncio]`, `asyncpg`, `pydantic`等核心依赖。
- **Docker支持**：标准Dockerfile + docker-compose.yml配置，包含PostgreSQL服务
- **环境配置**：使用`.env.example`模板，支持数据库URL等环境变量配置
- **应用生命周期**：使用`@asynccontextmanager`和`lifespan`参数管理启动/关闭逻辑
- **pytest配置**：
  - 异步测试：`@pytest.mark.asyncio`或配置`asyncio_mode = auto`
  - 测试客户端：`AsyncClient(app=app, base_url="http://test")`
  - 数据库fixture：`@pytest.fixture(scope="function")`
- **pytest配置文件格式**：
  - `pytest.ini`: `[tool:pytest]` + `asyncio_mode = auto`
  - `pyproject.toml`: `[tool.pytest.ini_options]` + `asyncio_mode = "auto"`
- **项目验证脚本**：创建`verify_project.py`脚本，检查文件存在性、模块导入、基础功能

## 实现细节（需验证）
- **项目结构**：
  ```
  mda_dual_agent_demo/
  ├── main.py                 # FastAPI应用入口
  ├── requirements.txt        # 项目依赖
  ├── .env.example           # 环境变量模板
  ├── Dockerfile             # Docker构建文件
  ├── docker-compose.yml     # Docker编排文件
  ├── README.md              # 项目说明
  ├── PROJECT_SUMMARY.md     # 项目总结文档
  ├── run.py                 # 启动脚本
  ├── start_server.py        # 服务器启动脚本
  ├── test.py                # 测试脚本
  ├── check.py               # 项目检查脚本
  ├── verify_project.py      # 项目验证脚本
  ├── pytest.ini            # pytest配置文件
  ├── pyproject.toml         # 项目配置文件
  ├── app/
  │   ├── __init__.py
  │   ├── database.py         # 异步数据库连接配置
  │   ├── dependencies.py     # 依赖注入配置
  │   ├── enums.py           # 枚举定义（可能在models目录下）
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── enums.py        # 所有枚举定义
  │   │   ├── database.py     # SQLAlchemy ORM模型
  │   │   ├── pydantic.py     # Pydantic DTO模型
  │   │   ├── book.py         # 图书模型
  │   │   ├── reader.py       # 读者模型
  │   │   ├── borrow_record.py # 借阅记录模型
  │   │   └── reservation_record.py # 预约记录模型
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   ├── books.py
  │   │   ├── readers.py
  │   │   ├── borrows.py
  │   │   ├── borrowing.py
  │   │   ├── borrowings.py
  │   │   ├── reservation.py
  │   │   └── reservations.py
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── book_service.py
  │   │   ├── reader_service.py
  │   │   ├── borrow_service.py
  │   │   ├── borrowing_service.py
  │   │   └── reservation_service.py
  │   └── repositories/
  │       ├── __init__.py
  │       ├── book_repository.py
  │       ├── reader_repository.py
  │       ├── borrow_repository.py
  │       ├── borrow_record_repository.py
  │       ├── reservation_repository.py
  │       └── reservation_record_repository.py
  └── tests/
      ├── __init__.py
      ├── conftest.py         # pytest配置
      ├── test_main.py        # 主应用测试
      ├── test_simple.py      # 简单功能测试
      ├── test_books.py
      ├── test_readers.py
      ├── test_borrows.py
      └── test_reservations.py
  ```
- **启动命令**：`uvicorn main:app --reload --host 0.0.0.0 --port 8000` (如端口占用可更换)
- **数据库配置模式**：
  - 主配置：`app/database.py`包含异步引擎和会话工厂
  - 依赖注入：`app/dependencies.py`提供服务层依赖
  - 测试配置：`tests/conftest.py`覆盖数据库依赖
- **服务层模式**：每个服务类包含核心业务逻辑，调用repository进行数据操作。
- **测试文件模式**：每个路由模块对应一个测试文件，保持1:1映射。
- **业务操作实现**：借书操作包含库存检查、读者状态验证、借阅记录创建等多步骤事务
- **数据库关系映射**：Book-BorrowRecord(一对多)、Reader-BorrowRecord(一对多)、Book-Reservation(一对多)等关系通过SQLAlchemy relationship定义
- **导入路径模式**：
  - 绝对导入：`from app.database import get_async_db`
  - 服务层导入：`from app.services.book_service import BookService`
  - 模型导入：`from app.models.database import Base`
- **测试fixture模式**：
  - 数据库会话：`@pytest.fixture(scope="function")`确保每个测试独立
  - 测试客户端：使用`AsyncClient`进行API测试
  - 依赖覆盖：`app.dependency_overrides[get_async_db] = override_get_async_db`

## 用户偏好与项目特点
- **输出目录**：项目代码生成在`/home/guci/aiProjects/mda/output/<project_name>/`目录下。
- **PSM文件位置**：通常位于`.../react_is_all_you_need/output/<project_name>/`目录下。
- **命名约定**：使用下划线命名法(snake_case)。
- **标准交付物**：除了完整的FastAPI应用代码结构，还应包含一个`requirements.txt`文件。
- **完整性要求**：生成完整可运行的项目，包括Docker支持、环境配置、详细README文档
- **测试覆盖**：为所有API端点生成对应的pytest测试用例，确保代码质量
- **辅助脚本偏好**：提供`run.py`启动脚本、`test.py`测试脚本、`check.py`项目检查脚本、`verify_project.py`验证脚本、`start_server.py`服务器启动脚本
- **数据库默认配置**：优先使用SQLite作为默认数据库，避免外部依赖
- **环境变量管理**：提供`.env.example`模板，但不创建实际`.env`文件，使用代码中的默认值
- **项目文档偏好**：生成`PROJECT_SUMMARY.md`详细项目说明文档，包含快速开始指南
- **配置文件偏好**：同时提供`pytest.ini`和`pyproject.toml`配置，确保测试环境兼容性
- **验证策略**：先运行简单测试验证基础功能，再进行完整测试，分步骤验证项目完整性