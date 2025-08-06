# 知识库索引

本知识库包含React Agent系统所需的各类知识文件，按照Python包的概念组织成模块化结构。

## 知识包结构

### core/ - 核心知识
系统核心功能相关的基础知识，所有agent都应该了解。

### programming/ - 编程知识
编程语言、框架、代码生成相关的专业知识。

### workflow/ - 工作流知识
任务执行模式、流程控制相关的知识。

### coordination/ - 协作知识
多agent协作、任务委派、上下文传递相关的知识。

### output/ - 输出知识
输出格式化、展示模板相关的知识。

### best_practices/ - 最佳实践
各种编程和系统设计的最佳实践。

### experimental/ - 实验性知识
实验性或临时的知识文件，可能会调整或移除。

## 使用方式

### 导入特定文件
```python
knowledge_files = [
    "knowledge/core/system_prompt.md",
    "knowledge/programming/python_programming_knowledge.md"
]
```

### 导入整个模块
```python
# 导入core模块的所有知识文件
knowledge_files = ["knowledge/core/"]
```

### 混合导入
```python
knowledge_files = [
    "knowledge/core/",  # 导入整个core模块
    "knowledge/best_practices/absolute_path_usage.md"  # 导入特定文件
]
```

## 维护指南

1. 新增知识文件时，放入最合适的目录
2. 如果现有目录都不合适，考虑创建新目录
3. 每个目录都应有自己的 `__init__.md` 说明文件
4. 定期清理 experimental/ 目录中的内容