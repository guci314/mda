# 协调器：阻止测试文件修改

## 给调试Agent的任务模板

当调用调试Agent时，必须使用以下模板：

```python
task = """
修复应用代码中的错误，使所有测试通过。

⚠️ 绝对禁令：
1. 不允许修改 tests/ 目录下的任何文件
2. 不允许修改 conftest.py
3. 所有错误都必须在 app/ 目录中修复

具体要求：
- 如果看到404错误：在app/routers/创建缺失的路由文件
- 如果看到导入错误：修复app/目录中的导入
- 如果看到模型错误：修复app/models/中的定义

记住：测试定义了需求，你的任务是让功能满足测试。
"""
```

## 检查调试结果

调试Agent返回后，协调器必须检查：

```python
# 检查是否修改了测试文件
if "tests/" in debug_result or "conftest" in debug_result:
    print("错误：调试Agent修改了测试文件！")
    print("需要重新调用，明确禁止修改测试")
    # 重新调用，加强禁令
    task = "只允许修改app/目录。绝对禁止修改tests/目录..."
```

## 正确的调试方向

### 看到这个错误时：
```
InvalidRequestError: Table 'books' is already defined for this MetaData instance
```

### 正确的修复：
在 `app/models/` 中检查：
1. 是否有重复的模型定义
2. 是否有循环导入
3. Base类是否被多次实例化

### 错误的修复：
❌ 修改 conftest.py
❌ 修改测试的导入方式
❌ 改变测试的数据库配置