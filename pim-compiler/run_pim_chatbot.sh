#!/bin/bash
# PIM Compiler Chatbot 启动脚本

# 切换到项目目录
cd "$(dirname "$0")"

echo "🤖 PIM Compiler Chatbot 启动器"
echo "================================"
echo ""

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "❌ 错误: 未找到 .env 文件"
    echo "请确保 .env 文件存在并包含必要的 API Keys"
    exit 1
fi

# 检查是否有 DEEPSEEK_API_KEY
if grep -q "^DEEPSEEK_API_KEY=" .env; then
    echo "✅ 检测到 DeepSeek API Key"
else
    echo "⚠️  警告: .env 文件中未找到 DEEPSEEK_API_KEY"
fi

# 显示选项
echo ""
echo "请选择运行模式:"
echo "1) 命令行模式 (使用 DeepSeek LLM)"
echo "2) 命令行增强版 (带历史和自动补全)"
echo "3) 简化版模式 (无需 LLM)"
echo "4) Web UI 模式 (使用 DeepSeek LLM)"
echo "5) 运行测试"
echo ""
read -p "选择 (1-5): " choice

case $choice in
    1)
        echo ""
        echo "启动命令行模式..."
        python pim_compiler_chatbot/chatbot.py
        ;;
    2)
        echo ""
        echo "启动命令行增强版..."
        echo "✨ 功能：命令历史、Tab 自动补全、帮助系统"
        python pim_compiler_chatbot/chatbot_enhanced.py
        ;;
    3)
        echo ""
        echo "启动简化版模式..."
        python pim_compiler_chatbot/chatbot_simple.py
        ;;
    4)
        echo ""
        echo "启动 Web UI 模式..."
        echo "浏览器将自动打开，或访问 http://127.0.0.1:7860"
        python pim_compiler_chatbot/chatbot_ui.py
        ;;
    5)
        echo ""
        echo "运行测试..."
        python pim_compiler_chatbot/test_chatbot.py
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac