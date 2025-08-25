```markdown
# 知识库

## 元知识
- **状态驱动的执行循环**: 对于复杂、长时运行的任务，可以通过一个外部状态文件（如JSON）来驱动。执行循环为：读取状态 -> 执行当前步骤 -> 更新状态 -> 重复。这使得任务可中断和可恢复。
- **声明式任务定义**: 将任务的"做什么"（步骤、依赖关系）在一个配置文件或模板中声明，与"如何做"（执行逻辑）分离，可以提高工作流的清晰度和可维护性。
- **自描述和可验证的模板**: 在模板内部（如YAML frontmatter）定义其元数据（ID, 版本, 描述）和参数（类型, 是否必须, 枚举值）。这使得模板本身具备了自描述和可验证的特性，提高了标准化和易用性。
- **通过模拟验证逻辑**: 在没有完整执行环境的情况下，可以使用简单的命令或脚本模拟复杂操作（如构建、部署、审批），以快速验证核心工作流逻辑的正确性。
- **从最终状态生成报告**: 任务完成后，利用最终的状态文件生成一份人类可读的报告，是一种有效的实践，可以提供清晰的审计和摘要信息。
- **系统性文件查找策略**: 当无法在预期路径找到文件时，应采用系统性策略：首先使用广域搜索工具（如 `search_files`）查找文件名；如果失败，则通过逐级列出父目录内容（`list_directory`）来理解当前文件系统结构，从而定位目标文件。

## 原理与设计
- **核心设计：状态机工作流**: 整个软件部署过程被设计成一个状态机，其状态被完整地记录在 `workflow_state.json` 文件中。Agent 的作用是作为状态机的"执行引擎"，根据当前状态执行相应的动作，并将结果写回状态文件，驱动状态转移。
- **工作流模板化与实例化**: 工作流可以被定义为可复用的模板（如Markdown/YAML文件），包含参数定义、步骤和逻辑。一个具体的工作流执行是该模板的一个"实例"，通过应用用户提供的参数生成。这极大地提高了工作流的标准化和复用性。
- **模板元数据驱动工作流实例**: 模板中的元数据（如 `template_id`, `type`）会被复制到工作流实例的状态文件中，确保了每个实例都带有其源模板的清晰标识和分类。
- **解耦**: 该设计将工作流的"定义"（模板文件和状态JSON）与"执行"（Agent逻辑）分离开来。这允许在不修改Agent代码的情况下，通过改变配置文件来调整或重用工作流。
- **幂等性与可恢复性**: 通过在状态文件中记录每个步骤的 `status` (`pending`, `completed`)，工作流具备了基本的幂等性。如果工作流中断，可以从上一个未完成的步骤安全地恢复，而无需重新执行已完成的步骤。
- **支持复杂流程**: 该架构通过不同的步骤类型（`action`, `condition`, `approval`, `parallel`）原生支持了条件分支、人工审批和并行执行等复杂的流程控制模式。例如，一个 `condition` 步骤可以根据变量（如 `environment`）决定是否需要执行一个 `approval` 步骤。`parallel` 步骤通过管理一组有独立状态的 `sub_tasks` 来实现并发。
- **明确的终止状态**: 工作流通过将顶层 `status` 设置为 `completed` 或 `failed`，并将 `current_step` 设置为 `null` 来表示执行结束，确保了状态机的终结性。
- **通过变量进行步骤间数据传递**: `variables` 对象不仅用作初始配置，还充当工作流的共享内存。步骤可以将其输出（如构建产物 `docker_image` 的名称）写入 `variables`，供后续步骤读取和使用。`condition` 步骤也可以修改 `variables`（如设置 `require_approval: true`）来影响流程。`parallel` 步骤通常会遍历 `variables` 中的数组（如 `servers` 列表）。

## 接口与API
- **核心输入文件**:
  - **工作流模板** (e.g., `deployment.md`): 定义工作流的结构、参数和步骤。通常是包含两个YAML frontmatter块的Markdown文件：一个用于定义模板元数据（`template_id`, `version`, `description`等），另一个用于定义参数（`parameters`）。
  - **工作流状态文件**: `workflow_state.json`
- **核心输出文件**: `deployment_report.md`
- **`workflow_state.json` 结构**:
  - `workflow_id` (string): 工作流的唯一标识符。
  - `template_ref` (string): 创建此工作流实例所使用的模板文件的绝对路径，用于追溯。例如：`/home/user/project/knowledge/workflow/templates/deployment.md`。
  - `template_id` (string): 模板文件中定义的ID。
  - `type` (string): 工作流类型，如 `software_deployment`。
  - `status` (string): 整个工作流的状态，如 `pending`, `running`, `completed`, `failed`。
  - `current_step` (string | null): 指向当前待执行步骤的 `id`。工作流完成时为 `null`。
  - `variables` (object): 存储工作流全局变量的键值对。它是一个动态对象，不仅包含初始参数，还会在工作流执行期间被步骤修改和扩充。例如: `{ "environment": "production", "servers": ["app-server-1", "app-server-2", "app-server-3"], "version": "v2.0.0", "skip_tests": false, "require_approval": true, "docker_image": "my-app:v2.0.0-production" }`。
  - `steps` (array): 定义工作流所有步骤的数组。每个步骤对象包含：
    - `id` (string): 步骤的唯一标识符。
    - `name` (string): 人类可读的步骤名称。
    - `type` (string): 步骤类型，如 `action`, `condition`, `approval`, `parallel`。
    - `status` (string): 步骤的执行状态，如 `pending`, `completed`。
    - `started_at` / `completed_at` (string): ISO 8601 格式的时间戳。
    - `details` (string, optional): 存储步骤执行过程中的人类可读信息或日志摘要。例如，可以存储 `execute_command` 的输出，如 `"Unit tests passed. Code quality check passed."`。
    - `result` (object, optional): 存储步骤执行结果的结构化数据。
    - `sub_tasks` (array, for `parallel` type): 定义并行执行的子任务。父步骤完成前，所有子任务状态需更新为 `completed`。

- **使用的工具**:
  - `write_file(path, content)`: 用于创建和更新 `workflow_state.json` 及生成最终报告 `deployment_report.md`。
  - `read_file(path)`: 用于读取工作流模板和当前工作流状态。
  - `execute_command(command)`: 用于执行模拟的外部命令（如测试、构建、部署）。
  - `search_files(pattern)`: 在文件系统中按模式搜索文件，用于定位模板等资源。
  - `list_directory(path)`: 列出目录内容，用于在文件搜索失败时探索文件系统结构。

## 实现细节（需验证）
- **文件**:
  - `workflow_state.json`: 核心状态管理文件。
  - `deployment_report.md`: 任务结束时生成的报告文件。
  - **模板文件位置**: 工作流模板文件可能位于项目特定的嵌套目录中，如 `[project_name]/knowledge/workflow/templates/[template_name].md`，而非总是在根目录。
  - **模板文件格式**: 模板通常是 Markdown 文件，其核心定义（元数据、参数）存储在文件顶部的 YAML frontmatter 块中。
- **工作流启动流程**:
  - 1. Agent 读取指定的模板文件。
  - 2. Agent 解析模板，结合用户输入的参数，生成初始的 `workflow_state.json` 文件，并记录 `template_ref`。
- **工作流推进机制**:
  - Agent 通过读取 `current_step` 字段来确定要执行哪个步骤。
  - 每完成一个步骤，Agent 会更新该步骤的 `status` 为 `completed`，并修改顶层的 `current_step` 字段为下一个步骤的 `id`。
  - 当最后一个步骤完成后，Agent 会将顶层 `status` 更新为 `completed`，并将 `current_step` 设置为 `null`。
- **条件逻辑实现**:
  - `condition` 类型的步骤通过读取 `variables` 中的值（如 `variables.environment === 'production'`）来决定下一个 `current_step` 的值，或动态修改 `variables` 中的其他值（如设置 `variables.require_approval = true`）。
- **审批流程实现**:
  - `approval` 类型的步骤会将工作流置于等待状态。审批通过是通过外部（或模拟）更新该步骤的 `status` 为 `completed` 来实现的。
- **并行任务实现**:
  - `parallel` 类型的步骤通常通过遍历 `variables` 中的数组（如 `servers` 列表）来实现。Agent 会为数组中的每个元素执行相应的操作，并在所有操作完成后，将该并行步骤本身标记为 `completed`。

## 用户偏好与项目特点
- **偏好基于模板的工作流**: 用户倾向于从可复用的模板（如 `deployment.md`）启动任务，并通过参数进行定制，而不是每次都从头定义工作流。
- **通过参数控制工作流分支**: 用户通过提供参数（如 `skip_tests: false`）来控制工作流的执行路径，例如是否跳过某些步骤。
- **重视可追溯性**: 完整的执行记录（步骤、状态、时间戳）和最终的摘要报告是用户的关键需求。这包括将工作流实例追溯回其源模板（通过 `template_ref` 字段）。
- **支持人工干预**: 工作流设计需要包含人工审批（`approval`）等节点，允许在关键步骤暂停并等待外部确认。
- **模块化步骤**: 用户将工作流分解为具有不同类型（`action`, `condition` 等）的独立步骤，便于理解和管理。
- **通过变量处理动态资源**: 用户倾向于在 `variables` 中定义资源列表（如服务器数组），以便工作流步骤可以动态地对这些资源进行操作。
- **模拟复杂场景**: 用户利用该框架模拟真实的、复杂的工作流（如包含审批和并行部署的生产发布流程），以在不影响实际环境的情况下验证流程的正确性。
```