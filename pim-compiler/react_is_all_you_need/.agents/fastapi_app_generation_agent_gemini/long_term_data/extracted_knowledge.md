# 知识库

## 元知识
- **PSM/PIM解析流程**：从PSM/PIM文档中提取数据模型（SQLAlchemy & Pydantic）、业务逻辑（Service层）、API接口（Router层）是生成代码的关键步骤。应优先遵循PSM文档中指定的具体文件路径（如`src/models/enums.py`）来决定生成结构。
- **模块化生成**：将大型应用拆分为独立的模块（如models, schemas, services, routers, repositories）进行生成，有助于管理复杂性和提高生成效率。
- **依赖关系处理**：在生成代码时，需要考虑模块间的依赖关系，例如数据库配置和会话管理模块应先于模型文件生成，`__init__.py`文件应在所有子模块生成后更新以确保导入。
- **逐步构建**：按照“基础配置 -> 数据模型 -> Pydantic模型 -> 数据仓库 -> 业务逻辑 -> API路由 -> 主应用 -> 依赖文件 -> 辅助文件 -> 测试文件”的顺序生成，是一种稳健的构建流程。
- **交互式任务分解**：当面对一个宏大、模糊的请求（如“生成完整应用”）时，系统可能无法一次性处理。有效的策略是将其分解为一系列更小、更具体的子任务（如“创建目录结构”、“生成模型文件”、“创建测试文件”），并逐步引导Agent完成。Agent的“需要更多步骤”等回应是任务需要分解的明确信号。
- **从使用中推断（Inference from Usage）**：当PSM/PIM等规范文档未明确定义某个组件（如Repository层）的具体实现时，可以根据其在其他代码（如Service层或Router层）中的调用方式来推断其应有的接口和方法。
- **文件存在性检查与纠正**：在读取或写入文件前，应先验证文件路径和名称的正确性，必要时通过列出目录内容 (`list_directory`) 进行确认和纠正。例如，当尝试访问`src/requirements.txt`失败时，应列出根目录以查找其真实位置。
- **生成后验证**：在完成文件和目录生成后，应使用`list_directory`等工具系统性地检查所有预期的文件和目录是否已正确创建，以确保任务的完整性。
- **Python模块导入问题排查法**：
    - **`__init__.py`的重要性**：`AttributeError`或`ModuleNotFoundError`通常与Python的模块系统有关。确保每个模块目录（如`app/models`, `app/schemas`）都包含一个`__init__.py`文件，以将其声明为可导入的包。
    - **`NameError`排查**：`NameError`通常由拼写错误或忘记导入引起。在生成代码后，应系统性地检查每个文件，确保所有使用的类和函数（如`pytest`，FastAPI的`Depends`）都已正确导入。
    - **绝对导入与相对导入**：在扁平的应用结构（如`app/models`, `app/schemas`）中，模块间的相互导入应使用从项目根目录开始的绝对路径（例如，在`app/schemas/schemas.py`中应使用`from app.models.models import ...`而非`from ..models.models import ...`），以避免在不同执行上下文（如`pytest` vs `uvicorn`）中出现路径问题。
- **单文件合并调试法**：当在模块化应用中遇到难以解决的`ImportError`、配置加载或循环依赖问题时，可采取以下步骤：1) 将所有代码（模型、服务、路由、主应用）合并到一个文件中。2) 验证单文件应用是否能正常工作（或通过测试）。3) 如果成功，问题就锁定在模块结构和导入语句上。4) 以此可工作的单文件为基准，逐步、正确地将其拆分回模块化结构，并在每一步后进行验证。
- **依赖版本冲突排查法**：
    - **Pydantic版本兼容性**：当遇到与`pydantic`相关的`ImportError`或依赖冲突时，首先检查`requirements.txt`。FastAPI的旧版本通常与Pydantic v1兼容，而新版本与v2兼容。一个常见的解决方法是在`requirements.txt`中明确固定Pydantic版本（如`pydantic==1.10.12`）。
    - **次级依赖冲突**：注意次级依赖（如`pydantic-settings`）可能强制要求不兼容的主依赖版本（如`pydantic` v2+）。解决方法包括：1) 寻找次级依赖的兼容版本。2) 如果找不到，考虑移除该次级依赖，并直接在代码中实现其功能（例如，在`config.py`中硬编码配置），以解除版本锁定。**Pydantic v2中，`BaseSettings`已移至`pydantic-settings`包，需在`requirements.txt`中添加该依赖并更新代码中的`import`语句。**
- **测试环境问题排查法**：
    - **配置优先于代码**：当测试框架出现`ScopeMismatch`等行为异常时，首先检查其配置文件（如`pytest.ini`）。**对于`pytest-asyncio`，在`pytest.ini`中设置`asyncio_mode = auto`是解决此类问题的关键步骤。**若配置项无效，再检查测试框架插件（如`pytest-asyncio`）的版本是否过时或 fixture 的作用域（scope）是否冲突。
    - **隔离外部依赖**：测试用例应尽可能独立于外部服务（如数据库）。当遇到`ConnectionRefusedError`或`socket.gaierror`时，应优先考虑使用内存数据库（如SQLite）替代真实的数据库，以实现快速、可靠的测试。
    - **确保测试状态纯净**：对于使用文件数据库（如`sqlite:///./test.db`）的测试，应在每次测试运行前确保旧的数据库文件被删除，以防止因旧数据导致`UNIQUE constraint failed`等状态相关错误。
    - **隔离与简化**：当测试套件出现不明原因的失败（如无法收集测试、无有效报错信息）时，应创建并运行一个极简的测试文件（如`tests/simple_test.py`，内容仅为`def test_simple(): assert 1 == 1`），以验证测试框架和环境本身是否正常。
    - **目标明确化**：如果测试套件整体运行失败，尝试用`pytest path/to/specific_test.py`命令单独运行某个文件，以获取更精确的错误信息。
    - **结构性排查**：如果`tests/`根目录下的测试能正常运行，而子目录（如`tests/api/`）下的测试失败，问题可能出在子目录的`__init__.py`文件或Python路径解析上。可尝试将失败的测试文件移动到根测试目录进行诊断。当`pytest.ini`中的`testpaths`和`addopts`等配置冲突时，可能导致`Plugin already registered`错误，应移除冗余配置。
- **Web服务静默失败排查法**：当Web服务（如Uvicorn）启动无报错但无法响应请求时，应采用系统化排查：
    1.  **进程检查**：使用 `ps aux | grep uvicorn` 确认服务进程正在运行。
    2.  **端口监听检查**：使用 `netstat -tuln | grep <port>` 确认端口已绑定并处于监听状态。
    3.  **客户端测试**：使用 `curl` 或 `httpx` 尝试访问根路径 (`/`)、文档路径 (`/docs`) 和具体API端点。
    4.  **日志审查**：尝试在前台启动服务以直接查看实时日志输出。
    5.  **代码审查**：仔细检查应用入口文件（如 `main.py`）是否存在不引发启动崩溃但破坏请求处理逻辑的微妙错误，例如函数重复定义、装饰器使用不当等。
- **级联导入失败排查法**：当测试框架（如`pytest`）和应用服务器（如`uvicorn`）都因`ImportError`或类似错误而启动失败时，问题根源通常在被导入的应用核心代码中，而非测试代码本身。
    1.  **优先分析应用启动日志**：`uvicorn`的启动回溯信息（如数据库连接错误`socket.gaierror`）通常比`pytest`的测试集收集错误信息更直接地指向问题源头。
    2.  **隔离排查**：如果日志不清晰，可尝试在Python REPL中或通过命令行 (`python -c "import <module>"`) 逐个导入`main.py`中的模块，以定位导致失败的具体`import`语句。

## 原理与设计
- **FastAPI应用结构**：一个典型的FastAPI应用可以遵循多种结构模式，其中`src`布局是推荐用于复杂应用的稳健模式。
    - **扁平结构 (`app/`)**：`app/main.py`, `app/models/`, `app/schemas/`等。结构简单，但当项目变大时，模块间的绝对导入路径（如`from app.services...`）管理可能变得复杂，容易出错。
    - **嵌套结构 (`src/`)**：更清晰的隔离，推荐用于较复杂的应用。
        - `src/main.py`：应用入口，使用`lifespan`上下文管理器处理启动和关闭事件（如初始化数据库）。
        - `src/api/`：API层，包含路由（`routers/`）和共享依赖项（`deps.py`）。
        - `src/core/`：核心配置（`config.py`）。
        - `src/db/`：数据库连接（`session.py`）和模型基类（`base.py`）。`session.py`是定义`engine`, `SessionLocal`和`get_db`依赖函数的正确位置。
        - `src/models/`：SQLAlchemy ORM模型定义。
        - `src/schemas/`：Pydantic数据验证和序列化模型。
        - `src/services/`：业务逻辑层。
        - `src/repositories/`：数据访问层，封装数据库操作。
        - `tests/`：测试文件，与`src`目录平行。
- **分层架构**：采用**模型-仓库-服务-路由 (Model-Repository-Service-Router)** 架构有助于代码的组织、可维护性和可测试性。Repository层专门负责与数据库的交互，Service层调用Repository层并实现业务逻辑。
- **PSM/PIM到代码的映射**：PSM/PIM中的“数据模型”直接映射到SQLAlchemy模型和Pydantic Schema；“业务逻辑”映射到Service层；“数据访问”映射到Repository层；“API端点”映射到Router层。PSM中指定的文件路径应被优先遵循，并作为决定项目结构（如`src`布局）的关键依据。
- **数据库无关性设计**：为确保代码在不同数据库（如生产用PostgreSQL，测试用SQLite）间的可移植性，应处理方言特定的数据类型。例如，通过SQLAlchemy的`TypeDecorator`为`UUID`等类型创建自定义实现，使其在不支持原生UUID的SQLite中能以字符串形式存储。
- **配置与状态的延迟初始化**：依赖于外部配置（如环境变量）的全局状态对象（如SQLAlchemy的`engine`），不应在模块加载时立即初始化。这会妨碍测试时对其进行覆盖。正确的做法是将其初始化推迟到应用生命周期事件中（如FastAPI的`lifespan`管理器），确保配置加载完毕后再创建对象。**硬编码配置（如数据库URL）是常见的错误源，会导致`socket.gaierror`等启动失败。**
- **Pydantic版本兼容性**：Pydantic v1和v2之间存在重大API变更。例如，v1使用`.dict()`方法序列化模型，而v2使用`.model_dump()`。v2还将`BaseSettings`移至独立的`pydantic-settings`包。在开发和代码生成时，必须确保所写的代码与环境中安装的Pydantic版本一致。
- **FastAPI静默失败模式**：FastAPI应用可能因入口文件（`main.py`）中存在不显眼的Python语法错误（如函数重复定义）而进入一种“静默失败”状态。在此状态下，Uvicorn服务能正常启动并监听端口，但无法处理任何传入的HTTP请求，通常客户端会超时。
- **测试环境隔离**：为保证测试的独立性和可重复性，测试环境应与开发/生产环境完全隔离。这包括使用独立的配置（如内存数据库代替生产数据库），并通过依赖注入在测试启动时覆盖应用的原有依赖（如`get_db`）。`conftest.py`是实现这种隔离的核心。**`pytest`的`client` fixture必须正确使用`async with`和`yield`来提供`httpx.AsyncClient`实例，否则会导致`AttributeError: 'async_generator' object has no attribute 'post'`或`RuntimeError: Cannot send a request, as the client has been closed.`。**

## 接口与API
- **文件操作工具**：
    - `read_file(filepath)`：读取指定路径文件内容。
    - `create_directory(dirpath)`：创建指定路径的目录。
    - `write_file(filepath, content)`：向指定路径文件写入内容。
    - `list_directory()`: 列出当前目录下的文件和文件夹。
    - `search_replace(filepath, search_pattern, replace_pattern)`: 在文件中查找并替换内容。
- **系统与进程工具**：
    - `execute_command("ps aux | grep <process>")`: 检查进程是否存在。
    - `execute_command("netstat -tuln | grep <port>")`: 检查端口监听状态。
    - `execute_command("kill <pid>")`: 终止指定进程。
    - `execute_command("rm <file>")`: 删除文件，可用于在测试前清理状态或解决文件损坏问题。
    - `execute_command("mv <source> <destination>")`: 移动文件，可用于在调试时改变测试文件结构。
- **FastAPI/SQLAlchemy相关概念**：
    - SQLAlchemy `Base`：用于声明性模型的基础类。
    - SQLAlchemy `engine`：连接池和数据库方言的接口，其创建应延迟到应用启动时。
    - SQLAlchemy `TypeDecorator`：用于创建自定义数据类型，以增强数据库可移植性。
    - Pydantic `BaseModel`：用于数据验证和序列化的基础类。
    - FastAPI `APIRouter`：用于组织API路由。
    - FastAPI `Depends`：FastAPI的依赖注入标记。
    - FastAPI `lifespan`：一个异步上下文管理器，用于在应用启动和关闭时执行代码（如初始化数据库连接），是`@app.on_event`的现代替代方案，也是解决测试中配置覆盖问题的关键。
    - FastAPI `main.py`：通过`app.include_router()`注册路由。
    - FastAPI `ResponseValidationError`：当API返回的数据与`response_model`定义的模式不匹配时引发的异常。
- **Uvicorn启动方式**：
    - `uvicorn app.main:app --host 0.0.0.0 --port 8000`: 标准启动命令。
    - `python -m uvicorn src.main:app --host 0.0.0.0 --port 8000`: 适用于`src`布局的启动命令。
- **Python包管理**：
    - `pip install -r requirements.txt`：安装项目依赖。
    - `pip install pytest httpx aiosqlite pytest-asyncio`：安装测试所需依赖。
    - `pip uninstall <package>`：卸载包以解决冲突。
- **Pytest配置 (`pytest.ini`)**：
    - 用于解决`pytest-asyncio`的`ScopeMismatch`错误和配置测试路径：
      ```ini
      [pytest]
      asyncio_mode = auto
      testpaths = tests
      python_files = test_*.py
      ```
- **Pytest执行**：
    - `pytest`: 运行所有在`testpaths`中找到的测试。
    - `pytest -v`: 以详细模式运行。
    - `pytest <path/to/file.py>`: 只运行指定的测试文件，用于隔离调试。

## 实现细节（需验证）
- **项目初始化 (src layout)**：
    - 创建根目录：`src`, `tests`
    - 创建子目录：`src/api/v1`, `src/core`, `src/db`, `src/models`, `src/repositories`, `src/schemas`, `src/services`
    - 创建对应的测试子目录：`tests/api/v1`, `tests/services`
    - 在每个目录中创建空的`__init__.py`文件以使其成为可导入的包。
- **模块化文件组织**：为提高可维护性，建议为每个主要实体（如Book, Reader）创建独立的模块文件，例如：
    - `src/models/book.py`, `src/models/reader.py`
    - `src/schemas/book.py`, `src/schemas/reader.py`
    - `src/repositories/book_repository.py`, `src/repositories/reader_repository.py`
    - `src/services/book_service.py`, `src/services/reader_service.py`
    - `src/api/v1/books.py`, `src/api/v1/readers.py`
- **`requirements.txt`生成**：
    - 包含`fastapi`, `uvicorn`, `sqlalchemy`, `asyncpg` (或 `psycopg2-binary`), `python-dotenv`。
    - **更正**：为保证兼容性，应固定Pydantic版本，如 `pydantic==1.10.12`。
    - 移除`pydantic-settings`等可能引发版本冲突的非核心依赖。**或者，如果使用Pydantic v2+，则必须包含`pydantic-settings`。**
- **数据库模块实现 (`app/db/session.py`)**：
    - **反模式**：不要在模块顶层直接创建`engine`，或硬编码数据库连接字符串，如 `DATABASE_URL = "postgresql+asyncpg://user:password@host/dbname"`。这会导致`socket.gaierror`等连接错误。
    - **推荐模式**：从环境变量加载`DATABASE_URL`，并将`engine`的创建和表的初始化推迟到`main.py`的`lifespan`中。对于本地开发或测试，可配置为使用SQLite (`sqlite+aiosqlite:///./app.db`)。
- **`src/core/config.py`实现**：
    - 使用Pydantic v2+时，应从`pydantic_settings`导入`BaseSettings`：`from pydantic_settings import BaseSettings`。
- **`src/api/deps.py`生成**：创建一个专门的文件来管理和提供API路由的依赖项（如`get_db`, `get_book_service`），这有助于解耦和重用。确保所有使用的函数（如`Depends`）都已正确导入。
- **模型文件中的数据库兼容性处理 (`src/db/models.py`)**：
    - 为`UUID`类型添加`TypeDecorator`，以兼容SQLite。
- **Repository层实现 (`src/repositories/base.py`, `src/repositories/book_repository.py`)**：
    - `base.py`可定义一个包含通用CRUD方法的泛型基类。**注意：基类中的方法必须有具体实现，否则会导致运行时错误。**
    - 各实体的Repository继承基类并实现特定查询。
    - **层间数据约定**：为避免`AttributeError: 'dict' object has no attribute 'model_dump'`等类型错误，应明确Service层和Repository层之间传递的数据类型。一个稳健的模式是：Service层将Pydantic模型对象传递给Repository，Repository层负责调用`.model_dump()` (Pydantic v2)或`.dict()` (Pydantic v1)来获取字典数据，并用其创建SQLAlchemy模型实例。
    - **推断实现**：如果PSM未提供Repository的实现，可根据Service层对其方法的调用（如`book_repository.create_book(...)`）来生成相应的方法签名。
- **测试配置 (`tests/conftest.py`)**：
    - 为实现独立的集成测试，应配置使用内存SQLite数据库。
    - 创建一个指向内存数据库 (`sqlite+aiosqlite:///:memory:`) 的`async` SQLAlchemy引擎。
    - 定义一个`session`-scoped的fixture，在测试会话开始时使用`Base.metadata.create_all(bind=engine)`创建所有表。
    - 定义一个覆盖应用`get_db`依赖的fixture，使其使用测试数据库会话。该fixture必须从`get_db`的原始位置（如`src/db/session.py`）导入，而不是从模型文件导入。
    - **`client` fixture实现**：为避免`AttributeError: 'async_generator' object has no attribute 'get/post'`和`RuntimeError: Cannot send a request...`，`client` fixture必须正确地管理`httpx.AsyncClient`的生命周期。一个可靠的模式是使用`async with`和`yield`：
      ```python
      @pytest.fixture
      async def client(test_app: FastAPI) -> AsyncClient:
          async with AsyncClient(app=test_app, base_url="http://test") as client:
              yield client
      ```
- **`pytest.ini`文件创建**：在项目根目录创建`pytest.ini`文件，并设置`asyncio_mode = auto`和`testpaths = tests`，以避免`pytest-asyncio`插件的`ScopeMismatch`错误并确保测试被发现。
- **`main.py`生成**：
    - 使用`lifespan`上下文管理器在应用启动时调用`init_db`或直接创建表。
    - 创建FastAPI应用实例。
    - 遍历并`include_router`所有在`src/api/v1/`中定义的路由。
    - **注意**：必须避免函数重复定义，这可能导致服务静默失败。
- 注：实现细节可能已变化，使用前需验证。

## 用户偏好与项目特点
- **PSM/PIM驱动开发**：用户倾向于通过提供平台特定模型（PSM）或平台无关模型（PIM）来指导代码生成。PSM可以指定应用的逻辑、数据模型以及具体的文件和目录结构。
    - **容错性**：期望系统能够处理不完整的PSM，通过从上下文推断缺失的部分（如Repository层），以生成一个功能完整的应用。
- **交互式与引导式生成**：用户能够适应并主导一个交互式的、包含大量调试的生成流程。当初始目标无法达成时，用户会通过提供具体的、分步的指令（如“运行测试”、“修复代码”）来引导Agent完成整个任务。用户对“运行测试→分析失败→修复代码→重新测试”的循环有明确要求。
- **FastAPI + SQLAlchemy技术栈**：用户偏好使用FastAPI作为Web框架，SQLAlchemy作为ORM。
- **完整应用生成**：用户期望生成一个可直接运行的完整FastAPI应用，包括数据库配置、模型、Schema、业务逻辑和API路由。
- **清晰的模块划分**：用户偏好将代码按功能（models, schemas, services, routers）进行清晰的模块化组织。
    - **Repository层**：引入Repository层来封装数据访问逻辑是一种受欢迎的进阶模式。
    - **文件粒度**：为每个主要实体（如Book, Reader）创建独立的`service`, `repository`, `schema`和`router`文件是首选的组织方式，而不是将所有内容放在一个大的`services.py`或`routers.py`中。
    - **结构选择**：虽然扁平的`app/`结构在小型项目中可行，但其复杂的导入规则容易导致错误。`src/`布局在隔离性和可维护性上更优，是更稳健的选择。
- **生成辅助文件**：用户期望生成`.env.example`, `README.md`等辅助文件，以提高项目可用性。
- **生成可独立运行的测试**：用户期望生成使用内存数据库、配置完整的测试套件，并要求Agent修复所有测试失败，以验证生成代码的正确性，而无需依赖外部服务。**测试通过率100%是硬性要求。**