# TODO App

## 项目介绍

这是一个简单的TODO应用，使用Python实现。允许用户管理任务列表，包括添加新任务、删除任务和标记任务为完成。

## 功能特性

- **添加任务**：向任务列表中添加新的待办事项。
- **删除任务**：根据索引删除指定的任务。
- **标记完成**：将指定的任务标记为已完成。
- **任务列表管理**：维护一个任务列表，每个任务包含任务描述和完成状态。

## 安装说明

1. 确保您的系统已安装Python 3.x。
2. 下载或克隆项目到本地。
3. 无需额外依赖，直接运行Python脚本。

## 使用方法

此应用目前以类库形式提供。您可以在Python脚本中使用`TodoApp`类：

```python
from todo_app import TodoApp

app = TodoApp()

# 添加任务
app.add_task("Buy groceries")

# 标记任务完成（假设索引为0）
app.mark_complete(0)

# 删除任务（假设索引为0）
app.delete_task(0)

# 查看任务列表
print(app.tasks)
```

注意：当前版本没有命令行界面（CLI）。如果需要CLI，可以扩展代码添加命令行参数处理。

## 测试说明

项目使用Python的unittest框架进行单元测试。

运行测试：

```bash
cd demo_project
python -m unittest test_todo_app.py
```

或使用pytest（如果安装）：

```bash
pytest test_todo_app.py
```

测试覆盖了添加任务、删除任务、标记完成以及边界情况。

## 项目结构

- `todo_app.py`: 主应用文件，包含`TodoApp`类及其方法。
- `test_todo_app.py`: 单元测试文件，包含对应用功能的测试用例。
- `__pycache__/`: Python字节码缓存目录（自动生成）。

## 许可证

此项目采用MIT许可证。详情请见LICENSE文件（如果有）。