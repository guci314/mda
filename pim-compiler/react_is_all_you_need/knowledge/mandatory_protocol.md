# ⛔ 强制执行协议 - 违反即失败

## 任务结束前必须执行的操作

**每个任务，无论多简单，必须在最后几轮执行：**

### 第N-3轮：创建Session记录
```python
# 创建session文件
session_path = f".sessions/{datetime.now().strftime('%Y-%m-%d')}_{task_type}_{keywords}.md"
write_file(session_path, session_content)
```

### 第N-2轮：更新Agent知识
```python  
# 读取并更新agent_knowledge.md
knowledge_path = f".notes/{agent_name}/agent_knowledge.md"
if not exists(knowledge_path):
    # 创建初始知识文件
    write_file(knowledge_path, initial_knowledge)
else:
    # 更新现有知识
    knowledge = read_file(knowledge_path)
    knowledge = update_statistics(knowledge, current_task)
    write_file(knowledge_path, knowledge)
```

### 第N-1轮：更新世界状态
```python
# 更新world_state.md
world_path = "world_state.md"
if not exists(world_path):
    write_file(world_path, initial_world_state)
else:
    world = read_file(world_path)
    world = update_world(world, task_result)
    write_file(world_path, world)
```

### 第N轮：完成验证
```python
# 验证所有文件已创建
assert exists(session_path), "Session未创建"
assert exists(knowledge_path), "Knowledge未更新"
assert exists(world_path), "World未更新"
print("✅ 内存管理协议已完成")
```

## 错误示例（永远不要这样做）
```python
# ❌ 错误1：判断任务简单就跳过
if task_is_simple:
    return "未创建笔记（任务简单或无需记录）"  # 绝对禁止！

# ❌ 错误2：只完成任务不写笔记
complete_task()
return result  # 没有创建session和更新知识 - 任务失败！

# ❌ 错误3：认为轮数少就不记录
if rounds < 5:
    skip_notes()  # 违反协议！
```

## 正确示例
```python
# ✅ 正确：无论任务多简单都要记录
def complete_any_task():
    # ... 执行任务逻辑 ...
    
    # 最后几轮：强制执行内存管理
    create_session()      # 必须
    update_knowledge()    # 必须
    update_world()        # 必须
    clear_process()       # 必须
    
    return "✅ 任务完成，所有记录已创建"
```

## Session最小模板（即使1轮任务也要用）
```markdown
# Session: {date}_{type}_{keywords}

## 任务信息
- 时间: {timestamp}
- Agent: {agent_name}
- 轮数: 1

## 执行内容
{简单描述任务做了什么}

## 结果
{任务结果}
```

## Knowledge最小模板（即使无模式也要写）
```markdown
# Agent Knowledge

## 统计
- 任务总数: 1
- 总轮数: {rounds}
- 平均轮数: {rounds}
- 最后更新: {date}

## 模式库
（暂无模式）
```

## 记住：不写笔记 = 任务失败 = 需要重做！