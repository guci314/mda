#!/bin/bash

LOG_FILE="psm_codegen_v2.log"
CHECK_INTERVAL=60
COUNTER=0

echo "开始监控 PSM 代码生成任务..."
echo "日志文件: $LOG_FILE"
echo "检查间隔: ${CHECK_INTERVAL}秒"
echo "="*60

while true; do
    COUNTER=$((COUNTER + 1))
    echo -e "\n[第 $COUNTER 次检查] $(date '+%Y-%m-%d %H:%M:%S')"
    echo "-"*40
    
    # 检查进程是否还在运行
    if ps aux | grep -v grep | grep "agent_cli run" > /dev/null; then
        echo "状态: 运行中"
    else
        echo "状态: 已完成"
    fi
    
    # 显示日志的最后20行
    echo -e "\n最新日志:"
    tail -20 "$LOG_FILE"
    
    # 检查是否有错误
    if grep -q "ERROR" "$LOG_FILE"; then
        echo -e "\n⚠️  发现错误:"
        grep "ERROR" "$LOG_FILE" | tail -5
    fi
    
    # 检查是否完成
    if grep -q "Task completed" "$LOG_FILE"; then
        echo -e "\n✅ 任务已完成!"
        break
    elif grep -q "Task failed" "$LOG_FILE"; then
        echo -e "\n❌ 任务失败!"
        break
    fi
    
    echo -e "\n等待 ${CHECK_INTERVAL} 秒后进行下一次检查..."
    sleep $CHECK_INTERVAL
done

echo -e "\n监控结束。检查生成的文件:"
ls -la hello_world_project/