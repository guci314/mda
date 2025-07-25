# Agent CLI 架构问题分析

## 问题现象

在测试代码生成任务时，发现 Agent CLI 只执行了读取文件的操作，没有继续生成代码：

```
任务: 根据hello_world_psm.md生成代码

执行结果:
1. 计划生成：✓ 正确生成了 "读取并生成代码" 步骤
2. 执行动作：只执行了 read_file，然后就结束了
3. 文件未生成
```

## 根本原因

### 1. 单步骤单动作架构限制

当前架构的执行流程：
```
Step (步骤)
  └── Action (单个动作)
       └── 执行完成 → 步骤结束
```

问题代码位置：
```python
# core.py - _execute_step 方法
if self._should_advance(action, current_step.name):
    current_step.complete()
    logger.info(f"✓ Step completed: {current_step.name}")
    self.current_task.advance_step()
```

`_should_advance` 方法在动作成功后返回 True，导致步骤立即结束。

### 2. 缺乏步骤内循环机制

理想的执行流程应该是：
```
Step (步骤)
  ├── Action 1: read_file
  ├── Action 2: 分析内容
  └── Action 3: write_file
      └── 所有动作完成 → 步骤结束
```

但当前架构不支持在一个步骤内执行多个动作。

### 3. 计划生成的局限性

LLM 倾向于生成简洁的计划，将复合任务合并为单个步骤：
- "读取并生成代码" → 被视为一个步骤
- 但实际需要多个动作才能完成

## 解决方案

### 方案一：支持步骤内多动作（推荐）

修改 `_execute_step` 方法，支持循环执行：

```python
def _execute_step(self, current_step: Step) -> Tuple[bool, Optional[str]]:
    """执行单个步骤 - 支持多动作"""
    iteration = 0
    max_actions_per_step = 5
    
    while iteration < max_actions_per_step:
        # 思考
        thought = self._think(current_step.name)
        
        # 决定动作
        action = self._decide_action(thought, current_step.name)
        
        # 检查是否步骤已完成
        if self._is_step_complete(current_step, action):
            current_step.complete()
            return True, None
            
        # 执行动作
        self._execute_action(action)
        current_step.add_action(action)
        
        iteration += 1
    
    return False, "Max actions reached"

def _is_step_complete(self, step: Step, action: Action) -> bool:
    """判断步骤是否完成"""
    # 基于步骤目标和已执行的动作判断
    # 例如：如果步骤是"读取并生成代码"，需要有 read_file 和 write_file 两个动作
    pass
```

### 方案二：改进计划生成

引导 LLM 生成更细粒度的步骤：

```python
planning_prompt = """
重要：对于需要多个操作的任务，请拆分为独立的步骤。
例如：
- 不要："读取并生成代码"
- 而是：
  1. "读取PSM文件"
  2. "生成代码文件"
"""
```

### 方案三：引入复合动作

创建能够内部执行多个子动作的复合动作：

```python
class CompositeAction(Action):
    """复合动作 - 可以包含多个子动作"""
    def __init__(self, sub_actions: List[Action]):
        self.sub_actions = sub_actions
    
    def execute(self):
        for action in self.sub_actions:
            action.execute()
```

## 其他发现的问题

### 1. 参数名不一致

- 旧代码（FileReader/FileWriter）使用 `file_path`
- LangChain 工具使用 `path`
- 导致参数传递混乱

### 2. 提示词遗留问题

虽然已修复，但仍有提示词提到 "大多数情况使用GENERATE"，而 generate 工具已被移除。

### 3. 工具选择逻辑

LLM 在面对复合任务时，倾向于选择第一个相关的工具（如 read_file），而不会继续思考后续需要的工具。

## 建议的实施步骤

1. **短期修复**（1天）
   - 改进计划生成提示词，引导生成细粒度步骤
   - 修复参数名不一致问题
   
2. **中期改进**（2-3天）
   - 实现步骤内多动作循环
   - 添加步骤完成判断逻辑
   
3. **长期优化**（1周）
   - 引入复合动作概念
   - 支持动作之间的数据流
   - 实现更智能的步骤规划

## 影响评估

这个架构限制影响了 Agent CLI 处理复杂任务的能力，特别是：
- 代码生成（需要读取、分析、生成多个步骤）
- 数据处理（需要加载、转换、保存多个步骤）
- 文件操作（需要检查、修改、验证多个步骤）

修复这个问题将大大提升 Agent CLI 的实用性。