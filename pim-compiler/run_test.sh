#!/bin/bash

# PIM 编译器测试运行脚本

echo "PIM 编译器测试运行脚本"
echo "======================="
echo ""

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️  需要设置 DEEPSEEK_API_KEY 环境变量"
    echo ""
    echo "请运行以下命令设置 API key:"
    echo "  export DEEPSEEK_API_KEY=your-deepseek-api-key"
    echo ""
    echo "获取 DeepSeek API key:"
    echo "  1. 访问 https://platform.deepseek.com/"
    echo "  2. 注册/登录账号"
    echo "  3. 在控制台创建 API key"
    echo ""
fi

if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  可选：设置 GEMINI_API_KEY 以启用自动修复功能"
    echo ""
    echo "  export GEMINI_API_KEY=your-gemini-api-key"
    echo ""
    echo "获取 Gemini API key:"
    echo "  1. 访问 https://makersuite.google.com/app/apikey"
    echo "  2. 创建 API key"
    echo ""
fi

# 安装依赖
echo "检查 Python 依赖..."
pip install black flake8 pytest > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ 依赖已安装"
else
    echo "⚠️  安装依赖失败，请手动运行: pip install black flake8 pytest"
fi

echo ""
echo "准备就绪后，运行测试:"
echo "  python tests/test_compiler.py"
echo ""

# 如果已设置 API key，询问是否运行测试
if [ ! -z "$DEEPSEEK_API_KEY" ]; then
    read -p "是否现在运行测试? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo "开始运行测试..."
        echo ""
        python tests/test_compiler.py
    fi
fi