# 知识库

## 元知识
- **Sequential Thinking模式**：使用thought_chain.json结构化思维过程，包含thoughts数组、branches分支、conclusions结论
- **需求分析方法**：将需求分解为功能需求（实时个性化推荐）和非功能需求（千万级用户、<100ms延迟、CTR提升20%）
- **技术方案探索**：使用分支机制并行探索不同技术栈（协同过滤 vs 深度学习），每个分支包含置信度评估
- **决策验证方法**：通过revisions机制修正错误分析，确保最终决策有理有据
- **架构文档生成**：从思维链中提取关键决策点，生成结构化的recommendation_system.md
- **文件操作模式**：使用write_file/read_file进行完整文件读写，避免部分更新风险
- **状态追踪**：通过status字段（thinking/branching/concluding/completed）跟踪思维过程阶段
- **强制完成机制与自检循环**：任务必须严格按照指定步骤和数量完成（如8个thoughts），并通过内部自检循环（如`while not all_conditions_met(): ...`）反复验证所有成功条件，确保任务完整性，宁可超时也不返回未完成状态。
- **JSON更新新方法**：采用全量覆盖写入确保格式完整，避免部分更新导致的JSON破坏
- **工具缺失处理**：当指定工具不可用时（如str_replace_editor），切换到可靠的全量更新模式
- **验证驱动开发**：任务返回前必须严格对照预设的“验证清单”（包含明确的“成功条件”和“失败标志”）进行自检，确保所有条件满足。这是一种“门禁式”检查，不满足则循环修正，直到满足为止。

## 原理与设计
- **实时推荐系统核心原则**：
  - 延迟优先：推荐延迟<100ms要求缓存预计算和近似算法
  - 规模设计：千万级用户需要分布式架构和水平扩展
  - 效果导向：CTR提升20%需要A/B测试框架和持续优化
- **技术选型权衡**：
  - 协同过滤：实现简单但冷启动问题严重，延迟<50ms
  - 深度学习：效果好但计算复杂度高，延迟80-120ms
  - 混合方案：平衡效果与性能的最佳选择
- **架构分层设计**：
  - 召回层：快速筛选候选集（<50ms），使用ItemCF+缓存
  - 排序层：精准排序（<30ms），使用Wide&Deep模型
  - 重排层：业务规则调整（<20ms），实时过滤和多样性
- **性能优化策略**：预计算+缓存+近似算法是满足延迟要求的关键
- **冷启动解决方案**：使用内容特征+热门商品兜底策略
- **混合架构优势**：结合协同过滤的实时性和深度学习的精准性，通过分层架构实现延迟与效果的平衡
- **决策流程**：遵循从需求分析→技术分支→性能对比→效果评估→最终决策的完整闭环。例如，在推荐系统设计中，此流程体现为：分析需求 -> 设定CF和DL两个技术分支 -> 对比延迟和CTR潜力 -> 决策采用分层混合架构。

## 接口与API
- **thought_chain.json结构**：
  ```json
  {
    "session_id": "string",
    "created_at": "ISO8601",
    "total_thoughts_estimate": "number",
    "current_thought": "number",
    "status": "thinking|branching|concluding|completed",
    "thoughts": [{
      "id": "number",
      "content": "string",
      "timestamp": "ISO8601",
      "type": "initial|branch|conclusion",
      "branch_id": "string|null",
      "confidence": 0-1,
      "tags": ["string"]
    }],
    "branches": {
      "branch_name": {
        "parent": "thought_id",
        "thoughts": ["thought_id"]
      }
    },
    "conclusions": {
      "main": "string",
      "alternatives": ["string"]
    }
  }
  ```
- **thought_chain.json内容约束**：
    - `thoughts`数组必须包含**精确数量**（如exactly 8）的元素。
    - 每个`thought`的`content`字段内容需完整（不少于50字）。
    - `conclusions.main`字段必须非空。
    - `status`字段最终必须设置为"completed"。
    - `current_thought`字段需随新增思考步骤严格递增。
- **工具函数**：
  - `write_file(path, content)`：全量覆盖写入文件
  - `read_file(path)`：读取完整文件内容
- **分支创建方法**：在branches对象中添加新分支，指定parent thought_id
- **状态更新流程**：按顺序添加thoughts→创建branches→更新conclusions→设置status=completed
- **任务验证清单（成功条件）**：任务返回前必须对照明确的验证清单进行自检，清单内容包括但不限于：
    - `thought_chain.json`存在且格式正确。
    - `thoughts`数组包含**精确数量**的元素（例如，exactly 8）。
    - `branches`对象包含所有指定分支（例如，"collaborative_filtering"和"deep_learning"）。
    - `conclusions.main`字段非空且包含最终决策。
    - `status`字段值为"completed"。
    - 所有必需的产出文件（如`recommendation_system.md`）已生成。
- **文档生成模板**：从thought_chain.json提取关键信息生成recommendation_system.md

## 实现细节（需验证）
- **文件结构**：
  - `output/react_sequential_thinking/thought_chain.json`：思维链存储文件
  - `output/react_sequential_thinking/recommendation_system.md`：架构文档
- **工作流程**：
  1. 初始化thought_chain.json，`status`为`thinking`。
  2. 通过`read_file`获取当前状态。
  3. 严格按顺序添加指定数量的thoughts，例如8个：需求分析 -> 分支点 -> 分支1分析 -> 分支2分析 -> 性能对比 -> 效果评估 -> 最终决策 -> 总结。
  4. 在对应步骤创建技术方案分支（如"collaborative_filtering"和"deep_learning"）。
  5. 在最后一个thought中，更新`conclusions.main`并设置`status`为`completed`。
  6. 所有thought完成后，通过`write_file`全量覆盖`thought_chain.json`。
  7. 基于最终的`thought_chain.json`生成`recommendation_system.md`。
- **状态管理**：`current_thought`字段需严格递增，`status`最终设为`completed`。
- **注意事项**：
  - 全量写入时需确保JSON格式正确
  - `thoughts`数组必须包含完整内容（>50字）
  - 每个分支需有对应的`parent` thought_id
- **文件操作顺序**：先`read_file`获取状态→在内存中修改数据结构→`write_file`全量更新。

## 用户偏好与项目特点
- **严格步骤执行**：必须完成所有指定思考步骤（如8步），不能减少或跳过。
- **验证驱动**：返回前需完成所有检查项，将“验证清单”作为任务完成的最终门禁。
- **容错要求**：当工具不可用时自动降级到安全模式（全量更新）。
- **完整性优先**：宁可超时也不返回未完成或部分完成的状态，通过自检循环确保所有成功条件达成。
- **架构设计模式**：推荐系统需包含召回/排序/重排三层。