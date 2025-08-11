# 知识库

## 元知识
- **任务前置验证**：在开始修复任务（如“修复测试”）前，首先运行相关命令（如`pytest`）验证问题是否确实存在，避免在已经正常工作的系统上进行不必要的操作。
- **模块属性错误诊断**：当遇到模块的`AttributeError`（例如 `module 'app.services' has no attribute 'category_service'`）时，优先检查该模块的`__init__.py`文件，确认相关的子模块或变量是否已正确导入。这是本项目中一种反复出现的错误模式，适用于`models`, `schemas`, `services`, `crud`等所有包。
- **数据库兼容性诊断**：当遇到数据库编译错误（如`sqlalchemy.exc.CompileError`），特别是关于数据类型的错误，应检查模型定义中是否使用了特定数据库方言的类型（如`postgresql.UUID`），这可能与测试数据库（如SQLite）不兼容。
- **项目结构推断与验证**：当预期文件（如`models/category.py`或`tests/conftest.py`）不存在时，不要立即认定为缺失。应先列出其父目录内容，以核实项目是否采用了不同的组织方式或该文件确实需要被创建。
- **测试文件创建策略**：当测试配置文件（如`conftest.py`）不存在时，根据行业标准实践（如使用fixture进行设置和拆卸）创建它，以建立一个健壮、可维护的测试环境，而不是在每个测试文件中进行单独修补。
- **路由前缀验证**：检查路由注册路径（如`/api/articles`）与测试期望路径的一致性。
- **批量创建模式**：发现多个缺失文件时，一次性创建所有相关文件（路由、模型、模式）。
- **路径重复诊断**：当测试返回404但路由已注册时，检查是否存在双重前缀（router内prefix + include_router prefix）。
- **API路径验证**：使用`curl`或`TestClient`直接访问预期路径，确认实际可用路由列表。
- **测试数据库错误诊断**：
    - `OperationalError: no such table`：表示在测试运行前，数据库表（`Base.metadata.create_all(engine)`）未被创建。应检查测试的设置（setup）逻辑，通常在`conftest.py`的fixture中。
    - `Table '...' is already defined`：表示`Base.metadata.create_all()`在一个测试会话中被多次调用。应确保数据库初始化只发生一次。
    - `IntegrityError: UNIQUE constraint failed`：表示测试之间缺乏隔离，前一个测试的数据污染了后一个测试。应确保每个测试函数都在一个干净的数据库环境中运行（例如，通过`function`作用域的fixture进行创建和销毁）。
- **缓存问题诊断**：当代码修复后测试仍然失败，且错误与已修复的问题相同时，应怀疑是测试运行器的缓存问题。可尝试清除缓存（如`pytest --cache-clear`）后重试。
- **Pydantic响应验证错误诊断**：当测试因`pydantic.ValidationError`失败，且错误信息为`response value is not a valid dict`时，几乎可以肯定是API端点直接返回了一个SQLAlchemy等ORM对象，而不是一个Pydantic可序列化的字典。
- **语法与逻辑错误区分**：当自动语法修复工具（如`fix_python_syntax_errors`）无法解决`NameError`或`IndentationError`时，应怀疑问题出在逻辑结构上，例如不正确的类嵌套，需要手动审查代码结构。

## 原理与设计
- **分层架构要求**：系统采用多层架构，职责分离：models（数据模型）、crud（数据访问）、services（业务逻辑）、schemas（数据验证/DTO）、routers（API接口）。
- **服务层返回协定**：服务层（services）的函数不应返回原始的数据库ORM对象（如SQLAlchemy模型实例）。它们必须返回与API响应模式（schemas）兼容的字典或Pydantic模型，以确保正确的序列化和验证。
- **Schema与Model职责划分**：Pydantic schemas定义API的数据契约，而SQLAlchemy models定义数据库表结构。为避免冲突（如`TypeError: got multiple values for keyword argument`），应在单一层级（通常是数据库模型或服务层）设置默认值（如`status`），而不是在输入schema和数据库模型中同时设置。
- **Python类定义范围**：在定义Pydantic Schema时，相关的类（如`CategoryBase`, `CategoryCreate`, `Category`）应在模块的顶层定义，而不是错误地嵌套在彼此内部。错误的嵌套会导致`NameError`或`IndentationError`。
- **数据库类型可移植性**：为确保代码在不同数据库后端（如生产环境的PostgreSQL和测试环境的SQLite）之间正常工作，模型定义应避免使用特定方言的类型。如果必须使用，应提供一个自定义的`TypeDecorator`以实现跨数据库兼容。
- **Python包模块暴露机制**：一个包（带`__init__.py`的目录）内的子模块（如`article_service.py`）必须在该包的`__init__.py`文件中被显式导入，才能作为包的属性被外部调用（如`app.services.article_service`）。
- **路由模块化设计**：每个资源应有独立的路由文件（articles.py、categories.py、comments.py）。
- **测试驱动开发原则**：测试文件定义了期望的API契约，即使测试文件缺失，也应根据项目结构推断测试需求。
- **统一路由前缀**：API路由应使用统一前缀（如`/api/`）进行版本和作用域隔离。
- **渐进式修复策略**：从解决导入错误开始，逐步构建完整功能，而非一次性实现所有功能。
- **单一前缀原则**：路由前缀应在注册时（include_router）统一设置，避免在router定义中重复设置。
- **测试隔离原则**：单元测试必须相互独立。每个测试函数都应在可预测的、干净的环境中执行。对于数据库测试，这意味着在每个测试运行前后进行表的创建和销毁，以防止数据污染和顺序依赖。
- **Pytest Fixture作用域**：`pytest`的fixture作用域（如`function`, `session`）是管理测试资源生命周期的关键。对于需要每个测试都重置的资源（如数据库状态），应使用`scope="function"`。
- **FastAPI应用生命周期与测试**：FastAPI的`TestClient`在执行测试时，不会自动触发应用级别的`lifespan`事件。因此，在`lifespan`中定义的数据库初始化等逻辑，在测试环境中必须通过测试专用的fixture来显式调用。

## 接口与API
- **测试套件执行**：
    - `pytest`：在项目根目录运行完整的单元测试套件。
    - `pytest --cache-clear`：运行测试前清除缓存，用于解决因缓存导致的修复不生效问题。
- **代码修复工具**：
    - `fix_python_syntax_errors <file_path>`：自动修复指定Python文件中的基本语法错误，如缩进问题。
- **FastAPI路由注册**：
  ```python
  app.include_router(articles.router, prefix="/api/articles", tags=["articles"])
  ```
- **包初始化（`__init__.py`）**：为使包内的模块可被直接访问，需在`__init__.py`中导入。这是项目中的一个常见模式，适用于`models`, `schemas`, `services`, `crud`等层。
  ```python
  # app/services/__init__.py
  from . import article_service
  from . import category_service
  from . import comment_service
  ```
- **ORM对象到字典的转换**：为满足服务层的返回协定，需要将SQLAlchemy模型实例转换为字典。
    - **简单转换**：`model_instance.__dict__`。这是一种快捷方式，但可能包含非预期的内部状态（如`_sa_instance_state`），或在复杂响应模式下缺少字段。
    - **健壮转换**：手动构建字典。当响应模式与模型字段不完全匹配时，这是更可靠的方法。
      ```python
      # In a service file
      return {
          "id": db_comment.id,
          "content": db_comment.content,
          "created_at": db_comment.created_at,
          "status": db_comment.status,
          "article_id": db_comment.article_id,
          "author_id": db_comment.author_id,
      }
      ```
- **自定义SQLAlchemy类型（兼容UUID）**：为解决SQLite不支持UUID的问题，可使用`TypeDecorator`。
- **测试数据库配置**：
  ```python
  # app/database.py
  SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
  engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
  TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
  ```
- **pytest fixture模式（带隔离）**：在`tests/conftest.py`中定义，确保每个测试函数都有独立的数据库环境。
- **路由路径检查**：使用`TestClient(app).get("/openapi.json")`获取实际注册的所有路由路径。

## 实现细节（需验证）
- **项目文件结构**（更正：增加了`crud`层，模型被合并到`blog.py`，增加了`conftest.py`）：
  ```
  blog/
  ├── app/
  │   ├── __init__.py
  │   ├── main.py
  │   ├── database.py
  │   ├── crud/
  │   ├── models/
  │   │   ├── blog.py      # 包含Article, Category, Comment等所有模型
  │   ├── schemas/
  │   │   ├── blog.py      # 包含所有schema
  │   ├── routers/
  │   └── services/
  └── tests/
      ├── conftest.py      # 存放pytest fixtures
      └── ...
  ```
- **模型定义位置**：所有核心数据模型（Article, Category, Comment）均定义在`app/models/blog.py`文件中。
- **Schema定义位置与结构**：所有Pydantic Schema定义在`app/schemas/blog.py`中。所有类定义必须在模块的顶层，不能相互嵌套。
- **服务层实现**：`app/services/`中的服务类方法必须返回字典，而不是原始的ORM对象，以兼容FastAPI的响应模型。
- **包模块初始化**：`models`, `schemas`, `services`, `crud` 等目录下的 `__init__.py` 文件必须显式导入其子模块，否则会导致 `AttributeError`。
- **测试数据库管理**：测试数据库的创建（`create_all`）和销毁（`drop_all`）由`tests/conftest.py`中的`function`-scoped fixture管理，以确保测试隔离。
- **路由前缀设置位置**：应在`main.py`的`include_router`中设置prefix，**不应**在router文件中设置prefix。

## 用户偏好与项目特点
- **分层架构**：项目采用清晰的分层架构（models, crud, services, schemas, routers），而非传统MVC。职责分离明确。
- **服务层返回约定**：服务层必须将ORM对象转换为字典或Pydantic模型后才能返回给路由层，这是确保API响应正确验证和序列化的关键。
- **API前缀约定**：所有API路由使用`/api/`前缀。
- **测试隔离**：项目通过`conftest.py`中的`function`-scoped fixture强制实现测试隔离，每个测试使用独立的、干净的数据库。