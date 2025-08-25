# 后置断言验证强制执行知识

## 核心原则

**每个Agent必须验证成功条件，这是不可协商的纪律**

## 验证的三个阶段

### 1. 识别阶段
在开始执行任务前，识别所有成功判定条件：
- 扫描"成功判定条件"、"后置断言"、"成功条件"等关键词
- 提取具体的验证指标
- 理解每个条件的含义

### 2. 执行阶段
执行任务时保持验证意识：
- 记录每个生成的文件路径
- 记录关键操作的结果
- 为验证阶段准备数据

### 3. 验证阶段【强制】
完成任务后立即验证：
```
生成完成 → 验证条件 → 报告结果
         ↑_____不满足____↓
```

## 验证方法矩阵

| 条件类型 | 验证工具 | 验证命令示例 |
|---------|---------|-------------|
| 文件存在 | list_directory/read_file | `list_directory("app/")` |
| 内容包含 | read_file + 检查 | `"章节名" in read_file("file.md")` |
| 目录结构 | list_directory递归 | 遍历检查所有子目录 |
| 测试通过 | execute_command | `pytest` |
| 服务运行 | execute_command | `curl localhost:8000` |

## 失败处理策略

### 部分成功
- 识别缺失部分
- 继续生成缺失内容
- 重新验证

### 完全失败
- 分析失败原因
- 如果是能力问题：报告失败
- 如果是疏忽：重新执行

### 无法验证
- 明确说明无法验证的原因
- 请求人工确认

## 验证报告模板

```markdown
=== 任务完成验证报告 ===

📋 成功条件检查：
✅ 条件1：[描述] - 已满足
✅ 条件2：[描述] - 已满足
❌ 条件3：[描述] - 未满足
  原因：[具体原因]
  
📊 完成度：2/3 (66.7%)

🔄 后续行动：
- [如果有未满足条件，说明补救措施]
```

## 常见错误模式

### ❌ 错误1：假设性验证
```python
# 错误：假设文件已生成
print("已生成app/main.py")

# 正确：实际验证
if read_file("app/main.py"):
    print("✅ 验证：app/main.py存在")
```

### ❌ 错误2：选择性验证
```python
# 错误：只验证部分条件
check_file1()  # 验证了
# file2和file3没验证就报告成功

# 正确：验证所有条件
for file in required_files:
    verify_exists(file)
```

### ❌ 错误3：验证时机错误
```python
# 错误：先报告成功再验证
print("任务完成")
verify_conditions()  # 太晚了

# 正确：先验证再报告
if verify_conditions():
    print("任务完成")
```

## 与其他知识的关系

### adaptive_task_decomposition.md
- 如果验证失败，触发自适应分解
- 验证结果决定是否需要分解

### generation_knowledge.md
- 生成知识中的第0条强调验证
- 本知识是对第0条的详细展开

### debugging_knowledge.md
- 调试Agent依赖生成Agent的验证结果
- 准确的验证避免误导调试

## 执行示例

### 示例1：PSM生成验证
```python
# 任务：生成PSM
generate_psm()

# 立即验证
psm_content = read_file("blog_psm.md")
required_sections = ["Domain Models", "Service Layer", ...]

missing = []
for section in required_sections:
    if section not in psm_content:
        missing.append(section)

if missing:
    # 继续生成缺失章节
    for section in missing:
        generate_section(section)
    # 再次验证
    verify_again()
else:
    print("✅ PSM生成完整")
```

### 示例2：代码生成验证
```python
# 任务：生成FastAPI代码
generate_code()

# 验证文件结构
files = {
    "app/main.py": False,
    "app/models.py": False,
    "tests/test_main.py": False
}

for file in files:
    if check_file_exists(file):
        files[file] = True

completion_rate = sum(files.values()) / len(files)

if completion_rate < 1.0:
    missing_files = [f for f, exists in files.items() if not exists]
    print(f"⚠️ 缺失文件: {missing_files}")
    # 生成缺失文件
    for file in missing_files:
        generate_file(file)
```

## 关键提醒

1. **验证是义务，不是建议**
2. **没有验证的成功是虚假的成功**
3. **宁可报告失败，不要虚假成功**
4. **验证成本很低，失败成本很高**
5. **每个Agent都要为自己的输出负责**

## 实施检查清单

- [ ] 任务开始时识别了所有成功条件？
- [ ] 执行过程中记录了关键路径？
- [ ] 完成后使用工具验证了每个条件？
- [ ] 验证失败时采取了补救措施？
- [ ] 最终报告准确反映了实际完成情况？

记住：**验证不是额外工作，而是工作的一部分**。