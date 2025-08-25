# Agent元认知任务分解架构

## 概述

元认知任务分解是Agent面对复杂任务时的自适应能力。当任务复杂度超过模型能力边界时（如Kimi失败而Gemini成功的场景），Agent需要具备：
1. **元认知能力**：检测任务失败或复杂度过高
2. **分解能力**：将复杂任务拆分为可管理的子任务
3. **领域无关性**：适用于任何领域的任务分解

## 核心问题

### 案例：MDA生成任务失败分析

```
现象：
- Gemini 2.5 Pro成功完成"生成FastAPI程序"
- Kimi失败在同一任务上
- 原因：单步骤复杂度超过Kimi的处理能力

人类解决方案：
- 检测到任务太复杂
- 将任务分解为更小的步骤
- 逐步完成每个子任务
```

## 元认知检测机制

### 1. 失败模式识别

```python
class MetacognitiveDetector:
    """元认知失败检测器"""
    
    def detect_failure_patterns(self, execution_trace):
        """检测执行中的失败模式"""
        
        patterns = {
            "循环失败": self._check_repetitive_errors(execution_trace),
            "输出截断": self._check_output_truncation(execution_trace),
            "理解偏差": self._check_comprehension_drift(execution_trace),
            "资源耗尽": self._check_resource_exhaustion(execution_trace),
            "超时": self._check_timeout(execution_trace),
            "不完整输出": self._check_incomplete_output(execution_trace)
        }
        
        return patterns
    
    def _check_repetitive_errors(self, trace):
        """检测重复错误"""
        error_counts = {}
        for event in trace:
            if event.type == "error":
                error_counts[event.message] = error_counts.get(event.message, 0) + 1
        
        # 同一错误出现3次以上
        return any(count >= 3 for count in error_counts.values())
    
    def _check_output_truncation(self, trace):
        """检测输出被截断"""
        for event in trace:
            if event.type == "output":
                if event.is_truncated or len(event.content) >= event.max_length * 0.95:
                    return True
        return False
    
    def _check_comprehension_drift(self, trace):
        """检测理解偏差"""
        # 输出与期望严重不符
        for event in trace:
            if event.type == "validation":
                if event.similarity_score < 0.3:
                    return True
        return False
```

### 2. 复杂度评估

```python
class ComplexityAnalyzer:
    """任务复杂度分析器"""
    
    def analyze_task_complexity(self, task_description):
        """评估任务复杂度"""
        
        metrics = {
            "步骤数量": self._count_steps(task_description),
            "依赖深度": self._analyze_dependencies(task_description),
            "领域知识要求": self._assess_domain_knowledge(task_description),
            "输出规模": self._estimate_output_size(task_description),
            "认知负载": self._calculate_cognitive_load(task_description)
        }
        
        # 综合评分 (0-1)
        complexity_score = self._calculate_overall_complexity(metrics)
        
        return {
            "score": complexity_score,
            "metrics": metrics,
            "decomposition_needed": complexity_score > 0.7
        }
    
    def _calculate_cognitive_load(self, task):
        """计算认知负载"""
        factors = {
            "概念数量": len(self._extract_concepts(task)),
            "抽象层次": self._measure_abstraction_level(task),
            "上下文切换": self._count_context_switches(task),
            "记忆需求": self._estimate_memory_requirement(task)
        }
        
        # 加权计算
        load = (
            factors["概念数量"] * 0.3 +
            factors["抽象层次"] * 0.3 +
            factors["上下文切换"] * 0.2 +
            factors["记忆需求"] * 0.2
        )
        
        return min(load / 100, 1.0)
```

## 领域无关的任务分解策略

### 1. 通用分解模式

```python
class UniversalDecomposer:
    """通用任务分解器"""
    
    def decompose(self, task, model_capability):
        """根据模型能力分解任务"""
        
        # 选择分解策略
        strategy = self._select_strategy(task, model_capability)
        
        # 应用分解
        subtasks = strategy.decompose(task)
        
        # 验证子任务复杂度
        for subtask in subtasks:
            if self._is_still_complex(subtask, model_capability):
                # 递归分解
                subtask.children = self.decompose(subtask, model_capability)
        
        return subtasks
    
    def _select_strategy(self, task, capability):
        """选择分解策略"""
        
        strategies = [
            TemporalDecomposition(),      # 时序分解
            FunctionalDecomposition(),     # 功能分解
            DataFlowDecomposition(),       # 数据流分解
            HierarchicalDecomposition(),   # 层次分解
            IterativeRefinement()          # 迭代细化
        ]
        
        # 评分选择最佳策略
        best_strategy = max(
            strategies,
            key=lambda s: s.fitness_score(task, capability)
        )
        
        return best_strategy
```

### 2. 时序分解策略

```python
class TemporalDecomposition:
    """按时间顺序分解任务"""
    
    def decompose(self, task):
        steps = []
        
        # 识别时序标记
        temporal_markers = [
            "首先", "然后", "接下来", "最后",
            "第一步", "第二步", "步骤1", "步骤2",
            "before", "after", "then", "finally"
        ]
        
        # 提取时序步骤
        segments = self._split_by_markers(task.description, temporal_markers)
        
        for i, segment in enumerate(segments):
            steps.append({
                "id": f"step_{i+1}",
                "description": segment,
                "dependencies": [f"step_{i}"] if i > 0 else [],
                "type": "sequential"
            })
        
        return steps
```

### 3. 功能分解策略

```python
class FunctionalDecomposition:
    """按功能模块分解任务"""
    
    def decompose(self, task):
        modules = []
        
        # 识别功能动词
        functional_verbs = [
            "创建", "生成", "验证", "测试", "部署",
            "分析", "设计", "实现", "优化", "配置",
            "create", "generate", "validate", "test", "deploy"
        ]
        
        # 提取功能模块
        functions = self._extract_functions(task.description, functional_verbs)
        
        for func in functions:
            modules.append({
                "id": f"func_{func.name}",
                "function": func.name,
                "inputs": func.inputs,
                "outputs": func.outputs,
                "description": func.description,
                "type": "functional"
            })
        
        return modules
```

### 4. 递归分解策略

```python
class RecursiveDecomposition:
    """递归分解直到达到可处理粒度"""
    
    def decompose(self, task, max_depth=5):
        if max_depth == 0:
            return [task]
        
        # 评估任务复杂度
        complexity = self._assess_complexity(task)
        
        if complexity <= self.threshold:
            return [task]
        
        # 分解为子任务
        subtasks = self._split_task(task)
        
        result = []
        for subtask in subtasks:
            # 递归分解每个子任务
            decomposed = self.decompose(subtask, max_depth - 1)
            result.extend(decomposed)
        
        return result
    
    def _split_task(self, task):
        """将任务分割为2-4个子任务"""
        
        # 尝试不同的分割方法
        split_methods = [
            self._split_by_conjunctions,    # 按连词分割
            self._split_by_sentences,        # 按句子分割
            self._split_by_paragraphs,       # 按段落分割
            self._split_by_concepts          # 按概念分割
        ]
        
        for method in split_methods:
            subtasks = method(task)
            if 2 <= len(subtasks) <= 4:
                return subtasks
        
        # 强制二分
        return self._binary_split(task)
```

## 自适应分解框架

### 1. 模型能力感知

```python
class ModelCapabilityProfile:
    """模型能力画像"""
    
    def __init__(self, model_name):
        self.model_name = model_name
        self.capabilities = self._load_profile(model_name)
    
    def _load_profile(self, model_name):
        """加载模型能力配置"""
        
        profiles = {
            "gemini-2.5-pro": {
                "max_tokens": 32000,
                "complexity_threshold": 0.9,
                "parallel_capacity": 10,
                "domain_expertise": ["code", "analysis", "reasoning"],
                "strengths": ["complex_generation", "multi_step_reasoning"],
                "weaknesses": []
            },
            "kimi-k2-turbo": {
                "max_tokens": 128000,
                "complexity_threshold": 0.6,
                "parallel_capacity": 5,
                "domain_expertise": ["general", "search"],
                "strengths": ["long_context", "information_retrieval"],
                "weaknesses": ["complex_generation", "deep_reasoning"]
            },
            "gpt-4": {
                "max_tokens": 8000,
                "complexity_threshold": 0.8,
                "parallel_capacity": 8,
                "domain_expertise": ["general", "code", "creative"],
                "strengths": ["reasoning", "creativity"],
                "weaknesses": ["long_output"]
            }
        }
        
        return profiles.get(model_name, self._default_profile())
    
    def can_handle(self, task_complexity):
        """判断模型是否能处理任务"""
        return task_complexity.score <= self.capabilities["complexity_threshold"]
```

### 2. 动态分解调整

```python
class AdaptiveDecomposer:
    """自适应任务分解器"""
    
    def __init__(self, model_profile):
        self.model = model_profile
        self.decomposition_history = []
    
    def decompose_with_feedback(self, task):
        """带反馈的分解"""
        
        # 初始分解
        subtasks = self._initial_decomposition(task)
        
        # 测试执行
        for subtask in subtasks[:1]:  # 测试第一个子任务
            success, feedback = self._test_execution(subtask)
            
            if not success:
                # 根据反馈调整分解粒度
                subtasks = self._refine_decomposition(
                    task, 
                    subtasks, 
                    feedback
                )
        
        return subtasks
    
    def _refine_decomposition(self, task, current_subtasks, feedback):
        """根据反馈细化分解"""
        
        if "too_complex" in feedback:
            # 进一步细分
            refined = []
            for subtask in current_subtasks:
                refined.extend(self._split_further(subtask))
            return refined
        
        elif "missing_context" in feedback:
            # 增加上下文
            return self._add_context(current_subtasks)
        
        elif "wrong_order" in feedback:
            # 调整顺序
            return self._reorder_subtasks(current_subtasks)
        
        return current_subtasks
```

## 执行与监控

### 1. 检查点机制

```python
class CheckpointExecutor:
    """带检查点的执行器"""
    
    def execute_with_checkpoints(self, subtasks):
        """执行并保存检查点"""
        
        completed = []
        checkpoint_file = "execution_checkpoint.json"
        
        # 恢复之前的进度
        if os.path.exists(checkpoint_file):
            completed = self._load_checkpoint(checkpoint_file)
        
        for i, subtask in enumerate(subtasks):
            if subtask.id in completed:
                continue  # 跳过已完成的
            
            try:
                # 执行子任务
                result = self._execute_subtask(subtask)
                
                # 验证结果
                if self._validate_result(result, subtask):
                    completed.append(subtask.id)
                    self._save_checkpoint(checkpoint_file, completed)
                else:
                    # 失败处理
                    self._handle_failure(subtask, result)
                    
            except Exception as e:
                # 异常处理
                self._handle_exception(subtask, e)
                break
        
        return completed
```

### 2. 进度追踪

```python
class ProgressTracker:
    """进度追踪器"""
    
    def __init__(self, total_subtasks):
        self.total = total_subtasks
        self.completed = 0
        self.failed = 0
        self.in_progress = None
        self.start_time = time.time()
    
    def update(self, subtask_id, status):
        """更新进度"""
        
        if status == "completed":
            self.completed += 1
        elif status == "failed":
            self.failed += 1
        elif status == "in_progress":
            self.in_progress = subtask_id
        
        # 计算统计信息
        self.progress_percentage = (self.completed / self.total) * 100
        self.success_rate = self.completed / (self.completed + self.failed) if (self.completed + self.failed) > 0 else 0
        self.estimated_completion = self._estimate_completion()
        
        # 生成报告
        return self._generate_report()
    
    def _generate_report(self):
        """生成进度报告"""
        return {
            "总任务数": self.total,
            "已完成": self.completed,
            "失败": self.failed,
            "进度": f"{self.progress_percentage:.1f}%",
            "成功率": f"{self.success_rate:.1%}",
            "当前任务": self.in_progress,
            "预计完成时间": self.estimated_completion
        }
```

## 实现示例

### 1. 完整的元认知Agent

```python
class MetacognitiveAgent(GenericReactAgent):
    """具有元认知能力的Agent"""
    
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        
        # 初始化元认知组件
        self.detector = MetacognitiveDetector()
        self.analyzer = ComplexityAnalyzer()
        self.decomposer = UniversalDecomposer()
        self.executor = CheckpointExecutor()
        
        # 模型能力画像
        self.model_profile = ModelCapabilityProfile(config.llm_model)
    
    def execute_task(self, task_description):
        """执行任务（带元认知）"""
        
        # 1. 复杂度分析
        complexity = self.analyzer.analyze_task_complexity(task_description)
        
        if not complexity["decomposition_needed"]:
            # 直接执行
            return super().execute_task(task_description)
        
        # 2. 任务分解
        print(f"🧠 任务复杂度 {complexity['score']:.2f} 超过阈值，启动分解...")
        
        subtasks = self.decomposer.decompose(
            task_description,
            self.model_profile
        )
        
        print(f"📝 分解为 {len(subtasks)} 个子任务")
        
        # 3. 逐步执行
        results = []
        tracker = ProgressTracker(len(subtasks))
        
        for subtask in subtasks:
            tracker.update(subtask.id, "in_progress")
            
            try:
                # 执行子任务
                result = super().execute_task(subtask.description)
                
                # 检测失败
                if self._detect_failure(result):
                    # 进一步分解
                    print(f"⚠️ 子任务 {subtask.id} 失败，进一步分解...")
                    sub_subtasks = self.decomposer.decompose(
                        subtask,
                        self.model_profile
                    )
                    
                    # 递归执行
                    for sst in sub_subtasks:
                        sub_result = super().execute_task(sst.description)
                        results.append(sub_result)
                else:
                    results.append(result)
                    tracker.update(subtask.id, "completed")
                    
            except Exception as e:
                print(f"❌ 子任务 {subtask.id} 执行失败: {e}")
                tracker.update(subtask.id, "failed")
                
                # 决定是否继续
                if not self._should_continue_after_failure(e):
                    break
        
        # 4. 合并结果
        return self._merge_results(results)
    
    def _detect_failure(self, execution_result):
        """检测执行是否失败"""
        
        # 多维度检测
        checks = {
            "空结果": execution_result is None,
            "错误标记": "error" in str(execution_result).lower(),
            "不完整": self._is_incomplete(execution_result),
            "质量差": self._is_low_quality(execution_result)
        }
        
        return any(checks.values())
```

### 2. 使用示例

```python
# 配置元认知Agent
config = ReactAgentConfig(
    work_dir=work_dir,
    memory_level=MemoryLevel.SMART,
    enable_metacognition=True,  # 启用元认知
    decomposition_threshold=0.7,  # 分解阈值
    **llm_config
)

# 创建Agent
agent = MetacognitiveAgent(config, name="smart_agent")

# 执行复杂任务
task = """
创建一个完整的电商系统，包括：
1. 用户管理系统（注册、登录、权限）
2. 商品管理（CRUD、分类、搜索）
3. 购物车功能
4. 订单系统
5. 支付集成
6. 物流跟踪
确保所有功能都有完整的API和测试
"""

# Agent会自动：
# 1. 检测到任务复杂
# 2. 分解为6个主要模块
# 3. 每个模块进一步分解
# 4. 逐步实现每个子功能
# 5. 整合最终结果

result = agent.execute_task(task)
```

## 集成到React Agent

### 1. 扩展配置

```python
class ReactAgentConfig:
    """扩展配置支持元认知"""
    
    # 元认知配置
    enable_metacognition: bool = False
    decomposition_threshold: float = 0.7
    max_decomposition_depth: int = 3
    checkpoint_enabled: bool = True
    
    # 失败检测配置
    failure_detection: Dict = {
        "max_retries": 3,
        "timeout_seconds": 300,
        "quality_threshold": 0.6
    }
    
    # 分解策略配置
    decomposition_strategies: List[str] = [
        "temporal",
        "functional", 
        "recursive",
        "hierarchical"
    ]
```

### 2. 知识文件

创建 `knowledge/metacognition/decomposition_patterns.md`:

```markdown
# 任务分解模式

## 时序分解
适用于有明确步骤顺序的任务
关键词：首先、然后、最后、步骤

## 功能分解
适用于可以按功能模块划分的任务
关键词：模块、功能、组件、系统

## 数据流分解
适用于数据处理任务
关键词：输入、处理、输出、转换

## 递归分解
适用于可以递归细分的任务
方法：不断细分直到原子任务
```

## 优势与价值

### 1. 突破模型能力边界
- 让弱模型完成强模型的任务
- 通过分解降低单步复杂度
- 实现渐进式问题解决

### 2. 提高成功率
- 失败可以局部重试
- 检查点支持断点续传
- 降低整体失败风险

### 3. 领域无关性
- 不依赖特定领域知识
- 通用分解策略
- 可扩展到任何任务类型

### 4. 可解释性
- 清晰的任务分解树
- 每步都可追踪
- 便于调试和优化

## 最佳实践

### 1. 分解粒度控制
```python
# 太粗：仍然复杂
"生成完整的Web应用"

# 太细：效率低下
"创建一个变量"

# 合适：可独立完成
"实现用户注册API端点"
```

### 2. 依赖管理
```python
# 明确子任务依赖
subtasks = [
    {"id": "1", "task": "设计数据模型", "depends_on": []},
    {"id": "2", "task": "创建数据库表", "depends_on": ["1"]},
    {"id": "3", "task": "实现API", "depends_on": ["2"]},
    {"id": "4", "task": "编写测试", "depends_on": ["3"]}
]
```

### 3. 失败恢复
```python
# 智能重试策略
if failure_type == "timeout":
    # 进一步分解
    new_subtasks = decompose_further(failed_task)
elif failure_type == "error":
    # 修复后重试
    fixed_task = apply_fix(failed_task, error_info)
elif failure_type == "quality":
    # 换策略重做
    alternative_task = use_alternative_approach(failed_task)
```

## 未来扩展

### 1. 学习优化
- 记录成功的分解模式
- 学习最优分解粒度
- 个性化模型能力画像

### 2. 协作分解
- 多Agent协作分解
- 专家Agent提供领域分解建议
- 分布式执行子任务

### 3. 智能调度
- 并行执行独立子任务
- 动态资源分配
- 优先级调度

## 总结

元认知任务分解架构通过：

1. **元认知检测**：识别任务失败和复杂度
2. **智能分解**：领域无关的任务拆分
3. **自适应执行**：根据能力调整粒度
4. **检查点机制**：支持断点续传
5. **进度追踪**：实时监控执行状态

实现了让Agent具备"**遇到困难就分解**"的人类认知能力，显著提升了处理复杂任务的成功率。

这不仅是技术实现，更是向通用人工智能迈进的重要一步——让AI学会如何学习和解决问题，而不仅仅是执行预定义的任务。