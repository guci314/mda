#\!/bin/bash
LOG_FILE="agent_cli_deepseek_test_20250726_005306.log"
PID=3142967
START_TIME=$(date +%s)

echo "=== Agent CLI v2 改进版 - DeepSeek 实际测试监控 ==="
echo "进程 ID: $PID"
echo "日志文件: $LOG_FILE"
echo "开始时间: $(date +%H:%M:%S)"
echo "LLM: DeepSeek"
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
        echo -e "\n[$(date +%H:%M:%S)] ✅ 进程已完成"
        echo "总执行时间: ${ELAPSED}秒 ($(($ELAPSED/60))分$(($ELAPSED%60))秒)"
        
        # 执行统计
        if [ -f "$LOG_FILE" ]; then
            echo -e "\n=== 执行统计 ==="
            echo "步骤总数: $(grep -c "Step [0-9]" $LOG_FILE 2>/dev/null || echo 0)"
            echo "动作总数: $(grep -c "Action [0-9]" $LOG_FILE 2>/dev/null || echo 0)"
            echo "工具调用: $(grep -c "Executing tool" $LOG_FILE 2>/dev/null || echo 0)"
            echo "文件创建: $(grep -c "write_file" $LOG_FILE 2>/dev/null || echo 0)"
            echo "文件读取: $(grep -c "read_file" $LOG_FILE 2>/dev/null || echo 0)"
            
            # 优化效果
            echo -e "\n=== 优化效果 ==="
            echo "缓存命中: $(grep -c "缓存命中\ < /dev/null | Cache hit" $LOG_FILE 2>/dev/null || echo 0)"
            echo "决策跳过: $(grep -c "跳过检查\|Skip" $LOG_FILE 2>/dev/null || echo 0)"
            echo "路径修正: $(grep -c "路径验证\|Path validation" $LOG_FILE 2>/dev/null || echo 0)"
            echo "文件合并: $(grep -c "智能合并\|Smart merge" $LOG_FILE 2>/dev/null || echo 0)"
            
            # 执行结果
            echo -e "\n=== 执行结果 ==="
            grep -E "执行结果:|Task completed|成功|失败" $LOG_FILE | tail -5
            
            # 生成的文件
            echo -e "\n=== 生成的文件 ==="
            if [ -d "blog_management_output_v3" ]; then
                find blog_management_output_v3 -type f -name "*.py" | sort | head -10
                echo "总文件数: $(find blog_management_output_v3 -type f | wc -l)"
            else
                echo "输出目录不存在"
            fi
        fi
        break
    fi
    
    # 显示进度
    ELAPSED=$(($(date +%s) - START_TIME))
    echo -e "\n[#$COUNTER] $(date +%H:%M:%S) - 运行中 (${ELAPSED}秒)"
    
    if [ -f "$LOG_FILE" ]; then
        CURRENT_LINE_COUNT=$(wc -l < $LOG_FILE 2>/dev/null || echo 0)
        NEW_LINES=$((CURRENT_LINE_COUNT - LAST_LINE_COUNT))
        LAST_LINE_COUNT=$CURRENT_LINE_COUNT
        
        SIZE=$(ls -lh $LOG_FILE 2>/dev/null | awk '{print $5}')
        echo "日志: $SIZE / $CURRENT_LINE_COUNT 行 (+$NEW_LINES)"
        
        # 当前步骤
        CURRENT_STEP=$(grep "Step [0-9]" $LOG_FILE 2>/dev/null | tail -1)
        if [ -n "$CURRENT_STEP" ]; then
            echo "当前步骤: $CURRENT_STEP"
        fi
        
        # 当前动作
        CURRENT_ACTION=$(grep -E "Action [0-9]|Executing tool" $LOG_FILE 2>/dev/null | tail -1)
        if [ -n "$CURRENT_ACTION" ]; then
            echo "当前动作: ${CURRENT_ACTION:0:80}..."
        fi
        
        # 实时优化统计
        CACHE_NOW=$(grep -c "缓存命中\|Cache hit" $LOG_FILE 2>/dev/null || echo 0)
        SKIP_NOW=$(grep -c "跳过检查\|Skip" $LOG_FILE 2>/dev/null || echo 0)
        FILES_NOW=$(grep -c "write_file" $LOG_FILE 2>/dev/null || echo 0)
        echo "进度: 文件=$FILES_NOW, 缓存=$CACHE_NOW, 跳过=$SKIP_NOW"
        
        # 错误检查
        ERROR_COUNT=$(grep -iE "error|exception|traceback" $LOG_FILE 2>/dev/null | wc -l)
        if [ $ERROR_COUNT -gt 0 ]; then
            echo "⚠️  发现 $ERROR_COUNT 个错误"
            grep -iE "error|exception" $LOG_FILE | tail -1
        fi
    fi
    
    # 每30秒更新
    sleep 30
done

echo -e "\n测试监控结束"
