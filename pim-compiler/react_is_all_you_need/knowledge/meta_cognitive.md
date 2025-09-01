# 元认知知识库 - 动态Agent创建策略

## 核心理念
元认知Agent作为"调度器"，根据任务特征动态决定：
1. 使用哪个LLM模型
2. 加载哪些知识文件
3. 设置什么参数
4. 创建并调用子Agent执行任务

## 任务分类与模型选择

### 1. 调试与错误修复任务
**特征识别**：
- 关键词：debug, fix, error, bug, test, failure, traceback
- 存在错误栈信息
- 需要多步推理找到根因

**模型选择**：
```python
if task_type == "debugging":
    # 优先级顺序
    models = [
        ("anthropic/claude-3-opus", "最佳但昂贵"),
        ("deepseek/deepseek-r1-distill-qwen-32b", "性价比最高"),
        ("openai/o3-mini", "快速可靠"),
    ]
    knowledge_files = [
        "knowledge/debug_knowledge.md",
        "knowledge/structured_notes.md",
        "knowledge/error_patterns.md"
    ]
```

### 2. 代码生成任务
**特征识别**：
- 关键词：create, implement, write, build, develop
- 需要生成新代码
- 有明确的功能需求

**模型选择**：
```python
if task_type == "code_generation":
    models = [
        ("google/gemini-2.5-flash", "速度最快"),
        ("anthropic/claude-3.5-sonnet", "质量好"),
        ("qwen/qwen3-coder", "专门优化"),
    ]
    knowledge_files = [
        "knowledge/coding_patterns.md",
        "knowledge/best_practices.md"
    ]
```

### 3. 代码审查与重构
**特征识别**：
- 关键词：review, refactor, optimize, improve
- 需要分析现有代码
- 提出改进建议

**模型选择**：
```python
if task_type == "code_review":
    models = [
        ("deepseek/deepseek-r1", "深度分析"),
        ("anthropic/claude-3.5-sonnet", "平衡选择"),
    ]
    knowledge_files = [
        "knowledge/code_review_checklist.md",
        "knowledge/refactoring_patterns.md"
    ]
```

### 4. 文档与解释任务
**特征识别**：
- 关键词：explain, document, describe, how, why
- 需要理解和解释
- 生成文档

**模型选择**：
```python
if task_type == "documentation":
    models = [
        ("anthropic/claude-3.5-sonnet", "表达清晰"),
        ("google/gemini-2.5-flash", "快速生成"),
    ]
    knowledge_files = [
        "knowledge/documentation_guide.md"
    ]
```

### 5. 数据分析任务
**特征识别**：
- 关键词：analyze, data, statistics, report
- 涉及数据处理
- 需要分析洞察

**模型选择**：
```python
if task_type == "data_analysis":
    models = [
        ("deepseek/deepseek-r1", "推理分析"),
        ("openai/gpt-4", "通用分析"),
    ]
    knowledge_files = [
        "knowledge/data_analysis.md"
    ]
```

## 任务复杂度评估

### 复杂度指标
```python
def assess_complexity(task_description):
    complexity_score = 0
    
    # 代码行数
    if "large" in task or "complex" in task:
        complexity_score += 3
    
    # 多文件涉及
    if "multiple files" in task or "across" in task:
        complexity_score += 2
    
    # 需要推理
    if "why" in task or "debug" in task:
        complexity_score += 3
    
    # 时间敏感
    if "urgent" in task or "quickly" in task:
        complexity_score -= 1  # 倾向快速模型
    
    return complexity_score
```

### 基于复杂度的模型调整
```python
if complexity_score > 5:
    # 使用推理模型
    use_reasoning_model = True
    temperature = 0  # 确定性输出
elif complexity_score > 2:
    # 使用平衡模型
    use_balanced_model = True
    temperature = 0.3
else:
    # 使用快速模型
    use_fast_model = True
    temperature = 0.5
```

## 知识文件选择策略

### 基础知识文件（始终加载）
```python
base_knowledge = [
    "knowledge/structured_notes.md",  # 笔记系统
    "knowledge/agent_knowledge.md",   # 基础知识
]
```

### 任务特定知识文件
```python
task_specific_knowledge = {
    "debugging": ["debug_knowledge.md", "error_patterns.md"],
    "testing": ["test_patterns.md", "pytest_guide.md"],
    "api": ["api_design.md", "rest_patterns.md"],
    "database": ["sql_patterns.md", "orm_guide.md"],
    "frontend": ["react_patterns.md", "ui_guidelines.md"],
    "performance": ["optimization.md", "profiling.md"],
}
```

### 动态知识加载
```python
def select_knowledge_files(task, detected_tech_stack):
    files = base_knowledge.copy()
    
    # 根据任务类型
    for keyword, knowledge in task_specific_knowledge.items():
        if keyword in task.lower():
            files.extend(knowledge)
    
    # 根据技术栈
    if "fastapi" in detected_tech_stack:
        files.append("knowledge/fastapi_patterns.md")
    if "react" in detected_tech_stack:
        files.append("knowledge/react_patterns.md")
    
    # 去重
    return list(set(files))
```

## Agent创建决策流程

### 1. 任务分析
```python
def analyze_task(task_description):
    return {
        "type": classify_task_type(task_description),
        "complexity": assess_complexity(task_description),
        "urgency": detect_urgency(task_description),
        "tech_stack": detect_tech_stack(task_description),
        "requires_reasoning": needs_reasoning(task_description)
    }
```

### 2. 资源分配
```python
def allocate_resources(task_analysis):
    # 模型选择
    if task_analysis["requires_reasoning"]:
        if task_analysis["urgency"] == "high":
            model = "openai/o3-mini"  # 快速推理
        else:
            model = "deepseek/deepseek-r1"  # 深度推理
    else:
        if task_analysis["complexity"] > 3:
            model = "anthropic/claude-3.5-sonnet"
        else:
            model = "google/gemini-2.5-flash"
    
    # 知识文件
    knowledge = select_knowledge_files(
        task_analysis["type"], 
        task_analysis["tech_stack"]
    )
    
    # 参数设置
    params = {
        "temperature": 0 if task_analysis["requires_reasoning"] else 0.3,
        "max_iterations": 100 if task_analysis["complexity"] > 5 else 50,
        "sliding_window": 50 if task_analysis["complexity"] > 3 else 30
    }
    
    return model, knowledge, params
```

### 3. Agent创建与执行
```python
def create_and_execute_agent(task):
    # 分析任务
    analysis = analyze_task(task)
    
    # 分配资源
    model, knowledge, params = allocate_resources(analysis)
    
    # 创建Agent
    agent = ReactAgentMinimal(
        work_dir="my_project",
        model=model,
        knowledge_files=knowledge,
        temperature=params["temperature"],
        max_iterations=params["max_iterations"],
        sliding_window_size=params["sliding_window"]
    )
    
    # 执行任务
    result = agent.run(task)
    
    # 返回结果和元信息
    return {
        "result": result,
        "meta": {
            "model_used": model,
            "knowledge_files": knowledge,
            "complexity": analysis["complexity"],
            "iterations": agent.iteration_count
        }
    }
```

## 自适应学习机制

### 性能追踪
```python
performance_history = {
    "debugging": {
        "claude-opus": {"success_rate": 0.95, "avg_iterations": 68},
        "deepseek-r1": {"success_rate": 0.85, "avg_iterations": 99},
    },
    "code_generation": {
        "gemini-2.5": {"success_rate": 0.90, "avg_iterations": 11},
        "claude-sonnet": {"success_rate": 0.92, "avg_iterations": 25},
    }
}
```

### 动态调整策略
```python
def update_model_preference(task_type, model, success, iterations):
    # 更新历史记录
    history = performance_history[task_type][model]
    history["success_rate"] = (
        history["success_rate"] * 0.9 + 
        (1.0 if success else 0.0) * 0.1
    )
    history["avg_iterations"] = (
        history["avg_iterations"] * 0.9 + 
        iterations * 0.1
    )
    
    # 重新排序模型优先级
    rerank_models_for_task(task_type)
```

## 成本优化策略

### 成本感知决策
```python
def cost_aware_model_selection(task_analysis, budget_constraint):
    models = get_suitable_models(task_analysis)
    
    for model in models:
        cost = estimate_cost(model, task_analysis["complexity"])
        if cost <= budget_constraint:
            return model
    
    # 降级到更便宜的模型
    return fallback_to_cheaper_model(task_analysis)
```

### 分阶段执行
```python
def staged_execution(task):
    # 第一阶段：快速模型尝试
    quick_result = try_with_fast_model(task)
    if quick_result.success:
        return quick_result
    
    # 第二阶段：推理模型
    reasoning_result = try_with_reasoning_model(task)
    return reasoning_result
```

## 实际应用示例

### 示例1：调试任务
```python
task = "运行单元测试，如果失败，修复代码"

# 元认知分析
analysis = {
    "type": "debugging",
    "complexity": 7,
    "requires_reasoning": True
}

# 决策
model = "deepseek/deepseek-r1-distill-qwen-32b"
knowledge = [
    "debug_knowledge.md",
    "structured_notes.md",
    "error_patterns.md"
]

# 创建并执行
agent = create_agent(model, knowledge)
result = agent.run(task)
```

### 示例2：简单代码生成
```python
task = "创建一个TODO列表组件"

# 元认知分析
analysis = {
    "type": "code_generation",
    "complexity": 2,
    "requires_reasoning": False
}

# 决策
model = "google/gemini-2.5-flash"
knowledge = ["react_patterns.md"]

# 快速执行
agent = create_agent(model, knowledge)
result = agent.run(task)
```

## 监控与反馈

### 执行监控
```python
def monitor_execution(agent, task):
    metrics = {
        "start_time": time.time(),
        "iterations": 0,
        "errors": [],
        "model_switches": 0
    }
    
    # 实时监控
    while agent.is_running():
        if agent.iteration > 50 and not agent.making_progress():
            # 考虑切换模型
            switch_to_better_model(agent)
            metrics["model_switches"] += 1
    
    return metrics
```

### 结果评估
```python
def evaluate_result(result, expected_outcome):
    score = 0
    
    # 正确性
    if result.meets_requirements(expected_outcome):
        score += 5
    
    # 效率
    if result.iterations < expected_iterations:
        score += 2
    
    # 成本
    if result.cost < budget:
        score += 3
    
    return score
```

## 最佳实践

1. **始终从简单模型开始**：除非明确需要推理
2. **知识文件精简**：只加载必要的知识
3. **设置超时机制**：避免无限循环
4. **保留执行历史**：用于持续优化
5. **成本预算控制**：设置最大花费限制
6. **降级机制**：高级模型失败时的备选方案
7. **并行尝试**：紧急任务可多模型并行
8. **缓存结果**：相似任务复用之前的分析