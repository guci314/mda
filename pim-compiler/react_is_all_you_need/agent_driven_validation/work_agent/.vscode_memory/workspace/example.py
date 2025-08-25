"""
任务管理系统使用示例
"""

from task_manager import TaskManager
from task import TaskStatus

def main():
    # 创建任务管理器
    tm = TaskManager()
    
    # 添加一些任务
    task1 = tm.add_task("完成项目计划", "制定下一季度的项目开发计划")
    task2 = tm.add_task("编写文档", "为新功能编写使用文档")
    task3 = tm.add_task("代码审查", "审查团队成员提交的代码")
    
    print("=== 添加任务后 ===")
    for task in tm.list_tasks():
        print(f"{task}")
    
    # 更新任务状态
    tm.update_task(task1.id, status=TaskStatus.IN_PROGRESS)
    tm.update_task(task2.id, status=TaskStatus.COMPLETED)
    
    print("\n=== 更新状态后 ===")
    for task in tm.list_tasks():
        print(f"{task}")
    
    # 按状态查看任务
    print("\n=== 已完成的任务 ===")
    completed = tm.list_tasks_by_status(TaskStatus.COMPLETED)
    for task in completed:
        print(f"{task}")
    
    print("\n=== 进行中的任务 ===")
    in_progress = tm.list_tasks_by_status(TaskStatus.IN_PROGRESS)
    for task in in_progress:
        print(f"{task}")
    
    # 删除任务
    tm.remove_task(task3.id)
    print(f"\n=== 删除任务后，剩余任务数: {tm.get_task_count()} ===")
    for task in tm.list_tasks():
        print(f"{task}")

if __name__ == "__main__":
    main()