#\!/bin/bash
LOG_FILE="agent_cli_deepseek_final_20250726_012243.log"
PID=3174249
START_TIME=$(date +%s)

echo "=== Agent CLI v2 改进版 - 最终测试监控 ==="
echo "进程 ID: $PID"
echo "日志文件: $LOG_FILE"
echo ""

COUNTER=0
while true; do
    COUNTER=$((COUNTER + 1))
    
    # 检查进程
    if \! ps -p $PID > /dev/null 2>&1; then
        ELAPSED=$(($(date +%s) - START_TIME))
        echo -e "\n✅ 测试完成 (总时间: $(($ELAPSED/60))分$(($ELAPSED%60))秒)"
        
        # 最终统计
        echo -e "\n=== 执行统计 ==="
        grep -c "Planning step" $LOG_FILE  < /dev/null |  xargs echo "步骤数:"
        grep -c "Executing tool" $LOG_FILE | xargs echo "工具调用:"
        grep -c "write_file" $LOG_FILE | xargs echo "文件创建:"
        
        echo -e "\n=== 优化效果 ==="
        grep -c "缓存命中" $LOG_FILE | xargs echo "缓存命中:"
        grep -c "跳过检查" $LOG_FILE | xargs echo "决策跳过:"
        
        echo -e "\n=== 执行结果 ==="
        tail -5 $LOG_FILE
        
        echo -e "\n=== 生成的文件 ==="
        find blog_management_output_v3 -type f 2>/dev/null | wc -l | xargs echo "文件总数:"
        break
    fi
    
    # 进度显示
    ELAPSED=$(($(date +%s) - START_TIME))
    echo -e "\n[$(date +%H:%M:%S)] 运行中... (${ELAPSED}秒)"
    
    LINES=$(wc -l < $LOG_FILE 2>/dev/null || echo 0)
    echo "日志行数: $LINES"
    
    # 当前步骤
    grep "Planning step" $LOG_FILE 2>/dev/null | tail -1 | sed 's/.*Planning/Planning/'
    
    # 最近动作
    grep "Executing tool" $LOG_FILE 2>/dev/null | tail -1 | sed 's/.*Executing/Executing/'
    
    # 优化统计
    CACHE=$(grep -c "缓存命中" $LOG_FILE 2>/dev/null || echo 0)
    SKIP=$(grep -c "跳过检查" $LOG_FILE 2>/dev/null || echo 0)
    [ $CACHE -gt 0 ] || [ $SKIP -gt 0 ] && echo "优化: 缓存=$CACHE, 跳过=$SKIP"
    
    sleep 30
done
