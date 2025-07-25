#\!/bin/bash
LOG_FILE="agent_cli_v2_improved_test_20250726_002908.log"
PID=3116665
START_TIME=$(date +%s)

echo "=== Agent CLI v2 改进版测试监控 ==="
echo "进程 ID: $PID"
echo "日志文件: $LOG_FILE"
echo "开始时间: $(date +%H:%M:%S)"
echo ""

# 初始等待，让进程启动
sleep 10

COUNTER=0
while true; do
    COUNTER=$((COUNTER + 1))
    
    # 检查进程是否仍在运行
    if \! ps -p $PID > /dev/null 2>&1; then
        echo -e "\n[$(date +%H:%M:%S)] 进程已结束"
        ELAPSED=$(($(date +%s) - START_TIME))
        echo "总执行时间: ${ELAPSED}秒 ($(($ELAPSED/60))分$(($ELAPSED%60))秒)"
        
        # 显示执行结果
        echo -e "\n=== 执行结果 ==="
        grep -E "(执行结果: < /dev/null | 成功|失败|Task completed|错误)" $LOG_FILE | tail -10
        
        # 统计信息
        echo -e "\n=== 执行统计 ==="
        echo "步骤数: $(grep -c "Step [0-9]" $LOG_FILE 2>/dev/null || echo 0)"
        echo "动作数: $(grep -c "Action [0-9]" $LOG_FILE 2>/dev/null || echo 0)"
        echo "文件创建: $(grep -c "write_file" $LOG_FILE 2>/dev/null || echo 0)"
        echo "缓存命中: $(grep -c "Cache hit" $LOG_FILE 2>/dev/null || echo 0)"
        echo "决策跳过: $(grep -c "Skip.*decision" $LOG_FILE 2>/dev/null || echo 0)"
        echo "文件合并: $(grep -c "Merge" $LOG_FILE 2>/dev/null || echo 0)"
        
        # 显示最后的日志
        echo -e "\n=== 最后20行日志 ==="
        tail -20 $LOG_FILE
        break
    fi
    
    # 显示进度
    ELAPSED=$(($(date +%s) - START_TIME))
    echo -e "\n[#$COUNTER] $(date +%H:%M:%S) - 运行中 (${ELAPSED}秒)..."
    
    # 日志信息
    if [ -f "$LOG_FILE" ]; then
        SIZE=$(ls -lh $LOG_FILE | awk '{print $5}')
        LINES=$(wc -l < $LOG_FILE)
        echo "日志: $SIZE / $LINES 行"
        
        # 当前步骤
        CURRENT_STEP=$(grep "Step [0-9]" $LOG_FILE | tail -1)
        if [ -n "$CURRENT_STEP" ]; then
            echo "当前: $CURRENT_STEP"
        fi
        
        # 最近动作
        RECENT_ACTION=$(grep -E "(Action [0-9]:|Executing tool)" $LOG_FILE | tail -1)
        if [ -n "$RECENT_ACTION" ]; then
            echo "动作: $RECENT_ACTION"
        fi
        
        # 优化效果
        CACHE_HITS=$(grep -c "Cache hit" $LOG_FILE 2>/dev/null || echo 0)
        SKIPS=$(grep -c "Skip" $LOG_FILE 2>/dev/null || echo 0)
        if [ $CACHE_HITS -gt 0 ] || [ $SKIPS -gt 0 ]; then
            echo "优化: 缓存命中=$CACHE_HITS, 决策跳过=$SKIPS"
        fi
        
        # 检查错误
        ERROR_COUNT=$(grep -iE "(error|exception|traceback)" $LOG_FILE | wc -l)
        if [ $ERROR_COUNT -gt 0 ]; then
            echo "⚠️  发现 $ERROR_COUNT 个错误"
            grep -iE "(error|exception)" $LOG_FILE | tail -2
        fi
    else
        echo "等待日志文件创建..."
    fi
    
    # 每30秒检查一次
    sleep 30
done
