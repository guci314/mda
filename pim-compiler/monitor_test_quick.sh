#!/bin/bash

echo "=== Test Quick Monitor ==="
echo "Started at: $(date)"
echo "Monitoring test_quick_output.log"
echo

check_count=0
max_checks=10  # 最多检查10次（5分钟）

while [ $check_count -lt $max_checks ]; do
    echo "=== Check #$((check_count+1)) at $(date) ==="
    
    if [ -f test_quick_output.log ]; then
        # 获取文件大小
        SIZE=$(stat -c%s test_quick_output.log 2>/dev/null || stat -f%z test_quick_output.log 2>/dev/null)
        echo "Log file size: $SIZE bytes"
        
        # 检查是否有错误
        if grep -q "Error:" test_quick_output.log; then
            echo "❌ 发现错误："
            grep -A3 "Error:" test_quick_output.log | tail -10
        fi
        
        # 检查关键执行步骤
        echo -e "\n--- 执行进度 ---"
        grep -E "(Planning Result|Step completed|Task completed|message:)" test_quick_output.log | tail -10
        
        # 检查是否完成
        if grep -q "完成!" test_quick_output.log; then
            echo -e "\n✅ 测试完成！"
            
            # 显示最终结果
            echo -e "\n--- 最终结果 ---"
            tail -20 test_quick_output.log | grep -E "(状态|耗时|成功|失败)"
            
            # 显示完整输出
            echo -e "\n--- 完整输出 ---"
            cat test_quick_output.log
            break
        fi
        
        # 检查是否有具体的工具执行
        echo -e "\n--- 工具执行情况 ---"
        grep -E "(Executing:|read_file -|write_file -)" test_quick_output.log | tail -5
        
    else
        echo "日志文件还未创建..."
    fi
    
    check_count=$((check_count+1))
    
    if [ $check_count -lt $max_checks ]; then
        echo -e "\n等待30秒后继续检查...\n"
        sleep 30
    fi
done

if [ $check_count -eq $max_checks ]; then
    echo -e "\n⚠️ 达到最大检查次数，测试可能超时"
    echo "最后的日志内容："
    tail -50 test_quick_output.log
fi

echo -e "\n=== 监控结束 at $(date) ==="