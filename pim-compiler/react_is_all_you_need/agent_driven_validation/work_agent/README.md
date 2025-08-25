# 任务管理系统

一个简单的任务管理系统，使用Python实现，包含任务的增删改查功能。

## 项目结构

- `task.py`: 任务数据模型
- `task_manager.py`: 任务管理器类
- `test_task_manager.py`: 单元测试文件
- `example.py`: 使用示例

## 功能特性

1. 添加任务
2. 删除任务
3. 更新任务（标题、描述、状态）
4. 查询任务
5. 按状态筛选任务
6. 获取任务统计信息

## 安装和运行

直接运行Python文件即可：

```bash
# 运行测试
python -m pytest test_task_manager.py -v

# 运行示例
python example.py
```

## 使用方法

```python
from task_manager import TaskManager
from task import TaskStatus

# 创建任务管理器
tm = TaskManager()

# 添加任务
task = tm.add_task("任务标题", "任务描述")

# 更新任务
tm.update_task(task.id, status=TaskStatus.COMPLETED)

# 查询任务
task = tm.get_task(task.id)

# 删除任务
tm.remove_task(task.id)
```

## 测试

运行测试确保所有功能正常工作：

```bash
python -m pytest test_task_manager.py -v
```

## 任务状态

- PENDING: 待处理
- IN_PROGRESS: 进行中
- COMPLETED: 已完成
- CANCELLED: 已取消