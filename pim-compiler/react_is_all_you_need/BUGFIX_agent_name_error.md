# Bug 修复报告：KeyError: 'agent_name'

## 问题描述

在运行极简 Agent 时出现错误：

```
❌ 任务执行出错: 'agent_name'
KeyError: 'agent_name'
```

## 错误分析

错误发生在 `ReactAgentMinimal._build_minimal_prompt()` 方法中，具体位置：

- 文件：`core/react_agent_minimal.py`
- 方法：`_build_minimal_prompt()`
- 行号：498-505

## 根本原因

1. 系统提示词模板文件 `knowledge/system_prompt.md` 中使用了 `{{agent_name}}` 占位符
2. 但在 `template.format()` 调用时，没有提供 `agent_name` 参数
3. 导致字符串格式化时找不到对应的占位符值

## 修复方案

在 `_build_minimal_prompt()` 方法的 `template.format()` 调用中添加 `agent_name` 参数：

```python
# 修复前
prompt = template.format(
    work_dir=self.work_dir,
    notes_dir=self.notes_dir,
    notes_file=self.notes_file,
    window_size=self.window_size,
    knowledge_content=knowledge_section
)

# 修复后
prompt = template.format(
    work_dir=self.work_dir,
    notes_dir=self.notes_dir,
    notes_file=self.notes_file,
    agent_name=self.agent_name,  # 添加这一行
    window_size=self.window_size,
    knowledge_content=knowledge_section
)
```

## 验证结果

✅ 修复后测试通过：

- `_build_minimal_prompt()` 方法执行成功
- `agent_name` 正确替换到系统提示词中
- PSM 生成 Agent 可以正常创建和初始化

## 影响范围

- 影响所有使用外部系统提示词模板的 ReactAgentMinimal 实例
- 不影响使用内置提示词的降级模式
- 修复后所有 Agent 都能正常工作

## 修复时间

2025-01-06

## 修复者

AI Assistant
