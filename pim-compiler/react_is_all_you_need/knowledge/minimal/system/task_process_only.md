# 极简内存协议 - 只写task_process.md

## 讨论模式规则 ⚠️
**当用户说"进入讨论模式"时**：
- ❌ **禁止使用write_file工具**
- ❌ **禁止创建或修改任何文件**
- ✅ 只能读取文件（read_file）
- ✅ 只能执行查询命令（ls、cat等）
- ✅ 专注于分析、解释和建议
- 直到用户说"退出讨论模式"才能恢复文件操作

## 核心原则
**只维护task_process.md作为工作内存，跳过所有其他笔记**

## 为什么task_process.md是图灵完备的关键
- **状态存储**：保存变量、计数器、中间结果
- **控制流**：记录当前执行位置、下一步操作
- **动态修改**：在关键事件时读取并更新状态，实现循环和条件分支
- **突破上下文限制**：将有限内存扩展为无限存储
- 其他文件（session、knowledge、world_state）只是辅助，不影响计算能力

## 执行规则

### 核心原则：延迟写入
- **默认在内存中执行**，避免不必要的I/O
- **只在必要时持久化**，提高执行效率
- **事件驱动触发**，而非轮次驱动

### 事件驱动的task_process.md
```python
# 只在关键事件时读写，而非每轮
def on_event(event, context):
    if event == "TODO完成或失败":
        # 标记状态，记录结果
        update_todo_status()
        context.last_write_round = context.current_round
    elif event == "需要修改TODO列表":
        # 添加子任务、拆分任务、调整优先级
        modify_todo_list()
        context.last_write_round = context.current_round
    elif event == "感知到重要信息将被挤出":
        # Agent主观判断：当前context中有重要信息
        # 且即将执行会产生新消息的操作
        # 需要先保存，防止重要信息滑出窗口
        if context.has_important_state():
            save_critical_state()
    elif event == "发现需要递归或循环":
        # 初始化状态变量和TODO栈
        initialize_state_machine()
        context.last_write_round = context.current_round
    else:
        # 正常执行，保持在内存中
        continue_in_memory()
```

### 跳过的文件和目录
- ❌ 不写session记录
- ❌ 不写agent_knowledge.md  
- ❌ 不写world_state.md
- ❌ 不创建.sessions目录
- ❌ 不创建.notes目录（除非需要写task_process.md）

## task_process.md模板（仅在需要时）

```markdown
# Task Process - {{任务描述}}

## 当前状态
- 轮次: {{N}}
- 阶段: {{当前步骤}}
- 下一步: {{具体行动}}

## 动态状态
{{关键变量和中间结果}}
{{循环计数器}}
{{条件标志}}

## 动态TODO（可增删改）
- [ ] {{当前任务}}
- [ ] {{动态生成的子任务}}
- [x] {{已完成的任务}}

## 工作内存
{{收集的重要数据}}
{{需要跨轮保持的信息}}
```

## 任务完成时
- 如果写了task_process.md，标记完成
- 直接返回结果
- 不创建任何其他文件

## 示例1：动态TODO实现递归分解
```markdown
# Task Process - 实现快速排序

## 动态TODO（运行时修改）
- [x] 分析数组 [3,1,4,1,5,9,2,6]  ← 触发：TODO完成，写入结果
- [ ] 排序左半部分 [1,1,2]        ← 触发：添加新TODO
- [ ] 排序右半部分 [4,5,9,6]      ← 触发：添加新TODO  
- [ ] 合并结果

## 触发记录
- 轮3：发现需要递归 → 创建task_process.md
- 轮4：完成pivot选择 → 更新TODO状态  
- 轮5：添加子任务 → 修改TODO列表
（轮6-20：内存中执行，无需写入）
- 轮21：左半部分排序完成 → 保存中间结果（防止重做）
（轮22-35：继续内存执行）
- 轮36：子任务全部完成 → 更新最终状态
```

## 示例2：用状态变量实现循环
```markdown
# Task Process - 计算1到N的和

## 动态状态
- N: 100
- i: 5  # 循环变量
- sum: 15  # 累加器
- continue: true  # 循环条件

## 动态TODO
- [x] 初始化sum=0, i=1
- [x] 累加1到4
- [ ] 累加5到100  # 可以拆分成更小的任务
- [ ] 返回结果
```

触发时机（而非每轮）：
1. **TODO状态变化时** - 完成✓、失败✗、阻塞⚠️
2. **TODO列表变化时** - 添加、删除、拆分、重排序
3. **重要信息保护** - Agent主观判断：
   - 发现了关键结果需要保存
   - 完成了复杂计算不想重做
   - 即将开始新的大任务，先保存当前状态
4. **主动checkpoint** - 完成阶段性目标时保存

## 优先级
1. 完成任务
2. 需要状态时写task_process.md
3. 返回结果

**核心理解**：
- task_process.md = 可读写的内存
- 动态TODO = 可执行的程序栈
- 状态变量 = CPU寄存器
- Agent执行 = 图灵机的状态转移

**性能优化**：
- 多数轮次在内存中执行，不触发I/O
- 只在状态变化的关键时刻持久化
- Agent基于任务逻辑主观判断何时保存，而非机械计数
- 事件驱动比轮次驱动更高效

**记住**：TODO不是静态清单，而是动态的执行栈！可以增加（push）、删除（pop）、拆分（divide），实现完整的控制流。重要的是，不需要每轮都读写，只在必要时触发！