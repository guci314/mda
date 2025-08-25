# NLPL记忆系统务实设计 v2.0
基于文件系统和ReactAgent的认知架构

## 设计约束
- **存储架构**：文件系统 + NLPL文本文件
- **计算架构**：ReactAgent + 知识文件
- **记忆表达**：全部使用NLPL（放弃OWL和产生式规则）
- **核心原则**：简单、可读、可执行

## 1. 记忆的文件系统组织

```
.memory/
├── episodic/                       # 情景记忆：具体事件
│   ├── 2024-08-21/
│   │   ├── 14-30-00_create_calculator.nlpl
│   │   ├── 14-30-00_detailed.nlpl          # 详细版本
│   │   ├── 14-30-00_summary.nlpl           # 摘要版本
│   │   └── 14-30-00_gist.nlpl              # 要点版本
│   └── index.nlpl                           # 时间线索引
│
├── semantic/                        # 语义记忆：抽象知识
│   ├── concepts/
│   │   ├── file_operations.nlpl
│   │   └── error_handling.nlpl
│   ├── patterns/
│   │   ├── create_test_file.nlpl
│   │   └── validate_input.nlpl
│   └── relations.nlpl              # 概念关系网络
│
├── procedural/                      # 程序性记忆：技能
│   ├── skills/
│   │   ├── debug_python_error.nlpl
│   │   └── optimize_code.nlpl
│   ├── habits/
│   │   ├── always_validate.nlpl
│   │   └── test_first.nlpl
│   └── proficiency.nlpl            # 技能熟练度
│
├── working/                         # 工作记忆：当前上下文
│   ├── current_task.nlpl
│   ├── active_goals.nlpl
│   └── attention_focus.nlpl
│
└── metacognitive/                   # 元认知记忆
    ├── self_knowledge.nlpl          # 自我认知
    ├── strategy_effectiveness.nlpl  # 策略评估
    └── learning_history.nlpl        # 学习历程
```

## 2. NLPL记忆表达格式

### 2.1 情景记忆（Episodic Memory）

```markdown
# 事件：创建计算器模块
时间：2024-08-21 14:30:00
持续：2分15秒

## 任务
用户要求创建一个计算器模块，包含基本运算功能

## 执行过程

### 阶段1：理解任务
- **思考**：需要创建calculator.py和test_calculator.py
- **决策**：先写主模块，再写测试
- **信心度**：0.9

### 阶段2：创建主模块
- **工具**：write_file
- **参数**：
  - 文件：calculator.py
  - 内容：[四个基本运算函数]
- **结果**：成功
- **用时**：0.8秒

### 阶段3：创建测试
- **工具**：write_file
- **参数**：
  - 文件：test_calculator.py
  - 内容：[单元测试]
- **结果**：成功
- **用时**：1.2秒

## 关键时刻
- **T+0.5s**：识别需要防止除零错误
- **T+1.8s**：决定使用unittest而非pytest

## 情绪标记
- **满意度**：高（任务顺利完成）
- **挑战性**：低（熟悉的任务）
- **重要性**：中（基础功能）

## 经验提取
当创建Python模块时，总是同时创建对应的测试文件
```

### 2.2 语义记忆（Semantic Memory）

```markdown
# 概念：文件操作

## 定义
文件操作是与文件系统交互的行为，包括创建、读取、更新、删除文件

## 相关概念
- **前置概念**：路径、编码、权限
- **后续概念**：文件锁、缓冲、原子操作
- **平行概念**：目录操作、符号链接

## 典型模式

### 安全写入模式
```nlpl
# 安全写入文件
1. 检查目标路径是否存在
2. 如果存在，备份原文件
3. 写入新内容到临时文件
4. 验证写入成功
5. 原子性重命名临时文件
```

### 批量处理模式
```nlpl
# 批量处理文件
对于每个 文件 在 文件列表：
  - 验证文件可访问
  - 应用转换函数
  - 记录处理结果
汇总所有结果
```

## 常见陷阱
- 忘记处理编码问题（使用UTF-8）
- 不检查磁盘空间
- 没有处理并发访问

## 性能考虑
- 大文件使用流式处理
- 批量操作使用事务
- 缓存频繁访问的内容
```

### 2.3 程序性记忆（Procedural Memory）

```markdown
# 技能：调试Python错误

## 触发条件
当出现Python异常或错误时

## 执行步骤

### 步骤1：读取错误信息
- **关注**：错误类型、错误位置、调用栈
- **提取**：文件名、行号、具体错误

### 步骤2：定位问题代码
- **工具**：read_file
- **参数**：错误文件的相关行
- **范围**：错误行前后各5行

### 步骤3：分析原因
**如果** 是语法错误：
  - 检查缩进
  - 检查括号匹配
  - 检查关键字拼写

**如果** 是运行时错误：
  - 检查变量是否定义
  - 检查类型是否匹配
  - 检查边界条件

### 步骤4：生成修复方案
- **快速修复**：最小改动解决问题
- **正确修复**：解决根本原因
- **预防修复**：添加验证防止复发

### 步骤5：验证修复
- **工具**：execute_python
- **测试**：原始触发条件
- **扩展**：相关边界情况

## 熟练度指标
- **使用次数**：47次
- **成功率**：89%
- **平均用时**：3.2轮
- **自动化程度**：0.7
```

### 2.4 工作记忆（Working Memory）

```markdown
# 当前工作上下文
更新时间：2024-08-21 14:35:00

## 活动任务
**主任务**：创建计算器模块
**状态**：已完成
**子任务**：
- [x] 创建calculator.py
- [x] 创建test_calculator.py
- [ ] 运行测试验证

## 注意力焦点
- **当前关注**：测试覆盖率
- **优先级队列**：
  1. 完成测试验证
  2. 添加文档字符串
  3. 考虑边界情况

## 临时状态
- **变量**：
  - module_name = "calculator"
  - test_framework = "unittest"
- **约束**：
  - 时间限制：5分钟内完成
  - 质量要求：测试覆盖率>80%

## 激活的记忆
- semantic/patterns/create_test_file.nlpl (相似度: 0.9)
- procedural/skills/write_unittest.nlpl (相似度: 0.8)
- episodic/2024-08-20/similar_task.nlpl (相似度: 0.7)
```

### 2.5 元认知记忆（Metacognitive Memory）

```markdown
# 元认知评估
评估时间：2024-08-21 15:00:00

## 自我认知

### 能力评估
- **强项**：
  - 文件操作（精通）
  - Python编程（熟练）
  - 模式识别（良好）
- **弱项**：
  - 复杂算法（需提升）
  - 并发处理（学习中）

### 认知风格
- **决策风格**：快速启动，迭代改进
- **学习偏好**：从例子中学习
- **错误倾向**：有时过度优化

## 策略有效性

### 成功策略
```nlpl
# 分而治之策略
当 任务复杂度 > 阈值：
  1. 分解为子任务
  2. 逐个解决
  3. 整合结果
成功率：92%
```

### 需改进策略
```nlpl
# 一次性完成策略
尝试一次写出完美代码
成功率：45%
建议：改为迭代式开发
```

## 学习曲线
- **本周新技能**：3个
- **巩固技能**：5个
- **遗忘风险**：2个（长期未用）

## 自我调节建议
1. 减少工作记忆负载：及时记录中间结果
2. 提高元认知监控：每5轮评估一次进展
3. 平衡探索与利用：80%用已知策略，20%尝试新方法
```

## 3. ReactAgent知识文件设计

### 3.1 L1工作Agent知识（knowledge/work_agent.nlpl）

```markdown
# 工作Agent执行知识

## 角色定位
我是任务执行者，负责将用户指令转换为具体行动

## 执行策略

### 任务接收
当 收到任务：
  1. 理解任务目标
  2. 识别任务类型
  3. 激活相关记忆

### 任务规划
如果 任务简单：
  - 直接执行
否则：
  - 分解为步骤
  - 制定执行顺序

### 执行监控
每轮执行后：
  - 检查是否接近目标
  - 评估剩余工作量
  - 决定继续或完成

## 记忆交互

### 记忆查询
当 需要经验：
  - 搜索: grep -r "相似任务" .memory/episodic/
  - 搜索: grep -r "相关模式" .memory/semantic/patterns/
  - 激活: .memory/procedural/skills/相关技能.nlpl

### 记忆生成
每次执行后：
  - 保存执行轨迹到 .memory/working/current_task.nlpl
  - 标记关键决策点
  - 记录成功/失败
```

### 3.2 L2观察Agent知识（knowledge/observer_agent.nlpl）

```markdown
# 观察Agent知识

## 观察策略

### 观察触发
每当 工作Agent完成10轮 或 遇到关键事件：
  1. 读取 .memory/working/current_task.nlpl
  2. 分析执行模式
  3. 生成观察报告

## 注意力分配

### 显著性计算
显著性 = 新颖性 × 重要性 × 情绪强度

### 选择性注意
只关注 显著性 > 0.7 的事件：
  - 首次出现的错误
  - 创新的解决方案
  - 异常的执行路径

## 观察输出

### 生成情景记忆
将观察结果保存为：
  - 详细版: .memory/episodic/日期/时间_detailed.nlpl
  - 摘要版: .memory/episodic/日期/时间_summary.nlpl
  - 要点版: .memory/episodic/日期/时间_gist.nlpl

### 更新索引
追加到 .memory/episodic/index.nlpl：
  - 时间戳
  - 任务类型
  - 关键特征
  - 文件路径
```

### 3.3 L3海马体Agent知识（knowledge/hippocampus_agent.nlpl）

```markdown
# 海马体Agent巩固知识

## 巩固策略

### 巩固触发
每当 积累50个情景记忆 或 每天固定时间：
  1. 扫描近期情景记忆
  2. 识别重复模式
  3. 提取抽象知识

## 记忆转换

### 情景→语义
当 发现重复模式：
  1. 提取共同特征
  2. 生成抽象概念
  3. 保存到 .memory/semantic/concepts/
  
### 情景→程序性
当 发现成功策略：
  1. 提取执行步骤
  2. 参数化处理
  3. 保存到 .memory/procedural/skills/

## 时间衰减处理

### 清晰度退化
对于 每个情景记忆：
  如果 年龄 > 7天：
    - 删除 detailed.nlpl
    - 保留 summary.nlpl
  如果 年龄 > 30天：
    - 删除 summary.nlpl
    - 保留 gist.nlpl
  如果 年龄 > 90天 且 重要性 < 0.5：
    - 归档到 .memory/archive/

### 记忆强化
当 记忆被检索：
  - 更新最后访问时间
  - 增加重要性权重
  - 防止过早衰减
```

### 3.4 L4元认知Agent知识（knowledge/metacognition_agent.nlpl）

```markdown
# 元认知Agent知识

## 监控策略

### 系统监控
每100轮 或 每日结束：
  1. 评估整体表现
  2. 识别改进空间
  3. 生成优化建议

## 自我评估

### 效率评估
计算指标：
  - 任务完成率
  - 平均执行轮数
  - 错误率趋势
  - 记忆利用率

### 策略评估
对于 每个使用的策略：
  - 统计成功率
  - 计算平均耗时
  - 识别适用场景

## 学习与适应

### 更新策略库
如果 某策略成功率 < 60%：
  - 分析失败原因
  - 生成改进版本
  - 更新到 .memory/procedural/

### 知识重组
定期执行：
  1. 合并相似概念
  2. 更新概念关系
  3. 删除过时知识

## 元认知输出

保存评估结果到：
  - .memory/metacognitive/self_knowledge.nlpl
  - .memory/metacognitive/strategy_effectiveness.nlpl
  - .memory/metacognitive/learning_history.nlpl
```

## 4. 记忆检索机制

### 4.1 基于grep的快速检索

```bash
# 检索相似任务
grep -r "calculator" .memory/episodic/ --include="*.nlpl" | head -10

# 检索特定模式
grep -r "错误处理" .memory/semantic/patterns/ --include="*.nlpl"

# 检索技能
grep -r "熟练度.*>.*0.8" .memory/procedural/ --include="*.nlpl"
```

### 4.2 基于文件名的时序检索

```python
import os
from datetime import datetime, timedelta

def get_recent_memories(days=7):
    """获取最近N天的记忆"""
    cutoff = datetime.now() - timedelta(days=days)
    memories = []
    
    for root, dirs, files in os.walk(".memory/episodic"):
        for file in files:
            if file.endswith(".nlpl"):
                # 从文件名解析时间
                try:
                    file_time = parse_time_from_filename(file)
                    if file_time > cutoff:
                        memories.append(os.path.join(root, file))
                except:
                    continue
    
    return sorted(memories, reverse=True)
```

### 4.3 基于内容的语义检索

```markdown
# 检索相关记忆

## 输入
查询：如何处理文件编码错误

## 检索步骤

### 步骤1：关键词提取
关键词：[文件, 编码, 错误, 处理]

### 步骤2：多路径检索
并行执行：
  - 搜索情景记忆：grep "编码.*错误" .memory/episodic/
  - 搜索语义概念：grep "编码" .memory/semantic/concepts/
  - 搜索程序技能：grep "处理.*错误" .memory/procedural/skills/

### 步骤3：相关性排序
对每个结果：
  - 计算关键词匹配度
  - 考虑时间因素（近期优先）
  - 考虑使用频率（常用优先）

### 步骤4：返回Top-K
返回最相关的5个记忆文件路径
```

## 5. 认知循环实现

### 5.1 完整的认知循环

```python
def cognitive_cycle():
    """完整的认知循环"""
    
    # 1. 工作记忆激活
    working_memory = load_nlpl(".memory/working/current_task.nlpl")
    
    # 2. 执行任务（L1）
    work_agent = ReactAgent(
        knowledge_files=["knowledge/work_agent.nlpl"],
        work_dir=".memory/working"
    )
    execution_trace = work_agent.execute_task(working_memory.task)
    
    # 3. 观察记录（L2）- 每10轮触发
    if execution_trace.rounds % 10 == 0:
        observer = ReactAgent(
            knowledge_files=["knowledge/observer_agent.nlpl"],
            work_dir=".memory/episodic"
        )
        observer.execute_task(f"观察执行轨迹：{execution_trace}")
    
    # 4. 记忆巩固（L3）- 每50个事件触发
    if count_episodes() >= 50:
        hippocampus = ReactAgent(
            knowledge_files=["knowledge/hippocampus_agent.nlpl"],
            work_dir=".memory"
        )
        hippocampus.execute_task("巩固近期记忆")
    
    # 5. 元认知反思（L4）- 每100轮触发
    if total_rounds % 100 == 0:
        metacognition = ReactAgent(
            knowledge_files=["knowledge/metacognition_agent.nlpl"],
            work_dir=".memory/metacognitive"
        )
        metacognition.execute_task("评估系统表现")
```

### 5.2 记忆的生命周期

```markdown
# 记忆生命周期管理

## 阶段1：生成
工作Agent执行 → 生成执行轨迹 → 保存到working/

## 阶段2：编码
观察Agent分析 → 生成情景记忆 → 保存3个清晰度版本

## 阶段3：巩固
海马体Agent提取 → 生成语义/程序性记忆 → 更新knowledge/

## 阶段4：衰减
时间流逝 → 删除详细版本 → 只保留要点

## 阶段5：强化
记忆被检索使用 → 更新重要性 → 延缓衰减

## 阶段6：遗忘
长期未用 + 低重要性 → 归档 → 最终删除
```

## 6. 实现优势

### 6.1 技术简单性
- ✅ 只需文件系统，无需数据库
- ✅ NLPL文本可读，便于调试
- ✅ grep检索快速高效
- ✅ 版本控制友好（Git）

### 6.2 认知真实性
- ✅ 模拟时间衰减（多版本文件）
- ✅ 支持三种记忆类型
- ✅ 实现注意力选择（显著性过滤）
- ✅ 包含元认知监控

### 6.3 实用性
- ✅ ReactAgent直接执行NLPL知识
- ✅ 记忆可手动编辑和修正
- ✅ 支持增量学习
- ✅ 易于备份和迁移

## 7. 示例：完整的执行流程

```markdown
# 示例任务：创建并测试计算器

## 1. 用户输入
"创建一个计算器模块"

## 2. 工作Agent执行
- 读取任务
- 检索相关记忆：
  - grep "计算器" .memory/episodic/ 
  - 找到类似任务
- 执行创建
- 保存轨迹到 .memory/working/current_task.nlpl

## 3. 观察Agent记录（10轮后）
- 读取执行轨迹
- 识别模式："文件创建任务"
- 生成三个版本：
  - detailed.nlpl (500行)
  - summary.nlpl (50行)
  - gist.nlpl (5行)

## 4. 海马体巩固（50个事件后）
- 扫描情景记忆
- 发现模式："创建模块时总是创建测试"
- 更新 .memory/semantic/patterns/create_with_test.nlpl
- 更新 .memory/procedural/skills/module_creation.nlpl

## 5. 元认知评估（100轮后）
- 评估："文件创建类任务效率高"
- 建议："可以预生成常用模板"
- 更新 .memory/metacognitive/strategy_effectiveness.nlpl
```

## 8. 与认知心理学原理的对应

| 认知原理 | 实现方式 |
|---------|---------|
| 工作记忆容量限制 | working/目录只保留当前任务 |
| 时间衰减 | 文件版本（detailed→summary→gist） |
| 语义网络 | semantic/目录的NLPL关系描述 |
| 程序性知识 | procedural/目录的可执行NLPL |
| 元认知监控 | 定期运行的元认知Agent |
| 注意力选择 | 显著性过滤（只记录重要事件） |
| 记忆巩固 | 海马体Agent的模式提取 |
| 检索练习 | grep检索时更新访问时间 |

## 9. 总结

这个设计在技术约束下实现了认知心理学的核心原理：

1. **存储简单**：纯文件系统，无需复杂基础设施
2. **表达统一**：全部用NLPL，人机可读
3. **认知真实**：模拟真实的记忆机制
4. **易于实现**：ReactAgent + 知识文件即可

记忆不是数据的堆积，而是经验的组织和知识的萃取。通过NLPL，我们让记忆"活"起来——它既是记录，也是程序；既是历史，也是智慧。