# 记忆控制协议

## 记忆层次

### 1. 工作内存（task_process.md）- 智能触发
- **何时写入**：接近上下文限制时（如第30轮后）
- **控制方式**：自动，无需开关
- **原因**：这是图灵完备的核心，必要时自动启用

### 2. 长期记忆（session）- enable_session控制
- **默认**：False
- **用途**：审计、回溯、调试
- **场景**：生产环境、需要追踪历史时开启

### 3. 学习系统（agent_knowledge.md）- enable_learning控制
- **默认**：False
- **用途**：经验积累、模式识别
- **场景**：需要持续优化的长期任务

### 4. 世界概览（world_state.md）- enable_world_view控制
- **默认**：False
- **用途**：多Agent协作、全局状态
- **场景**：复杂系统、多Agent环境

## 执行规则

```python
# 判断是否需要写入
if task_rounds > 30:  # 智能触发
    write_task_process()

if enable_session:
    write_session()
    
if enable_learning:
    write_agent_knowledge()
    
if enable_world_view:
    write_world_state()
```

## 预设模式

### 开发模式（默认）
```python
enable_session=False
enable_learning=False  
enable_world_view=False
# 最快速度，最少IO
```

### 生产模式
```python
enable_session=True
enable_learning=True
enable_world_view=False  # 除非多Agent
```

### 调试模式
```python
enable_session=True
enable_learning=True
enable_world_view=True
# 完整记录，方便调试
```