# 知识库

## 元知识
- **PSM到代码的映射方法**：先读取PSM文件→提取领域模型→按MVC/分层架构组织→先生成基础结构→再填充业务逻辑
- **FastAPI项目结构验证**：通过`uvicorn main:app --reload`快速验证主应用文件是否正确
- **枚举类设计模式**：使用`str, Enum`组合确保数据库兼容性和API文档可读性
- **Pydantic模型分层**：区分`BaseModel`(请求/响应)和数据库模型(SQLAlchemy)，避免循环引用

## 原理与设计
- **分层架构**：清晰的repository-service-router三层分离，repository处理数据访问，service封装业务逻辑，router处理HTTP层
- **依赖注入模式**：使用FastAPI的`Depends`实现数据库会话、服务层的依赖注入
- **DTO模式**：请求/响应模型与数据库模型分离，避免直接暴露内部数据结构
- **软删除设计**：通过状态字段(如`BookStatus.REMOVED`)而非物理删除，保持数据完整性
- **事务边界**：在service层控制事务，确保业务操作的原子性

## 接口与API
- **FastAPI标准模式**：
  - 主应用：`FastAPI(title, description, version)` + `include_router`
  - 路由：`APIRouter(prefix, tags, responses)` + 标准CRUD端点
  - 响应模型：`response_model=List[BookResponse]`确保类型安全
- **SQLAlchemy配置**：
  - 异步引擎：`create_async_engine(DATABASE_URL, echo=True)`
  - 会话：`async_sessionmaker(engine, expire_on_commit=False)`
- **Alembic迁移**：标准初始化`alembic init alembic` + 配置`alembic.ini`
- **测试工具**：`pytest-asyncio` + `AsyncClient` + `TestClient`组合测试

## 实现细节（需验证）
- **项目结构**：
  ```
  mda_dual_agent_demo/
  ├── main.py                 # FastAPI应用入口
  ├── app/
  │   ├── __init__.py
  │   ├── database/
  │   │   ├── __init__.py
  │   │   └── connection.py   # 数据库连接配置
  │   ├── models/
  │   │   ├── __init__.py
  │   │   ├── enums.py        # 所有枚举定义
  │   │   └── database.py     # SQLAlchemy模型
  │   ├── routers/
  │   │   ├── __init__.py
  │   │   ├── books.py        # 图书相关路由
  │   │   ├── readers.py      # 读者相关路由
  │   │   └── borrows.py      # 借阅相关路由
  │   ├── services/
  │   │   ├── __init__.py
  │   │   ├── book_service.py
  │   │   ├── reader_service.py
  │   │   └── borrow_service.py
  │   └── repositories/
  │       ├── __init__.py
  │       ├── book_repository.py
  │       ├── reader_repository.py
  │       └── borrow_repository.py
  └── tests/
      ├── __init__.py
      ├── conftest.py         # pytest配置
      └── test_*.py           # 各模块测试
  ```
- **关键配置**：
  - 数据库URL格式：`postgresql+asyncpg://user:pass@localhost/dbname`
  - CORS配置：`app.add_middleware(CORSMiddleware, allow_origins=["*"])`
- **启动命令**：`uvicorn main:app --reload --host 0.0.0.0 --port 8000`

## 用户偏好与项目特点
- **输出目录**：固定使用`/home/guci/aiProjects/mda/output/`作为根目录
- **PSM文件位置**：通常位于`.../react_is_all_you_need/output/`目录下
- **命名约定**：使用下划线命名法，文件名反映功能（如`book_service.py`）
- **测试覆盖**：每个路由模块对应一个测试文件，保持1:1映射