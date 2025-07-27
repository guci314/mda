#!/usr/bin/env python3
"""DeepSeek Token计数器 - 解决 ConversationSummaryBufferMemory 的问题"""

from typing import List, Dict, Any
from langchain_core.messages import BaseMessage
import tiktoken

class DeepSeekTokenCounter:
    """为 DeepSeek 模型提供 token 计数功能"""
    
    def __init__(self):
        # DeepSeek 使用类似 GPT-3.5/4 的分词器
        # 使用 cl100k_base 作为近似
        try:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        except:
            # 备用方案：使用 gpt-3.5 的编码
            self.encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    
    def count_tokens(self, text: str) -> int:
        """计算文本的 token 数量"""
        return len(self.encoding.encode(text))
    
    def count_messages_tokens(self, messages: List[BaseMessage]) -> int:
        """计算消息列表的总 token 数量"""
        total = 0
        for message in messages:
            # 消息元数据的 token（角色等）
            total += 4  # 每条消息的固定开销
            
            # 消息内容的 token
            if hasattr(message, 'content'):
                total += self.count_tokens(str(message.content))
            
            # 如果是函数调用消息，计算额外内容
            if hasattr(message, 'additional_kwargs'):
                total += self.count_tokens(str(message.additional_kwargs))
                
        return total
    
    def estimate_tokens(self, obj: Any) -> int:
        """估算任意对象的 token 数量"""
        if isinstance(obj, str):
            return self.count_tokens(obj)
        elif isinstance(obj, list):
            return sum(self.estimate_tokens(item) for item in obj)
        elif isinstance(obj, dict):
            return sum(self.estimate_tokens(k) + self.estimate_tokens(v) 
                      for k, v in obj.items())
        else:
            return self.count_tokens(str(obj))


# 猴子补丁函数 - 修复 DeepSeek 的 token 计数
def patch_deepseek_token_counting(llm):
    """为 DeepSeek LLM 添加 token 计数功能"""
    counter = DeepSeekTokenCounter()
    
    def get_num_tokens(self, text: str) -> int:
        """计算文本的 token 数量"""
        return counter.count_tokens(text)
    
    def get_num_tokens_from_messages(self, messages: List[BaseMessage]) -> int:
        """计算消息列表的 token 数量"""
        return counter.count_messages_tokens(messages)
    
    # 动态添加方法
    llm.get_num_tokens = get_num_tokens.__get__(llm, llm.__class__)
    llm.get_num_tokens_from_messages = get_num_tokens_from_messages.__get__(llm, llm.__class__)
    
    return llm


# 使用示例
if __name__ == "__main__":
    counter = DeepSeekTokenCounter()
    
    # 测试文本
    test_text = "你好，这是一个测试文本。Hello, this is a test text."
    print(f"Text: {test_text}")
    print(f"Tokens: {counter.count_tokens(test_text)}")
    
    # 测试消息
    from langchain_core.messages import HumanMessage, AIMessage
    messages = [
        HumanMessage(content="创建一个用户管理系统"),
        AIMessage(content="好的，我将为您创建一个用户管理系统...")
    ]
    print(f"\nMessages tokens: {counter.count_messages_tokens(messages)}")