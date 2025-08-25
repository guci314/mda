# Agent基于LLM的元认知任务分解

## 核心理念转变

### 从符号主义到连接主义

**错误的方向（符号主义）**：
- 预定义失败模式
- 硬编码分解规则
- 固定的复杂度指标
- 规则驱动的决策树

**正确的方向（连接主义）**：
- LLM判断任务是否失败
- LLM决定如何分解
- LLM评估复杂度
- LLM驱动的自适应

## LLM驱动的元认知架构

### 1. 元认知检测Agent

```python
class MetacognitiveDetector:
    """使用LLM进行元认知检测"""
    
    def __init__(self, llm):
        self.llm = llm
        self.detection_prompt = """
你是一个元认知检测器。分析以下任务执行情况，判断是否出现问题。

## 任务描述
{task_description}

## 执行结果
{execution_result}

## 执行日志
{execution_log}

## 请分析并回答

1. 任务是否成功完成？(是/否)
2. 如果失败，失败的原因是什么？
3. 失败是因为任务太复杂吗？
4. 是否需要将任务分解？
5. 你的信心评分（0-10）？

请以JSON格式回答：
{
  "success": boolean,
  "failure_reason": "string or null",
  "too_complex": boolean,
  "needs_decomposition": boolean,
  "confidence": number,
  "analysis": "详细分析"
}
"""
    
    def detect(self, task, result, log):
        """让LLM检测执行状态"""
        
        response = self.llm.complete(
            self.detection_prompt.format(
                task_description=task,
                execution_result=result,
                execution_log=log
            )
        )
        
        return json.loads(response)
```

### 2. LLM驱动的任务分解

```python
class LLMDecomposer:
    """使用LLM进行任务分解"""
    
    def __init__(self, llm):
        self.llm = llm
        self.decomposition_prompt = """
你是一个任务分解专家。请将复杂任务分解为更简单的子任务。

## 原始任务
{task}

## 失败原因（如果有）
{failure_reason}

## 模型能力
{model_capability}

## 分解要求
1. 每个子任务应该独立可完成
2. 子任务复杂度要适合当前模型能力
3. 明确子任务之间的依赖关系
4. 子任务数量控制在2-7个之间

## 请提供分解方案

以JSON格式返回：
{
  "decomposition_strategy": "你选择的分解策略",
  "reasoning": "为什么这样分解",
  "subtasks": [
    {
      "id": "task_1",
      "description": "子任务描述",
      "dependencies": [],
      "estimated_complexity": "low/medium/high"
    }
  ]
}
"""
    
    def decompose(self, task, failure_reason=None, model_capability=None):
        """让LLM分解任务"""
        
        response = self.llm.complete(
            self.decomposition_prompt.format(
                task=task,
                failure_reason=failure_reason or "无",
                model_capability=model_capability or "标准"
            )
        )
        
        return json.loads(response)
```

### 3. 复杂度评估Agent

```python
class LLMComplexityEvaluator:
    """使用LLM评估任务复杂度"""
    
    def __init__(self, llm):
        self.llm = llm
        self.evaluation_prompt = """
评估以下任务的复杂度。

## 任务
{task}

## 评估维度
1. 认知负载：任务需要多少思考
2. 输出长度：预期输出的长度
3. 领域知识：需要的专业知识深度
4. 步骤数量：完成任务需要多少步骤
5. 依赖关系：任务内部的依赖复杂度

## 模型信息
模型：{model_name}
上下文窗口：{context_window}
已知能力：{known_capabilities}

## 请回答

1. 该任务对于{model_name}来说复杂度如何？(1-10分)
2. 主要的复杂性在哪里？
3. 是否建议分解？如果是，建议如何分解？

JSON格式：
{
  "complexity_score": number,
  "complexity_factors": {
    "cognitive_load": number,
    "output_length": number,
    "domain_knowledge": number,
    "step_count": number,
    "dependencies": number
  },
  "main_challenges": ["challenge1", "challenge2"],
  "recommend_decomposition": boolean,
  "decomposition_hint": "string or null"
}
"""
    
    def evaluate(self, task, model_info):
        """让LLM评估复杂度"""
        
        response = self.llm.complete(
            self.evaluation_prompt.format(
                task=task,
                model_name=model_info['name'],
                context_window=model_info['context_window'],
                known_capabilities=model_info.get('capabilities', '通用')
            )
        )
        
        return json.loads(response)
```

## 自反思的执行循环

### 元认知执行Agent

```python
class MetacognitiveAgent(GenericReactAgent):
    """具有LLM驱动元认知的Agent"""
    
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        
        # 创建元认知LLM（可以是同一个或不同的模型）
        self.meta_llm = self._create_meta_llm(config)
        
        # 元认知组件
        self.detector = MetacognitiveDetector(self.meta_llm)
        self.decomposer = LLMDecomposer(self.meta_llm)
        self.evaluator = LLMComplexityEvaluator(self.meta_llm)
    
    def execute_task(self, task_description):
        """带元认知的任务执行"""
        
        # 1. 先让LLM评估复杂度
        complexity = self.evaluator.evaluate(
            task_description,
            {'name': self.config.llm_model, 'context_window': 32000}
        )
        
        if not complexity['recommend_decomposition']:
            # 直接执行
            return self._execute_with_monitoring(task_description)
        
        # 2. LLM建议分解，让它分解
        print(f"🧠 LLM判断任务复杂度为 {complexity['complexity_score']}/10")
        print(f"主要挑战: {', '.join(complexity['main_challenges'])}")
        
        decomposition = self.decomposer.decompose(
            task_description,
            model_capability=self.config.llm_model
        )
        
        print(f"📝 分解策略: {decomposition['decomposition_strategy']}")
        print(f"理由: {decomposition['reasoning']}")
        
        # 3. 执行子任务
        return self._execute_subtasks(decomposition['subtasks'])
    
    def _execute_with_monitoring(self, task):
        """执行并监控"""
        
        # 执行
        result = super().execute_task(task)
        
        # 让LLM检测是否成功
        detection = self.detector.detect(
            task,
            result,
            self.get_execution_log()
        )
        
        if detection['success']:
            return result
        
        if detection['needs_decomposition']:
            # LLM认为需要分解
            print(f"⚠️ LLM检测到失败: {detection['failure_reason']}")
            print(f"🔄 启动分解...")
            
            # 让LLM分解
            decomposition = self.decomposer.decompose(
                task,
                failure_reason=detection['failure_reason']
            )
            
            # 执行分解后的任务
            return self._execute_subtasks(decomposition['subtasks'])
        
        # 其他类型的失败
        return self._handle_failure(detection)
    
    def _execute_subtasks(self, subtasks):
        """执行子任务列表"""
        
        results = {}
        
        for subtask in subtasks:
            # 检查依赖
            if self._dependencies_met(subtask, results):
                # 递归执行（子任务可能还需要分解）
                result = self.execute_task(subtask['description'])
                results[subtask['id']] = result
        
        # 让LLM合并结果
        return self._merge_results_with_llm(results)
    
    def _merge_results_with_llm(self, results):
        """让LLM合并子任务结果"""
        
        merge_prompt = """
合并以下子任务的执行结果为一个连贯的整体。

## 子任务结果
{results}

## 要求
1. 整合所有结果
2. 确保连贯性
3. 生成最终输出

## 最终结果
"""
        
        response = self.meta_llm.complete(
            merge_prompt.format(
                results=json.dumps(results, indent=2, ensure_ascii=False)
            )
        )
        
        return response
```

## 自适应分解策略

### 让LLM选择分解策略

```python
class AdaptiveDecomposer:
    """LLM自适应选择分解策略"""
    
    def __init__(self, llm):
        self.llm = llm
        self.strategy_selection_prompt = """
分析任务并选择最佳分解策略。

## 任务
{task}

## 可用策略
1. **时序分解**: 按时间顺序分解步骤
2. **功能分解**: 按功能模块分解
3. **数据流分解**: 按数据处理流程分解  
4. **层次分解**: 从高层到底层逐级分解
5. **并行分解**: 识别可并行的独立部分
6. **迭代分解**: 重复相似操作的批处理分解

## 请分析

1. 这个任务的特征是什么？
2. 哪种分解策略最适合？为什么？
3. 使用该策略如何分解？

以JSON返回：
{
  "task_characteristics": ["特征1", "特征2"],
  "best_strategy": "策略名称",
  "reasoning": "选择理由",
  "decomposition_plan": "分解计划概述"
}
"""
    
    def select_and_decompose(self, task):
        """让LLM选择策略并分解"""
        
        # 第一步：选择策略
        strategy_response = self.llm.complete(
            self.strategy_selection_prompt.format(task=task)
        )
        
        strategy_info = json.loads(strategy_response)
        
        # 第二步：应用策略分解
        decompose_prompt = f"""
使用{strategy_info['best_strategy']}策略分解以下任务。

## 任务
{task}

## 策略说明
{strategy_info['decomposition_plan']}

## 生成具体的子任务列表

JSON格式：
{{
  "subtasks": [
    {{
      "id": "string",
      "description": "string", 
      "type": "sequential|parallel|conditional",
      "dependencies": []
    }}
  ]
}}
"""
        
        decomposition = self.llm.complete(decompose_prompt)
        return json.loads(decomposition)
```

## 失败学习机制

### 让LLM从失败中学习

```python
class FailureLearner:
    """LLM驱动的失败学习"""
    
    def __init__(self, llm):
        self.llm = llm
        self.failure_history = []
    
    def learn_from_failure(self, task, failure_info, successful_approach=None):
        """让LLM分析失败并学习"""
        
        learning_prompt = """
从任务失败中学习。

## 失败的任务
{task}

## 失败信息
{failure}

## 成功的方法（如果有）
{success}

## 历史失败模式
{history}

## 请分析

1. 失败的根本原因是什么？
2. 这次失败有什么模式？
3. 未来如何避免类似失败？
4. 对于类似任务，建议的分解粒度是什么？

JSON格式：
{
  "root_cause": "string",
  "failure_pattern": "string",
  "prevention_strategy": "string",
  "recommended_granularity": "fine|medium|coarse",
  "learned_rule": "一句话总结的经验"
}
"""
        
        response = self.llm.complete(
            learning_prompt.format(
                task=task,
                failure=failure_info,
                success=successful_approach or "无",
                history=self.failure_history[-5:]  # 最近5次失败
            )
        )
        
        learning = json.loads(response)
        
        # 保存学习结果
        self.failure_history.append({
            'task': task,
            'pattern': learning['failure_pattern'],
            'rule': learning['learned_rule']
        })
        
        return learning
```

## 实践示例

### 完整的元认知循环

```python
def metacognitive_execution_loop(agent, task):
    """完整的元认知执行循环"""
    
    max_attempts = 3
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n🔄 第 {attempt} 次尝试")
        
        # 1. 让LLM评估任务
        complexity = agent.evaluator.evaluate(task, agent.model_info)
        
        if complexity['complexity_score'] > 7:
            print("📊 LLM判断: 任务复杂，需要分解")
            
            # 2. 让LLM选择分解策略
            strategy = agent.adaptive_decomposer.select_and_decompose(task)
            print(f"📋 策略: {strategy['best_strategy']}")
            
            # 3. 执行分解后的子任务
            subtasks = strategy['subtasks']
            results = []
            
            for subtask in subtasks:
                # 递归调用元认知循环
                sub_result = metacognitive_execution_loop(agent, subtask['description'])
                results.append(sub_result)
                
                # 让LLM检查中间结果
                check = agent.detector.detect(
                    subtask['description'],
                    sub_result,
                    ""
                )
                
                if not check['success']:
                    print(f"⚠️ 子任务失败: {check['failure_reason']}")
                    # 让LLM决定是否继续
                    should_continue = agent.ask_llm_should_continue(check)
                    if not should_continue:
                        break
            
            # 4. 让LLM合并结果
            return agent.merge_results_with_llm(results)
        
        else:
            # 直接执行
            print("📊 LLM判断: 可以直接执行")
            result = agent.execute_simple_task(task)
            
            # 5. 让LLM验证结果
            validation = agent.detector.detect(task, result, "")
            
            if validation['success']:
                print("✅ LLM确认: 任务成功完成")
                return result
            else:
                print(f"❌ LLM检测到问题: {validation['failure_reason']}")
                
                # 6. 让LLM学习失败
                learning = agent.failure_learner.learn_from_failure(
                    task,
                    validation
                )
                print(f"💡 LLM学到: {learning['learned_rule']}")
                
                # 根据学习结果调整策略
                if learning['recommended_granularity'] == 'fine':
                    # 下次循环会用更细的分解
                    task = f"{task}\n注意：需要更细粒度的分解"
    
    return None  # 最终失败
```

### 纯提示词驱动的元认知

```python
class PromptDrivenMetacognition:
    """完全通过提示词实现元认知"""
    
    METACOGNITIVE_SYSTEM_PROMPT = """
你是一个具有元认知能力的AI助手。

## 元认知能力

1. **自我监控**: 随时评估自己的理解和执行状态
2. **复杂度感知**: 判断任务是否超出能力范围
3. **自适应分解**: 遇到复杂任务自动分解
4. **失败检测**: 识别执行失败并分析原因
5. **策略调整**: 根据反馈调整执行策略

## 执行协议

当收到任务时：
1. 先评估任务复杂度（内心独白）
2. 如果太复杂，主动分解为子任务
3. 执行时监控自己的状态
4. 如果遇到困难，停下来重新分解
5. 完成后自我验证结果

## 输出格式

思考过程用【思考】标记
执行动作用【执行】标记
遇到困难用【困难】标记
分解任务用【分解】标记
最终结果用【结果】标记

示例：
【思考】这个任务要求创建完整的系统，很复杂
【分解】我将把它分解为：1)用户模块 2)商品模块 3)订单模块
【执行】开始实现用户模块...
【困难】用户认证部分较复杂
【分解】将认证分为：注册、登录、token管理
【执行】实现注册功能...
【结果】完成所有模块实现
"""
    
    def execute_with_metacognition(self, task):
        """使用元认知提示词执行"""
        
        messages = [
            {"role": "system", "content": self.METACOGNITIVE_SYSTEM_PROMPT},
            {"role": "user", "content": task}
        ]
        
        response = llm.complete(messages)
        
        # LLM会自动进行元认知处理
        return response
```

## 关键优势

### 1. 真正的自适应
- 不需要预定义规则
- LLM根据具体情况判断
- 能处理未见过的任务类型

### 2. 上下文感知
- LLM理解任务的语义
- 考虑任务间的关系
- 保持分解的连贯性

### 3. 持续学习
- 从失败中学习模式
- 积累分解经验
- 优化未来的执行

### 4. 灵活性
- 没有硬编码的限制
- 可以创造性地分解
- 适应不同模型能力

## 实现要点

### 1. 提示词工程
```python
# 关键：让LLM"思考自己的思考"
metacognitive_prompt = """
在执行任务前，先问自己：
1. 我理解这个任务吗？
2. 这个任务对我来说困难吗？
3. 我应该如何分解它？
4. 我的执行计划是什么？
"""
```

### 2. 递归元认知
```python
# 子任务也可以触发元认知
def recursive_metacognition(task):
    if llm_thinks_complex(task):
        subtasks = llm_decompose(task)
        for subtask in subtasks:
            # 递归调用
            recursive_metacognition(subtask)
    else:
        execute_directly(task)
```

### 3. 多级验证
```python
# 让不同的LLM验证
validator_llm.validate(executor_llm.result)
```

## 总结

连接主义的元认知架构：

1. **LLM判断复杂度**，而不是规则计算
2. **LLM决定分解策略**，而不是预定义模式
3. **LLM检测失败**，而不是硬编码指标
4. **LLM学习经验**，而不是固定知识库
5. **LLM验证结果**，而不是规则匹配

这才是真正的元认知：让LLM"思考如何思考"，"知道自己不知道什么"，"判断任务是否超出能力"，然后"决定如何分解问题"。

**核心洞察**：元认知不是一套规则系统，而是LLM的自我反思能力。通过适当的提示词，我们可以激活LLM的元认知，让它像人类一样遇到困难就分解任务。