# @sequential-thinking 契约函数

## 函数签名
```python
@sequential-thinking(problem: str, max_thoughts: int = 5) -> str
```

## 目的
通过序列化的思考步骤，深入分析问题，逐步构建理解，最终得出结论。

## 执行步骤

### 1. **初始化思考**
```python
thoughts = []
current_thought = 1
total_thoughts = estimate_complexity(problem)  # 初步估算需要的思考步骤
```

### 2. **序列化思考循环**
对每个思考步骤：

```python
while current_thought <= total_thoughts and need_more_thinking:
    thought = {
        "number": current_thought,
        "content": think_about(problem, previous_thoughts),
        "type": classify_thought(),  # 分析/综合/评估/修正
        "confidence": 0.0-1.0,
        "next_needed": True/False
    }
    thoughts.append(thought)

    # 动态调整
    if realized_more_complex():
        total_thoughts += n
    if found_solution_early():
        next_needed = False
```

### 3. **思考类型分类**

| 类型 | 说明 | 示例 |
|------|------|------|
| **分析** | 分解问题，理解组成部分 | "这个问题包含三个子问题..." |
| **综合** | 整合信息，建立联系 | "结合前两点，我发现..." |
| **评估** | 判断和比较 | "方案A优于方案B因为..." |
| **修正** | 发现错误，调整方向 | "我之前的假设有误..." |
| **洞察** | 突然的理解 | "关键洞察：这本质是..." |

### 4. **深度控制机制**

```python
# 避免过度思考
if current_thought > max_thoughts:
    return summarize_best_understanding()

# 避免循环
if detecting_circular_reasoning():
    break_with_new_angle()

# 提前结束
if confidence >= 0.95:
    return final_conclusion()
```

### 5. **输出格式**

```markdown
## 思考过程

### 思考1：[类型]
[具体思考内容]
置信度：X.X

### 思考2：[类型]
[基于思考1的深入分析]
置信度：X.X

...

## 最终结论
[综合所有思考得出的结论]
总体置信度：X.X
```

## 使用场景

### 适合使用的情况
- 🎯 复杂问题需要分步分析
- 🎯 需要权衡多个因素
- 🎯 需要展示推理过程
- 🎯 探索性问题，答案不明确
- 🎯 需要自我修正的场景

### 不适合的情况
- ❌ 简单直接的问题
- ❌ 需要快速回答
- ❌ 事实性查询

## 示例调用

### 示例1：技术决策
```python
@sequential-thinking("should we use microservices or monolith?")

思考1：[分析] 需要考虑团队规模、项目复杂度、扩展需求...
思考2：[综合] 当前团队5人，项目中等复杂度，未来可能扩展...
思考3：[评估] 微服务增加复杂度但提供灵活性...
思考4：[洞察] 关键是团队能力和维护成本的平衡...
思考5：[结论] 建议从模块化单体开始，预留微服务迁移路径...
```

### 示例2：问题诊断
```python
@sequential-thinking("why is the API returning 500 errors?")

思考1：[分析] 500错误通常是服务器端问题，需要检查日志...
思考2：[分析] 错误开始于部署后，可能与新代码相关...
思考3：[洞察] 日志显示数据库连接超时...
思考4：[综合] 新代码增加了数据库查询，可能是连接池耗尽...
思考5：[结论] 根本原因：连接池大小不足，建议增加到100...
```

## 高级特性

### 1. 分支思考
```python
if multiple_valid_paths():
    branch_1 = explore_path_1()
    branch_2 = explore_path_2()
    merge_insights(branch_1, branch_2)
```

### 2. 回溯修正
```python
if realize_wrong_assumption():
    backtrack_to(thought_n)
    revise_from_there()
```

### 3. 元认知
```python
# 思考自己的思考
"我注意到我在假设X，让我质疑这个假设..."
"我的思考似乎陷入了Y模式，需要换个角度..."
```

## 与其他契约函数的关系

- **@learning**：sequential-thinking的结果可以作为学习材料
- **@validation**：可以用sequential-thinking来验证复杂逻辑
- **@meta-cognitive**：sequential-thinking是元认知的具体实现

## 实现要点

1. **保持思考连贯性**：每个思考基于前面的思考
2. **动态调整**：可以增加或减少思考步骤
3. **避免过度**：设置合理的上限
4. **记录路径**：保留完整的思考过程
5. **置信度追踪**：量化每步的确定性

## 哲学基础

### 认知科学依据
- **序列处理**：人类意识是序列化的
- **工作记忆限制**：每次只能处理有限信息
- **递增理解**：理解是渐进的过程

### 计算理论依据
- **分治法**：大问题分解为小问题
- **迭代改进**：逐步接近最优解
- **状态机**：思考作为状态转换

## 质量标准

✅ 好的sequential-thinking：
- 每步都有明确目的
- 思考之间有逻辑联系
- 能够自我修正
- 得出的结论有依据

❌ 差的sequential-thinking：
- 思考重复或冗余
- 缺乏深度
- 忽视重要因素
- 过早下结论

## 总结

@sequential-thinking将隐式的思考过程显式化，让复杂问题的解决过程可追踪、可验证、可学习。它是Agent深度思考能力的核心契约。