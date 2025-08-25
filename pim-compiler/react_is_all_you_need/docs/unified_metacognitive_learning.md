# 统一的元认知学习架构

## 核心洞察

学习本质上是一种元认知活动：
- **元认知**：知道自己知道什么，不知道什么
- **学习**：从经验中提取知识，改进未来表现
- **统一视角**：学习是元认知的知识更新机制

## 现状分析

### 当前React Agent的学习机制

```python
# 现有的知识提取（在 react_agent.py 中）
if self.config.memory_level == MemoryLevel.SMART:
    # 提取知识
    knowledge = self._extract_knowledge_from_history()
    # 保存到文件
    self._save_knowledge(knowledge)
```

问题：
1. 学习是被动的（任务结束后）
2. 与执行过程分离
3. 没有主动反思机制

### 理想的元认知学习

```python
# 统一的元认知学习循环
class MetacognitiveLearningAgent:
    """融合元认知和学习的Agent"""
    
    def execute_with_learning(self, task):
        # 1. 执行前：调用已有知识
        prior_knowledge = self.recall_relevant_knowledge(task)
        
        # 2. 执行中：实时学习
        result = self.execute_with_monitoring(task, prior_knowledge)
        
        # 3. 执行后：反思和更新
        new_knowledge = self.reflect_and_learn(task, result)
        
        # 4. 知识整合
        self.integrate_knowledge(prior_knowledge, new_knowledge)
```

## 统一架构设计

### 1. 元认知学习循环

```python
class UnifiedMetacognitiveLearning:
    """统一的元认知学习系统"""
    
    def __init__(self, llm):
        self.llm = llm
        self.knowledge_base = KnowledgeBase()
        
    def metacognitive_loop(self, task):
        """完整的元认知学习循环"""
        
        # Phase 1: 认知准备（调用已有知识）
        preparation = self.cognitive_preparation(task)
        
        # Phase 2: 执行监控（边做边学）
        execution = self.monitored_execution(task, preparation)
        
        # Phase 3: 反思学习（总结经验）
        reflection = self.reflective_learning(task, execution)
        
        # Phase 4: 知识更新（整合新知）
        self.knowledge_integration(reflection)
        
        return execution.result
```

### 2. LLM驱动的知识调用

```python
class CognitivePreparation:
    """执行前的认知准备"""
    
    RECALL_PROMPT = """
准备执行以下任务。回忆相关经验。

## 当前任务
{task}

## 知识库摘要
{knowledge_summary}

## 请回答
1. 我以前做过类似的任务吗？
2. 哪些经验可能有用？
3. 可能遇到什么问题？
4. 建议的执行策略是什么？

JSON格式：
{
  "similar_experiences": ["经验1", "经验2"],
  "useful_knowledge": ["知识点1", "知识点2"],
  "potential_issues": ["问题1", "问题2"],
  "recommended_strategy": "策略描述",
  "confidence": 0.8
}
"""
    
    def prepare(self, task, knowledge_base):
        """让LLM调用相关知识"""
        
        # 获取可能相关的知识
        relevant_knowledge = knowledge_base.search(task, top_k=5)
        
        response = self.llm.complete(
            self.RECALL_PROMPT.format(
                task=task,
                knowledge_summary=self.summarize(relevant_knowledge)
            )
        )
        
        return json.loads(response)
```

### 3. 执行中的实时学习

```python
class MonitoredExecution:
    """边执行边学习"""
    
    MONITORING_PROMPT = """
我正在执行任务，请监控我的状态。

## 任务
{task}

## 已完成步骤
{completed_steps}

## 当前步骤
{current_step}

## 当前结果
{current_result}

## 元认知检查
1. 我的执行是否偏离目标？
2. 我是否遇到了意外情况？
3. 我学到了什么新东西？
4. 是否需要调整策略？

JSON格式：
{
  "on_track": boolean,
  "unexpected_findings": ["发现1", "发现2"],
  "learned_insights": ["洞察1", "洞察2"],
  "strategy_adjustment": "调整建议或null",
  "continue": boolean
}
"""
    
    def monitor_step(self, task, step_info):
        """监控单个执行步骤"""
        
        response = self.llm.complete(
            self.MONITORING_PROMPT.format(
                task=task,
                completed_steps=step_info['completed'],
                current_step=step_info['current'],
                current_result=step_info['result']
            )
        )
        
        monitoring = json.loads(response)
        
        # 实时记录学到的东西
        if monitoring['learned_insights']:
            self.record_insights(monitoring['learned_insights'])
        
        return monitoring
```

### 4. 反思性学习

```python
class ReflectiveLearning:
    """执行后的深度反思"""
    
    REFLECTION_PROMPT = """
任务已完成，进行深度反思和学习。

## 任务描述
{task}

## 执行过程
{execution_trace}

## 最终结果
{result}

## 反思问题
1. 什么做得好？什么做得不好？
2. 最重要的经验教训是什么？
3. 如果重做，会如何改进？
4. 这次经历如何改变了我的认知？
5. 有什么通用模式可以提取？

## 知识提取
请提取：
- 成功模式
- 失败模式
- 领域知识
- 方法论知识
- 元认知知识

JSON格式：
{
  "performance_analysis": {
    "strengths": ["优点1", "优点2"],
    "weaknesses": ["缺点1", "缺点2"],
    "improvements": ["改进1", "改进2"]
  },
  "key_lessons": ["教训1", "教训2"],
  "knowledge_gained": {
    "success_patterns": ["模式1", "模式2"],
    "failure_patterns": ["模式1", "模式2"],
    "domain_knowledge": ["知识1", "知识2"],
    "methodology": ["方法1", "方法2"],
    "metacognitive": ["元认知1", "元认知2"]
  },
  "cognitive_update": "这次经历如何改变了认知"
}
"""
    
    def reflect(self, task, execution_trace, result):
        """深度反思学习"""
        
        response = self.llm.complete(
            self.REFLECTION_PROMPT.format(
                task=task,
                execution_trace=execution_trace,
                result=result
            )
        )
        
        return json.loads(response)
```

### 5. 知识整合与更新

```python
class KnowledgeIntegration:
    """整合新旧知识"""
    
    INTEGRATION_PROMPT = """
整合新学到的知识与已有知识。

## 已有知识
{existing_knowledge}

## 新学知识
{new_knowledge}

## 整合任务
1. 识别知识冲突
2. 解决矛盾
3. 合并相似知识
4. 建立知识连接
5. 更新知识优先级

JSON格式：
{
  "conflicts": ["冲突1", "冲突2"],
  "resolutions": ["解决1", "解决2"],
  "merged_knowledge": ["合并后知识1", "合并后知识2"],
  "knowledge_graph": {
    "nodes": ["概念1", "概念2"],
    "edges": [["概念1", "关系", "概念2"]]
  },
  "priority_updates": {
    "promoted": ["提升优先级的知识"],
    "demoted": ["降低优先级的知识"]
  }
}
"""
    
    def integrate(self, existing, new):
        """让LLM整合知识"""
        
        response = self.llm.complete(
            self.INTEGRATION_PROMPT.format(
                existing_knowledge=existing,
                new_knowledge=new
            )
        )
        
        integration = json.loads(response)
        
        # 更新知识库
        self.update_knowledge_base(integration)
        
        return integration
```

## 知识的层次结构

### 三层知识体系

```python
class HierarchicalKnowledge:
    """分层的知识体系"""
    
    def __init__(self):
        # 第一层：事实性知识（What）
        self.factual = {
            "domain_facts": [],      # 领域事实
            "case_studies": [],      # 具体案例
            "examples": []           # 示例
        }
        
        # 第二层：程序性知识（How）
        self.procedural = {
            "methods": [],           # 方法步骤
            "strategies": [],        # 策略模式
            "heuristics": []        # 经验法则
        }
        
        # 第三层：元认知知识（Why & When）
        self.metacognitive = {
            "when_to_apply": [],    # 何时使用
            "why_it_works": [],     # 为何有效
            "limitations": [],      # 局限性
            "self_knowledge": []    # 自我认知
        }
```

### 知识的动态优先级

```python
class DynamicKnowledgePriority:
    """动态调整知识优先级"""
    
    def update_priorities(self, knowledge_item, usage_result):
        """根据使用效果更新优先级"""
        
        update_prompt = """
根据知识使用效果更新其优先级。

## 使用的知识
{knowledge}

## 使用场景
{context}

## 使用效果
{result}

## 评估
1. 这个知识有多有用？(0-10)
2. 适用范围有多广？(0-10)
3. 可靠性如何？(0-10)
4. 是否需要修正？

JSON格式：
{
  "usefulness": number,
  "generality": number,
  "reliability": number,
  "needs_revision": boolean,
  "revision_suggestion": "建议或null",
  "new_priority": number
}
"""
        
        response = self.llm.complete(
            update_prompt.format(
                knowledge=knowledge_item,
                context=usage_result['context'],
                result=usage_result['outcome']
            )
        )
        
        return json.loads(response)
```

## 实践：完整的元认知学习Agent

```python
class MetacognitiveLearningAgent(GenericReactAgent):
    """融合元认知和学习的Agent"""
    
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)
        
        # 统一的元认知学习系统
        self.metacognitive = UnifiedMetacognitiveLearning(self.llm)
        
    def execute_task(self, task_description):
        """带元认知学习的任务执行"""
        
        # 1. 认知准备：激活相关知识
        print("🧠 认知准备...")
        preparation = self.metacognitive.cognitive_preparation(task_description)
        
        if preparation['similar_experiences']:
            print(f"📚 调用经验: {', '.join(preparation['similar_experiences'])}")
        
        if preparation['potential_issues']:
            print(f"⚠️ 潜在问题: {', '.join(preparation['potential_issues'])}")
        
        # 2. 设置执行策略
        self.set_strategy(preparation['recommended_strategy'])
        
        # 3. 执行with监控
        print("\n🚀 开始执行...")
        execution_trace = []
        
        # 分步执行
        steps = self.plan_steps(task_description, preparation)
        
        for i, step in enumerate(steps):
            print(f"\n步骤 {i+1}/{len(steps)}: {step['description']}")
            
            # 执行步骤
            step_result = self.execute_step(step)
            
            # 实时监控和学习
            monitoring = self.metacognitive.monitor_step(
                task_description,
                {
                    'completed': execution_trace,
                    'current': step,
                    'result': step_result
                }
            )
            
            if monitoring['learned_insights']:
                print(f"💡 新发现: {', '.join(monitoring['learned_insights'])}")
            
            if monitoring['strategy_adjustment']:
                print(f"🔄 策略调整: {monitoring['strategy_adjustment']}")
                self.adjust_strategy(monitoring['strategy_adjustment'])
            
            execution_trace.append({
                'step': step,
                'result': step_result,
                'monitoring': monitoring
            })
            
            if not monitoring['continue']:
                print("🛑 元认知决定停止执行")
                break
        
        # 4. 反思学习
        print("\n🤔 反思学习...")
        reflection = self.metacognitive.reflect(
            task_description,
            execution_trace,
            self.get_final_result()
        )
        
        print(f"✨ 关键经验: {', '.join(reflection['key_lessons'])}")
        
        # 5. 知识整合
        print("\n📝 更新知识库...")
        self.metacognitive.integrate_knowledge(reflection['knowledge_gained'])
        
        # 6. 返回结果
        return self.get_final_result()
    
    def set_strategy(self, strategy):
        """设置执行策略"""
        self.current_strategy = strategy
        
    def adjust_strategy(self, adjustment):
        """动态调整策略"""
        self.current_strategy = adjustment
```

## 知识库的自然语言表示

```python
class NaturalLanguageKnowledge:
    """用自然语言存储知识"""
    
    def save_knowledge(self, knowledge, file_path):
        """保存为Markdown格式"""
        
        content = f"""# 知识库

## 最近更新
{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 成功模式
{self.format_patterns(knowledge['success_patterns'])}

## 失败模式
{self.format_patterns(knowledge['failure_patterns'])}

## 领域知识
{self.format_domain(knowledge['domain_knowledge'])}

## 方法论
{self.format_methodology(knowledge['methodology'])}

## 元认知洞察
{self.format_metacognitive(knowledge['metacognitive'])}

## 经验索引
{self.format_experience_index(knowledge['experiences'])}
"""
        
        with open(file_path, 'w') as f:
            f.write(content)
    
    def load_and_query(self, query):
        """用LLM查询知识库"""
        
        query_prompt = """
从知识库中查找相关信息。

## 查询
{query}

## 知识库内容
{knowledge_content}

## 返回最相关的知识
"""
        
        return self.llm.complete(query_prompt)
```

## 元认知学习的优势

### 1. 主动学习 vs 被动记录

**传统方式**：
```python
# 被动记录
history.append(action)
# 任务结束后提取
knowledge = extract_from_history(history)
```

**元认知方式**：
```python
# 主动学习
insight = monitor_and_learn(action)
immediately_apply(insight)
reflect_and_integrate(insight)
```

### 2. 深度理解 vs 表面记忆

**传统方式**：
- 记录发生了什么
- 保存成功的步骤

**元认知方式**：
- 理解为什么成功/失败
- 提取通用原则
- 建立知识连接

### 3. 自适应 vs 固定

**传统方式**：
- 固定的学习模板
- 统一的知识格式

**元认知方式**：
- LLM决定学什么
- LLM决定如何组织
- LLM决定优先级

## 实现建议

### 1. 渐进式整合

```python
# 第一步：在现有基础上添加元认知
class EnhancedReactAgent(GenericReactAgent):
    def execute_task(self, task):
        # 调用已有知识
        self.prepare_with_knowledge(task)
        
        # 执行原有逻辑
        result = super().execute_task(task)
        
        # 反思学习
        self.reflect_and_learn(task, result)
        
        return result
```

### 2. 统一的知识表示

```python
# 合并 extracted_knowledge.md 和元认知洞察
knowledge_structure = {
    "factual": {},      # What - 事实
    "procedural": {},   # How - 方法
    "metacognitive": {} # Why/When - 元认知
}
```

### 3. 提示词模板

```python
UNIFIED_LEARNING_PROMPT = """
你是一个具有元认知学习能力的Agent。

执行任务时：
1. 先问：我知道什么相关的？
2. 执行中问：我在学到什么？
3. 完成后问：我学到了什么？
4. 最后问：这如何改变我的认知？

将学习融入执行的每一步。
"""
```

## 总结

**学习应该是元认知的核心组成部分**，而不是独立的功能：

1. **元认知包含学习**：知道自己不知道什么→学习→知道了
2. **学习需要元认知**：反思什么值得学→如何组织知识→何时应用
3. **统一的循环**：准备→执行→监控→反思→整合→应用

这种整合让Agent真正具备了：
- **自我意识**：知道自己的知识边界
- **自我改进**：从经验中持续学习
- **自我适应**：根据学到的调整行为

最终实现：**一个会思考如何思考、会学习如何学习的Agent**。