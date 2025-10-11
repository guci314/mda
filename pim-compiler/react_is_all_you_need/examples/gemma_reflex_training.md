# 条件反射训练原理详解

## 一、当前实现的简单原理

### 基础版本（当前代码）

```python
def train_reflex(self, examples: List[Tuple[str, str]], name: str):
    """训练新的条件反射"""
    patterns = []
    for input_text, expected_response in examples:
        # 简单的模式提取（取前两个词）
        words = input_text.lower().split()
        pattern = "|".join(words[:2])
        patterns.append(pattern)

    # 创建统一模式
    unified_pattern = f"({')|(').join(set(patterns))})"

    # 使用第一个响应作为模板
    response_template = examples[0][1]
```

**问题**：
- ❌ 过于简单，只取前两个词
- ❌ 不能捕获语义相似性
- ❌ 不能泛化到未见过的表达

## 二、科学的训练原理

### 1. 模式提取算法

```python
def extract_pattern_advanced(examples):
    """高级模式提取"""

    # Step 1: 找出共同特征
    common_features = {
        'keywords': [],      # 关键词
        'pos_patterns': [],  # 词性模式
        'syntax_trees': [],  # 句法结构
        'semantic_roles': [] # 语义角色
    }

    # Step 2: 统计分析
    for input_text, response in examples:
        # 提取关键词（TF-IDF）
        keywords = extract_keywords_tfidf(input_text)

        # 提取词性模式
        pos_pattern = get_pos_pattern(input_text)

        # 提取句法特征
        syntax = parse_syntax_tree(input_text)

        # 语义角色标注
        semantic = semantic_role_labeling(input_text)

        common_features['keywords'].extend(keywords)
        common_features['pos_patterns'].append(pos_pattern)
        common_features['syntax_trees'].append(syntax)
        common_features['semantic_roles'].append(semantic)

    # Step 3: 找出最具代表性的模式
    pattern = find_most_representative_pattern(common_features)

    return pattern
```

### 2. 基于相似度的模式学习

```python
class SimilarityBasedReflexTrainer:
    """基于相似度的反射训练器"""

    def __init__(self, model):
        self.model = model  # Gemma 270M
        self.embeddings_cache = {}

    def get_embedding(self, text):
        """获取文本的向量表示"""
        if text not in self.embeddings_cache:
            # 使用Gemma的隐藏层获取embedding
            inputs = self.tokenizer(text, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs, output_hidden_states=True)
                # 使用最后一层的平均池化作为embedding
                embedding = outputs.hidden_states[-1].mean(dim=1)
            self.embeddings_cache[text] = embedding
        return self.embeddings_cache[text]

    def train_from_examples(self, examples):
        """从示例中学习"""

        # 1. 计算所有示例的embedding
        embeddings = []
        for input_text, response in examples:
            emb = self.get_embedding(input_text)
            embeddings.append(emb)

        # 2. 找出质心（代表性向量）
        centroid = torch.stack(embeddings).mean(dim=0)

        # 3. 计算触发阈值（基于示例的离散度）
        distances = [
            torch.cosine_similarity(emb, centroid, dim=0)
            for emb in embeddings
        ]
        threshold = min(distances) * 0.9  # 留10%余量

        # 4. 创建基于相似度的反射
        def similarity_trigger(input_text):
            emb = self.get_embedding(input_text)
            similarity = torch.cosine_similarity(emb, centroid, dim=0)
            return similarity > threshold

        return similarity_trigger, centroid, threshold
```

### 3. 增量学习机制

```python
class IncrementalReflexLearner:
    """增量学习反射系统"""

    def __init__(self):
        self.positive_examples = []  # 正例
        self.negative_examples = []  # 负例
        self.pattern = None
        self.confidence = 0.5

    def add_example(self, input_text, response, is_correct):
        """添加新的训练样本"""
        if is_correct:
            self.positive_examples.append((input_text, response))
        else:
            self.negative_examples.append((input_text, response))

        # 重新训练
        self.retrain()

    def retrain(self):
        """重新训练模式"""
        if len(self.positive_examples) < 3:
            return  # 样本太少

        # 1. 从正例中提取模式
        positive_patterns = self.extract_patterns(self.positive_examples)

        # 2. 从负例中提取反模式
        if self.negative_examples:
            negative_patterns = self.extract_patterns(self.negative_examples)

            # 3. 找出区分性特征
            discriminative_features = self.find_discriminative_features(
                positive_patterns,
                negative_patterns
            )

            # 4. 构建新模式
            self.pattern = self.build_pattern(discriminative_features)
        else:
            # 只有正例，直接使用
            self.pattern = positive_patterns

        # 5. 更新置信度
        self.update_confidence()

    def find_discriminative_features(self, positive, negative):
        """找出最具区分性的特征"""
        discriminative = []

        for feat in positive:
            if feat not in negative:
                discriminative.append(feat)

        return discriminative
```

## 三、训练流程

### 完整的训练流程

```python
def train_reflex_complete(name, examples, model=None):
    """完整的反射训练流程"""

    # Phase 1: 数据预处理
    processed_examples = []
    for input_text, response in examples:
        # 清理和标准化
        clean_input = preprocess_text(input_text)
        clean_response = preprocess_text(response)
        processed_examples.append((clean_input, clean_response))

    # Phase 2: 特征提取
    features = {
        'lexical': [],     # 词汇特征
        'syntactic': [],   # 句法特征
        'semantic': []     # 语义特征
    }

    for input_text, response in processed_examples:
        # 词汇层面
        features['lexical'].append({
            'keywords': extract_keywords(input_text),
            'ngrams': get_ngrams(input_text, n=[1,2,3]),
            'word_freq': word_frequency(input_text)
        })

        # 句法层面
        features['syntactic'].append({
            'pos_tags': pos_tagging(input_text),
            'dependency': dependency_parsing(input_text),
            'constituency': constituency_parsing(input_text)
        })

        # 语义层面（如果有模型）
        if model:
            features['semantic'].append({
                'embedding': get_embedding(model, input_text),
                'intent': classify_intent(model, input_text),
                'entities': extract_entities(model, input_text)
            })

    # Phase 3: 模式学习
    pattern = learn_pattern_from_features(features)

    # Phase 4: 响应模板生成
    response_template = generate_response_template(
        [r for _, r in processed_examples]
    )

    # Phase 5: 验证和优化
    reflex = Reflex(
        name=name,
        pattern=pattern,
        response=response_template
    )

    # 交叉验证
    accuracy = cross_validate(reflex, processed_examples)

    # 优化阈值
    if accuracy < 0.9:
        reflex.threshold = optimize_threshold(reflex, processed_examples)

    return reflex
```

## 四、实际应用示例

### 1. 训练客服反射

```python
# 训练数据
customer_service_examples = [
    ("我的订单在哪里", "正在为您查询订单状态..."),
    ("订单什么时候到", "正在为您查询订单状态..."),
    ("查看物流信息", "正在为您查询订单状态..."),
    ("快递到哪了", "正在为您查询订单状态...")
]

# 训练后生成的模式
# pattern: "(订单|物流|快递).*(哪|到|状态|信息)"
# 能匹配：订单状态、物流在哪、快递信息等变体
```

### 2. 训练代码纠错反射

```python
# 训练数据
error_detection_examples = [
    ("NameError: name 'x' is not defined",
     "变量x未定义，请检查是否拼写错误或忘记初始化"),
    ("NameError: name 'count' is not defined",
     "变量count未定义，请检查是否拼写错误或忘记初始化"),
    ("NameError: name 'result' is not defined",
     "变量result未定义，请检查是否拼写错误或忘记初始化")
]

# 训练后生成的模式
# pattern: "NameError:.*'(\w+)'.*not defined"
# response: "变量{1}未定义，请检查是否拼写错误或忘记初始化"
```

### 3. 使用Gemma增强训练

```python
class GemmaEnhancedTrainer:
    """使用Gemma增强的训练器"""

    def __init__(self, gemma_model):
        self.model = gemma_model

    def train_with_augmentation(self, examples):
        """使用数据增强训练"""

        # 1. 原始示例
        all_examples = list(examples)

        # 2. 使用Gemma生成相似示例
        for input_text, response in examples:
            # 让Gemma生成变体
            prompt = f"生成5个与'{input_text}'意思相似的句子："

            variations = self.model.generate(prompt)

            # 添加生成的变体
            for var in variations:
                all_examples.append((var, response))

        # 3. 训练更鲁棒的模式
        reflex = train_reflex_complete("augmented", all_examples)

        return reflex
```

## 五、高级技术

### 1. 主动学习

```python
class ActiveLearningReflex:
    """主动学习的反射系统"""

    def __init__(self):
        self.uncertainty_threshold = 0.3
        self.query_queue = []

    def predict_with_uncertainty(self, input_text):
        """预测并返回不确定性"""
        # 计算多个模型的预测
        predictions = []
        for model in self.ensemble:
            pred = model.predict(input_text)
            predictions.append(pred)

        # 计算不确定性（方差）
        uncertainty = np.var(predictions)

        if uncertainty > self.uncertainty_threshold:
            # 不确定，请求人工标注
            self.query_queue.append(input_text)
            return None, uncertainty

        return majority_vote(predictions), uncertainty
```

### 2. 元学习

```python
class MetaLearningReflex:
    """元学习：学习如何学习反射"""

    def __init__(self):
        self.meta_knowledge = {
            'best_features': {},
            'best_algorithms': {},
            'best_thresholds': {}
        }

    def learn_from_task(self, task_type, examples, performance):
        """从任务中学习元知识"""
        # 记录哪些特征对这类任务有效
        if performance > 0.9:
            self.meta_knowledge['best_features'][task_type] = \
                self.current_features
            self.meta_knowledge['best_algorithms'][task_type] = \
                self.current_algorithm

    def apply_meta_knowledge(self, new_task_type):
        """应用元知识到新任务"""
        if new_task_type in self.meta_knowledge['best_features']:
            # 使用已知有效的配置
            return self.meta_knowledge['best_features'][new_task_type]
        else:
            # 找最相似的任务
            similar = find_most_similar(
                new_task_type,
                self.meta_knowledge['best_features'].keys()
            )
            return self.meta_knowledge['best_features'][similar]
```

## 六、训练效果评估

### 评估指标

| 指标 | 计算方法 | 目标值 |
|-----|---------|--------|
| 精确率 | 正确触发/总触发 | >0.95 |
| 召回率 | 正确触发/应触发 | >0.90 |
| F1分数 | 2×精确率×召回率/(精确率+召回率) | >0.92 |
| 响应时间 | 平均触发时间 | <50ms |
| 泛化能力 | 未见样本准确率 | >0.85 |

### 测试方法

```python
def evaluate_reflex(reflex, test_set):
    """评估反射性能"""

    metrics = {
        'true_positive': 0,
        'false_positive': 0,
        'false_negative': 0,
        'response_times': []
    }

    for input_text, expected_trigger in test_set:
        start_time = time.time()
        triggered = reflex.check(input_text)
        response_time = time.time() - start_time

        metrics['response_times'].append(response_time)

        if triggered and expected_trigger:
            metrics['true_positive'] += 1
        elif triggered and not expected_trigger:
            metrics['false_positive'] += 1
        elif not triggered and expected_trigger:
            metrics['false_negative'] += 1

    # 计算指标
    precision = metrics['true_positive'] / (
        metrics['true_positive'] + metrics['false_positive']
    )
    recall = metrics['true_positive'] / (
        metrics['true_positive'] + metrics['false_negative']
    )
    f1 = 2 * precision * recall / (precision + recall)
    avg_time = np.mean(metrics['response_times'])

    return {
        'precision': precision,
        'recall': recall,
        'f1': f1,
        'avg_response_time': avg_time
    }
```

## 总结

训练新反射的核心原理是：

1. **模式识别**：从示例中提取共同特征
2. **泛化学习**：不仅记住示例，还要能识别变体
3. **阈值优化**：平衡精确率和召回率
4. **增量改进**：从反馈中持续学习

结合Gemma 270M的优势：
- 使用embedding进行语义相似度计算
- 利用模型生成数据增强
- 结合符号规则和神经网络

这样训练出的反射既快速又智能！