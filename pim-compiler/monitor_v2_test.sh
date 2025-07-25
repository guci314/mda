#\!/bin/bash
LOG_FILE="agent_cli_v2_improved_test_20250726_002442.log"
PID_FILE="agent_cli_v2_test.pid"
PID=$(cat $PID_FILE)

echo "=== Agent CLI v2 改进版测试监控 ==="
echo "进程 ID: $PID"
echo "日志文件: $LOG_FILE"
echo "开始时间: $(date +%H:%M:%S)"
echo ""

# 初始等待
sleep 5

while true; do
    # 检查进程是否仍在运行
    if \! ps -p $PID > /dev/null 2>&1; then
        echo -e "\n[$(date +%H:%M:%S)] 进程已结束"
        echo "=== 执行结果 ==="
        tail -30 $LOG_FILE  < /dev/null |  grep -E "(执行结果|成功|失败|完成|错误)"
        echo -e "\n=== 最终日志（最后50行）==="
        tail -50 $LOG_FILE
        break
    fi
    
    # 显示时间和进程状态
    echo -e "\n[$(date +%H:%M:%S)] 进程运行中..."
    
    # 显示日志大小和行数
    SIZE=$(ls -lh $LOG_FILE 2>/dev/null | awk '{print $5}')
    LINES=$(wc -l < $LOG_FILE 2>/dev/null || echo 0)
    echo "日志: ${SIZE:-0} / ${LINES} 行"
    
    # 显示步骤进度
    echo "--- 步骤进度 ---"
    grep -E "(Step \d+:|步骤 \d+:|Planning step|Executing step)" $LOG_FILE 2>/dev/null | tail -5
    
    # 显示动作执行
    echo "--- 最近动作 ---"
    grep -E "(Action \d+:|Executing tool|Tool:)" $LOG_FILE 2>/dev/null | tail -3
    
    # 显示文件操作
    echo "--- 文件创建 ---"
    grep -E "(write_file|Created:|Writing to|生成的文件)" $LOG_FILE 2>/dev/null | tail -3
    
    # 显示优化效果
    echo "--- 优化效果 ---"
    grep -E "(缓存命中|Cache hit|跳过检查|Skip|智能决策|Smart|合并|Merge)" $LOG_FILE 2>/dev/null | tail -3
    
    # 显示错误（如果有）
    ERROR_COUNT=$(grep -iE "(error|exception|failed|失败)" $LOG_FILE 2>/dev/null | wc -l)
    if [ $ERROR_COUNT -gt 0 ]; then
        echo "--- 错误信息 (共 $ERROR_COUNT 个) ---"
        grep -iE "(error|exception|failed|失败)" $LOG_FILE 2>/dev/null | tail -3
    fi
    
    # 等待30秒
    sleep 30
done

# 最终统计
echo -e "\n=== 执行统计 ==="
echo "总执行时间: $(($(date +%s) - $(stat -c %Y $LOG_FILE))) 秒"
echo "文件创建数: $(grep -c "write_file" $LOG_FILE 2>/dev/null || echo 0)"
echo "缓存命中数: $(grep -c "Cache hit" $LOG_FILE 2>/dev/null || echo 0)"
echo "决策跳过数: $(grep -c "Skip" $LOG_FILE 2>/dev/null || echo 0)"
