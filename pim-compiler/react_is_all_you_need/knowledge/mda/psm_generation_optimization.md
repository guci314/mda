# PSM生成优化知识

## 高效生成PSM文档的方法

### 原则：一次性生成，避免多次追加

对于PSM这种结构化文档，应该：

1. **先构建完整内容** - 在Python中构建完整的文档字符串
2. **一次性写入** - 使用write_file一次写入所有内容
3. **如果超过4000字符** - 使用Python脚本直接写入，不受限制

### 推荐的PSM生成流程

```python
# 第1步：记录精确的开始时间
import time
start_time = time.time()

# 第2步：读取PIM文件
pim_content = read_file(pim_file)

# 第3步：构建完整的PSM内容
psm_content = f"""
# Platform Specific Model (PSM)

## 1. Domain Models
{generate_domain_models(pim_content)}

## 2. Service Layer  
{generate_service_layer(pim_content)}

## 3. REST API Design
{generate_api_design(pim_content)}

## 4. Application Configuration
{generate_config(pim_content)}

## 5. Testing Specifications
{generate_testing(pim_content)}
"""

# 第4步：使用Python直接写入（不受4000字符限制）
execute_command(f'''python3 -c "
content = '''{psm_content}'''
with open('psm.md', 'w') as f:
    f.write(content)
"''')

# 第5步：验证并报告耗时
elapsed = time.time() - start_time
print(f"PSM生成完成，耗时: {elapsed:.2f}秒")
```

### 文件操作最佳实践

详见 `knowledge/large_file_handling.md` 了解大文件处理的完整指南。

核心原则：
- ✅ 一次性生成完整内容
- ✅ 使用Python脚本处理大文档（>4KB）
- ✅ 使用Here Document处理特殊字符
- ❌ 避免逐行echo追加

## 时间记录最佳实践

### 必须记录精确时间

```python
# 开始任务时
import time
start_time = time.time()

# 或使用datetime
from datetime import datetime
start_time = datetime.now()

# 任务完成时
elapsed = time.time() - start_time
print(f"任务耗时: {elapsed:.2f}秒")
```

### 在笔记中记录

```python
# task_process.md中记录
write_file('.notes/task_process.md', f"""
# 任务过程
- 开始时间戳: {start_time}
- 开始时间: {datetime.fromtimestamp(start_time)}
- 任务: 生成PSM文档
""")
```

## PSM生成检查清单

生成PSM时，按以下步骤执行：

1. ✅ 记录精确开始时间 `start_time = time.time()`
2. ✅ 读取完整PIM文件
3. ✅ 构建完整PSM内容（所有5个章节）
4. ✅ 一次性写入文件
5. ✅ 验证所有章节存在
6. ✅ 计算并报告耗时

## 性能目标

- PSM生成应在 **5轮以内** 完成
- 执行时间应在 **30秒以内**
- 避免超过10次工具调用