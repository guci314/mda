# React Agent 提示词体系说明

## 概述

React Agent 使用两层提示词体系：
1. **系统提示词** - 定义 Agent 的基本行为
2. **知识文件** - 提供额外的领域知识

## 系统提示词

### 配置方式
```python
config = ReactAgentConfig(
    work_dir="./workspace",
    system_prompt_file="knowledge/system_prompt.md"  # 默认值
)
```

### 默认文件
- 文件路径：`knowledge/system_prompt.md`
- 内容：通用的任务执行指导，包括：
  - 立即执行原则
  - 工具使用方法
  - 推理策略（猜想-验证、退一步思考）
  - Python 文件命名规范
  - 项目分析最佳实践
  - 搜索技巧

### 备用提示词
如果文件不存在，会使用内置的备用提示词（已更新为简洁版本）。

## 知识文件

### 配置方式
```python
config = ReactAgentConfig(
    work_dir="./workspace",
    knowledge_files=["knowledge/system_prompt.md"]  # 新的默认值
)
```

### 默认文件
- 原默认：`knowledge/综合知识.md`（包含 FastAPI、PIM/PSM 等专业知识）
- 新默认：`knowledge/system_prompt.md`（优秀的通用系统提示词）

### 知识文件内容
知识文件会被注入到系统提示词之后，作为"领域知识"部分。

## 完整的提示词结构

最终 Agent 使用的提示词由以下部分组成：

```
1. 系统提示词（从 system_prompt_file 加载）
2. 工作目录信息
3. 私有数据区信息
4. 提取的知识（如果有）
5. 领域知识（从 knowledge_files 加载）
```

## 推荐配置

### 通用 Agent
```python
config = ReactAgentConfig(
    work_dir="./workspace",
    # 使用默认的 system_prompt_file 和 knowledge_files
)
```

### 专业 Agent
```python
config = ReactAgentConfig(
    work_dir="./workspace",
    knowledge_files=[
        "knowledge/system_prompt.md",
        "knowledge/python_programming_knowledge.md",
        "knowledge/your_domain_knowledge.md"
    ]
)
```

### 自定义 Agent
```python
config = ReactAgentConfig(
    work_dir="./workspace",
    system_prompt_file="custom/my_system_prompt.md",
    knowledge_files=["custom/my_knowledge.md"]
)
```

## 注意事项

1. **系统提示词**定义基本行为，应该保持通用
2. **知识文件**提供专业知识，可以根据任务定制
3. 两者配合使用，实现灵活的 Agent 配置
4. 支持 include 机制，可以在知识文件中引用其他文件