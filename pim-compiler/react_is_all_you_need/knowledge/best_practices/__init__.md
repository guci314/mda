# Best Practices 知识包

各种编程和系统设计的最佳实践集合。

## 包含的知识文件

### absolute_path_usage.md
- **用途**: 文件路径处理的最佳实践
- **适用对象**: 所有涉及文件操作的agent
- **主要内容**: 绝对路径使用、路径规范化、跨平台兼容

### code_review_ethics.md
- **用途**: 代码审查的道德准则
- **适用对象**: 代码审查agent
- **主要内容**: 审查原则、反馈方式、改进建议

### test_execution_best_practices.md
- **用途**: 测试执行的最佳实践
- **适用对象**: 测试相关的agent
- **主要内容**: 测试策略、执行流程、结果分析

### simple_approach.md
- **用途**: 简单优先的设计原则
- **适用对象**: 所有agent
- **主要内容**: KISS原则、避免过度设计、迭代优化

## 使用建议

1. **通用原则**: `simple_approach.md` 适用于所有agent
2. **专项实践**: 根据agent职能选择相应的最佳实践
3. **组合使用**: 多个最佳实践可以同时应用

## 示例用法

```python
# 文件操作agent
knowledge_files = [
    "knowledge/best_practices/absolute_path_usage.md",
    "knowledge/best_practices/simple_approach.md"
]

# 代码审查agent
knowledge_files = [
    "knowledge/best_practices/code_review_ethics.md"
]

# 测试agent
knowledge_files = [
    "knowledge/best_practices/test_execution_best_practices.md"
]

# 通用开发agent
knowledge_files = [
    "knowledge/best_practices/"  # 应用所有最佳实践
]
```

## 核心原则

1. **实用性**: 最佳实践必须经过验证且实用
2. **可操作性**: 提供具体的操作指导
3. **适应性**: 可根据具体场景调整
4. **持续改进**: 根据新经验更新实践

## 贡献指南

添加新的最佳实践时：
1. 基于实际经验总结
2. 提供正反两面的例子
3. 说明适用场景和限制
4. 包含可度量的改进指标