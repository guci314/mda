# 绝对路径使用规范

## 核心原则

在多 Agent 协作环境中，**必须使用绝对路径**来确保文件操作的一致性。

## 强制规则

### 规则1：文件操作必须使用绝对路径

当你需要创建、读取、搜索或操作文件时：

1. **如果你的 specification 中包含工作目录信息**，使用该路径：
   ```
   工作目录：/home/user/project/output/shared_workspace
   ```

2. **文件操作示例**：
   ```python
   # ❌ 错误：使用相对路径
   write_file("math_utils.py", content)
   read_file("./test.py")
   search_files("*.py", ".")
   
   # ✅ 正确：使用绝对路径
   write_file("/home/user/project/output/shared_workspace/math_utils.py", content)
   read_file("/home/user/project/output/shared_workspace/test.py")
   search_files("*.py", "/home/user/project/output/shared_workspace")
   ```

### 规则2：私有数据区域使用绝对路径

访问你的私有数据区域时：
```python
# ❌ 错误
write_file(".agent_data/my_agent/workflow.bpmn", content)

# ✅ 正确
write_file("/home/user/project/output/shared_workspace/.agent_data/my_agent/workflow.bpmn", content)
```

### 规则3：搜索文件时指定绝对目录

使用 search_files 工具时：
```python
# ❌ 错误：使用当前目录
search_files("math_utils.py")
search_files("*.py", ".")

# ✅ 正确：使用绝对路径
search_files("math_utils.py", "/home/user/project/output/shared_workspace")
search_files("*.py", "/home/user/project/output/shared_workspace")
```

## 实用技巧

### 1. 从 specification 提取工作目录

如果你的 specification 包含工作目录信息，例如：
```
"专门审查代码质量，提供改进建议和最佳实践指导。工作目录：/home/user/project/output/shared_workspace"
```

你应该：
1. 识别工作目录路径
2. 在所有文件操作中使用这个绝对路径

### 2. 构建完整路径

当需要操作子目录中的文件时：
```python
# 基础目录
base_dir = "/home/user/project/output/shared_workspace"

# 构建完整路径
file_path = f"{base_dir}/src/utils/helper.py"
test_path = f"{base_dir}/tests/test_helper.py"
```

### 3. 列出目录内容时使用绝对路径

```python
# ❌ 错误
list_directory(".")
list_directory("src")

# ✅ 正确
list_directory("/home/user/project/output/shared_workspace")
list_directory("/home/user/project/output/shared_workspace/src")
```

## 错误处理

如果遇到"文件未找到"错误：

1. **检查是否使用了相对路径**
2. **确认工作目录的绝对路径**
3. **使用 list_directory 确认文件位置**：
   ```python
   list_directory("/home/user/project/output/shared_workspace")
   ```

## 协作最佳实践

在多 Agent 协作环境中：

1. **所有 Agent 使用相同的绝对基础路径**
2. **在任务描述中明确文件的完整路径**
3. **避免依赖"当前目录"的概念**
4. **始终验证文件是否存在于预期位置**

## 示例场景

### 场景1：代码生成后的审查

代码生成 Agent：
```python
write_file("/home/user/project/output/shared_workspace/math_utils.py", code_content)
```

代码审查 Agent：
```python
# 搜索文件
search_files("math_utils.py", "/home/user/project/output/shared_workspace")

# 读取文件
read_file("/home/user/project/output/shared_workspace/math_utils.py")
```

### 场景2：测试文件的创建和运行

测试创建：
```python
write_file("/home/user/project/output/shared_workspace/test_math.py", test_content)
```

测试运行：
```python
execute_command("python /home/user/project/output/shared_workspace/test_math.py")
```

## 记住

**绝对路径是多 Agent 协作成功的关键！**