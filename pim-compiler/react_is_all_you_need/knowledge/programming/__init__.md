# Programming 知识包

编程语言、框架和代码生成相关的专业知识。

## 包含的知识文件

### python_programming_knowledge.md
- **用途**: Python编程最佳实践和规范
- **适用对象**: 编写Python代码的agent
- **主要内容**: Python语法、惯用法、性能优化

### fastapi_generation_knowledge.md
- **用途**: FastAPI框架的代码生成知识
- **适用对象**: 生成Web API的agent
- **主要内容**: FastAPI路由、模型、中间件等

### pim_to_psm_knowledge.md
- **用途**: PIM到PSM的转换规则
- **适用对象**: 模型转换相关的agent
- **主要内容**: MDA架构中的模型转换策略

### 编程规范知识.md
- **用途**: 通用编程规范和代码风格
- **适用对象**: 所有编写代码的agent
- **主要内容**: 命名规范、代码组织、注释规范

## 使用建议

1. **代码生成agent**: 应导入相应语言和框架的知识
2. **代码审查agent**: 应导入编程规范知识
3. **可组合使用**: 多个知识文件可以组合使用

## 示例用法

```python
# Python开发agent
knowledge_files = [
    "knowledge/programming/python_programming_knowledge.md",
    "knowledge/programming/编程规范知识.md"
]

# FastAPI开发agent
knowledge_files = [
    "knowledge/programming/python_programming_knowledge.md",
    "knowledge/programming/fastapi_generation_knowledge.md"
]

# 模型转换agent
knowledge_files = [
    "knowledge/programming/pim_to_psm_knowledge.md"
]
```

## 扩展指南

添加新的编程语言或框架知识时：
1. 文件命名: `{语言/框架}_knowledge.md`
2. 内容结构: 包含基础知识、最佳实践、常见陷阱
3. 示例代码: 提供实用的代码示例