#!/bin/bash
# API Keys设置脚本

echo "📝 设置API Keys..."
echo ""
echo "请执行以下命令设置你的API keys："
echo ""
echo "# 1. DeepSeek API Key (用于deepseek-chat和deepseek-reasoner)"
echo "export DEEPSEEK_API_KEY='你的deepseek密钥'"
echo ""
echo "# 2. OpenRouter API Key (用于QwQ和Qwen)"
echo "export OPENROUTER_API_KEY='你的openrouter密钥'"
echo ""
echo "或者从.env文件加载："
echo "source /home/guci/aiProjects/mda/pim-compiler/.env"
echo ""
echo "设置完成后，运行: python test_model_config.py 验证配置"