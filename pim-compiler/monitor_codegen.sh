#!/bin/bash
# 监控代码生成任务

LOG_FILE="hello_world_v2_gen.log"
OUTPUT_DIR="hello_world_v2_output"

echo "监控 Agent CLI v2 代码生成任务"
echo "日志文件: $LOG_FILE"
echo "输出目录: $OUTPUT_DIR"
echo ""

start_time=$(date +%s)

while true; do
    current_time=$(date +%s)
    elapsed=$((current_time - start_time))
    
    echo "=== 检查时间: $(date '+%H:%M:%S') (已运行 ${elapsed}秒) ==="
    
    # 检查进程
    if pgrep -f "agent_cli run" > /dev/null; then
        echo "状态: 正在执行..."
    else
        echo "状态: 执行完成"
    fi
    
    # 显示执行进度
    if [ -f "$LOG_FILE" ]; then
        echo ""
        echo "最新日志:"
        tail -20 "$LOG_FILE" | grep -E "(步骤|动作|Action|Step|✓|✗|完成|成功|失败|ERROR)"
        
        # 检查生成的文件
        echo ""
        echo "已生成文件:"
        ls -la "$OUTPUT_DIR" 2>/dev/null | grep -E "(main\.py|requirements\.txt|README\.md)"
        
        # 检查是否有多动作步骤
        if grep -q "步骤执行了多个动作" "$LOG_FILE" 2>/dev/null || grep -q "Action [2-9]:" "$LOG_FILE" 2>/dev/null; then
            echo ""
            echo "✓ 检测到多动作步骤！v2 架构特性已体现"
        fi
        
        # 检查是否完成
        if grep -q "✅" "$LOG_FILE" || grep -q "Task completed successfully" "$LOG_FILE"; then
            echo ""
            echo "任务完成！"
            
            # 显示生成的文件内容预览
            if [ -f "$OUTPUT_DIR/main.py" ]; then
                echo ""
                echo "=== main.py 预览 ==="
                head -20 "$OUTPUT_DIR/main.py"
            fi
            
            break
        elif grep -q "❌" "$LOG_FILE" || grep -q "Task failed" "$LOG_FILE"; then
            echo ""
            echo "任务失败！"
            tail -50 "$LOG_FILE" | grep -A 5 -B 5 "ERROR\|Exception\|失败"
            break
        fi
    fi
    
    echo ""
    sleep 20
done

echo ""
echo "监控结束。完整日志: $LOG_FILE"