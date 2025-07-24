#!/usr/bin/env python3
"""
DeepSeek API 配置助手
帮助用户配置 DeepSeek API 访问
"""
import os
import sys
import json
import requests
from pathlib import Path
from getpass import getpass


def test_deepseek_api(api_key: str, base_url: str = "https://api.deepseek.com") -> bool:
    """测试 DeepSeek API 连接"""
    print("\n测试 API 连接...")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "temperature": 0.3,
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            f"{base_url}/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if "choices" in result:
                print("✅ API 连接成功！")
                return True
        else:
            print(f"❌ API 返回错误：{response.status_code}")
            print(f"错误信息：{response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 连接失败：{str(e)}")
        return False


def save_config(api_key: str, base_url: str = "https://api.deepseek.com"):
    """保存配置到文件"""
    config = {
        "api_key": api_key,
        "base_url": base_url,
        "model": "deepseek-chat"
    }
    
    # 保存到 .env 文件
    env_file = Path(".env")
    env_content = f"""# DeepSeek API Configuration
DEEPSEEK_API_KEY={api_key}
DEEPSEEK_BASE_URL={base_url}
DEEPSEEK_MODEL=deepseek-chat

# LLM Provider
LLM_PROVIDER=deepseek
"""
    
    with open(env_file, "w") as f:
        f.write(env_content)
    
    print(f"\n✅ 配置已保存到 {env_file}")
    
    # 同时保存为 JSON
    config_file = Path("deepseek_config.json")
    with open(config_file, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ 配置已保存到 {config_file}")


def setup_deepseek():
    """设置 DeepSeek API"""
    print("DeepSeek API 配置助手")
    print("=" * 60)
    print("\n访问 https://platform.deepseek.com 获取 API Key")
    print("DeepSeek 在中国地区访问稳定，价格实惠")
    print("=" * 60)
    
    # 检查现有配置
    existing_key = os.getenv("DEEPSEEK_API_KEY")
    if existing_key:
        print(f"\n检测到现有 API Key：{existing_key[:8]}...")
        use_existing = input("是否使用现有配置？[Y/n]: ").strip().lower()
        if use_existing != 'n':
            if test_deepseek_api(existing_key):
                print("\n✅ 现有配置有效！")
                return True
            else:
                print("\n❌ 现有配置无效，需要重新配置")
    
    # 输入新的 API Key
    print("\n请输入 DeepSeek API Key")
    print("(输入时不会显示，按回车确认)")
    api_key = getpass("API Key: ").strip()
    
    if not api_key:
        print("❌ API Key 不能为空")
        return False
    
    # 询问是否使用自定义 URL（如私有部署）
    use_custom = input("\n是否使用自定义 API 地址？[y/N]: ").strip().lower()
    if use_custom == 'y':
        base_url = input("API 地址 (默认: https://api.deepseek.com): ").strip()
        if not base_url:
            base_url = "https://api.deepseek.com"
    else:
        base_url = "https://api.deepseek.com"
    
    # 测试 API
    if test_deepseek_api(api_key, base_url):
        # 保存配置
        save_config(api_key, base_url)
        
        # 设置环境变量（当前会话）
        os.environ["DEEPSEEK_API_KEY"] = api_key
        os.environ["DEEPSEEK_BASE_URL"] = base_url
        
        print("\n✅ DeepSeek API 配置完成！")
        print("\n下一步：")
        print("1. 运行测试：python test_deepseek_cli.py")
        print("2. 使用 CLI：python -c 'from gemini_cli_deepseek import DeepSeekCLI; cli = DeepSeekCLI(); cli.execute_task(\"your task\")'")
        
        return True
    else:
        print("\n❌ API 配置失败，请检查 API Key 是否正确")
        return False


def check_deepseek_prices():
    """显示 DeepSeek 价格信息"""
    print("\nDeepSeek API 价格（2024年）:")
    print("-" * 40)
    print("模型: deepseek-chat")
    print("输入: ¥1 / 1M tokens")
    print("输出: ¥2 / 1M tokens")
    print("\n对比 GPT-4:")
    print("输入: $30 / 1M tokens (约 ¥210)")
    print("输出: $60 / 1M tokens (约 ¥420)")
    print("\nDeepSeek 价格优势：约为 GPT-4 的 1/200")
    print("-" * 40)


def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == "--prices":
        check_deepseek_prices()
        return
    
    success = setup_deepseek()
    
    if success:
        show_prices = input("\n查看价格信息？[y/N]: ").strip().lower()
        if show_prices == 'y':
            check_deepseek_prices()


if __name__ == "__main__":
    main()