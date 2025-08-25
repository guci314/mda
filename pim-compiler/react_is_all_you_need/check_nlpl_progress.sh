#!/bin/bash

# 简单的进度检查脚本

echo "=========================================="
echo "NLPL演示进度检查"
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 检查进程
if pgrep -f "demo_nlpl_complete.py" > /dev/null; then
    echo "✅ 程序正在运行..."
    echo ""
    echo "最新20行日志："
    echo "------------------------------------------"
    tail -20 nlpl_demo_fixed.log 2>/dev/null || echo "日志文件还未创建"
else
    echo "⏹️ 程序已结束"
    echo ""
    echo "最后30行日志："
    echo "------------------------------------------"
    tail -30 nlpl_demo_fixed.log 2>/dev/null || echo "日志文件不存在"
fi

echo ""
echo "生成的文件："
echo "------------------------------------------"
ls -la output/nlpl_complete/*.md 2>/dev/null || echo "主演示文件还未生成"
echo ""
ls -la output/nlpl_collaboration/*.md 2>/dev/null || echo "协作演示文件还未生成"

echo ""
echo "=========================================="