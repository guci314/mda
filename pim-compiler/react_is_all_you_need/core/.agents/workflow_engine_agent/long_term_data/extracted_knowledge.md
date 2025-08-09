# 知识库

## 元知识
- **状态驱动的执行循环**: 对于复杂、长时运行的任务，可以通过一个外部状态文件（如JSON）来驱动。执行循环为：读取状态 -> 执行当前步骤 -> 更新状态 -> 重复。这使得任务可中断和可恢复。
- **声明式任务定义**: 将任务的“做什么”（步骤、依赖关系）在一个配置文件中声明，与“如何做”（执行逻辑）分离，可以提高工作流的清晰度和可维护性。
- **通过模拟验证逻辑**: 在没有完整执行环境的情况下，可以使用简单的命令或脚本模拟复杂操作（如构建、部署），以快速验证核心工作流逻辑的正确性。
- **从最终状态生成报告**: 任务完成后，利用最终的状态文件生成一份人类可读的报告，是一种有效的实践，可以提供清晰的审计和摘要信息。

## 原理与设计
- **核心设计：状态机工作流**: 整个软件部署过程被设计成一个状态机，其状态被完整地记录在 `workflow_state.json` 文件中。Agent 的作用是作为状态机的“执行引擎”，根据当前状态执行相应的动作，并将结果写回状态文件，驱动状态转移。
- **解耦**: 该设计将工作流的“定义”（JSON文件）与“执行”（Agent逻辑）分离开来。这允许在不修改Agent代码的情况下，通过改变JSON文件来调整或重用工作流。
- **幂等性与可恢复性**: 通过在状态文件中记录每个步骤的 `status` (`pending`, `completed`)，工作流具备了基本的幂等性。如果工作流中断，可以从上一个未完成的步骤安全地恢复，而无需重新执行已完成的步骤。
- **支持复杂流程**: 该架构通过不同的步骤类型（`action`, `condition`, `approval`, `parallel`）原生支持了条件分支、人工审批和并行执行等复杂的流程控制模式。

## 接口与API
- **核心配置文件**: `workflow_state.json`
- **`workflow_state.json` 结构**:
  - `workflow_id` (string): 工作流的唯一标识符。
  - `type` (string): 工作流类型，如 `software_deployment`。
  - `status` (string): 整个工作流的状态，如 `pending`, `running`, `completed`, `failed`。
  - `current_step` (string): 指向当前待执行步骤的 `id`。
  - `variables` (object): 存储工作流全局变量的键值对，如 `environment`, `docker_image`, `servers`。
  - `steps` (array): 定义工作流所有步骤的数组。
    - `id` (string): 步骤的唯一标识符。
    - `name` (string): 人类可读的步骤名称。
    - `type` (string): 步骤类型，如 `action`, `condition`, `approval`, `parallel`。
    - `status` (string): 步骤的执行状态，如 `pending`, `completed`。
    - `started_at` / `completed_at` (string): ISO 8601 格式的时间戳。
    - `result` (object, optional): 存储步骤执行结果的详细信息。
    - `sub_tasks` (array, for `parallel` type): 包含并行执行的子任务对象。

- **使用的工具**:
  - `write_file(path, content)`: 用于创建和更新 `workflow_state.json` 及生成最终报告 `deployment_report.md`。
  - `read_file(path)`: 用于在执行每个步骤前读取当前工作流状态。
  - `execute_command(command)`: 用于执行模拟的外部命令（如测试、构建、部署）。

## 实现细节（需验证）
- **文件**:
  - `workflow_state.json`: 核心状态管理文件。
  - `deployment_report.md`: 任务结束时生成的报告文件。
- **工作流推进机制**:
  - Agent 通过读取 `current_step` 字段来确定要执行哪个步骤。
  - 每完成一个步骤，Agent 会更新该步骤的 `status` 为 `completed`，并修改顶层的 `current_step` 字段为下一个步骤的 `id`。
- **条件逻辑实现**:
  - `condition` 类型的步骤（如 `deploy_decision`）通过读取 `variables` 中的值（如 `environment`）来决定下一个 `current_step` 的值，从而实现分支。
- **审批流程实现**:
  - `approval` 类型的步骤会将工作流置于等待状态。审批通过是通过外部（在此次任务中是Agent模拟）更新该步骤的 `status` 为 `completed` 来实现的。
- **并行任务实现**:
  - `parallel` 类型的步骤包含一个 `sub_tasks` 数组。Agent 会并发执行所有子任务，并在所有子任务成功后，将该并行步骤本身标记为 `completed`。

## 用户偏好与项目特点
- **偏好明确的工作流定义**: 用户倾向于将一个复杂的任务流程，通过结构化的方式（如JSON）进行清晰、完整的定义。
- **重视可追溯性**: 完整的执行记录（步骤、状态、时间戳）和最终的摘要报告是用户的关键需求。
- **支持人工干预**: 工作流设计需要包含人工审批（`approval`）等节点，允许在关键步骤暂停并等待外部确认。
- **模块化步骤**: 用户将工作流分解为具有不同类型（`action`, `condition` 等）的独立步骤，便于理解和管理。