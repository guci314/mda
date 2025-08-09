# 知识库

## 元知识
- **Sequential Thinking模式**：使用thought_chain.json结构化思维过程，包含thoughts数组、branches分支、conclusions结论
- **需求分析方法**：将需求分解为功能需求（实时个性化推荐）和非功能需求（千万级用户、<100ms延迟、CTR提升20%）
- **技术方案探索**：使用分支机制并行探索不同技术栈（协同过滤 vs 深度学习），每个分支包含置信度评估
- **决策验证方法**：通过revisions机制修正错误分析，确保最终决策有理有据
- **架构文档生成**：从思维链中提取关键决策点，生成结构化的recommendation_system.md
- **文件操作模式**：使用write_file/read_file/str_replace_editor进行文件管理，注意JSON格式和转义字符处理
- **状态追踪**：通过status字段（thinking/branching/concluding/completed）跟踪思维过程阶段
- **强制完成机制**：必须完成所有指定步骤（如8个thoughts）才能返回，避免半途而废

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

## 接口与API
- **thought_chain.json结构**：
  ```json
  {
    "session_id": "string",
    "created_at": "ISO8601",
    "total_thoughts_estimate": "number",
    "current_thought": "number",
    "status": "thinking|branching|concluding|completed",
    "thoughts": [{"id": "string", "content": "string", "confidence": 0-1}],
    "branches": {"branch_name": {"parent": "thought_id", "thoughts": [...]}},
    "conclusions": {"main": "string", "alternatives": ["string"]}
  }
  ```
- **工具函数**：
  - `write_file(path, content)`：写入文件（注意JSON转义）
  - `read_file(path)`：读取文件内容
  - `str_replace_editor(path, old_str, new_str)`：替换文件内容（需精确匹配）
- **分支创建方法**：在branches对象中添加新分支，指定parent thought_id
- **状态更新流程**：按顺序添加thoughts→创建branches→更新conclusions→设置status=completed

## 实现细节（需验证）
- **文件结构**：
  - `thought_chain.json`：思维链存储文件（可能已变化）
  - `recommendation_system.md`：最终架构文档（可能已变化）
- **工作流程**：
  1. 初始化thought_chain.json
  2. 按顺序添加thoughts到thoughts数组
  3. 使用branches创建技术方案分支
  4. 通过revisions修正错误
  5. 在conclusions中总结决策
- **状态管理**：status字段跟踪思维过程阶段
- **注意事项**：JSON文件更新时需注意转义字符和格式完整性
- **验证清单**：必须检查thoughts数量、分支完整性、conclusions填写、status状态

## 用户偏好与项目特点
- **文档要求**：每个重要决策必须记录在thought_chain.json中
- **性能指标**：严格延迟要求（<100ms）驱动技术选型
- **效果验证**：需要量化的CTR提升目标（20%）
- **探索模式**：鼓励并行探索多种技术方案而非单一路径
- **格式规范**：使用ISO8601时间戳，confidence值0-1范围
- **强制完成**：必须完成所有指定步骤，不接受部分完成