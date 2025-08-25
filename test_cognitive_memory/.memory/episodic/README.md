# 待办事项应用

一个简单的命令行待办事项应用，支持添加、列出、完成和删除任务。

## 功能特性

- 添加新任务
- 列出所有任务
- 标记任务为完成
- 删除任务
- 数据持久化存储

## 使用方法

```python
from todo_app import add_task, list_tasks, complete_task, delete_task

# 添加任务
add_task("学习Python")

# 列出所有任务
tasks = list_tasks()

# 完成任务
complete_task(1)

# 删除任务
delete_task(2)
```

## 数据存储

任务数据存储在 `tasks.json` 文件中。