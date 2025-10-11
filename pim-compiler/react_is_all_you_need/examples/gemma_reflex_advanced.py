#!/usr/bin/env python3
"""
Gemma 270M 高级条件反射训练系统
实现科学的模式学习和训练机制
"""

import re
import time
import json
import numpy as np
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass, field
from collections import Counter, defaultdict
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForCausalLM


@dataclass
class TrainingExample:
    """训练样本"""
    input_text: str
    expected_response: str
    metadata: Dict = field(default_factory=dict)


@dataclass
class Pattern:
    """学习到的模式"""
    regex_pattern: Optional[str] = None
    keyword_set: List[str] = field(default_factory=list)
    embedding_centroid: Optional[torch.Tensor] = None
    similarity_threshold: float = 0.8
    confidence: float = 0.5


class AdvancedReflexTrainer:
    """高级反射训练器"""

    def __init__(self, model_id: str = "unsloth/gemma-3-270m-it"):
        self.model = None
        self.tokenizer = None
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    def load_model(self):
        """加载Gemma模型用于语义分析"""
        print("📚 加载Gemma模型用于训练...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.float16 if self.device != "cpu" else torch.float32
        ).to(self.device)
        self.model.eval()
        print("✅ 模型加载完成")

    def train_from_examples(self,
                           examples: List[Tuple[str, str]],
                           name: str) -> Pattern:
        """从示例中训练模式"""
        print(f"\n🎓 开始训练反射: {name}")
        print(f"   训练样本数: {len(examples)}")

        # 转换为TrainingExample对象
        training_data = [
            TrainingExample(inp, resp)
            for inp, resp in examples
        ]

        # 1. 提取多层特征
        features = self._extract_features(training_data)

        # 2. 学习模式
        pattern = self._learn_pattern(features, training_data)

        # 3. 验证模式
        accuracy = self._validate_pattern(pattern, training_data)
        pattern.confidence = accuracy

        print(f"✅ 训练完成，准确率: {accuracy:.2%}")
        return pattern

    def _extract_features(self, examples: List[TrainingExample]) -> Dict:
        """提取特征"""
        features = {
            'keywords': [],
            'patterns': [],
            'embeddings': [],
            'lengths': [],
            'pos_patterns': []
        }

        for example in examples:
            # 提取关键词
            keywords = self._extract_keywords(example.input_text)
            features['keywords'].extend(keywords)

            # 提取模式
            patterns = self._extract_patterns(example.input_text)
            features['patterns'].extend(patterns)

            # 提取语义嵌入（如果模型已加载）
            if self.model:
                embedding = self._get_embedding(example.input_text)
                features['embeddings'].append(embedding)

            # 长度特征
            features['lengths'].append(len(example.input_text.split()))

        return features

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词（简化版TF-IDF）"""
        # 分词
        words = re.findall(r'\w+', text.lower())

        # 过滤停用词
        stopwords = {'的', '了', '是', '在', '我', '你', '他',
                    'the', 'is', 'a', 'an', 'and', 'or', 'but'}
        keywords = [w for w in words if w not in stopwords and len(w) > 1]

        return keywords

    def _extract_patterns(self, text: str) -> List[str]:
        """提取文本模式"""
        patterns = []

        # N-gram模式
        words = text.lower().split()
        for n in [1, 2, 3]:
            for i in range(len(words) - n + 1):
                ngram = ' '.join(words[i:i+n])
                patterns.append(ngram)

        # 特殊模式
        if re.search(r'\d+', text):
            patterns.append('<NUMBER>')
        if re.search(r'[A-Z][a-z]+', text):
            patterns.append('<PROPER_NOUN>')
        if '?' in text or '？' in text:
            patterns.append('<QUESTION>')

        return patterns

    def _get_embedding(self, text: str) -> torch.Tensor:
        """获取文本的语义嵌入"""
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=128
        ).to(self.device)

        with torch.no_grad():
            outputs = self.model(**inputs, output_hidden_states=True)
            # 使用最后一层隐藏状态的平均作为嵌入
            last_hidden = outputs.hidden_states[-1]
            embedding = last_hidden.mean(dim=1).squeeze()

        return embedding

    def _learn_pattern(self, features: Dict,
                       examples: List[TrainingExample]) -> Pattern:
        """学习模式"""
        pattern = Pattern()

        # 1. 学习关键词模式
        if features['keywords']:
            # 找出高频关键词
            keyword_counter = Counter(features['keywords'])
            # 选择出现在50%以上样本中的关键词
            threshold = len(examples) * 0.5
            common_keywords = [
                word for word, count in keyword_counter.items()
                if count >= threshold
            ]
            pattern.keyword_set = common_keywords

            # 构建正则表达式
            if common_keywords:
                # 创建包含所有关键词的正则表达式
                pattern.regex_pattern = '|'.join(
                    re.escape(kw) for kw in common_keywords
                )

        # 2. 学习语义模式（如果有嵌入）
        if features['embeddings']:
            # 计算嵌入质心
            embeddings = torch.stack(features['embeddings'])
            pattern.embedding_centroid = embeddings.mean(dim=0)

            # 计算阈值（基于样本内相似度）
            similarities = []
            for emb in features['embeddings']:
                sim = F.cosine_similarity(
                    emb.unsqueeze(0),
                    pattern.embedding_centroid.unsqueeze(0)
                ).item()
                similarities.append(sim)

            # 设置阈值为最小相似度的90%
            pattern.similarity_threshold = min(similarities) * 0.9

        return pattern

    def _validate_pattern(self, pattern: Pattern,
                         examples: List[TrainingExample]) -> float:
        """验证模式准确率"""
        correct = 0
        total = len(examples)

        for example in examples:
            if self._match_pattern(pattern, example.input_text):
                correct += 1

        return correct / total if total > 0 else 0

    def _match_pattern(self, pattern: Pattern, text: str) -> bool:
        """检查文本是否匹配模式"""
        # 1. 检查正则表达式
        if pattern.regex_pattern:
            if re.search(pattern.regex_pattern, text.lower()):
                return True

        # 2. 检查关键词
        if pattern.keyword_set:
            text_words = set(re.findall(r'\w+', text.lower()))
            if text_words.intersection(pattern.keyword_set):
                return True

        # 3. 检查语义相似度（如果有模型和质心）
        if self.model and pattern.embedding_centroid is not None:
            embedding = self._get_embedding(text)
            similarity = F.cosine_similarity(
                embedding.unsqueeze(0),
                pattern.embedding_centroid.unsqueeze(0)
            ).item()
            if similarity >= pattern.similarity_threshold:
                return True

        return False


class IncrementalReflexLearner:
    """增量学习系统"""

    def __init__(self, trainer: AdvancedReflexTrainer):
        self.trainer = trainer
        self.positive_examples = defaultdict(list)  # 正例
        self.negative_examples = defaultdict(list)  # 负例
        self.patterns = {}  # 学习到的模式
        self.performance_history = defaultdict(list)  # 性能历史

    def add_feedback(self, reflex_name: str, input_text: str,
                     response: str, is_correct: bool):
        """添加反馈样本"""
        example = TrainingExample(input_text, response)

        if is_correct:
            self.positive_examples[reflex_name].append(example)
            print(f"✅ 添加正例到 {reflex_name}")
        else:
            self.negative_examples[reflex_name].append(example)
            print(f"❌ 添加负例到 {reflex_name}")

        # 如果积累了足够的样本，重新训练
        total_examples = (len(self.positive_examples[reflex_name]) +
                         len(self.negative_examples[reflex_name]))

        if total_examples >= 5 and total_examples % 5 == 0:
            print(f"📊 样本数达到{total_examples}，触发重新训练")
            self.retrain(reflex_name)

    def retrain(self, reflex_name: str):
        """重新训练反射"""
        positives = self.positive_examples[reflex_name]
        negatives = self.negative_examples[reflex_name]

        if len(positives) < 3:
            print(f"⚠️ 正例太少({len(positives)}个)，暂不训练")
            return

        # 从正例学习模式
        positive_pattern = self.trainer._learn_pattern(
            self.trainer._extract_features(positives),
            positives
        )

        # 如果有负例，调整模式以排除它们
        if negatives:
            # 找出区分性特征
            positive_features = self._get_discriminative_features(
                positives, negatives
            )
            positive_pattern.keyword_set = positive_features

        # 评估新模式
        accuracy = self._evaluate_pattern(
            positive_pattern, positives, negatives
        )

        # 记录性能
        self.performance_history[reflex_name].append({
            'timestamp': time.time(),
            'accuracy': accuracy,
            'num_positive': len(positives),
            'num_negative': len(negatives)
        })

        # 保存模式
        self.patterns[reflex_name] = positive_pattern

        print(f"🎯 {reflex_name} 重训练完成，准确率: {accuracy:.2%}")

    def _get_discriminative_features(self,
                                    positives: List[TrainingExample],
                                    negatives: List[TrainingExample]) -> List[str]:
        """找出区分正负例的特征"""
        # 提取正例特征
        positive_words = Counter()
        for ex in positives:
            words = self.trainer._extract_keywords(ex.input_text)
            positive_words.update(words)

        # 提取负例特征
        negative_words = Counter()
        for ex in negatives:
            words = self.trainer._extract_keywords(ex.input_text)
            negative_words.update(words)

        # 找出主要出现在正例中的词
        discriminative = []
        for word, pos_count in positive_words.items():
            neg_count = negative_words.get(word, 0)
            # 正例中出现频率明显高于负例
            if pos_count > neg_count * 2:
                discriminative.append(word)

        return discriminative

    def _evaluate_pattern(self, pattern: Pattern,
                         positives: List[TrainingExample],
                         negatives: List[TrainingExample]) -> float:
        """评估模式准确率"""
        correct = 0
        total = 0

        # 测试正例（应该匹配）
        for ex in positives:
            if self.trainer._match_pattern(pattern, ex.input_text):
                correct += 1
            total += 1

        # 测试负例（不应该匹配）
        for ex in negatives:
            if not self.trainer._match_pattern(pattern, ex.input_text):
                correct += 1
            total += 1

        return correct / total if total > 0 else 0


class ActiveLearningReflex:
    """主动学习系统：主动请求标注不确定的样本"""

    def __init__(self, trainer: AdvancedReflexTrainer):
        self.trainer = trainer
        self.uncertainty_threshold = 0.3
        self.query_queue = []  # 待标注队列
        self.labeled_data = defaultdict(list)  # 已标注数据

    def predict_with_uncertainty(self, input_text: str,
                                patterns: Dict[str, Pattern]) -> Tuple[Optional[str], float]:
        """预测并返回不确定性"""
        matches = []

        # 对所有模式计算匹配度
        for name, pattern in patterns.items():
            if self.trainer._match_pattern(pattern, input_text):
                # 计算置信度
                confidence = self._calculate_confidence(pattern, input_text)
                matches.append((name, confidence))

        if not matches:
            # 没有匹配，高不确定性
            self.query_queue.append(input_text)
            return None, 1.0

        # 按置信度排序
        matches.sort(key=lambda x: x[1], reverse=True)
        best_match, best_confidence = matches[0]

        # 计算不确定性
        if len(matches) > 1:
            # 如果有多个匹配，不确定性基于最佳和次佳的差距
            second_confidence = matches[1][1]
            uncertainty = 1.0 - (best_confidence - second_confidence)
        else:
            # 只有一个匹配，不确定性基于置信度
            uncertainty = 1.0 - best_confidence

        # 如果不确定性太高，请求标注
        if uncertainty > self.uncertainty_threshold:
            self.query_queue.append(input_text)
            print(f"❓ 不确定样本已加入队列: {input_text[:30]}...")

        return best_match, uncertainty

    def _calculate_confidence(self, pattern: Pattern, text: str) -> float:
        """计算匹配置信度"""
        confidence = pattern.confidence  # 基础置信度

        # 根据匹配类型调整
        if pattern.regex_pattern and re.search(pattern.regex_pattern, text.lower()):
            confidence *= 1.2  # 正则匹配加分

        if pattern.keyword_set:
            text_words = set(re.findall(r'\w+', text.lower()))
            overlap = len(text_words.intersection(pattern.keyword_set))
            confidence *= (1 + overlap * 0.1)  # 关键词重叠加分

        return min(confidence, 1.0)  # 限制在0-1范围

    def request_labels(self, max_queries: int = 5):
        """请求人工标注最不确定的样本"""
        if not self.query_queue:
            print("📭 没有待标注的样本")
            return

        # 选择最不确定的样本
        queries = self.query_queue[:max_queries]
        self.query_queue = self.query_queue[max_queries:]

        print(f"\n🏷️ 请标注以下{len(queries)}个样本：")

        for i, query in enumerate(queries, 1):
            print(f"\n{i}. 输入: {query}")
            label = input("   应该触发哪个反射？(输入名称或'none'): ")

            if label and label != 'none':
                response = input("   期望的响应: ")
                self.labeled_data[label].append(
                    TrainingExample(query, response)
                )
                print(f"   ✅ 已标注为: {label}")

        return self.labeled_data


def demo_advanced_training():
    """演示高级训练功能"""
    print("\n" + "="*50)
    print("🧪 高级反射训练演示")
    print("="*50)

    # 初始化训练器
    trainer = AdvancedReflexTrainer()

    # 训练示例1：问候反射
    greeting_examples = [
        ("你好", "您好！有什么可以帮助您的吗？"),
        ("早上好", "早上好！祝您有美好的一天！"),
        ("晚上好", "晚上好！今天过得怎么样？"),
        ("嗨", "嗨！很高兴见到您！"),
        ("您好", "您好！请问有什么需要帮助的吗？")
    ]

    print("\n训练问候反射...")
    greeting_pattern = trainer.train_from_examples(greeting_examples, "greeting")

    # 测试泛化能力
    test_inputs = [
        "你好啊",  # 变体
        "早安",    # 同义词
        "Hi",      # 英文
        "吃饭了吗", # 不相关
    ]

    print("\n测试泛化能力:")
    for test in test_inputs:
        match = trainer._match_pattern(greeting_pattern, test)
        print(f"  '{test}' -> {'匹配' if match else '不匹配'}")

    # 训练示例2：数学计算反射
    math_examples = [
        ("1+1等于多少", "让我计算一下：1+1=2"),
        ("100减去50", "让我计算一下：100-50=50"),
        ("5乘以6", "让我计算一下：5*6=30"),
        ("计算10除以2", "让我计算一下：10/2=5"),
        ("20加30的结果", "让我计算一下：20+30=50")
    ]

    print("\n训练数学反射...")
    math_pattern = trainer.train_from_examples(math_examples, "math")


def demo_incremental_learning():
    """演示增量学习"""
    print("\n" + "="*50)
    print("📈 增量学习演示")
    print("="*50)

    trainer = AdvancedReflexTrainer()
    learner = IncrementalReflexLearner(trainer)

    # 初始训练
    print("\n初始训练阶段:")
    learner.add_feedback("weather", "今天天气怎么样", "查询天气中...", True)
    learner.add_feedback("weather", "天气预报", "查询天气中...", True)
    learner.add_feedback("weather", "会下雨吗", "查询天气中...", True)

    # 添加负例
    print("\n添加负例:")
    learner.add_feedback("weather", "你好", "查询天气中...", False)
    learner.add_feedback("weather", "现在几点", "查询天气中...", False)

    # 触发重训练
    learner.retrain("weather")

    # 查看性能历史
    if "weather" in learner.performance_history:
        print("\n性能历史:")
        for record in learner.performance_history["weather"]:
            print(f"  准确率: {record['accuracy']:.2%} "
                  f"(正例: {record['num_positive']}, "
                  f"负例: {record['num_negative']})")


def demo_active_learning():
    """演示主动学习"""
    print("\n" + "="*50)
    print("🎯 主动学习演示")
    print("="*50)

    trainer = AdvancedReflexTrainer()
    active_learner = ActiveLearningReflex(trainer)

    # 创建一些模式
    patterns = {
        "greeting": Pattern(regex_pattern="你好|早上好|晚上好", confidence=0.9),
        "question": Pattern(regex_pattern="什么|怎么|为什么", confidence=0.8),
    }

    # 测试不确定的输入
    test_inputs = [
        "你好吗",      # 可能是问候也可能是问题
        "早",         # 不完整的问候
        "什么时候",    # 明确的问题
        "哈喽",       # 问候的变体
        "这是啥"      # 口语化的问题
    ]

    print("\n预测结果:")
    for text in test_inputs:
        prediction, uncertainty = active_learner.predict_with_uncertainty(
            text, patterns
        )
        print(f"  '{text}' -> 预测: {prediction}, "
              f"不确定性: {uncertainty:.2f}")

    # 请求标注
    print("\n请求人工标注:")
    active_learner.request_labels(max_queries=3)


def main():
    """主函数"""
    print("="*60)
    print("🧠 Gemma 270M 高级反射训练系统")
    print("="*60)

    while True:
        print("\n" + "="*60)
        print("📋 功能菜单")
        print("="*60)
        print("1. 高级训练演示")
        print("2. 增量学习演示")
        print("3. 主动学习演示")
        print("4. 加载模型并训练（需要Gemma）")
        print("0. 退出")

        choice = input("\n选择功能 (0-4): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            demo_advanced_training()
        elif choice == "2":
            demo_incremental_learning()
        elif choice == "3":
            demo_active_learning()
        elif choice == "4":
            print("\n加载Gemma模型中...")
            trainer = AdvancedReflexTrainer()
            trainer.load_model()

            # 使用语义嵌入训练
            examples = [
                ("打开灯", "正在打开照明..."),
                ("开灯", "正在打开照明..."),
                ("把灯打开", "正在打开照明..."),
                ("灯光开启", "正在打开照明...")
            ]

            pattern = trainer.train_from_examples(examples, "light_control")

            # 测试语义相似的输入
            test = "请开一下灯"
            match = trainer._match_pattern(pattern, test)
            print(f"\n测试 '{test}' -> {'匹配' if match else '不匹配'}")
        else:
            print("无效选择")

    print("\n👋 感谢使用高级训练系统！")


if __name__ == "__main__":
    main()