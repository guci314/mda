#!/bin/bash

echo "监控编译器测试进度..."
echo "进程 PID: $(ps aux | grep test_compiler.py | grep -v grep | awk '{print $2}')"
echo ""

# 监控日志文件
while true; do
    # 获取日志文件的最后一行（去除进度行）
    last_line=$(grep -v "编译中..." compiler.log | tail -n 1)
    
    # 检查是否完成
    if grep -q "测试总结" compiler.log; then
        echo ""
        echo "测试完成！"
        tail -n 30 compiler.log
        break
    fi
    
    # 显示当前状态
    current_time=$(tail -1 compiler.log | grep -o "[0-9]*秒" | tail -1)
    echo -ne "\r当前状态: 编译中... $current_time"
    
    sleep 2
done