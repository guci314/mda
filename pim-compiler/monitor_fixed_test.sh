#\!/bin/bash
LOG_FILE="agent_cli_deepseek_fixed_20250726_011026.log"
PID=3162957
START_TIME=$(date +%s)

echo "=== Agent CLI v2 改进版 - DeepSeek 修复后测试监控 ==="
echo "进程 ID: $PID"
echo "日志文件: $LOG_FILE"
echo "开始时间: $(date +%H:%M:%S)"
echo ""

# 等待初始化
sleep 10

COUNTER=0
LAST_LINE_COUNT=0

while true; do
    COUNTER=$((COUNTER + 1))
    
    # 检查进程状态
    if \! ps -p $PID > /dev/null 2>&1; then
        ELAPSED=$(($(date +%s) - START_TIME))
        echo -e "\n[$(date +%H:%M:%S)] ✅ 测试完成"
        echo "总执行时间: ${ELAPSED}秒 ($(($ELAPSED/60))分$(($ELAPSED%60))秒)"
        
        # 最终统计
        if [ -f "$LOG_FILE" ]; then
            echo -e "\n=== 执行统计 ==="
            echo "步骤数: $(grep -c "Planning step" $LOG_FILE 2>/dev/null || echo 0)"
            echo "动作数: $(grep -c "Executing tool" $LOG_FILE 2>/dev/null || echo 0)"
            echo "文件创建: $(grep -c "write_file" $LOG_FILE 2>/dev/null || echo 0)"
            
            # 优化效果
            echo -e "\n=== 优化效果 ==="
            CACHE_HITS=$(grep -c "缓存命中\ < /dev/null | Cache hit" $LOG_FILE 2>/dev/null || echo 0)
            SKIP_DECISIONS=$(grep -c "跳过检查\|Skip.*decision" $LOG_FILE 2>/dev/null || echo 0)
            PATH_FIXES=$(grep -c "路径修正\|Fixed path" $LOG_FILE 2>/dev/null || echo 0)
            FILE_MERGES=$(grep -c "智能合并\|Smart merge" $LOG_FILE 2>/dev/null || echo 0)
            
            echo "缓存命中: $CACHE_HITS 次"
            echo "决策跳过: $SKIP_DECISIONS 次"
            echo "路径修正: $PATH_FIXES 次"
            echo "文件合并: $FILE_MERGES 次"
            
            # 执行结果
            echo -e "\n=== 执行结果 ==="
            tail -10 $LOG_FILE | grep -E "执行结果|成功|失败|完成"
            
            # 生成的文件
            echo -e "\n=== 生成的文件 ==="
            if [ -d "blog_management_output_v3" ]; then
                FILE_COUNT=$(find blog_management_output_v3 -type f | wc -l)
                echo "总文件数: $FILE_COUNT"
                echo "目录结构:"
                tree blog_management_output_v3 2>/dev/null || find blog_management_output_v3 -type f | sort
            fi
        fi
        break
    fi
    
    # 进度显示
    ELAPSED=$(($(date +%s) - START_TIME))
    echo -e "\n[#$COUNTER] $(date +%H:%M:%S) - 运行中 (${ELAPSED}秒)"
    
    if [ -f "$LOG_FILE" ]; then
        CURRENT_LINE_COUNT=$(wc -l < $LOG_FILE 2>/dev/null || echo 0)
        NEW_LINES=$((CURRENT_LINE_COUNT - LAST_LINE_COUNT))
        LAST_LINE_COUNT=$CURRENT_LINE_COUNT
        
        echo "新增日志: +$NEW_LINES 行 (总计: $CURRENT_LINE_COUNT 行)"
        
        # 当前步骤和动作
        CURRENT_STEP=$(grep "Planning step" $LOG_FILE 2>/dev/null | tail -1)
        if [ -n "$CURRENT_STEP" ]; then
            echo "步骤: ${CURRENT_STEP#*Planning step }"
        fi
        
        RECENT_ACTION=$(grep "Executing tool" $LOG_FILE 2>/dev/null | tail -1)
        if [ -n "$RECENT_ACTION" ]; then
            echo "动作: ${RECENT_ACTION#*Executing tool }"
        fi
        
        # 实时优化统计
        CACHE_NOW=$(grep -c "缓存命中" $LOG_FILE 2>/dev/null || echo 0)
        SKIP_NOW=$(grep -c "跳过检查" $LOG_FILE 2>/dev/null || echo 0)
        FILES_NOW=$(grep -c "write_file.*成功" $LOG_FILE 2>/dev/null || echo 0)
        
        if [ $CACHE_NOW -gt 0 ] || [ $SKIP_NOW -gt 0 ]; then
            echo "优化: 缓存命中=$CACHE_NOW, 决策跳过=$SKIP_NOW, 文件创建=$FILES_NOW"
        fi
    fi
    
    # 每30秒更新
    sleep 30
done

echo -e "\n监控结束"
