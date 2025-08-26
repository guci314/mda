# TODO 管理知识

## 核心原则
根据任务复杂度决定是否使用 TODO 系统，避免过度工程化。

## 任务复杂度评估

### 简单任务（直接处理，无需 TODO）
- 单一操作任务（如：读取一个文件）
- 简单查询（如：解释概念）
- 快速修复（如：修改一行代码）
- 信息检索（如：搜索特定内容）
- 执行时间 < 3 步

### 复杂任务（需要 TODO 管理）
- 多步骤任务（≥ 3 个独立步骤）
- 需要协调多个组件
- 涉及多个文件修改
- 需要迭代开发
- 包含测试和验证步骤
- 用户明确要求使用 TODO

## TODO 文件管理流程

### 1. 任务评估阶段
```
收到任务 → 分析复杂度 → 决策：
- 简单 → 直接执行
- 复杂 → 创建 TODO 文件
```

### 2. TODO 文件创建
当判定为复杂任务时，创建 `TODO.json` 文件：

**重要提示**：使用 `write_file` 工具时，必须将 JSON 内容转换为字符串格式，不能直接传递 Python 字典。使用 `json.dumps()` 或直接传递 JSON 字符串。

```json
{
  "task_name": "任务名称",
  "created_at": "ISO时间戳",
  "complexity": "complex",
  "estimated_steps": 5,
  "todos": [
    {
      "id": "1",
      "content": "步骤描述",
      "status": "pending",  // pending/in_progress/completed
      "created_at": "时间戳",
      "completed_at": null,
      "notes": ""
    }
  ],
  "current_step": 0,
  "overall_progress": "0%"
}
```

### 3. 状态管理规则

#### 状态转换
- `pending` → `in_progress`：开始执行任务时
- `in_progress` → `completed`：任务成功完成
- `in_progress` → `pending`：遇到阻塞需要等待

#### 更新时机
- **开始任务前**：标记为 `in_progress`
- **完成任务后**：立即标记为 `completed`
- **遇到错误**：记录到 `notes`，保持 `in_progress`
- **需要用户输入**：标记回 `pending`，添加说明

### 4. 进度追踪
```
overall_progress = (已完成数 / 总任务数) * 100%
```

## 具体执行策略

### 简单任务处理
```markdown
1. 接收任务
2. 直接执行
3. 返回结果
```

### 复杂任务处理
```markdown
1. 接收任务
2. 分解为子任务
3. 创建 TODO.json
4. 逐项执行：
   - 读取 TODO.json
   - 找到下一个 pending 任务
   - 更新为 in_progress
   - 执行任务
   - 更新为 completed
   - 计算并更新 overall_progress
5. 所有完成后，生成总结报告
```

## 判断示例

### 无需 TODO 的例子
- "解释什么是 React"
- "读取 config.json 文件"
- "修复这行代码的语法错误"
- "当前目录有哪些文件"

### 需要 TODO 的例子
- "创建一个完整的 Web 应用"
- "重构整个代码库"
- "实现用户认证系统"
- "数据库迁移并更新所有相关代码"

## TODO 文件位置
- 默认位置：`{work_dir}/TODO.json`
- 可以有多个 TODO 文件：`TODO_<task_name>.json`

## 最佳实践

### 1. 避免过度使用
不要为每个任务都创建 TODO，只在真正需要时使用。

### 2. 原子性操作
每个 TODO 项应该是原子的、可独立完成的。

### 3. 及时更新
状态变化应立即反映在 TODO 文件中。

### 4. 清晰描述
TODO 内容应该具体、可执行，避免模糊描述。

### 5. 定期清理
完成的 TODO 文件可以归档到 `completed/` 目录。

## 错误处理

### 任务失败
```json
{
  "id": "3",
  "content": "部署到生产环境",
  "status": "in_progress",
  "notes": "错误: 权限不足，需要管理员权限"
}
```

### 依赖阻塞
```json
{
  "id": "5",
  "content": "集成测试",
  "status": "pending",
  "notes": "等待: 依赖任务4完成"
}
```

## 报告生成

任务完成后，生成简洁报告：
```markdown
# 任务完成报告

## 概览
- 任务：{task_name}
- 总步骤：{total_steps}
- 完成时间：{duration}
- 成功率：{success_rate}%

## 已完成
✅ 任务1
✅ 任务2
...

## 问题与解决
- 问题1：描述 → 解决方案
```

## 决策树

```
收到任务
├── 评估复杂度
│   ├── 简单（<3步）→ 直接执行
│   └── 复杂（≥3步）→ 创建TODO
│       ├── 分解任务
│       ├── 创建TODO.json
│       └── 逐步执行
│           ├── 更新状态
│           ├── 执行任务
│           └── 更新进度
└── 返回结果
```

## 关键洞察

1. **TODO 不是必需的**：大部分任务不需要 TODO
2. **复杂度是关键**：根据实际复杂度决定
3. **保持简单**：TODO 系统本身要简单
4. **用户优先**：如果用户要求，就使用 TODO

记住：**工具是为了解决问题，不是为了使用而使用。**