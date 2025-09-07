# Domain-Specific task_process.md架构

## 核心洞察：没有通用的Hook点

Hook点的问题：
```python
# 这个hook在哪里触发？
on_after_think?  # Debug时太频繁
on_after_tool?   # Generate时太稀疏  
on_pattern_found? # 只有学习任务才有
```

**结论**：通用hook是伪需求，真实需求是domain-specific的状态管理。

## 新思路：让知识驱动task_process.md

### 核心理念
不是通过代码Hook，而是通过**知识文件**告诉Agent何时更新task_process.md。

## 方案A：知识模板驱动

### 1. Debug知识模板
```markdown
# debug_task_process_template.md

## 何时更新task_process.md

### 发现错误时
```python
error_found = analyze_error()
append_to_task_process(f"""
### 错误 #{error_count}
- 文件: {file}
- 行号: {line}
- 类型: {error_type}
""")
```

### 修复完成时
```python
mark_in_task_process(f"- [x] 修复错误 #{error_num}")
```

### 测试通过时
```python
update_task_process("## 状态: 所有错误已修复")
```
```

### 2. Generation知识模板
```markdown
# generation_task_process_template.md

## 何时更新task_process.md

### 分析完PSM后
```python
write_task_process(f"""
## 待生成文件
- [ ] app/main.py
- [ ] app/models.py
- [ ] app/schemas.py
""")
```

### 每个文件生成后
```python
mark_completed(f"- [x] {file_path}")
add_stats(f"已生成: {files_count}/{total_files}")
```
```

### 3. Optimization知识模板
```markdown
# optimization_task_process_template.md

## 何时更新task_process.md

### 基线测试后
```python
record_baseline(f"""
## 基线性能
- 响应时间: {baseline_time}ms
- 内存使用: {baseline_memory}MB
""")
```

### 每次优化后
```python
append_optimization(f"""
### 优化 #{opt_count}: {technique}
- 改进: {improvement}%
- 新指标: {new_metrics}
""")
```
```

## 方案B：Convention驱动（约定优于配置）

### 文件命名约定
```
.notes/{agent_name}/
├── task_process.md         # 标准名称
├── task_process.debug.md   # Debug专用
├── task_process.gen.md     # Generation专用
└── task_process.opt.md     # Optimization专用
```

### Agent自动选择
```python
# Agent根据任务类型自动选择文件
if "debug" in task or "fix" in task:
    process_file = "task_process.debug.md"
elif "generate" in task or "create" in task:
    process_file = "task_process.gen.md"
elif "optimize" in task or "improve" in task:
    process_file = "task_process.opt.md"
else:
    process_file = "task_process.md"
```

## 方案C：消息协议驱动

### 标准化状态消息
```python
# ProgramAgent发送标准化消息
def report_state(state_type, data):
    """通过工具调用报告状态"""
    write_file(".notes/state_report.json", {
        "timestamp": now(),
        "type": state_type,
        "data": data
    })

# 不同domain有不同的state_type
DEBUG_STATES = ["error_found", "error_fixed", "test_passed"]
GEN_STATES = ["file_created", "validation_passed"]
OPT_STATES = ["baseline_measured", "optimization_applied"]
```

### OSAgent监听和转换
```python
# OSAgent监听状态报告
state_reports = read_file(".notes/state_report.json")

# 根据domain转换为task_process.md
if state["type"] in DEBUG_STATES:
    format_debug_process(state)
elif state["type"] in GEN_STATES:
    format_generation_process(state)
```

## 方案D：自然语言协议

### 最简单的方案：直接说！
```markdown
# 在任务执行中，ProgramAgent直接说：

"现在更新task_process：发现了3个错误"
"现在更新task_process：已修复第1个错误"
"现在更新task_process：所有测试通过"
```

### OSAgent解析自然语言
```python
# OSAgent监听包含"更新task_process"的消息
if "更新task_process" in agent_output:
    content = extract_after("更新task_process：", agent_output)
    append_to_task_process(content)
```

## 方案E：双层架构（推荐）

### Layer 1：通用机制（简单可靠）
```python
# ReactAgentMinimal提供最基础的机制
class ReactAgentMinimal:
    def write_process_state(self, content):
        """通用的状态写入方法"""
        current = read_file(self.task_process_file)
        updated = current + "\n" + content
        write_file(self.task_process_file, updated)
```

### Layer 2：Domain知识（灵活强大）
```markdown
# debug_knowledge.md
## 使用write_process_state记录调试过程

当发现错误时：
write_process_state(f"错误#{n}: {description}")

当修复完成时：
write_process_state(f"修复#{n}: {solution}")

# generation_knowledge.md  
## 使用write_process_state记录生成过程

每生成一个文件：
write_process_state(f"✅ 生成: {file_path}")
```

## 最终建议：知识驱动 + 约定

### 1. 不改ReactAgentMinimal代码
保持核心简单，不加domain-specific的hook。

### 2. 通过知识文件定义行为
每个domain有自己的task_process管理知识：
- `debug_task_process_guide.md`
- `generation_task_process_guide.md`
- `optimization_task_process_guide.md`

### 3. 使用约定简化
- 标准文件名：`task_process.md`
- 标准结构：TODO列表 + 状态信息
- 标准更新时机：在知识中明确定义

### 4. OSAgent作为保底
如果ProgramAgent忘记更新，OSAgent可以：
```python
# 检测task_process.md最后更新时间
if not updated_recently(task_process):
    # 从agent的输出推断状态
    inferred_state = infer_from_output(agent.messages)
    update_task_process(inferred_state)
```

## 哲学思考

### Unix哲学的启示
> "Provide mechanism, not policy"

ReactAgentMinimal应该：
- 提供**机制**：read_file, write_file
- 不定**策略**：何时更新task_process.md

策略应该在知识层定义，因为它是domain-specific的。

### 生物学类比
- **DNA（代码）**：提供基础机制
- **表观遗传（知识）**：定义具体行为
- **进化（学习）**：优化行为模式

## 结论

**不需要通用Hook！**

正确的架构是：
1. **ReactAgentMinimal**：提供文件读写机制
2. **Domain知识**：定义何时/如何更新task_process.md
3. **约定规范**：统一文件名和格式
4. **OSAgent**：监督和保底

这样每个domain可以有自己的task_process管理策略，而核心代码保持简单通用。

> "The right abstraction is no abstraction" - 当抽象不合适时，不如不抽象