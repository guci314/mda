# Execution Context 强制外部化方案

## 问题分析

### LLM的本能行为
Agent验证图书添加时，会自然地：
```python
# 直接读文件验证（内部完成）
books = read_file("books.json")
if check_book_exists(books):
    print("验证成功")
```

这是合理的！人类也会这样做。但这不符合符号主义验证的要求。

### 符号主义的要求
我们需要：
1. 创建独立的验证脚本
2. 脚本可独立运行
3. 过程可追溯、可重复
4. 验证逻辑外部化

## 核心矛盾

**LLM训练出的本能 vs 科学方法的要求**

- LLM倾向于：效率、直接、内部推理
- 我们需要：可见、可重复、外部验证

## 解决方案：强制外部化

### 方案1：Execution Context程序正义

```python
class ExecutionContext:
    def __init__(self):
        self.required_steps = []
        self.completed_steps = []
        self.artifacts = []  # 必须产生的artifacts

    def require_step(self, step_name, artifact_type=None):
        """声明必须执行的步骤"""
        self.required_steps.append({
            'name': step_name,
            'artifact': artifact_type,
            'completed': False
        })

    def execute_step(self, step_name, action, result):
        """执行并记录步骤"""
        # 检查步骤是否在required_steps中
        if step_name not in [s['name'] for s in self.required_steps]:
            raise ValueError(f"步骤 {step_name} 未声明")

        # 执行action
        output = action()

        # 记录完成
        self.completed_steps.append({
            'name': step_name,
            'action': action,
            'result': output
        })

        # 如果需要artifact，检查是否生成
        step = next(s for s in self.required_steps if s['name'] == step_name)
        if step['artifact']:
            if not os.path.exists(output):
                raise ValueError(f"步骤 {step_name} 未生成required artifact: {step['artifact']}")

        return output

    def verify_completion(self):
        """验证所有required步骤都已完成"""
        for step in self.required_steps:
            if step['name'] not in [s['name'] for s in self.completed_steps]:
                raise ValueError(f"必需步骤 {step['name']} 未执行")

        # 检查artifacts
        for step in self.required_steps:
            if step['artifact']:
                artifact_path = f"{step['artifact']}"
                if not os.path.exists(artifact_path):
                    raise ValueError(f"缺少必需artifact: {artifact_path}")
```

### 方案2：在知识函数中嵌入Context要求

```markdown
#### 函数：@执行符号主义验证(函数名, 执行结果)
[强制外部化要求]

必须使用ExecutionContext：
```python
with ExecutionContext() as ctx:
    # 声明必须的步骤
    ctx.require_step("创建验证脚本", artifact="validate_*.py")
    ctx.require_step("执行验证脚本", artifact="validation_result.json")
    ctx.require_step("解析验证结果")

    # 步骤1：创建脚本
    ctx.execute_step("创建验证脚本",
        lambda: write_file(f"validate_{函数名}.py", script_content),
        expected_output=script_path
    )

    # 步骤2：执行脚本
    ctx.execute_step("执行验证脚本",
        lambda: execute_command(f"python {script_path}"),
        expected_output=result_json
    )

    # 步骤3：解析结果
    ctx.execute_step("解析验证结果",
        lambda: parse_json(result_json),
        expected_output=validation_report
    )

    # 验证所有步骤完成
    ctx.verify_completion()
```

如果Agent试图跳过任何步骤，Context会抛出异常。

### 方案3：工具层强制

修改CreateAgentTool，在创建Agent后强制检查：

```python
class CreateAgentTool:
    def execute(self, ...):
        # 创建Agent
        agent = create_agent(...)

        # 强制验证检查
        validation_artifacts = self.check_validation_artifacts(agent.work_dir)

        if not validation_artifacts['has_scripts']:
            # 强制创建验证脚本
            self.force_create_validation_scripts(agent)

        if not validation_artifacts['scripts_executed']:
            # 强制执行验证
            self.force_execute_validation(agent)

        # 只有通过验证才返回agent
        if not validation_artifacts['all_passed']:
            raise ValidationError("Agent未通过符号主义验证")

        return agent
```

## 实施建议

### 第一阶段：软约束
- 在知识文件中明确要求
- 记录是否创建了验证脚本
- 生成compliance报告

### 第二阶段：硬约束
- 实施ExecutionContext
- 不完成所有步骤就失败
- 强制artifact生成

### 第三阶段：智能引导
- 提供验证脚本模板
- 自动生成基础验证代码
- 让正确的路径变简单

## 关键洞察

### 抑制本能的必要性
LLM的"本能"（直接验证）虽然高效，但不符合科学方法。我们需要：
1. **程序正义**：不仅结果正确，过程也必须正确
2. **可追溯性**：每个步骤都有记录
3. **可重复性**：验证脚本可独立运行

### 类比
- **法庭**：不能仅凭法官的直觉，必须有证据链
- **科学实验**：不能仅有结论，必须有可重复的方法
- **软件测试**：不能仅手工验证，必须有自动化测试

## 预期效果

### Before（LLM本能）
```
思考：我读了books.json，看到书已经添加了，验证通过 ✓
```

### After（强制外部化）
```
步骤1：创建验证脚本 validate_add_book.py ✓
步骤2：执行 python validate_add_book.py ✓
步骤3：解析输出 {"passed": true} ✓
验证通过（有脚本为证）✓
```

## 实现优先级

1. **工具层检查**（最简单）
   - 在CreateAgentTool中添加验证
   - 立即可见效

2. **知识函数要求**（中等难度）
   - 修改知识文件
   - 明确Context使用

3. **ExecutionContext**（最完整）
   - 系统性解决
   - 需要架构改动

## 注意事项

### 平衡点
- 不是所有操作都需要外部化
- 只在关键验证点强制
- 保留一定的灵活性

### 避免过度
- 不要让Agent变成纯粹的脚本执行器
- 保留必要的推理能力
- 在约束和自由之间找平衡

## 结论

通过Execution Context强制外部化，我们可以：
1. 抑制LLM的"偷懒"本能
2. 确保符号主义验证的执行
3. 让过程可见、可追溯、可重复

这是在LLM的自然倾向和科学方法要求之间的必要妥协。

---

*创建时间：2025-01-19*
*核心洞察：LLM的本能需要被规则约束*