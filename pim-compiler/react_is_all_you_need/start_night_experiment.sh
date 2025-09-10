#!/bin/bash
# 夜间实验启动脚本

echo "🌙 准备启动夜间实验..."

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️ 警告: DEEPSEEK_API_KEY 未设置"
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "⚠️ 警告: OPENROUTER_API_KEY 未设置"
fi

# 创建实验目录
mkdir -p output/experiments

# 启动实验（后台运行）
nohup python night_experiment.py > experiment.log 2>&1 &
PID=$!

echo "✅ 实验已在后台启动 (PID: $PID)"
echo ""
echo "📊 查看进度:"
echo "  tail -f experiment.log"
echo ""
echo "🛑 停止实验:"
echo "  kill $PID"
echo ""
echo "💤 现在你可以去睡觉了！"
echo "明天早上查看 experiment_report.md 获取结果"