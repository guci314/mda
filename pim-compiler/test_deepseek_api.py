#!/usr/bin/env python3
"""测试 DeepSeek API 连接"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
project_root = Path(__file__).parent.parent
env_file = project_root / ".env"
if env_file.exists():
    load_dotenv(env_file)
    print(f"✓ 已加载环境变量文件: {env_file}")

# 检查 API key
api_key = os.getenv("DEEPSEEK_API_KEY")
if not api_key:
    print("❌ 错误: 未找到 DEEPSEEK_API_KEY")
    sys.exit(1)

print(f"✓ 找到 DEEPSEEK_API_KEY: {api_key[:10]}...")

# 测试 API 调用
try:
    from langchain_openai import ChatOpenAI
    from langchain_core.messages import HumanMessage
    from pydantic import SecretStr
    
    print("\n测试 DeepSeek API 连接...")
    
    # 创建 LLM 客户端
    llm = ChatOpenAI(
        temperature=0.7,
        model="deepseek-chat",
        base_url="https://api.deepseek.com",
        api_key=SecretStr(api_key)
    )
    
    # 发送测试消息
    response = llm.invoke([HumanMessage(content="Hello, please respond with 'API is working'")])
    print(f"✓ API 响应: {response.content}")
    
except Exception as e:
    print(f"❌ API 调用失败: {e}")
    import traceback
    traceback.print_exc()