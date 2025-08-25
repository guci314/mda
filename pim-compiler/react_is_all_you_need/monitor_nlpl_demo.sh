#!/bin/bash

# NLPL演示监控脚本

echo "=========================================="
echo "NLPL演示执行监控"
echo "=========================================="
echo ""

# 检查进程是否还在运行
check_process() {
    if pgrep -f "demo_nlpl_complete.py" > /dev/null; then
        echo "✅ 演示程序正在运行..."
        return 0
    else
        echo "⏹️ 演示程序已结束"
        return 1
    fi
}

# 显示日志的最后N行
show_log_tail() {
    local lines=$1
    if [ -f nlpl_demo.log ]; then
        echo ""
        echo "📋 最新日志（最后 $lines 行）："
        echo "----------------------------------------"
        tail -n $lines nlpl_demo.log
    else
        echo "⚠️ 日志文件还未创建"
    fi
}

# 显示生成的文件
show_generated_files() {
    echo ""
    echo "📁 生成的文件："
    echo "----------------------------------------"
    
    if [ -d output/nlpl_complete ]; then
        echo "主演示输出："
        find output/nlpl_complete -type f -name "*.md" -o -name "*.txt" | head -10
    fi
    
    if [ -d output/nlpl_collaboration ]; then
        echo ""
        echo "协作演示输出："
        find output/nlpl_collaboration -type f -name "*.md" -o -name "*.txt" | head -10
    fi
}

# 主监控循环
monitor_count=0
while [ $monitor_count -lt 5 ]; do
    clear
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] 监控中..."
    echo ""
    
    # 检查进程状态
    if ! check_process; then
        # 进程已结束，显示完整结果
        show_log_tail 50
        show_generated_files
        
        echo ""
        echo "=========================================="
        echo "✅ 演示执行完成！"
        echo "完整日志：nlpl_demo.log"
        echo "=========================================="
        break
    fi
    
    # 显示最新日志
    show_log_tail 20
    
    # 显示已生成的文件
    show_generated_files
    
    echo ""
    echo "⏳ 10秒后刷新... (Ctrl+C 退出监控)"
    sleep 10
    
    monitor_count=$((monitor_count + 1))
done

# 如果循环结束还在运行，显示最终状态
if [ $monitor_count -eq 5 ]; then
    echo ""
    echo "⚠️ 监控超时，程序可能还在运行"
    echo "使用 'tail -f nlpl_demo.log' 继续查看日志"
fi