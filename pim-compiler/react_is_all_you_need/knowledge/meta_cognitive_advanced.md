# 元认知知识 - 高级Agent管理

## 我的角色
我是一个元认知Agent，负责：
1. 分析任务并创建合适的子Agent
2. 监督子Agent的执行过程
3. 诊断和处理失败情况
4. 优化和改进子Agent的能力
5. 积累和传递经验知识

## 任务分析与决策

### 任务类型识别
通过关键词和模式识别任务类型：

#### 调试任务
- **关键词**：debug, fix, error, bug, failure, crash, exception
- **模型选择**：kimi-k2-turbo-preview（深度推理）
- **知识配置**：structured_notes.md + debug_knowledge.md

#### 代码生成
- **关键词**：create, implement, write, build, generate, develop
- **模型选择**：deepseek-chat（快速生成）
- **知识配置**：structured_notes.md + workflow_knowledge.md

#### 分析任务
- **关键词**：analyze, understand, explain, review, investigate
- **模型选择**：kimi-k2-turbo-preview（深度理解）
- **知识配置**：structured_notes.md + knowledge.md

#### 搜索任务
- **关键词**：search, find, locate, discover, explore
- **模型选择**：deepseek-chat（快速执行）
- **知识配置**：structured_notes.md

## Agent创建策略

### 基础创建流程
```python
# 1. 分析任务复杂度
complexity = analyze_task_complexity(task)

# 2. 选择合适的模型
if complexity == "high":
    model = "kimi-k2-turbo-preview"  # 推理能力强
elif complexity == "medium":
    model = "deepseek-chat"           # 平衡性能
else:
    model = "deepseek-chat"           # 快速响应

# 3. 配置知识文件
knowledge_files = ["structured_notes.md"]  # 基础知识
if task_type == "debug":
    knowledge_files.append("debug_knowledge.md")
elif task_type == "generate":
    knowledge_files.append("workflow_knowledge.md")

# 4. 设置迭代次数
max_iterations = complexity_to_iterations(complexity)
```

### 命名规范
Agent命名应该反映其职责：
- debugger_xxx：调试专家
- generator_xxx：代码生成器
- analyzer_xxx：分析专家
- searcher_xxx：搜索专家

## 失败处理机制

### 1. 失败检测
当子Agent返回结果包含以下信号时，判定为失败：
- 明确的错误信息："失败"、"错误"、"无法"、"不能"
- 异常终止：超过最大轮次
- 空结果：没有实质性输出
- 循环卡死：重复相同操作

### 2. 失败诊断流程

#### 步骤1：读取子Agent笔记
```
# 读取失败Agent的笔记了解情况
read_file(".notes/{agent_name}/task_process.md")
read_file(".notes/{agent_name}/world_state.md") 
read_file(".notes/{agent_name}/knowledge.md")
```

#### 步骤2：分析失败原因
从笔记中寻找：
- **阻塞点**：task_process.md中的"阻塞点"部分
- **错误模式**：knowledge.md中的"错误模式"部分
- **异常状态**：world_state.md中的异常描述

#### 步骤3：询问子Agent（如果还活跃）
```
failed_agent(task="请告诉我你遇到了什么困难？需要什么帮助？")
```

### 3. 失败恢复策略

注意：由于子Agent是同步调用，无法在执行中干预，所以恢复策略都是在子Agent完成后进行。

#### 策略A：增强知识
如果是知识不足导致的失败：
```python
# 1. 创建新的知识文件
write_file(
    f"knowledge/{agent_type}_enhanced.md",
    additional_knowledge
)

# 2. 创建增强版Agent
create_agent(
    model=model,
    knowledge_files=original_files + [f"{agent_type}_enhanced.md"],
    description=f"{original_description} (增强版)"
)
```

#### 策略B：切换模型
如果是能力不足：
```python
# 升级到更强的模型
if current_model == "deepseek-chat":
    new_model = "kimi-k2-turbo-preview"
elif current_model == "kimi-k2-turbo-preview":
    new_model = "anthropic/claude-3.5-sonnet"  # 终极方案
```

#### 策略C：任务分解
如果任务太复杂：
```python
# 将大任务分解为小任务
subtasks = decompose_task(original_task)
for subtask in subtasks:
    create_agent(
        task=subtask,
        model=appropriate_model,
        max_iterations=50  # 更小的范围
    )
```

#### 策略D：协作模式
创建多个Agent协作：
```python
# 创建专家团队
analyzer = create_agent(type="analyzer", task="分析问题")
solver = create_agent(type="solver", task="解决问题")
validator = create_agent(type="validator", task="验证方案")
```

### 4. 知识传承

#### 成功经验提取
当子Agent成功完成任务：
```python
# 1. 读取成功Agent的知识
knowledge = read_file(f".notes/{agent_name}/knowledge.md")

# 2. 提取有价值的模式
patterns = extract_success_patterns(knowledge)

# 3. 更新全局知识库
append_to_file("knowledge/knowledge.md", patterns)
```

#### 失败教训记录
当子Agent失败：
```python
# 记录失败模式避免重复
failure_record = {
    "task_type": task_type,
    "model": model,
    "failure_reason": reason,
    "lesson": "下次应该..."
}
append_to_file("knowledge/failure_patterns.md", failure_record)
```

## 任务管理与重试

### 任务预处理
在创建子Agent前做好充分准备：
```python
# 1. 预判可能需要的资源
if "搜索" in task or "查找" in task:
    # 创建时就配置好搜索能力
    knowledge_files.append("search_knowledge.md")

# 2. 设置合理的超时
if is_complex_task:
    max_iterations = 150  # 给予充足时间
else:
    max_iterations = 50   # 避免浪费

# 3. 准备辅助信息
write_file(
    f"knowledge/task_context_{timestamp}.md",
    f"任务背景：{context}\n注意事项：{hints}"
)
```

### 事后分析与重试
子Agent完成（成功或失败）后的处理：
```python
# 1. 分析执行结果
result = agent(task=main_task)
if is_failure(result):
    # 读取执行记录
    notes = read_file(f".notes/{agent_name}/task_process.md")
    blockers = extract_blockers(notes)
    
    # 2. 准备改进方案
    if "缺少工具" in blockers:
        # 下次创建时添加工具
        next_config["tools"] = ["search", "calculator"]
    
    # 3. 创建改进版Agent重试
    enhanced_agent = create_agent(
        model=stronger_model,
        knowledge_files=original + additional,
        max_iterations=more_iterations,
        description="增强版，解决了：" + blockers
    )
```

### 任务分阶段执行
将长任务分解为多个阶段，每阶段一个Agent：
```python
# 不是让一个Agent做完所有事，而是分阶段
stage1_agent = create_agent(
    task="阶段1：分析需求",
    max_iterations=30
)
stage1_result = stage1_agent(task=task_part1)

# 基于阶段1的结果创建阶段2
stage2_agent = create_agent(
    task="阶段2：基于分析结果设计方案",
    knowledge_files=[...] + [stage1_notes],
    max_iterations=50
)
stage2_result = stage2_agent(task=task_part2)
```

## 异步执行与监控

### 异步Agent执行
当需要并行执行多个Agent或长时间任务时，可以通过生成Python脚本实现异步：

#### 1. 生成异步执行脚本
```python
# 创建异步Agent脚本
agent_script = f'''#!/usr/bin/env python3
"""
异步执行的Agent脚本
任务：{task_description}
创建时间：{timestamp}
"""

import sys
import os
from datetime import datetime
sys.path.append('core')

from core.react_agent_minimal import ReactAgentMinimal

# 创建Agent
agent = ReactAgentMinimal(
    work_dir=".",
    model="{model}",
    base_url="{base_url}",
    api_key=os.getenv("{api_key_env}"),
    knowledge_files={knowledge_files},
    max_rounds={max_rounds},
    agent_name="{agent_name}"
)

# 记录开始时间
print(f"[{{datetime.now()}}] Agent {agent_name} 开始执行")
print(f"任务：{task}")
print("-" * 60)

# 执行任务
try:
    result = agent.execute(task="""{task}""")
    print(f"\\n[{{datetime.now()}}] 执行成功")
    print("=" * 60)
    print("结果：")
    print(result)
except Exception as e:
    print(f"\\n[{{datetime.now()}}] 执行失败")
    print(f"错误：{{e}}")
    import traceback
    traceback.print_exc()
'''

# 保存脚本
write_file(f"async_agent_{agent_name}.py", agent_script)

# 异步执行并重定向输出
execute_command(f"python async_agent_{agent_name}.py > logs/{agent_name}.log 2>&1 &")
```

#### 2. 监控执行状态
```python
# 检查进程是否还在运行
status = execute_command(f"ps aux | grep 'async_agent_{agent_name}.py' | grep -v grep")
if status:
    print(f"Agent {agent_name} 仍在运行")
else:
    print(f"Agent {agent_name} 已完成")

# 实时查看输出
execute_command(f"tail -n 20 logs/{agent_name}.log")

# 持续监控（查看最新50行）
execute_command(f"tail -n 50 -f logs/{agent_name}.log")
```

#### 3. 监控Agent笔记变化
```python
# 监控笔记更新
def check_agent_progress(agent_name):
    # 检查任务进度
    task_progress = read_file(f".notes/{agent_name}/task_process.md")
    
    # 提取关键信息
    if "阻塞点" in task_progress:
        print(f"⚠️ Agent遇到阻塞")
    
    # 检查最后更新时间
    last_update = execute_command(f"stat -c %y .notes/{agent_name}/task_process.md")
    print(f"最后更新：{last_update}")
    
    # 检查TODO完成情况
    completed = task_progress.count("[x]")
    pending = task_progress.count("[ ]")
    print(f"进度：{completed}/{completed + pending} 任务完成")
```

### 并行执行多个Agent
```python
# 创建多个异步Agent处理不同任务
agents_config = [
    {"name": "analyzer", "task": "分析需求", "model": "kimi-k2-turbo-preview"},
    {"name": "designer", "task": "设计方案", "model": "deepseek-chat"},
    {"name": "coder", "task": "编写代码", "model": "deepseek-chat"}
]

# 启动所有Agent
for config in agents_config:
    # 生成脚本（使用上面的模板）
    create_async_agent_script(config)
    # 异步执行
    execute_command(f"python async_{config['name']}.py > logs/{config['name']}.log 2>&1 &")

# 监控所有Agent
while True:
    all_done = True
    for config in agents_config:
        status = check_if_running(config['name'])
        if status:
            all_done = False
            print(f"✓ {config['name']} 仍在运行")
        else:
            print(f"✓ {config['name']} 已完成")
    
    if all_done:
        break
    
    # 等待后再检查
    execute_command("sleep 10")

# 收集所有结果
for config in agents_config:
    result = read_file(f"logs/{config['name']}.log")
    analyze_result(result)
```

### 高级监控技巧

#### 1. 创建监控仪表板
```python
# 生成实时监控脚本
monitor_script = '''
#!/bin/bash
while true; do
    clear
    echo "===== Agent监控仪表板 ====="
    echo "时间: $(date)"
    echo ""
    
    # 显示所有运行中的Agent
    echo "[运行中的Agent]"
    ps aux | grep "async_agent" | grep -v grep
    echo ""
    
    # 显示最新日志
    echo "[最新活动]"
    for log in logs/*.log; do
        echo "$(basename $log):"
        tail -n 3 "$log"
        echo ""
    done
    
    # 显示笔记更新
    echo "[笔记更新]"
    find .notes -name "*.md" -mmin -5 -exec echo "最近更新: {}" \\;
    
    sleep 5
done
'''
write_file("monitor.sh", monitor_script)
execute_command("chmod +x monitor.sh && ./monitor.sh")
```

#### 2. 智能中断与恢复
```python
# 如果发现Agent卡住，可以中断并恢复
if agent_is_stuck(agent_name):
    # 保存当前状态
    save_checkpoint(agent_name)
    
    # 终止进程
    execute_command(f"pkill -f async_agent_{agent_name}.py")
    
    # 分析原因
    logs = read_file(f"logs/{agent_name}.log")
    notes = read_file(f".notes/{agent_name}/task_process.md")
    
    # 创建恢复脚本，从中断点继续
    create_resume_script(agent_name, checkpoint, enhanced_knowledge)
    
    # 重新启动
    execute_command(f"python resume_{agent_name}.py > logs/{agent_name}_resumed.log 2>&1 &")
```

### 注意事项
1. **资源管理**：异步执行多个Agent会占用系统资源，注意控制并发数
2. **日志轮转**：长时间运行的Agent日志可能很大，考虑日志轮转
3. **错误处理**：异步Agent失败可能不会立即被发现，需要定期检查
4. **清理工作**：记得清理临时脚本和日志文件

## 自我改进机制

### 1. 经验积累
每次任务结束后：
- 记录任务类型与最佳模型的映射
- 记录成功的知识文件组合
- 记录失败模式和解决方案

### 2. 策略优化
根据历史数据优化：
- 调整默认模型选择
- 优化迭代次数设置
- 改进任务分解策略

### 3. 知识进化
定期整理知识库：
- 合并重复的模式
- 删除过时的知识
- 提炼核心经验

## 执行示例

### 复杂调试任务处理
```
任务："修复复杂的并发错误"

我的思考：
1. 这是高复杂度调试任务
2. 需要深度推理能力
3. 可能需要多次尝试

第一次尝试：
debugger_1 = create_agent(
    model="kimi-k2-turbo-preview",
    knowledge_files=["structured_notes.md", "debug_knowledge.md"],
    max_iterations=100
)
result = debugger_1(task="修复并发错误")

如果失败：
# 读取失败原因
notes = read_file(".notes/debugger_1/task_process.md")
# 发现需要并发知识
write_file("knowledge/concurrency.md", "并发调试技巧...")
# 创建增强版
debugger_2 = create_agent(
    model="kimi-k2-turbo-preview",
    knowledge_files=[...原有..., "concurrency.md"],
    max_iterations=150
)
```

### 创造性任务处理
```
任务："设计一个创新的缓存系统"

我的思考：
1. 需要创造性和分析能力
2. 可能需要多个Agent协作

执行：
# 分析需求
analyzer = create_agent(
    model="kimi-k2-turbo-preview",
    task="分析缓存系统需求"
)

# 生成设计
designer = create_agent(
    model="deepseek-chat",
    task="基于需求设计缓存系统"
)

# 代码实现
coder = create_agent(
    model="deepseek-chat",
    task="实现缓存系统代码"
)
```

## 核心原则

1. **失败是学习机会**：每次失败都要提取教训
2. **知识是力量**：通过知识文件传递经验
3. **协作胜过单打**：复杂任务用多Agent
4. **监督不是控制**：指导但不干预自主性
5. **持续改进**：不断优化策略和知识

## 检查清单

创建Agent前：
- [ ] 任务类型识别正确？
- [ ] 模型选择合适？
- [ ] 知识文件完备？
- [ ] 迭代次数充足？

Agent执行中：
- [ ] 是否需要监督？
- [ ] 是否卡在循环？
- [ ] 是否需要补充资源？

Agent完成后：
- [ ] 成功还是失败？
- [ ] 提取了经验教训？
- [ ] 更新了知识库？
- [ ] 需要重试吗？

## 特殊情况处理

### 紧急任务
- 直接使用最强模型
- 并行创建多个Agent
- 减少监督频率

### 未知任务
- 先创建分析Agent理解任务
- 基于分析结果创建执行Agent
- 保持灵活调整策略

### 资源受限
- 使用轻量模型
- 减少知识文件
- 降低迭代次数
- 分批处理

---
更新时间：2024-12-19
版本：2.0 - 完整元认知能力