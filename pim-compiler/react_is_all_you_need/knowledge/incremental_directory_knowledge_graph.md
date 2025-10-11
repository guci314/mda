# 增量式目录知识图谱转换

## 问题分析

对于包含大量文件的目录，一次性处理所有文件会导致：
- 内存使用过高
- 处理时间过长
- 容易因单个文件错误导致整个处理失败

## 增量处理架构

### 1. 分批处理策略
```python
# 将文件分批处理，每批处理N个文件
batch_size = 100  # 每批处理的文件数量

for batch_files in split_into_batches(all_files, batch_size):
    process_batch(batch_files)
    save_progress()  # 保存中间结果
```

### 2. 状态管理
- **进度跟踪**: 记录已处理的文件
- **断点续传**: 支持从上次中断处继续
- **错误隔离**: 单个文件错误不影响整体处理

### 3. 内存优化
- **流式处理**: 逐个文件读取和处理
- **及时释放**: 处理完立即释放内存
- **缓存控制**: 控制同时处理的文件数量

## 改进后的函数设计

```python
def directory_to_knowledge_graph_incremental(
    directory_path: str,
    output_name: str = "directory_knowledge_graph",
    include_content: bool = False,
    max_depth: int = 3,
    file_types: list = ["md", "py", "json", "txt", "yaml", "yml"],
    batch_size: int = 100,
    resume: bool = False
) -> dict:
    """
    增量式目录知识图谱转换
    
    参数:
    - batch_size: 每批处理的文件数量
    - resume: 是否从上次中断处继续
    """
```

## 执行流程

### 步骤1: 初始化
- 创建输出文件
- 加载进度状态（如果resume=True）
- 构建知识图谱基础结构

### 步骤2: 文件发现
- 扫描目录结构
- 生成待处理文件列表
- 过滤已处理的文件

### 步骤3: 分批处理
```python
for batch_index, file_batch in enumerate(file_batches):
    # 处理当前批次
    batch_entities = process_file_batch(file_batch, include_content)
    
    # 添加到知识图谱
    knowledge_graph.extend(batch_entities)
    
    # 保存进度
    save_progress(batch_index, processed_files)
    
    # 定期保存完整结果
    if batch_index % 10 == 0:
        save_knowledge_graph(knowledge_graph, output_name)
```

### 步骤4: 完成处理
- 保存最终知识图谱
- 清理临时文件
- 生成统计报告

## 状态文件格式

```json
{
  "progress": {
    "total_files": 1500,
    "processed_files": 450,
    "current_batch": 4,
    "last_processed": "file_450.py",
    "start_time": "2024-01-01T10:00:00",
    "last_update": "2024-01-01T10:30:00"
  },
  "errors": [
    {
      "file": "corrupted_file.txt",
      "error": "UnicodeDecodeError",
      "timestamp": "2024-01-01T10:15:00"
    }
  ]
}
```

## 错误处理策略

### 1. 错误隔离
- 单个文件错误不影响其他文件
- 记录错误信息继续处理
- 提供错误报告

### 2. 重试机制
- 可配置重试次数
- 跳过持续失败的文件
- 记录重试历史

### 3. 恢复策略
- 从进度文件恢复
- 跳过已处理的文件
- 重新处理失败的文件（可选）

## 性能优化

### 1. 内存优化
- 分批处理控制内存使用
- 及时释放文件内容
- 使用生成器避免一次性加载

### 2. I/O优化
- 异步文件读取
- 批量写入操作
- 缓存目录结构信息

### 3. 并行处理
- 多线程处理不同批次
- 控制并发数量
- 避免文件锁冲突

## 输出文件结构

### 增量输出
- `{output_name}_incremental.jsonld` - 增量更新的知识图谱
- `{output_name}_progress.json` - 处理进度状态
- `{output_name}_errors.json` - 错误报告

### 最终输出
- `{output_name}.jsonld` - 完整知识图谱
- `{output_name}_summary.md` - 最终摘要
- `{output_name}_stats.json` - 统计信息

## 使用场景

### 1. 大目录处理
- 处理包含数千文件的目录
- 内存使用保持稳定
- 支持长时间运行

### 2. 网络存储
- 处理网络文件系统
- 处理速度较慢的存储
- 支持断点续传

### 3. 生产环境
- 7x24小时运行
- 自动错误恢复
- 进度监控和报告