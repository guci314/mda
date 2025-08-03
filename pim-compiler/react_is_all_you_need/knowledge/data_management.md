# 数据区域使用指南

## 你的私有数据空间

每个 agent 在 `.agent_data/<agent_name>/` 下有独占的数据目录，用于存储工作过程中的数据和状态。这个空间：
- 只有你可以读写
- 在任务之间持久保存
- 不会被其他 agent 访问

## 推荐的数据组织方式

### 1. 结构化数据 - JSON
适用于：任务列表、配置、状态管理
```json
// todo.json - 任务追踪
{
  "tasks": [
    {
      "id": 1,
      "description": "分析用户需求",
      "status": "completed",
      "created_at": "2024-01-20T10:00:00Z"
    }
  ]
}

// state.json - 执行状态
{
  "current_step": "testing",
  "last_error": null,
  "retry_count": 0
}
```

### 2. 文档和笔记 - Markdown
适用于：分析记录、决策过程、知识积累
```markdown
# 项目分析笔记.md

## 2024-01-20
- 发现用户管理模块使用了 JWT 认证
- 数据库采用 PostgreSQL
- API 遵循 RESTful 规范

## 关键发现
1. 认证流程在 auth.py 中实现
2. 用户数据模型定义在 models/user.py
```

### 3. 表格数据 - CSV
适用于：指标记录、批量数据、报告
```csv
timestamp,operation,duration_ms,status
2024-01-20T10:00:00Z,compile,1250,success
2024-01-20T10:01:00Z,test,3400,success
```

### 4. 缓存数据
适用于：临时文件、中间结果
```
cache/
├── analysis_2024-01-20.json
├── symbols_extracted.txt
└── dependency_graph.dot
```

## 使用场景示例

### 场景1：大型项目分析
当分析一个复杂项目时，可以：
1. 创建 `project_structure.json` 记录目录结构
2. 使用 `analysis_notes.md` 记录发现
3. 在 `symbols/` 目录下保存提取的类和函数信息

### 场景2：多步骤任务执行
执行复杂任务时：
1. 维护 `task_queue.json` 管理待办事项
2. 使用 `execution_log.md` 记录每步结果
3. 在 `checkpoints/` 保存中间状态

### 场景3：迭代开发
在反复修改代码时：
1. 保存 `iterations/` 目录记录每次尝试
2. 使用 `feedback.json` 记录用户反馈
3. 维护 `improvements.md` 追踪改进历史

## 最佳实践

### 1. 命名规范
- 使用描述性文件名
- 添加时间戳避免覆盖：`analysis_2024-01-20_v2.json`
- 按类型组织子目录：`logs/`, `cache/`, `reports/`

### 2. 数据生命周期
- 定期清理过期的缓存文件
- 重要数据做好备份
- 使用版本号管理迭代：`v1/`, `v2/`

### 3. 性能考虑
- 大文件分块存储
- 使用索引文件加速查找
- 避免在数据区存储二进制大文件

## 示例：任务管理系统

一个完整的任务管理示例：

```python
# 初始化任务列表
data_dir = "/path/to/.agent_data/my_agent"
todo_file = f"{data_dir}/todo.json"

# 读取现有任务
if os.path.exists(todo_file):
    with open(todo_file, 'r') as f:
        todos = json.load(f)
else:
    todos = {"tasks": [], "next_id": 1}

# 添加新任务
new_task = {
    "id": todos["next_id"],
    "description": "实现用户认证",
    "status": "pending",
    "created_at": datetime.now().isoformat()
}
todos["tasks"].append(new_task)
todos["next_id"] += 1

# 保存更新
with open(todo_file, 'w') as f:
    json.dump(todos, f, indent=2, ensure_ascii=False)
```

## 数据区域 vs 工作区域

- **工作区域**（work_dir）：存放最终产出，与其他 agent 共享
- **数据区域**（.agent_data）：存放工作数据，私有独占

记住：数据区域是你的"工作台"，工作区域是"成品展示区"。