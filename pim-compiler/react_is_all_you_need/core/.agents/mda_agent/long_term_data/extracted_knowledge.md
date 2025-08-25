# 知识库

## 元知识
- **通用项目分析方法**：
  - **起点**：从 `README.md` 开始，快速了解项目目标、技术栈和基本用法。
  - **依赖分析**：检查包管理文件（如 `package.json`, `pyproject.toml`）以理解项目依赖、脚本和核心工具（如构建工具、测试框架）。
  - **架构识别**：通过 `workspaces` 配置和 `packages/` 目录结构识别 Monorepo 架构。通过分析包间依赖关系（如 `cli` 依赖 `core`）来推断模块化设计。
  - **交互探查**：使用 `grep` 等代码搜索工具，查找特定库或 SDK（如 `@modelcontextprotocol/sdk`）的用法，以验证组件间的通信方式。
- **测试验证方法**：通过 `pytest` 命令直接运行测试，无需额外配置即可收集并执行测试用例。
- **测试发现机制**：pytest 自动发现以 `test_*.py` 命名的文件和以 `test_*` 命名的函数。
- **测试状态判断**：通过 pytest 输出中的 `collected X items` 和 `passed/failed` 统计快速判断测试覆盖率与成功率。
- **测试环境隔离**：使用独立测试数据库（`test.db`）避免污染生产数据。
- **快速验证技巧**：`pytest --collect-only` 可快速查看测试收集情况而不实际运行。

## 原理与设计
- **模块化与 Monorepo 架构 (Node.js 示例)**：
  - **核心思想**：将项目拆分为多个独立的包（packages），存放于一个代码仓库（monorepo）中。
  - **典型结构**：
    - `core` 包：包含可重用的核心业务逻辑，不依赖任何前端实现。
    - `cli` 包：实现命令行界面，作为 `core` 包的一个客户端。
    - `ide-extension` 包：实现 IDE 插件（如 VS Code），作为 `core` 包的另一个客户端。
  - **组件通信**：不同包之间可以通过一个共享的 SDK 或协议（如 `@modelcontextprotocol/sdk`）进行通信，通常采用客户端-服务器模式。
- **测试架构 (Python 示例)**：采用 pytest + FastAPI TestClient + SQLAlchemy 的测试组合。
- **数据库测试策略**：每个测试函数使用独立的数据库会话，确保测试隔离性。
- **fixture 设计**：使用 `@pytest.fixture(scope="function")` 为每个测试创建干净的数据库环境。
- **测试金字塔**：当前项目遵循单元测试优先，覆盖核心操作的基本测试策略。

## 接口与API
- **Node.js 生态工具**：
  - **包管理**：`npm`, `npx`。
  - **配置文件**：`package.json`（`workspaces` 用于 Monorepo，`scripts` 用于任务自动化，`dependencies` 用于依赖管理）。
  - **测试框架**：`vitest`。
  - **构建工具**：`esbuild`。
  - **CLI 开发库**：`yargs` (命令解析), `ink` (React for CLIs)。
  - **通信协议库**：`@modelcontextprotocol/sdk` 用于实现组件间通信。
- **Python 测试生态工具**：
  - **pytest 命令**：
    - `pytest` - 运行所有测试
    - `pytest -v` - 详细输出
    - `pytest --collect-only` - 仅收集测试用例
  - **FastAPI 测试工具**：`TestClient` 用于模拟 HTTP 请求测试 API 端点。
  - **测试插件**：项目使用 `pytest-benchmark` 插件，可能用于性能测试。
  - **测试配置**：`conftest.py` 中定义共享的测试 fixture（数据库会话、TestClient）。
  - **数据库测试配置**：
    - 测试数据库 URL：`sqlite:///./test.db`
    - 引擎参数：`connect_args={"check_same_thread": False}` 解决 SQLite 线程问题。

## 实现细节（需验证）
- **项目：`gemini-cli` (Node.js)**
  - **结构**：Monorepo 结构
    ```
    ├── packages/
    │   ├── core/              # 核心逻辑
    │   ├── cli/               # 命令行实现
    │   └── vscode-ide-companion/ # VS Code 插件
    ├── package.json
    └── esbuild.config.js
    ```
  - **关键文件**：
    - `packages/core/src/mcp-client.ts`：实现了 MCP 客户端。
    - `packages/vscode-ide-companion/src/ide-server.ts`：实现了 MCP 服务器。
- **项目：`pim-compiler` (Python)**
  - **测试文件位置**：`tests/` 目录下
  - **测试文件命名**：`test_articles.py`（对应功能模块）
  - **fixture 位置**：`tests/conftest.py` 包含数据库和客户端 fixture
  - **测试数据库**：项目根目录下的 `test.db`（自动生成）
  - **测试用例结构**：
    - **更正**：测试用例数量已变化。最新运行显示共收集到 3 个测试用例，而非原先的 5 个。具体的测试用例名称需重新检查。
  - **项目结构**：
    ```
    ├── tests/
    │   ├── __init__.py
    │   ├── conftest.py
    │   └── test_articles.py
    ├── app/
    │   ├── main.py
    │   ├── database.py
    │   └── models/
    └── test.db
    ```

## 用户偏好与项目特点
- **项目：`gemini-cli`**
  - **技术栈**：Node.js, TypeScript。
  - **架构**：Monorepo，采用 `core` + 多客户端（CLI, VS Code）模式。
  - **测试框架**：`vitest`。
  - **构建工具**：`esbuild`。
  - **CLI 界面**：使用 `ink` 构建交互式界面。
- **项目：`pim-compiler`**
  - **技术栈**：Python, FastAPI, SQLAlchemy。
  - **测试框架选择**：偏好 pytest 而非 unittest。
  - **测试数据库**：使用 SQLite 文件数据库而非内存数据库（可能为了调试方便）。
  - **测试范围**：当前重点测试核心功能（3个测试用例）。
  - **配置风格**：**更正：** 项目可能使用 `pytest.ini` 或 `pyproject.toml` 等配置文件，pytest 运行时会加载它们。
  - **工具偏好**：使用 `pytest-benchmark`，表明对性能测试有潜在需求。