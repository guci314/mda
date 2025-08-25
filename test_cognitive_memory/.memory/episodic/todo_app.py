# 待办事项应用

import json
import os
from datetime import datetime

TASKS_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

def add_task(description):
    tasks = load_tasks()
    task = {
        'id': len(tasks) + 1,
        'description': description,
        'completed': False,
        'created_at': datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    return task

def list_tasks():
    return load_tasks()

def complete_task(task_id):
    tasks = load_tasks()
    for task in tasks:
        if task['id'] == task_id:
            task['completed'] = True
            save_tasks(tasks)
            return task
    return None

def delete_task(task_id):
    tasks = load_tasks()
    tasks = [task for task in tasks if task['id'] != task_id]
    # 重新编号
    for i, task in enumerate(tasks):
        task['id'] = i + 1
    save_tasks(tasks)
    return tasks