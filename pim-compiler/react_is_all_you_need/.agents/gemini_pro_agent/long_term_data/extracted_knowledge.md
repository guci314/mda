# 知识库

## 元知识
- 分析一个目录或模块时，首先使用 `list_directory` 查看其文件和子目录结构，以建立初步认知。
- 要理解一个 Node.js 模块的角色和技术栈，应首先检查 `package.json` 文件，分析其 `dependencies`, `devDependencies` 和 `scripts`。
- 要理解一个模块的功能，可以从其主入口文件（如 `index.ts`, `gemini.tsx`）入手，分析其导入和调用的其他模块，以了解其组织方式。
- 仔细阅读代码中的文件级注释，它们通常会直接阐明模块的设计目的（例如 `acp.ts` 的注释解释了其 JSON-RPC 协议的功能）。
- 根据目录和文件名（如 `config/`, `ui/`, `utils/`）对模块功能进行初步假设，然后通过阅读关键文件来验证。

## 原理与设计
- 项目 `packages/cli` 是一个标准的 TypeScript/Node.js 模块，其核心逻辑依赖于一个独立的 `@google/gemini-cli-core` 包。
- 其结构遵循通用实践：`src` 存放源码，`dist` 存放编译结果，`package.json` 管理依赖，`tsconfig.json` 配置 TypeScript。
- 使用 Vitest (`vitest.config.ts`) 作为测试框架，使用 `yargs` 进行命令行参数解析。
- **多模式执行**: CLI 具有多种执行模式，由主入口 `gemini.tsx` 根据上下文进行分发：
    1. **交互式模式**: 在 TTY 环境下，通过 `gemini.tsx` 启动，使用 `ink` 和 `React` 构建丰富的命令行界面。
    2. **非交互式模式 (管道/重定向)**: 当检测到管道 (`|`) 或重定向 (`<`) 输入时，调用 `nonInteractiveCli.ts` 中的逻辑。该逻辑负责处理一次性命令的核心流程：通过 `sendMessageStream` 与 Gemini API 通信，并使用 `executeToolCall` 执行返回的工具调用。
    3. **Agent 通信协议 (ACP) 模式**: 当特定参数启用时，启动 `acp/` 模块，允许外部 GUI 应用连接并与 CLI Agent 交互。
- **沙箱环境**: 包含一个通过 `utils/sandbox.js` 启动的沙箱环境，用于隔离执行环境。
- **可扩展的斜杠命令系统**: 交互式界面支持 `/` 开头的命令（如 `/help`, `/clear`）。这些命令由 `services/CommandService.ts` 统一加载和管理，并分散在 `ui/commands/` 目录下定义，实现了功能的可扩展和模块化。

## 接口与API
- **工具: `list_directory`**
  - **功能**: 列出指定路径下的文件和目录。
  - **用法**: `list_directory <path>`
  - **输出格式**: 列表形式，每个条目前缀为 `[FILE]` 或 `[DIR]`。
- **工具: `read_file`**
  - **功能**: 读取指定文件的内容。
  - **用法**: `read_file <path>`
  - **输出格式**: 字符串形式的文件内容。
- **工具: `create_file`**
  - **功能**: 创建一个新文件并等待提供内容。
  - **用法**: `create_file <filename>`，Agent 会在文件创建后请求要写入的内容。
  - **示例**: `创建文件，名字是：“gemini_cli_记忆机制.md”`
- **内部模块接口**:
  - **功能**: CLI 内部各模块间调用的关键函数。
  - **配置**: `loadCliConfig`, `parseArguments` (from `config/config.js`)
  - **核心逻辑**: `sendMessageStream`, `executeToolCall` (from `@google/gemini-cli-core`)
  - **工具**: `readStdin` (from `utils/readStdin.js`), `start_sandbox` (from `utils/sandbox.js`)
- **内部接口: Slash Commands**
  - **功能**: 在交互式模式下，通过输入 `/` 开头的命令执行特定操作。
  - **示例**: `/help`, `/clear`, `/auth`。
  - **实现**: 由 `services/CommandService.ts` 注册，在 `ui/commands/` 目录下定义。

## 实现细节（需验证）
- **`packages/cli` 目录结构**:
  - `src/`: TypeScript 源码目录。
    - `gemini.tsx`: **主入口与调度器**。解析参数、加载配置，并根据执行环境（TTY、管道输入、ACP标志）决定调用交互式UI、非交互式逻辑还是ACP服务。
    - `nonInteractiveCli.ts`: **处理非交互式命令**（如管道输入）的逻辑。负责调用 Core 包的 `sendMessageStream` 和 `executeToolCall`。
    - `config/`: 配置加载 (`loadCliConfig`) 与参数解析 (`parseArguments`) 模块。
    - `ui/`: 存放交互式界面的 React (Ink) 组件 (`App.js`) 和斜杠命令定义 (`commands/`)。
    - `services/`: **命令服务**，特别是 `CommandService.ts`，用于加载和管理所有斜杠命令。也包含与外部服务交互的模块。
    - `acp/`: **Agent 通信协议**实现，提供 JSON-RPC 服务。
    - `utils/`: 通用辅助函数（如 `readStdin`, `sandbox`）。
    - `generated/`: 自动生成的文件。
  - `dist/`: 编译后的 JavaScript 输出目录。
  - `package.json`: Node.js 项目定义文件。
  - `tsconfig.json`: TypeScript 配置文件。
  - `vitest.config.ts`: Vitest 测试框架配置文件。
  - `node_modules/`: 项目依赖。
  - `coverage/`: 测试覆盖率报告。
  - `junit.xml`: 测试结果报告（JUnit 格式）。
- 注：实现细节可能已变化，使用前需验证

## 用户偏好与项目特点
- **技术栈**: 使用 TypeScript 和 React (Ink.js) 构建命令行界面，这表明项目重视交互式体验。
- **模块化设计**: 项目高度模块化，将配置、UI、服务、通信协议等关注点清晰地分离到不同目录中。**特别是将不同的执行模式（交互式、非交互式、ACP）逻辑分离到不同文件中，由一个主入口进行调度**。
- **实验性与高级功能**: 项目包含实验性功能（如 ACP）和高级功能（如沙箱环境），这些功能可能通过配置项启用。
- **重视知识沉淀**: 用户倾向于将分析结果和学习到的知识固化为文档（如创建 `_记忆机制.md` 文件），表明对知识的持久化和复用有明确需求。