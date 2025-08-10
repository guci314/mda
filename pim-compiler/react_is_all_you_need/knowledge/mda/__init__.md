# MDA (Model-Driven Architecture) 知识包

模型驱动架构相关的知识，包括PIM到PSM转换、代码生成、调试和协调流程。

## 包含的知识模块

### 核心转换模块

#### pim_to_psm_knowledge.md
- **用途**: PIM（平台无关模型）到PSM（平台特定模型）的转换
- **适用对象**: 模型转换Agent
- **主要内容**: 转换规则、映射策略、模型验证

### 代码生成模块

#### generation_knowledge.md
- **用途**: 通用代码生成策略
- **适用对象**: 代码生成Agent
- **主要内容**: 生成原则、代码结构、质量保证

#### fastapi_generation_knowledge.md
- **用途**: FastAPI应用代码生成
- **适用对象**: FastAPI生成Agent
- **主要内容**: FastAPI项目结构、API设计、数据模型生成

#### generate_fastapi_app.md
- **用途**: FastAPI应用生成的具体实现
- **适用对象**: FastAPI生成Agent
- **主要内容**: 完整的生成流程、模板定义、测试生成

### 调试模块

#### debugging_complete.md
- **用途**: 完整调试知识库（整合版）
- **适用对象**: 调试Agent
- **主要内容**: 
  - 完整调试工作流程和执行模板
  - Python语法错误处理策略
  - 错误模式识别与解决方案
  - 调试笔记维护规范
  - 测试结果解析方法
  - 与协调Agent的交互协议

#### debugging_validation.md
- **用途**: 调试验证增强策略
- **适用对象**: 调试Agent
- **主要内容**:
  - 严格的成功判定标准
  - 失败分类与处理策略
  - 防止过早退出机制
  - 进度追踪和诚实报告

### 协调模块

#### coordinator_workflow.md
- **用途**: MDA Pipeline协调工作流
- **适用对象**: 协调Agent
- **主要内容**: TODO管理、子Agent调用、循环控制

## 使用建议

### 1. 生成Agent配置
```python
# 专注于代码生成
knowledge_files = [
    "knowledge/mda/generation_knowledge.md",
    "knowledge/mda/fastapi_generation_knowledge.md",
    "knowledge/mda/generate_fastapi_app.md"
]
```

### 2. 调试Agent配置
```python
# 完整的调试能力（使用合并版）
knowledge_files = [
    "knowledge/mda/debugging_complete.md"
]
```

### 3. 协调Agent配置
```python
# Pipeline协调
knowledge_files = [
    "knowledge/mda/coordinator_workflow.md"
]
```

### 4. 完整MDA Pipeline配置
```python
# 包含所有MDA知识
knowledge_files = [
    "knowledge/mda/"  # 导入整个包
]
```

## 模块依赖关系

```
coordinator_workflow.md
    ├── generation_knowledge.md
    │   ├── fastapi_generation_knowledge.md
    │   └── generate_fastapi_app.md
    └── debugging_complete.md (整合了所有调试知识)
```

## 最佳实践

### 单一职责
- 生成Agent只负责生成，不做调试
- 调试Agent只负责修复，不做生成
- 协调Agent只负责协调，不做具体实现

### 知识组合
- 根据Agent角色选择合适的知识模块
- 避免加载不必要的知识，减少上下文负担
- 相关模块可以组合使用

### 执行流程
1. **模型转换**: pim_to_psm_knowledge.md
2. **代码生成**: generation + fastapi模块
3. **测试验证**: 协调Agent执行
4. **错误修复**: debugging模块
5. **循环迭代**: coordinator_workflow.md控制

## 注意事项

1. **工具依赖**: 调试模块需要配合debug_tools使用
2. **知识优先级**: 优先使用专门的知识模块而非通用模块
3. **版本兼容**: 确保知识文件与Agent工具版本匹配
4. **性能考虑**: 大型知识文件可能影响响应速度

## 更新历史

- 2024-01: 初始版本，包含基础MDA流程
- 2024-08: 添加调试工作流和协调工作流
- 2024-08: 优化知识模块组织结构
- 2024-08: 合并调试知识文件为 debugging_complete.md