#\!/bin/bash
LOG_FILE="agent_cli_v2_test_20250726_003700.log"
PID=3125362
START_TIME=$(date +%s)

echo "=== Agent CLI v2 改进版 - 最终测试监控 ==="
echo "进程 ID: $PID"
echo "日志文件: $LOG_FILE"
echo "开始时间: $(date +%H:%M:%S)"
echo ""

# 等待进程启动和初始化
sleep 15

COUNTER=0
LAST_LINE_COUNT=0

while true; do
    COUNTER=$((COUNTER + 1))
    
    # 检查进程状态
    if \! ps -p $PID > /dev/null 2>&1; then
        ELAPSED=$(($(date +%s) - START_TIME))
        echo -e "\n[$(date +%H:%M:%S)] ✅ 进程已完成"
        echo "总执行时间: ${ELAPSED}秒 ($(($ELAPSED/60))分$(($ELAPSED%60))秒)"
        
        # 最终统计
        if [ -f "$LOG_FILE" ]; then
            echo -e "\n=== 执行统计 ==="
            echo "步骤总数: $(grep -c "Planning step" $LOG_FILE 2>/dev/null || echo 0)"
            echo "动作总数: $(grep -c "Executing tool" $LOG_FILE 2>/dev/null || echo 0)"
            echo "文件创建: $(grep -c "write_file" $LOG_FILE 2>/dev/null || echo 0)"
            echo "文件读取: $(grep -c "read_file" $LOG_FILE 2>/dev/null || echo 0)"
            echo "缓存命中: $(grep -c "缓存命中" $LOG_FILE 2>/dev/null || echo 0)"
            echo "决策跳过: $(grep -c "跳过检查" $LOG_FILE 2>/dev/null || echo 0)"
            echo "路径修正: $(grep -c "路径验证" $LOG_FILE 2>/dev/null || echo 0)"
            echo "文件合并: $(grep -c "智能合并" $LOG_FILE 2>/dev/null || echo 0)"
            
            # 显示结果
            echo -e "\n=== 执行结果 ==="
            grep -A5 "执行结果:" $LOG_FILE  < /dev/null |  tail -10
            
            # 检查输出目录
            echo -e "\n=== 生成的文件 ==="
            if [ -d "blog_management_output_v3" ]; then
                find blog_management_output_v3 -type f | head -20
                echo "文件总数: $(find blog_management_output_v3 -type f | wc -l)"
            else
                echo "输出目录不存在"
            fi
        fi
        break
    fi
    
    # 显示进度
    ELAPSED=$(($(date +%s) - START_TIME))
    echo -e "\n[$(date +%H:%M:%S)] 运行中... (${ELAPSED}秒)"
    
    if [ -f "$LOG_FILE" ]; then
        CURRENT_LINE_COUNT=$(wc -l < $LOG_FILE)
        NEW_LINES=$((CURRENT_LINE_COUNT - LAST_LINE_COUNT))
        LAST_LINE_COUNT=$CURRENT_LINE_COUNT
        
        echo "日志增长: +${NEW_LINES} 行 (总计: $CURRENT_LINE_COUNT 行)"
        
        # 显示当前进度
        CURRENT_STEP=$(grep "Planning step" $LOG_FILE 2>/dev/null | tail -1)
        if [ -n "$CURRENT_STEP" ]; then
            echo "步骤: ${CURRENT_STEP#*Planning step }"
        fi
        
        CURRENT_ACTION=$(grep "Executing tool" $LOG_FILE 2>/dev/null | tail -1)
        if [ -n "$CURRENT_ACTION" ]; then
            echo "动作: ${CURRENT_ACTION#*Executing tool }"
        fi
        
        # 显示优化效果
        CACHE_COUNT=$(grep -c "缓存命中" $LOG_FILE 2>/dev/null || echo 0)
        SKIP_COUNT=$(grep -c "跳过检查" $LOG_FILE 2>/dev/null || echo 0)
        if [ $CACHE_COUNT -gt 0 ] || [ $SKIP_COUNT -gt 0 ]; then
            echo "优化: 缓存命中=$CACHE_COUNT, 决策跳过=$SKIP_COUNT"
        fi
        
        # 检查错误
        if grep -q -i "error\|exception\|traceback" $LOG_FILE; then
            echo "⚠️  发现错误:"
            grep -i "error\|exception" $LOG_FILE | tail -2
        fi
    fi
    
    # 每30秒更新一次
    sleep 30
done

echo -e "\n监控结束"
