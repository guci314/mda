# 知识库

## 元知识
- 当任务是运行一个程序时，首要步骤是定位其主程序文件或入口点。
- 探索未知项目时，首先列出根目录内容以了解其基本结构。检查 `requirements.txt` 文件可以快速了解项目的技术栈和运行依赖（如 `uvicorn`）。
- 当启动服务器的命令超时时，这可能意味着服务已成功启动并在后台运行。应通过其他方式（如发送请求或检查进程）进行验证。
- 当一个 Web 请求返回特定 HTTP 错误时，可以推断出不同的服务状态：
    - `404 Not Found`: 服务器在运行，但请求的 URL 路径不正确。应检查应用的路由配置。
    - `405 Method Not Allowed`: 服务器在运行且 URL 路径正确，但使用的 HTTP 方法（如 GET, POST）不被该端点支持。
    - `422 Unprocessable Entity`: 服务器在运行，URL 和方法都正确，但请求体的数据格式或内容不符合预期（如缺少必填字段）。
    - `500 Internal Server Error`: 服务器在运行，但在处理请求时遇到了代码级别的错误。应立即检查应用日志（如 `uvicorn.log`）以查看详细的错误回溯（traceback）。
- 在调试 API 路由问题时，可以先尝试访问根路径 (`/`) 进行简单的连通性测试，确认服务基础功能正常，然后再去排查具体的 API 端点。
- 如果一个验证方法（如 `curl` 失败或日志文件不明确）结果不明确，应立即使用备用方法（如检查进程列表 `ps aux` 或检查应用日志）进行交叉验证。
- 调试代码级 Bug 的一般流程：
    1. 通过 API 测试复现问题（如收到 500 错误）。
    2. 检查应用日志文件，找到与错误请求相关的 traceback。
    3. 根据 traceback 定位到出错的文件和代码行（如 `NameError` 或 `ValidationError`）。
    4. 阅读并理解相关代码（如服务层、模型层），找出逻辑错误。
    5. 修改代码以修复错误。如果小范围修改导致文件混乱，使用 `write_file` 整体重写是有效的恢复策略。
    6. 重启应用服务。
    7. 重新运行 API 测试以验证修复是否成功。
- 要在模块化项目中找到正确的 API 端点路径：
    1. 从主应用文件（如 `app/main.py`）开始，查看包含了哪些路由模块（通过 `app.include_router()`）及其全局前缀（`prefix`）。
    2. 检查具体的路由文件（如 `app/routers/articles.py`），找到其 `APIRouter` 定义。
    3. 找到目标端点的装饰器（如 `@router.get("/search")`）及其路径。
    4. 将服务器根地址、全局 `prefix` 和端点路径组合成完整的 URL（例如 `http://127.0.0.1:8000` + `/api/v1` + `/articles/search`）。
- 如果服务的默认端口被占用，应先找到并终止占用该端口的进程，然后再启动服务。
- 停止一个在特定端口上运行的服务，最可靠的方法是：先用 `lsof -t -i:<port>` 找到进程ID（PID），再用 `kill <PID>` 终止该进程，最后再次检查端口以确认进程已终止。
- 验证 Web 服务是否正在运行的有效方法是：
    - 使用 `curl` 向已知端点发送请求。
    - 使用 `ps aux | grep <process_name>` 检查相关进程是否存在。
    - 检查服务启动时指定的日志文件（如 `uvicorn.log`）以确认启动成功或查看请求日志。
- 在后台运行服务（使用 `&`）并将其输出重定向到日志文件（使用 `> filename.log`）是一种有效的、不阻塞终端的服务器启动方式。
- 当一个 API 端点在不同次启动后返回不同的数据（例如，从空列表变为有数据的列表），这表明应用可能连接了一个持久化数据存储。
- 任务完成后，应检查并清理所有临时或不再需要的进程，以确保环境的整洁。
- 当用户在任务指令中提供明确的“成功判定条件”或“终止条件”时，必须严格遵循这些条件来判断任务是否完成。
- 在执行任务前，应首先检查其终止条件。如果条件已经满足（例如，要求停止一个本就未运行的服务），应直接报告任务完成，无需执行任何操作。
- 如果用户指定了多个检查点（如检查多个端口），必须逐一验证所有条件都满足。
- 如果用户要求在任务成功后输出特定信息，应按要求生成该输出。
- 任务完成后，应明确声明任务完成并停止执行，避免对已验证成功的条件进行不必要的重复检查。

## 原理与设计
- Python Web 项目（如 FastAPI）通常将其核心应用代码组织在一个名为 `app` 的目录中。
- FastAPI 应用通常使用 `uvicorn` 作为 ASGI 服务器来运行。
- 如果在代码中未找到 `uvicorn.run()` 调用，则应用很可能是通过 `uvicorn` 命令行工具启动的。
- `uvicorn` 命令行启动时，若未指定端口，则默认使用 8000 端口。
- 使用 `--host 0.0.0.0` 参数可以使服务在网络上可被访问，而不仅仅是本地主机。
- 模块化的 FastAPI 项目通过在主应用实例上使用 `app.include_router()` 来组合来自不同文件的 `APIRouter`，从而组织 API 端点。
- `app.include_router` 可以接受一个 `prefix` 参数（如 `/api/v1`），该前缀会自动添加到其包含的所有路由之前，用于 API 版本控制或全局命名空间。
- `APIRouter` 也可以定义自己的 `prefix`（如 `/articles`），该前缀会拼接在全局前缀之后。
- FastAPI 应用可以使用 `lifespan` 上下文管理器或直接在启动时执行代码（如 `Base.metadata.create_all(bind=engine)`）来初始化数据库连接和表结构。
- 项目的路由结构（包含 `articles`, `comments`）表明它可能是一个博客或内容管理系统（CMS）。
- 应用通过某种持久化存储来管理数据，因此数据在应用重启后依然存在。
- 项目使用 SQLAlchemy 作为 ORM。`Base.metadata.create_all(bind=engine)` 语句会在应用启动时根据定义的模型自动创建数据库表。
- `requirements.txt` 中包含 `psycopg2-binary`，强烈暗示项目使用 PostgreSQL 作为其数据库，尽管可能存在用于本地测试的 SQLite 文件（如 `blog.db`）。
- 项目采用分层架构，将数据库交互、业务逻辑和数据校验分别放在 `models`、`services` 和 `schemas` 目录中。
- FastAPI 的 `response_model` 会对服务层返回的数据进行校验和序列化。如果服务层函数返回的数据结构与 `response_model` 定义的 Pydantic 模型不匹配，将导致服务器端 `ValidationError`，并向客户端返回 500 内部服务器错误。

## 接口与API
- **工具**: `list_directory`
  - **用法**: `list_directory [path]`，用于列出指定路径下的文件和目录。
- **工具**: `read_file`
  - **用法**: `read_file [path]`，用于读取文件内容，对调试和理解代码至关重要。
- **工具**: `write_file`
  - **用法**: `write_file [path] [content]`，用于完全重写一个文件，适合在代码修复出错后进行整体恢复。
- **工具**: `edit_lines`
  - **用法**: `edit_lines [path] [start_line] [end_line] [new_content]`，用于对文件进行小范围的精确修改。
- **工具**: `append_file`
  - **用法**: `append_file [path] [content]`，用于在文件末尾追加内容。
- **工具**: `curl`
  - **用法**: `curl --noproxy 127.0.0.1 [options] [URL]`，用于发送 HTTP 请求测试 API。（`--noproxy` 参数在此环境中必需）。
  - **示例 (POST with JSON)**: `curl --noproxy 127.0.0.1 -X POST -H "Content-Type: application/json" -d '{"key": "value"}' http://127.0.0.1:8000/api/v1/articles/`
- **工具**: `lsof`
  - **用法**: `lsof -t -i:<port>`，用于查找并仅返回占用指定端口的进程ID (PID)。
- **工具**: `kill`
  - **用法**: `kill <PID>`，用于终止指定ID的进程。
- **命令模式**: 启动 FastAPI 应用
  - **命令**: `uvicorn <module_path>:<app_instance_name> --host <ip> --port <port>`
  - **示例**: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
- **命令模式**: 在后台启动服务并记录日志
  - **命令**: `<command> > <log_file> 2>&1 &`
  - **示例**: `uvicorn app.main:app --port 8000 > uvicorn.log 2>&1 &`
- **命令模式**: 检查运行中的进程
  - **命令**: `ps aux | grep <process_name>`
- **命令模式**: 按端口号停止服务（查找->终止->验证）
  - **步骤 1 (查找PID)**: `lsof -t -i:<port>`
  - **步骤 2 (终止进程)**: `kill <PID>`
  - **步骤 3 (验证停止)**: 再次运行 `lsof -t -i:<port>`，预期命令会失败。
- **已知 API 端点**:
    - **更正**: 所有 API 端点都有 `/api/v1` 前缀。
    - `POST /api/v1/articles/`: 创建一篇新文章。需要一个符合 `ArticleCreate` 模式的 JSON body，包含 `title`, `content`, `author`。
    - `GET /api/v1/articles/search?query=<term>`: 搜索文章。
    - `POST /api/v1/comments/`: 创建一条新评论。
    - **潜在端点**: 根据路由文件推断，可能还存在 `/categories/` 等端点，很可能也在 `/api/v1` 前缀下。

## 实现细节（需验证）
- 注：实现细节可能已变化，使用前需验证
- **项目结构**:
    - `app/`: 目录，包含核心应用代码。
        - `main.py`: FastAPI 应用实例 (`app`) 的定义文件，是应用的入口。它通过 `app.include_router(..., prefix="/api/v1")` 加载其他路由。
        - `routers/`: 目录，包含 API 路由定义。
            - `articles.py`: 定义了 `/articles` 相关路由，如 `POST /articles/` 和 `GET /articles/search`。
            - `comments.py`: 定义了 `/comments` 相关路由。
        - `services/`: 目录，包含业务逻辑。
            - `article_service.py`: 实现了创建、搜索文章等功能。其返回的数据结构必须与 `routers` 中定义的 `response_model` 兼容。
        - `schemas/`: 目录，包含 Pydantic 数据校验模型。
            - `blog.py`: 定义了 `ArticleCreate`, `ArticleResponse` 等模型。
        - `models/`: 目录，包含 SQLAlchemy 数据库模型。
        - `database.py`: 包含数据库引擎 (`engine`)、基类 (`Base`) 和会话管理 (`get_db`)。
    - `requirements.txt`: 文件，项目依赖列表，包含 `fastapi`, `uvicorn`, `sqlalchemy`, `pydantic`, `psycopg2-binary` 等。
    - `blog.db`: 文件，可能是用于本地开发或测试的 SQLite 数据库文件。
- **启动模式**: 应用实例 `app` 在 `app/main.py` 中定义，通过 `uvicorn app.main:app` 命令启动。
- **日志文件**: 当服务在后台启动时，其日志被重定向到 `uvicorn.log` 文件。
    - **成功启动日志标志**: `Uvicorn running on http://0.0.0.0:XXXX`
    - **请求日志**: 文件中也会记录收到的请求及其状态码，如 `404 Not Found`, `405 Method Not Allowed`。
    - **错误日志标志**: `ERROR: Exception in ASGI application`，后面会跟随详细的 Python traceback，是调试 500 错误的关键。

## 用户偏好与项目特点
- **项目类型**: FastAPI 应用。
- **技术栈**: 使用 SQLAlchemy 作为 ORM，数据库很可能是 PostgreSQL。
- **项目结构**: 遵循常见的模块化模式，将应用代码放在 `app` 目录中，并进一步按功能（`routers`, `crud`, `services`, `models`, `schemas`）划分。
- **API 版本控制**: 项目 API 使用 `/api/v1` 前缀进行版本控制。
- **运行方式**: 倾向于使用 `uvicorn` 命令行工具直接运行。
- **后台服务**: 倾向于将 Web 服务作为后台进程运行，并将标准输出和错误重定向到日志文件。
- **数据持久化**: 项目包含一个持久化数据层，数据在会话之间得以保留。
- **潜在问题**: 项目代码可能存在 bug（如数据层与响应模型不匹配），需要具备通过日志进行调试和代码修复的能力。
- **网络环境要求**: 使用 `curl` 时必须添加 `--noproxy 127.0.0.1` 参数，以避免本地代理问题。
- **操作偏好**: 倾向于保持环境整洁，会主动清理任务执行过程中产生的临时或冗余进程。
- **交互模式**: 用户倾向于使用高层次、目标驱动的指令。指令中可能包含详细的成功/终止条件，助手必须严格遵循。