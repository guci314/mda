# Core 知识包

核心系统知识，包含所有agent都应该了解的基础功能。

## 包含的知识文件

### system_prompt.md
- **用途**: React Agent的系统提示词模板
- **适用对象**: 所有agent
- **主要内容**: 定义agent的基本行为准则和能力边界

### data_management.md
- **用途**: 数据管理和存储策略
- **适用对象**: 需要进行数据操作的agent
- **主要内容**: 文件操作、数据持久化、缓存策略

### world_overview_generation.md
- **用途**: 生成项目全局概览的方法
- **适用对象**: 分析和理解项目结构的agent
- **主要内容**: 使用git ls-files和eza命令分析项目结构

## 使用建议

1. **必须导入**: 所有agent都应该导入 `system_prompt.md`
2. **按需导入**: 根据agent的具体职责选择其他文件
3. **优先级高**: core包中的知识优先级最高，与其他知识冲突时以core为准

## 示例用法

```python
# 基础agent配置
knowledge_files = [
    "knowledge/core/system_prompt.md"
]

# 需要分析项目的agent
knowledge_files = [
    "knowledge/core/system_prompt.md",
    "knowledge/core/world_overview_generation.md"
]

# 需要数据操作的agent
knowledge_files = [
    "knowledge/core/"  # 导入所有core知识
]
```