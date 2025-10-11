#!/bin/bash
# Gemma 270M 快速启动脚本（使用社区版本，无需Token）

echo "🚀 Gemma 270M 快速启动"
echo "======================"
echo ""
echo "📦 安装依赖..."

# 安装基础依赖
pip install transformers torch sentencepiece protobuf psutil

echo ""
echo "✅ 依赖安装完成！"
echo ""
echo "🎯 运行Gemma 270M演示（社区版本，无需Token）"
echo ""

# 运行演示
python gemma_270m_demo.py

echo ""
echo "演示结束！"