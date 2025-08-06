# Coordination 知识包

多agent协作、任务委派和结果整合相关的知识。

## 包含的知识文件

### delegation_best_practices.md
- **用途**: 任务委派的最佳实践
- **适用对象**: 需要协调其他agent的管理型agent
- **主要内容**: 任务分配策略、委派原则、监督方法

### context_passing.md
- **用途**: agent间上下文传递策略
- **适用对象**: 所有参与协作的agent
- **主要内容**: 上下文格式、传递机制、信息保真

### result_extraction.md
- **用途**: 从agent输出中提取关键结果
- **适用对象**: 需要解析其他agent输出的agent
- **主要内容**: 结果解析、格式转换、错误处理

### efficient_coordination.md
- **用途**: 高效的多agent协作模式
- **适用对象**: 参与复杂协作任务的agent
- **主要内容**: 协作模式、通信优化、冲突解决

## 使用建议

1. **管理型agent**: 应导入所有协作知识
2. **执行型agent**: 重点关注 `context_passing.md`
3. **集成型agent**: 重点关注 `result_extraction.md`

## 示例用法

```python
# 项目管理agent
knowledge_files = [
    "knowledge/coordination/"  # 需要所有协作知识
]

# 普通执行agent
knowledge_files = [
    "knowledge/coordination/context_passing.md"
]

# 结果汇总agent
knowledge_files = [
    "knowledge/coordination/result_extraction.md",
    "knowledge/coordination/efficient_coordination.md"
]
```

## 协作原则

1. **明确职责**: 每个agent的职责必须清晰定义
2. **标准接口**: 使用统一的输入输出格式
3. **容错设计**: 考虑agent失败的情况
4. **性能优化**: 减少不必要的通信开销