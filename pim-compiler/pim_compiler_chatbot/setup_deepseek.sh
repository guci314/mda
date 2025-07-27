#!/bin/bash
# 设置 DeepSeek API Key

echo "=== PIM Compiler Chatbot 配置 ==="
echo ""
echo "请输入你的 DeepSeek API Key:"
echo "（可以从 https://platform.deepseek.com/api_keys 获取）"
echo ""
read -p "API Key: " api_key

if [ -z "$api_key" ]; then
    echo "❌ API Key 不能为空"
    exit 1
fi

# 导出环境变量
export DEEPSEEK_API_KEY="$api_key"

# 保存到配置文件
echo "export DEEPSEEK_API_KEY='$api_key'" > ~/.pim_compiler_chatbot_env

echo ""
echo "✅ 配置成功！"
echo ""
echo "现在可以运行聊天机器人："
echo "  python pim_compiler_chatbot/chatbot.py"
echo ""
echo "下次使用前，请先加载环境变量："
echo "  source ~/.pim_compiler_chatbot_env"
echo ""

# 询问是否立即运行
read -p "是否立即启动聊天机器人？(y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python pim_compiler_chatbot/chatbot.py
fi