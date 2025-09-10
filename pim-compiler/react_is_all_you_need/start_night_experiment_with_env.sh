#!/bin/bash
# 夜间实验启动脚本（带环境变量）

echo "🌙 准备启动夜间实验..."

# 加载.env文件
if [ -f "/home/guci/aiProjects/mda/pim-compiler/.env" ]; then
    echo "📝 加载.env文件..."
    export $(grep -v '^#' /home/guci/aiProjects/mda/pim-compiler/.env | xargs)
    echo "✅ 环境变量已加载"
else
    echo "❌ 找不到.env文件"
    exit 1
fi

# 验证环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "❌ 错误: DEEPSEEK_API_KEY 未设置"
    exit 1
else
    echo "✅ DEEPSEEK_API_KEY 已设置"
fi

if [ -z "$OPENROUTER_API_KEY" ]; then
    echo "❌ 错误: OPENROUTER_API_KEY 未设置"
    exit 1
else
    echo "✅ OPENROUTER_API_KEY 已设置"
fi

# 创建实验目录
mkdir -p output/experiments

# 先运行配置测试
echo ""
echo "🔍 验证模型配置..."
python test_model_config.py

# 询问是否继续
echo ""
echo "是否开始夜间实验？(y/n)"
read -r response
if [[ "$response" != "y" ]]; then
    echo "❌ 实验取消"
    exit 0
fi

# 启动实验（后台运行）
nohup python night_experiment.py > experiment.log 2>&1 &
PID=$!

echo ""
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