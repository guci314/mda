#!/usr/bin/env python3
"""
Gemma 270M 本地运行演示
展示如何在本机运行Google Gemma 270M模型

作者: Assistant
日期: 2025-01-04
"""

import os
import time
import psutil
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
from typing import Optional, List
import warnings
warnings.filterwarnings('ignore')

class Gemma270MDemo:
    """Gemma 270M模型本地运行演示类"""

    def __init__(self,
                 model_id: str = "unsloth/gemma-3-270m-it",  # 社区版本，无需Token
                 device: str = "auto",
                 quantize: bool = False):
        """
        初始化Gemma 270M模型

        Args:
            model_id: HuggingFace模型ID
            device: 运行设备 ('cpu', 'cuda', 'mps', 'auto')
            quantize: 是否使用量化以减少内存占用
        """
        self.model_id = model_id
        self.device = self._get_device(device)
        self.quantize = quantize

        print(f"🚀 正在加载Gemma 270M模型...")
        print(f"   模型: {model_id}")
        print(f"   设备: {self.device}")
        print(f"   量化: {'是' if quantize else '否'}")

        self.tokenizer = None
        self.model = None

    def _get_device(self, device: str) -> str:
        """自动检测最佳设备"""
        if device == "auto":
            if torch.cuda.is_available():
                return "cuda"
            elif torch.backends.mps.is_available():
                return "mps"
            else:
                return "cpu"
        return device

    def load_model(self):
        """加载模型和分词器"""
        start_time = time.time()

        # 加载分词器
        print("⏳ 加载分词器...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_id)

        # 加载模型
        print("⏳ 加载模型权重...")
        if self.quantize and self.device == "cuda":
            # 使用8-bit量化（需要bitsandbytes库）
            try:
                from transformers import BitsAndBytesConfig
                quantization_config = BitsAndBytesConfig(
                    load_in_8bit=True,
                    bnb_8bit_compute_dtype=torch.float16
                )
                self.model = AutoModelForCausalLM.from_pretrained(
                    self.model_id,
                    quantization_config=quantization_config,
                    device_map="auto"
                )
            except ImportError:
                print("⚠️ 量化需要安装bitsandbytes: pip install bitsandbytes")
                self._load_standard_model()
        else:
            self._load_standard_model()

        load_time = time.time() - start_time
        self._print_model_info(load_time)

    def _load_standard_model(self):
        """标准模型加载"""
        if self.device == "cpu":
            # CPU上使用float32
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float32
            )
        else:
            # GPU上使用float16以节省内存
            self.model = AutoModelForCausalLM.from_pretrained(
                self.model_id,
                torch_dtype=torch.float16
            )

        self.model = self.model.to(self.device)
        self.model.eval()

    def _print_model_info(self, load_time: float):
        """打印模型信息"""
        # 获取模型参数量
        total_params = sum(p.numel() for p in self.model.parameters())

        # 获取内存使用
        if self.device == "cuda":
            memory_used = torch.cuda.memory_allocated() / 1024**3
            memory_info = f"{memory_used:.2f} GB (GPU)"
        else:
            process = psutil.Process()
            memory_used = process.memory_info().rss / 1024**3
            memory_info = f"{memory_used:.2f} GB (RAM)"

        print(f"\n✅ 模型加载完成！")
        print(f"   参数量: {total_params/1e6:.1f}M")
        print(f"   内存占用: {memory_info}")
        print(f"   加载时间: {load_time:.2f}秒")

    def generate(self,
                 prompt: str,
                 max_length: int = 256,
                 temperature: float = 0.7,
                 top_p: float = 0.95,
                 stream: bool = True) -> str:
        """
        生成文本

        Args:
            prompt: 输入提示
            max_length: 最大生成长度
            temperature: 温度参数（0-1，越高越随机）
            top_p: nucleus sampling参数
            stream: 是否流式输出

        Returns:
            生成的文本
        """
        if not self.model:
            raise ValueError("请先调用load_model()加载模型")

        # 编码输入
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        input_length = inputs.input_ids.shape[1]

        # 生成参数
        gen_kwargs = {
            "max_new_tokens": max_length,
            "temperature": temperature,
            "top_p": top_p,
            "do_sample": temperature > 0,
            "pad_token_id": self.tokenizer.pad_token_id,
            "eos_token_id": self.tokenizer.eos_token_id,
        }

        print(f"\n💭 生成中...")
        start_time = time.time()

        if stream:
            return self._stream_generate(inputs, gen_kwargs, input_length)
        else:
            return self._batch_generate(inputs, gen_kwargs, input_length, start_time)

    def _batch_generate(self, inputs, gen_kwargs, input_length, start_time):
        """批量生成（一次性返回）"""
        with torch.no_grad():
            outputs = self.model.generate(inputs.input_ids, **gen_kwargs)

        # 解码输出
        generated_text = self.tokenizer.decode(
            outputs[0][input_length:],
            skip_special_tokens=True
        )

        gen_time = time.time() - start_time
        tokens_generated = outputs.shape[1] - input_length
        speed = tokens_generated / gen_time

        print(f"\n⏱️ 生成统计:")
        print(f"   Token数: {tokens_generated}")
        print(f"   生成时间: {gen_time:.2f}秒")
        print(f"   速度: {speed:.1f} tokens/秒")

        return generated_text

    def _stream_generate(self, inputs, gen_kwargs, input_length):
        """流式生成（逐token输出）"""
        from transformers import TextIteratorStreamer
        from threading import Thread

        streamer = TextIteratorStreamer(
            self.tokenizer,
            skip_prompt=True,
            skip_special_tokens=True
        )

        gen_kwargs["streamer"] = streamer

        # 在另一个线程中运行生成
        thread = Thread(target=self.model.generate,
                       args=(inputs.input_ids,),
                       kwargs=gen_kwargs)
        thread.start()

        # 流式输出
        generated_text = ""
        for new_text in streamer:
            print(new_text, end="", flush=True)
            generated_text += new_text

        thread.join()
        return generated_text

    def benchmark(self):
        """性能基准测试"""
        print("\n📊 运行性能基准测试...")

        test_prompts = [
            "什么是人工智能？",
            "写一个Python函数计算斐波那契数列",
            "解释量子计算的基本原理",
        ]

        results = []
        for prompt in test_prompts:
            print(f"\n测试: {prompt[:30]}...")

            start_time = time.time()
            output = self.generate(prompt, max_length=100, stream=False)
            gen_time = time.time() - start_time

            tokens = len(self.tokenizer.encode(output))
            speed = tokens / gen_time

            results.append({
                "prompt": prompt[:30],
                "tokens": tokens,
                "time": gen_time,
                "speed": speed
            })

        # 打印结果
        print("\n📈 基准测试结果:")
        print("-" * 60)
        for r in results:
            print(f"提示: {r['prompt']}")
            print(f"  生成Token数: {r['tokens']}")
            print(f"  生成时间: {r['time']:.2f}秒")
            print(f"  速度: {r['speed']:.1f} tokens/秒")

        avg_speed = sum(r['speed'] for r in results) / len(results)
        print(f"\n平均速度: {avg_speed:.1f} tokens/秒")

    def interactive_chat(self):
        """交互式对话模式"""
        print("\n💬 进入交互式对话模式")
        print("   输入'退出'或'quit'结束对话")
        print("   输入'清空'或'clear'清空对话历史")
        print("-" * 60)

        conversation_history = []

        while True:
            user_input = input("\n👤 你: ").strip()

            if user_input.lower() in ['退出', 'quit', 'exit']:
                print("👋 再见！")
                break

            if user_input.lower() in ['清空', 'clear']:
                conversation_history = []
                print("🗑️ 对话历史已清空")
                continue

            # 构建对话上下文
            if conversation_history:
                context = "\n".join(conversation_history[-4:])  # 保留最近2轮对话
                prompt = f"{context}\n用户: {user_input}\n助手:"
            else:
                prompt = f"用户: {user_input}\n助手:"

            print("\n🤖 Gemma: ", end="")
            response = self.generate(prompt, max_length=256, temperature=0.7)

            # 更新历史
            conversation_history.append(f"用户: {user_input}")
            conversation_history.append(f"助手: {response}")


def main():
    """主函数：演示Gemma 270M的各种功能"""

    print("=" * 60)
    print("🌟 Google Gemma 270M 本地运行演示")
    print("=" * 60)

    # 初始化模型
    demo = Gemma270MDemo(
        model_id="unsloth/gemma-3-270m-it",  # 使用社区版本，无需Token
        device="auto",  # 自动选择设备
        quantize=False  # 270M模型很小，通常不需要量化
    )

    # 加载模型
    try:
        demo.load_model()
    except Exception as e:
        print(f"\n❌ 模型加载失败: {e}")
        print("\n请确保:")
        print("1. 安装了必要的库: pip install transformers torch")
        print("2. 有稳定的网络连接（首次运行需要下载模型）")
        print("3. 有足够的磁盘空间（约550MB）")
        return

    # 功能演示菜单
    while True:
        print("\n" + "=" * 60)
        print("📋 功能菜单")
        print("=" * 60)
        print("1. 快速测试 - 生成一个简单回复")
        print("2. 代码生成 - 生成Python代码")
        print("3. 性能测试 - 运行基准测试")
        print("4. 交互对话 - 进入聊天模式")
        print("5. 自定义生成 - 自定义参数生成")
        print("0. 退出")

        choice = input("\n请选择功能 (0-5): ").strip()

        if choice == "0":
            print("\n👋 感谢使用！")
            break

        elif choice == "1":
            print("\n--- 快速测试 ---")
            prompt = "介绍一下Python编程语言的主要特点"
            print(f"提示: {prompt}")
            print("\n回复: ", end="")
            response = demo.generate(prompt, max_length=150)

        elif choice == "2":
            print("\n--- 代码生成 ---")
            prompt = "写一个Python函数，计算列表中所有数字的平均值"
            print(f"提示: {prompt}")
            print("\n生成的代码:\n")
            response = demo.generate(prompt, max_length=200, temperature=0.3)

        elif choice == "3":
            demo.benchmark()

        elif choice == "4":
            demo.interactive_chat()

        elif choice == "5":
            print("\n--- 自定义生成 ---")
            prompt = input("请输入提示文本: ")
            max_length = int(input("最大生成长度 (默认256): ") or "256")
            temperature = float(input("温度 0-1 (默认0.7): ") or "0.7")

            print(f"\n生成中...")
            response = demo.generate(
                prompt,
                max_length=max_length,
                temperature=temperature
            )
            print(f"\n生成结果:\n{response}")

        else:
            print("⚠️ 无效选择，请重试")


if __name__ == "__main__":
    main()