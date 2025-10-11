#!/bin/bash
"""
运行条件反射路由器演示
展示Gemini Flash做快速模式识别的效果
"""

echo "=========================================="
echo "🚀 Gemini条件反射路由器"
echo "=========================================="
echo ""
echo "准备工作："
echo "1. 设置API Keys"
echo ""

# 检查并提示设置API Keys
if [ -z "$GEMINI_API_KEY" ]; then
    echo "❌ GEMINI_API_KEY未设置"
    echo "   请运行: export GEMINI_API_KEY='your-gemini-api-key'"
    echo ""
    echo "   获取方式："
    echo "   1. 访问 https://makersuite.google.com/app/apikey"
    echo "   2. 创建API Key"
    echo ""
    exit 1
else
    echo "✅ GEMINI_API_KEY已设置"
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  DEEPSEEK_API_KEY未设置"
    echo "   通用问题将无法处理"
    echo "   可选: export DEEPSEEK_API_KEY='your-deepseek-api-key'"
else
    echo "✅ DEEPSEEK_API_KEY已设置"
fi

echo ""
echo "2. 安装依赖"
pip install requests > /dev/null 2>&1
echo "✅ 依赖已安装"

echo ""
echo "=========================================="
echo "选择运行模式："
echo "=========================================="
echo "1. 自动测试模式（运行预设测试用例）"
echo "2. 交互对话模式（手动输入测试）"
echo ""
read -p "请选择 (1/2): " choice

case $choice in
    1)
        echo ""
        echo "运行自动测试..."
        python gemini_reflex_router.py
        ;;
    2)
        echo ""
        echo "进入交互模式..."
        python gemini_reflex_router.py --interactive
        ;;
    *)
        echo "无效选择"
        exit 1
        ;;
esac