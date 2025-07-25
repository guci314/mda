#\!/bin/bash
LOG_FILE="agent_cli_test_20250726_002053.log"
PID_FILE="agent_cli_test.pid"
PID=$(cat $PID_FILE)

echo "=== Agent CLI 测试监控 ==="
echo "进程 ID: $PID"
echo "日志文件: $LOG_FILE"
echo ""

while true; do
    # 检查进程是否仍在运行
    if \! ps -p $PID > /dev/null 2>&1; then
        echo "[$(date +%H:%M:%S)] 进程已结束"
        echo "=== 最终日志 ==="
        tail -50 $LOG_FILE
        break
    fi
    
    # 显示时间和进程状态
    echo -e "\n[$(date +%H:%M:%S)] 进程运行中..."
    
    # 显示日志大小
    SIZE=$(ls -lh $LOG_FILE  < /dev/null |  awk '{print $5}')
    echo "日志大小: $SIZE"
    
    # 显示关键信息
    echo "--- 步骤进度 ---"
    grep -E "(Step \d+:|步骤 \d+:)" $LOG_FILE | tail -5
    
    echo "--- 动作执行 ---"
    grep -E "(Action \d+:|Executing tool)" $LOG_FILE | tail -3
    
    echo "--- 文件创建 ---"
    grep -E "(write_file|Created file|生成的文件)" $LOG_FILE | tail -3
    
    echo "--- 错误/警告 ---"
    grep -iE "(error|warning|failed|失败)" $LOG_FILE | tail -3
    
    echo "--- 优化效果 ---"
    grep -E "(缓存命中|跳过检查|智能决策|合并文件)" $LOG_FILE | tail -3
    
    # 等待30秒
    sleep 30
done
