#!/bin/bash

echo "=== PSM Code Generation Monitor ==="
echo "Started at: $(date)"
echo "Monitoring psm_codegen_full.log"
echo "Press Ctrl+C to stop"
echo

while true; do
    echo "=== Check at $(date) ==="
    
    # 检查日志文件大小
    if [ -f psm_codegen_full.log ]; then
        SIZE=$(stat -c%s psm_codegen_full.log 2>/dev/null || stat -f%z psm_codegen_full.log 2>/dev/null)
        echo "Log file size: $SIZE bytes"
        
        # 显示计划结果
        echo -e "\n--- Planning Result ---"
        grep -A 20 "=== Planning Result ===" psm_codegen_full.log | tail -25
        
        # 显示最新进度
        echo -e "\n--- Latest Progress ---"
        tail -20 psm_codegen_full.log | grep -E "(Iteration|Step completed|Task completed|Error|Generated)"
        
        # 检查是否完成
        if grep -q "Task completed successfully" psm_codegen_full.log; then
            echo -e "\n✅ Task completed successfully!"
            
            # 显示生成的文件
            echo -e "\n--- Generated Files ---"
            if [ -d hello_world_project/generated ]; then
                find hello_world_project/generated -type f
            fi
            break
        fi
        
        # 检查错误
        if grep -q "Error:" psm_codegen_full.log; then
            echo -e "\n❌ Errors found:"
            grep -A 5 "Error:" psm_codegen_full.log | tail -10
        fi
    else
        echo "Log file not found yet..."
    fi
    
    echo -e "\nWaiting 60 seconds for next check...\n"
    sleep 60
done

echo -e "\n=== Monitoring completed at $(date) ==="