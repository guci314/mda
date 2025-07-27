#!/bin/bash

echo "🚀 启动代码生成实验"
echo "===================="

# 清理之前的结果
echo "清理之前的实验结果..."
rm -rf generated_code_simple generated_code_detailed
rm -f code_gen_*.log
rm -f *_summary.json

# 运行简单 PSM 实验
echo ""
echo "📝 实验 1: 简单 PSM（无依赖关系说明）"
echo "后台运行中..."
nohup python code_gen_agent_background.py --scenario simple > simple_experiment.out 2>&1 &
SIMPLE_PID=$!
echo "PID: $SIMPLE_PID"

# 等待一会儿再启动第二个实验
sleep 5

# 运行详细 PSM 实验
echo ""
echo "📝 实验 2: 详细 PSM（有明确依赖关系）"
echo "后台运行中..."
nohup python code_gen_agent_background.py --scenario detailed > detailed_experiment.out 2>&1 &
DETAILED_PID=$!
echo "PID: $DETAILED_PID"

echo ""
echo "✅ 两个实验都已在后台启动"
echo ""
echo "监控日志命令："
echo "  tail -f code_gen_simple_*.log    # 查看简单 PSM 实验日志"
echo "  tail -f code_gen_detailed_*.log  # 查看详细 PSM 实验日志"
echo ""
echo "检查进程状态："
echo "  ps -p $SIMPLE_PID    # 简单 PSM 实验"
echo "  ps -p $DETAILED_PID  # 详细 PSM 实验"
echo ""
echo "查看生成的代码："
echo "  ls -la generated_code_simple/"
echo "  ls -la generated_code_detailed/"