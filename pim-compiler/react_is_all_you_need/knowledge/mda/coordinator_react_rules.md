# MDA Pipeline协调器 - React产生式规则系统

## 🎯 目标声明

**主目标**: 从PSM文件生成100%测试通过的FastAPI应用

**成功条件**:
```python
def goal_achieved():
    return (
        exists("coordinator_todo.json") and
        exists("app/main.py") and
        pytest_result.failed == 0 and
        pytest_result.exit_code == 0
    )
```

## 📋 状态定义

系统状态包含以下变量：
- `code_generated`: bool - 代码是否已生成
- `test_run`: bool - 测试是否已运行
- `test_failed_count`: int - 失败测试数量
- `test_passed_count`: int - 通过测试数量
- `debug_attempts`: int - 调试尝试次数
- `max_debug_attempts`: int = 20 - 最大调试次数
- `todo_initialized`: bool - TODO是否已初始化
- `current_task`: str - 当前任务

## 🔄 产生式规则集

### Rule 1: 初始化TODO
```
IF: 
    NOT todo_initialized
THEN: 
    write_file("coordinator_todo.json", initial_todo_structure)
    SET todo_initialized = True
    SET current_task = "初始化"
```

### Rule 2: 生成代码
```
IF: 
    todo_initialized == True AND
    code_generated == False
THEN:
    CALL code_generator("从PSM生成FastAPI应用")
    SET code_generated = True
    UPDATE_TODO(task="生成代码", status="completed")
    SET current_task = "代码生成"
```

### Rule 3: 首次运行测试
```
IF:
    code_generated == True AND
    test_run == False
THEN:
    result = execute_command("pytest tests/ -v")
    PARSE test_failed_count, test_passed_count FROM result
    SET test_run = True
    UPDATE_TODO(task="运行测试", status="completed")
    SET current_task = "测试验证"
```

### Rule 4: 调用调试Agent（当测试失败时）
```
IF:
    test_run == True AND
    test_failed_count > 0 AND
    debug_attempts < max_debug_attempts
THEN:
    CALL code_debugger("修复所有测试失败，使用fix_python_syntax_errors工具")
    INCREMENT debug_attempts
    SET current_task = "调试修复"
```

### Rule 5: 验证调试结果
```
IF:
    current_task == "调试修复" AND
    debug_attempts > 0
THEN:
    result = execute_command("pytest tests/ -v")
    PARSE test_failed_count, test_passed_count FROM result
    SET current_task = "验证修复"
```

### Rule 6: 继续调试（如果仍有失败）
```
IF:
    current_task == "验证修复" AND
    test_failed_count > 0 AND
    debug_attempts < max_debug_attempts
THEN:
    SET current_task = "需要继续调试"
    # 这会触发Rule 4
```

### Rule 7: 标记完成（当所有测试通过）
```
IF:
    test_run == True AND
    test_failed_count == 0
THEN:
    UPDATE_TODO(task="确认成功", status="completed")
    SET current_task = "已完成"
    REPORT "✅ 任务成功完成：所有测试通过"
```

### Rule 8: 标记失败（达到最大尝试）
```
IF:
    debug_attempts >= max_debug_attempts AND
    test_failed_count > 0
THEN:
    UPDATE_TODO(task="调试", status="failed")
    SET current_task = "需要人工介入"
    REPORT "❌ 达到最大调试次数，仍有{test_failed_count}个测试失败"
```

### Rule 9: 处理生成失败
```
IF:
    todo_initialized == True AND
    code_generated == False AND
    generation_failed == True
THEN:
    RETRY code_generator OR
    SET current_task = "生成失败"
    REPORT "❌ 代码生成失败"
```

### Rule 10: 处理测试命令失败
```
IF:
    test_command_error == True
THEN:
    CHECK environment
    CHECK tests_directory_exists
    REPORT "❌ 测试命令执行失败：{error_message}"
```

## 🔍 条件检查函数

### 检查测试结果
```python
def parse_test_result(output):
    # 从pytest输出解析失败数和通过数
    import re
    match = re.search(r'(\d+) failed.*(\d+) passed', output)
    if match:
        return int(match.group(1)), int(match.group(2))
    elif "all tests passed" in output:
        return 0, total_tests
    else:
        return -1, -1  # 解析失败
```

### 检查文件存在
```python
def check_files():
    return {
        "todo_exists": exists("coordinator_todo.json"),
        "app_exists": exists("app/main.py"),
        "tests_exist": exists("tests/")
    }
```

## 🎮 执行策略

### React循环
```python
def react_loop():
    """基于规则的React循环"""
    while not goal_achieved():
        # 评估所有规则条件
        for rule in RULES:
            if rule.condition_met(STATE):
                rule.execute()
                break  # 一次只执行一条规则
        
        # 防止无限循环
        if STATE.iterations > 100:
            break
```

### 状态转移图
```
[初始] → [TODO初始化] → [生成代码] → [运行测试]
                                          ↓
                                    [测试失败?]
                                      ↙     ↘
                                   是         否
                                    ↓         ↓
                              [调用调试]  [标记完成]
                                    ↓
                              [验证修复]
                                    ↓
                              [仍有失败?]
                                  ↙     ↘
                               是         否
                                ↓         ↓
                          [继续调试]  [标记完成]
```

## 💡 使用指南

### 为Kimi优化的提示

当使用这个规则系统时，你应该：

1. **每次只关注当前状态**
   - 不需要记住整个流程
   - 只需要检查条件，执行对应动作

2. **明确的状态检查**
   ```
   我的当前状态是什么？
   - code_generated? 
   - test_failed_count?
   - debug_attempts?
   ```

3. **简单的规则匹配**
   ```
   哪条规则的条件满足了？
   执行该规则的动作
   更新状态
   ```

4. **不需要复杂推理**
   - 规则已经编码了所有逻辑
   - 只需要模式匹配和执行

## 📊 验证检查清单

每个规则执行后验证：
- [ ] 状态变量已更新
- [ ] TODO已更新
- [ ] 如果运行了测试，解析了结果
- [ ] 如果调用了Agent，记录了返回
- [ ] current_task反映了真实状态

## 🚦 触发条件优先级

1. **最高优先级**: 初始化（Rule 1）
2. **高优先级**: 生成代码（Rule 2）
3. **中优先级**: 运行测试（Rule 3, 5）
4. **低优先级**: 调试（Rule 4, 6）
5. **终止条件**: 成功或失败（Rule 7, 8）

## 🎯 关键优势

### 相比工作流方式：

1. **无需维持复杂状态机**
   - 每个规则独立
   - 不需要记住在流程的哪一步

2. **适合条件反射式执行**
   - IF看到X THEN做Y
   - 不需要理解"为什么"

3. **容错性更强**
   - 即使忘记了之前做了什么
   - 只要状态正确，可以继续

4. **更适合Kimi等模型**
   - 降低了推理要求
   - 转化为模式匹配任务

## 📝 示例执行轨迹

```
状态: {code_generated: False, test_run: False}
触发: Rule 1 (初始化TODO)
动作: 创建coordinator_todo.json

状态: {todo_initialized: True, code_generated: False}
触发: Rule 2 (生成代码)
动作: 调用code_generator

状态: {code_generated: True, test_run: False}
触发: Rule 3 (运行测试)
动作: pytest tests/
结果: 5 failed, 8 passed

状态: {test_failed_count: 5, debug_attempts: 0}
触发: Rule 4 (调用调试)
动作: 调用code_debugger

状态: {debug_attempts: 1}
触发: Rule 5 (验证修复)
动作: pytest tests/
结果: 2 failed, 11 passed

状态: {test_failed_count: 2, debug_attempts: 1}
触发: Rule 4 (继续调试)
动作: 调用code_debugger

...循环直到...

状态: {test_failed_count: 0}
触发: Rule 7 (标记完成)
动作: 报告成功
```

## 🔑 成功的关键

> **"不需要思考，只需要反应"**
> 
> 像膝跳反射一样：
> - 锤子敲击（条件） → 腿弹起（动作）
> - 测试失败（条件） → 调用调试（动作）
> - 调试完成（条件） → 验证结果（动作）

这就是为什么即使是Kimi也可能成功执行协调任务 - 因为规则已经编码了所有智慧，执行者只需要做条件反射。

## 🎓 理论基础

这个系统基于：
- **产生式系统**（Production System）
- **专家系统**（Expert System）
- **条件-动作规则**（Condition-Action Rules）

将复杂的协调逻辑分解为简单的IF-THEN规则，降低了对执行者推理能力的要求。