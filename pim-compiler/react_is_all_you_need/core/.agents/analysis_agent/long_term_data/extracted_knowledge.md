# 知识库

## 元知识
- 分析代码库时，首要步骤是通过列出根目录文件 (`list_directory .`) 来快速了解项目技术栈、配置和整体结构。
- 优先查找并阅读高阶设计文档（如 `README.md`、`CONTRIBUTING.md` 以及文件名包含“架构”、“设计理念”的文档），这能最快地把握核心设计思想。
- 查看 `package.json`，特别是 `workspaces` 字段，可以快速确定项目是否为 monorepo 架构，并了解其子模块。
- 查看项目的构建配置文件（如 `esbuild.config.js`）可以帮助从打包后的产物（如 `bundle/` 目录下的文件）追溯到源码入口（如 `entryPoints` 配置）。
- 当根据引用关系查找文件失败时（File Not Found），应使用 `list_directory` 验证实际的文件名和扩展名（例如，`.ts` vs `.tsx`）。

## 原理与设计
- **分层模块化架构**：项目采用清晰的三层架构（CLI 表示层、Core 业务层、Tools 工具层），实现关注点分离，便于维护和扩展。
- **AI Agent 架构模式**：项目核心是一个具备对话式交互、工具调用、上下文感知和自主决策能力的 AI Agent。
- **双模 CLI 执行**：CLI 层支持两种执行模式：一个基于 React/Ink 的交互式 TUI（Terminal User Interface）模式，用于对话；一个非交互式模式，用于直接执行命令并输出结果。
- **CLI 执行生命周期**：启动时遵循一个明确的顺序：加载配置 -> 检查并启动沙箱 -> 用户认证 -> 判断并进入交互/非交互模式。
- **沙箱化执行**：CLI 在启动时会检查并按需启动一个沙箱环境来执行任务，以增强安全性。
- **Monorepo 架构**：项目采用 monorepo 结构，将不同的模块（如 `cli`, `core`）组织在 `packages/` 目录下，便于统一管理和代码复用。
- **核心概念**：
  - **记忆 (Memory)**：通过持久化存储（也称 `memport`）和检索用户上下文，实现跨会话的状态保持。
  - **工具 (Tool)**：作为功能扩展的核心机制，被 AI Agent 动态调用。
- **技术栈**：项目基于 Node.js (>=20.0.0) 和 TypeScript，使用 `esbuild` 进行构建，`eslint` 进行代码检查。

## 接口与API
- **工具**:
  - `list_directory: [PATH]`: 列出指定路径下的文件和目录，是探索项目结构的基础工具。
- **记忆管理 (Memory CLI)**:
  - `gemini memory save --name <名称>`: 保存当前会话记忆。
  - `gemini memory search --query <查询词>`: 检索历史记忆。
  - `gemini memory load --name <名称>`: 加载指定记忆。
- **项目交互**:
  - `Makefile`: 定义了项目的常用命令（如构建、测试、部署）。
  - `package.json` (`scripts`): 定义了项目的启动、调试等脚本。
  - `package.json` (`bin`): 定义了 CLI 命令（如 `gemini`）对应的可执行文件。
- **CLI 标志**:
  - `--prompt-interactive`: 强制进入交互式模式。
- **配置**:
  - `esbuild.config.js`: esbuild 的配置文件，`entryPoints` 字段定义了项目的打包入口。
  - `eslint.config.js`: ESLint 的配置文件，定义了代码规范。
  - `Dockerfile`: 定义了项目的容器化环境。

## 实现细节（需验证）
- **项目根目录结构**:
  - **文档**: `docs/`, `README.md`, `CONTRIBUTING.md`, `GEMINI.md`, `ROADMAP.md`, `LICENSE`, `gemini_cli_记忆机制.md`, `gemini_cli_memory_tool_summary.md`, `gemini_cli多轮对话保持状态.md`
  - **源码 (Monorepo)**: `packages/`, `integration-tests/`
    - `packages/cli`: 命令行接口实现。
      - **更正：** `index.ts` 是 CLI 的主入口，它调用 `src/gemini.tsx` 中的 `main` 函数。
      - `src/gemini.tsx`: CLI 的核心逻辑，负责启动时的完整生命周期：
        1. **配置加载**: 调用 `loadSettings`, `parseArguments`, `loadExtensions`, `loadCliConfig` 等函数合并生成最终配置。
        2. **沙箱检查**: 检查沙箱状态，如果需要则调用 `start_sandbox` 启动沙箱并退出当前进程。
        3. **用户认证**: 验证并刷新认证令牌。
        4. **模式判断**: 根据 `--prompt-interactive` 标志、命令行 prompt 和 TTY 输入，决定进入交互模式或非交互模式。
      - `src/nonInteractiveCli.ts`: 非交互式模式的实现，通过 `runNonInteractive` 函数处理请求。
      - `src/ui/App.js`: 交互式UI的根组件 (`AppWrapper`)，使用 `ink` 和 `React` 渲染。
      - `src/config/config.js`: 负责加载和合并 CLI 配置 (`loadCliConfig`)。
    - `packages/core`: 核心业务逻辑。
      - `src/tools`: 工具的具体实现。
      - `src/services`: 各种服务的实现。
      - `src/mcp`: 可能为 Model Context Protocol 的实现。
    - `packages/vscode-ide-companion`: VS Code 扩展。
  - **配置**: `.gcp/`, `.github/`, `.npmrc`, `package.json`, `.prettierrc.json`
  - **构建与环境**: `Dockerfile`, `Makefile`, `esbuild.config.js`, `eslint.config.js`, `eslint-rules/`
  - **运行时数据**: `.gemini/memory.json` (默认的记忆存储文件), `.gemini/settings.json` (用户设置)
- 注：实现细节可能已变化，使用前需验证

## 用户偏好与项目特点
- (暂无)