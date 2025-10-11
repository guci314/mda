#!/usr/bin/env python3
"""
Gemma 270M 条件反射系统
使用小模型构建快速响应的条件反射机制

核心理念：
- 条件反射 = 模式识别 + 即时响应
- 小模型 = 快速反应 + 低资源占用
- 类似生物神经反射弧：感受器→传入神经→中枢→传出神经→效应器
"""

import os
import re
import json
import time
import threading
from typing import Dict, List, Tuple, Optional, Callable
from dataclasses import dataclass
from collections import deque
from datetime import datetime

import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


@dataclass
class Reflex:
    """条件反射定义"""
    pattern: str  # 触发模式（正则表达式）
    response: str  # 响应模板
    priority: int = 0  # 优先级（数字越大优先级越高）
    learning_rate: float = 0.1  # 学习率
    threshold: float = 0.8  # 触发阈值
    count: int = 0  # 触发次数
    last_triggered: Optional[float] = None  # 上次触发时间


class GemmaReflexSystem:
    """基于Gemma 270M的条件反射系统"""

    def __init__(self, model_id: str = "unsloth/gemma-3-270m-it"):
        """初始化反射系统"""
        self.model_id = model_id
        self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # 反射库
        self.reflexes: Dict[str, Reflex] = {}

        # 反射历史（用于学习）
        self.reflex_history = deque(maxlen=100)

        # 模型和分词器
        self.model = None
        self.tokenizer = None

        # 性能统计
        self.stats = {
            "total_triggers": 0,
            "avg_response_time": 0,
            "fastest_response": float('inf'),
            "slowest_response": 0
        }

        # 初始化内置反射
        self._init_builtin_reflexes()

    def _init_builtin_reflexes(self):
        """初始化内置条件反射"""

        # 问候反射
        self.add_reflex(
            "greeting",
            pattern=r"(你好|hello|hi|早上好|晚上好)",
            response="你好！有什么可以帮助你的吗？",
            priority=10
        )

        # 紧急反射
        self.add_reflex(
            "emergency",
            pattern=r"(紧急|urgent|help|救命|危险)",
            response="检测到紧急情况！立即响应：",
            priority=100
        )

        # 数学反射
        self.add_reflex(
            "math",
            pattern=r"(\d+)\s*[\+\-\*\/]\s*(\d+)",
            response="计算结果：",
            priority=5
        )

        # 时间反射
        self.add_reflex(
            "time",
            pattern=r"(现在几点|what time|当前时间)",
            response=f"当前时间：{datetime.now().strftime('%H:%M:%S')}",
            priority=8
        )

        # 情绪反射
        self.add_reflex(
            "emotion",
            pattern=r"(开心|快乐|高兴|sad|happy|angry)",
            response="我感受到了你的情绪，",
            priority=6
        )

    def load_model(self):
        """加载Gemma模型"""
        print("⚡ 加载Gemma 270M反射模型...")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

        if self.device == "cpu":
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32
            )
        else:
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16
            )

        self.model = self.model.to(self.device)
        self.model.eval()

        print(f"✅ 模型加载完成 (设备: {self.device})")

    def add_reflex(self, name: str, pattern: str, response: str,
                   priority: int = 0, threshold: float = 0.8):
        """添加条件反射"""
        self.reflexes[name] = Reflex(
            pattern=pattern,
            response=response,
            priority=priority,
            threshold=threshold
        )
        print(f"➕ 添加反射: {name} (优先级: {priority})")

    def remove_reflex(self, name: str):
        """移除条件反射"""
        if name in self.reflexes:
            del self.reflexes[name]
            print(f"➖ 移除反射: {name}")

    def detect_trigger(self, input_text: str) -> List[Tuple[str, Reflex, float]]:
        """检测触发的反射"""
        triggered = []

        for name, reflex in self.reflexes.items():
            match = re.search(reflex.pattern, input_text, re.IGNORECASE)
            if match:
                # 计算匹配强度
                match_strength = len(match.group()) / len(input_text)

                # 基于历史调整强度
                if reflex.count > 0:
                    match_strength *= (1 + reflex.learning_rate * min(reflex.count, 10))

                if match_strength >= reflex.threshold:
                    triggered.append((name, reflex, match_strength))

        # 按优先级和匹配强度排序
        triggered.sort(key=lambda x: (x[1].priority, x[2]), reverse=True)

        return triggered

    def execute_reflex(self, reflex: Reflex, input_text: str) -> str:
        """执行条件反射"""
        start_time = time.time()

        # 更新反射统计
        reflex.count += 1
        reflex.last_triggered = time.time()

        # 特殊处理数学反射
        if "计算结果" in reflex.response:
            match = re.search(r"(\d+)\s*([\+\-\*\/])\s*(\d+)", input_text)
            if match:
                a, op, b = int(match.group(1)), match.group(2), int(match.group(3))
                result = eval(f"{a}{op}{b}")
                response = f"{reflex.response}{result}"
            else:
                response = reflex.response
        else:
            response = reflex.response

        # 记录响应时间
        response_time = time.time() - start_time
        self._update_stats(response_time)

        return response

    def generate_response(self, input_text: str, use_model: bool = True) -> str:
        """生成响应（结合反射和模型）"""

        # 1. 检查条件反射
        triggered = self.detect_trigger(input_text)

        if triggered:
            # 执行最高优先级的反射
            name, reflex, strength = triggered[0]
            reflex_response = self.execute_reflex(reflex, input_text)

            print(f"⚡ 触发反射: {name} (强度: {strength:.2f})")

            # 如果需要，使用模型增强响应
            if use_model and self.model and "：" in reflex_response:
                enhanced = self._enhance_with_model(
                    input_text,
                    reflex_response
                )
                return f"{reflex_response}{enhanced}"

            return reflex_response

        # 2. 如果没有触发反射，使用模型生成
        if use_model and self.model:
            return self._model_generate(input_text)

        return "没有匹配的反射，也没有加载模型。"

    def _enhance_with_model(self, input_text: str, reflex_response: str,
                           max_length: int = 50) -> str:
        """使用模型增强反射响应"""
        prompt = f"用户：{input_text}\n系统反射：{reflex_response}\n增强响应："

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=max_length,
                temperature=0.3,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )

        return response

    def _model_generate(self, input_text: str, max_length: int = 100) -> str:
        """纯模型生成"""
        prompt = f"用户：{input_text}\n助手："

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)

        with torch.no_grad():
            outputs = self.model.generate(
                inputs.input_ids,
                max_new_tokens=max_length,
                temperature=0.7,
                do_sample=True,
                pad_token_id=self.tokenizer.pad_token_id,
                eos_token_id=self.tokenizer.eos_token_id,
            )

        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        )

        return response

    def _update_stats(self, response_time: float):
        """更新性能统计"""
        self.stats["total_triggers"] += 1

        # 更新平均响应时间
        n = self.stats["total_triggers"]
        old_avg = self.stats["avg_response_time"]
        self.stats["avg_response_time"] = (old_avg * (n-1) + response_time) / n

        # 更新最快/最慢
        self.stats["fastest_response"] = min(
            self.stats["fastest_response"],
            response_time
        )
        self.stats["slowest_response"] = max(
            self.stats["slowest_response"],
            response_time
        )

    def learn_from_feedback(self, reflex_name: str, positive: bool):
        """从反馈中学习，调整反射参数"""
        if reflex_name in self.reflexes:
            reflex = self.reflexes[reflex_name]

            if positive:
                # 正反馈：降低阈值，提高优先级
                reflex.threshold = max(0.5, reflex.threshold - 0.05)
                reflex.priority = min(100, reflex.priority + 1)
            else:
                # 负反馈：提高阈值，降低优先级
                reflex.threshold = min(1.0, reflex.threshold + 0.05)
                reflex.priority = max(0, reflex.priority - 1)

            print(f"📈 学习更新: {reflex_name}")
            print(f"   新阈值: {reflex.threshold:.2f}")
            print(f"   新优先级: {reflex.priority}")

    def train_reflex(self, examples: List[Tuple[str, str]], name: str):
        """训练新的条件反射"""
        print(f"🎯 训练新反射: {name}")

        # 提取模式
        patterns = []
        for input_text, expected_response in examples:
            # 简单的模式提取（实际应用中可以更复杂）
            words = input_text.lower().split()
            pattern = "|".join(words[:2])  # 使用前两个词作为模式
            patterns.append(pattern)

        # 创建统一模式
        unified_pattern = f"({')|(').join(set(patterns))})"

        # 使用第一个响应作为模板
        response_template = examples[0][1]

        # 添加新反射
        self.add_reflex(
            name=name,
            pattern=unified_pattern,
            response=response_template,
            priority=5
        )

        print(f"✅ 训练完成: 模式='{unified_pattern[:50]}...'")

    def print_stats(self):
        """打印性能统计"""
        print("\n📊 反射系统统计")
        print("=" * 40)
        print(f"总触发次数: {self.stats['total_triggers']}")
        print(f"平均响应时间: {self.stats['avg_response_time']*1000:.2f}ms")

        if self.stats['fastest_response'] != float('inf'):
            print(f"最快响应: {self.stats['fastest_response']*1000:.2f}ms")
            print(f"最慢响应: {self.stats['slowest_response']*1000:.2f}ms")

        print("\n反射使用频率:")
        for name, reflex in sorted(
            self.reflexes.items(),
            key=lambda x: x[1].count,
            reverse=True
        ):
            if reflex.count > 0:
                print(f"  {name}: {reflex.count}次")


class ReflexMonitor:
    """反射监控器 - 实时监控和触发反射"""

    def __init__(self, reflex_system: GemmaReflexSystem):
        self.system = reflex_system
        self.running = False
        self.monitor_thread = None

        # 事件队列
        self.event_queue = deque(maxlen=50)

        # 监听器
        self.listeners: List[Callable] = []

    def add_listener(self, callback: Callable):
        """添加事件监听器"""
        self.listeners.append(callback)

    def trigger_event(self, event_type: str, data: str):
        """触发事件"""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": time.time()
        }

        self.event_queue.append(event)

        # 处理事件
        response = self.system.generate_response(data, use_model=False)

        # 通知监听器
        for listener in self.listeners:
            listener(event, response)

        return response

    def start_monitoring(self):
        """开始监控"""
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.start()
        print("🔍 反射监控器已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("🛑 反射监控器已停止")

    def _monitor_loop(self):
        """监控循环"""
        while self.running:
            # 这里可以添加各种触发源
            # 例如：文件变化、网络请求、传感器数据等
            time.sleep(0.1)


def demo_basic_reflexes():
    """演示基础条件反射"""
    print("\n" + "="*50)
    print("🧪 基础条件反射演示")
    print("="*50)

    # 创建反射系统
    system = GemmaReflexSystem()

    # 测试输入
    test_inputs = [
        "你好，今天天气怎么样？",
        "紧急！需要帮助！",
        "100 + 200",
        "现在几点了？",
        "我很开心！",
        "这个不会触发任何反射"
    ]

    for input_text in test_inputs:
        print(f"\n输入: {input_text}")
        response = system.generate_response(input_text, use_model=False)
        print(f"响应: {response}")

    # 打印统计
    system.print_stats()


def demo_learning():
    """演示学习机制"""
    print("\n" + "="*50)
    print("🧠 条件反射学习演示")
    print("="*50)

    system = GemmaReflexSystem()

    # 训练新反射
    examples = [
        ("查看天气", "正在查询天气信息..."),
        ("天气预报", "正在查询天气信息..."),
        ("今天天气", "正在查询天气信息...")
    ]

    system.train_reflex(examples, "weather")

    # 测试新反射
    print("\n测试新学习的反射:")
    test = "查看天气情况"
    print(f"输入: {test}")
    print(f"响应: {system.generate_response(test, use_model=False)}")

    # 学习调整
    print("\n学习调整演示:")
    system.learn_from_feedback("weather", positive=True)
    system.learn_from_feedback("greeting", positive=False)


def demo_with_model():
    """演示模型增强的条件反射"""
    print("\n" + "="*50)
    print("🤖 模型增强条件反射演示")
    print("="*50)

    system = GemmaReflexSystem()

    print("\n加载模型中...")
    system.load_model()

    # 测试混合响应
    test_inputs = [
        "紧急情况！服务器宕机了",
        "计算 42 * 17",
        "介绍一下Python"
    ]

    for input_text in test_inputs:
        print(f"\n输入: {input_text}")

        # 纯反射
        reflex_only = system.generate_response(input_text, use_model=False)
        print(f"纯反射: {reflex_only}")

        # 模型增强
        with_model = system.generate_response(input_text, use_model=True)
        print(f"模型增强: {with_model[:200]}")


def demo_realtime():
    """演示实时触发"""
    print("\n" + "="*50)
    print("⚡ 实时触发演示")
    print("="*50)

    system = GemmaReflexSystem()
    monitor = ReflexMonitor(system)

    # 添加监听器
    def on_event(event, response):
        print(f"\n[{datetime.fromtimestamp(event['timestamp']).strftime('%H:%M:%S')}]")
        print(f"事件: {event['type']}")
        print(f"数据: {event['data']}")
        print(f"反射响应: {response}")

    monitor.add_listener(on_event)

    # 启动监控
    monitor.start_monitoring()

    # 模拟事件
    events = [
        ("user_input", "你好"),
        ("alert", "紧急通知"),
        ("calculation", "15 + 25"),
        ("query", "现在几点"),
    ]

    for event_type, data in events:
        monitor.trigger_event(event_type, data)
        time.sleep(1)

    # 停止监控
    monitor.stop_monitoring()


def interactive_demo():
    """交互式演示"""
    print("\n" + "="*50)
    print("💬 交互式条件反射系统")
    print("="*50)

    system = GemmaReflexSystem()

    # 询问是否加载模型
    use_model = input("\n是否加载Gemma模型增强响应？(y/n): ").lower() == 'y'

    if use_model:
        system.load_model()

    print("\n系统准备就绪！")
    print("命令:")
    print("  /add <name> <pattern> <response> - 添加新反射")
    print("  /remove <name> - 移除反射")
    print("  /stats - 查看统计")
    print("  /learn <name> +/- - 学习调整")
    print("  /quit - 退出")
    print("-" * 40)

    while True:
        user_input = input("\n> ").strip()

        if user_input.startswith("/"):
            # 处理命令
            parts = user_input.split()
            cmd = parts[0]

            if cmd == "/quit":
                break
            elif cmd == "/stats":
                system.print_stats()
            elif cmd == "/add" and len(parts) >= 4:
                name = parts[1]
                pattern = parts[2]
                response = " ".join(parts[3:])
                system.add_reflex(name, pattern, response)
            elif cmd == "/remove" and len(parts) >= 2:
                system.remove_reflex(parts[1])
            elif cmd == "/learn" and len(parts) >= 3:
                name = parts[1]
                positive = parts[2] == "+"
                system.learn_from_feedback(name, positive)
            else:
                print("未知命令")
        else:
            # 处理输入
            response = system.generate_response(user_input, use_model=use_model)
            print(f"💭 {response}")


def main():
    """主函数"""
    print("="*60)
    print("🧠 Gemma 270M 条件反射系统")
    print("="*60)
    print("\n条件反射原理：")
    print("1. 模式识别 - 快速匹配输入模式")
    print("2. 优先响应 - 基于优先级选择反射")
    print("3. 即时反应 - 毫秒级响应速度")
    print("4. 自主学习 - 根据反馈调整参数")

    while True:
        print("\n" + "="*60)
        print("📋 演示菜单")
        print("="*60)
        print("1. 基础反射演示")
        print("2. 学习机制演示")
        print("3. 模型增强演示（需要下载模型）")
        print("4. 实时触发演示")
        print("5. 交互式系统")
        print("0. 退出")

        choice = input("\n选择演示 (0-5): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            demo_basic_reflexes()
        elif choice == "2":
            demo_learning()
        elif choice == "3":
            demo_with_model()
        elif choice == "4":
            demo_realtime()
        elif choice == "5":
            interactive_demo()
        else:
            print("无效选择")

    print("\n👋 感谢使用条件反射系统！")


if __name__ == "__main__":
    main()