# 知识函数：@directory_to_knowledge_graph

## 函数定义

```python
def directory_to_knowledge_graph(
    directory_path: str,
    output_name: str = "directory_knowledge_graph",
    include_content: bool = False,
    max_depth: int = 3,
    file_types: list = ["md", "py", "json", "txt", "yaml", "yml"]
) -> dict:
    """
    将目录结构转换为知识图谱
    
    参数:
    - directory_path: 要分析的目录路径
    - output_name: 输出文件的基础名称
    - include_content: 是否包含文件内容摘要
    - max_depth: 最大目录深度
    - file_types: 要处理的文件类型列表
    
    返回:
    - 包含生成文件路径的字典
    """
```

## 执行契约步骤

### 1. 验证目录存在性
- 检查目录是否存在
- 获取目录基本信息（大小、文件数量等）

### 2. 分析目录结构
- 递归遍历目录
- 识别文件和文件夹
- 提取文件元数据（大小、修改时间、类型）

### 3. 构建知识图谱结构
- 基于cnSchema定义实体和关系
- 创建目录、文件、内容等实体
- 建立层次关系和依赖关系

### 4. 生成输出文件
- JSON-LD格式的知识图谱
- 可视化摘要文档
- 统计报告

### 5. 验证结果
- 检查生成文件的完整性
- 验证知识图谱的结构正确性

## 输出文件

1. `{output_name}.jsonld` - 完整的知识图谱数据
2. `{output_name}_summary.md` - 可视化摘要
3. `{output_name}_stats.json` - 统计信息

## 实体映射

| 目录概念 | cnSchema映射 | 知识图谱实体 |
|---------|-------------|-------------|
| 目录 | DigitalDocument | Directory |
| 文件 | DigitalDocument | File |
| 文件类型 | Class | FileType |
| 文件内容 | Text | Content |
| 文件大小 | Property | size |
| 修改时间 | Property | dateModified |

## 关系定义

- `contains`: 目录包含文件/子目录
- `hasType`: 文件有类型
- `hasContent`: 文件有内容
- `hasSize`: 文件有大小
- `hasModificationTime`: 文件有修改时间