#!/bin/bash

echo "=== User Management PSM Generation Monitor ==="
echo "Started at: $(date)"
echo "Monitoring user_psm_codegen.log"
echo "Press Ctrl+C to stop"
echo

while true; do
    echo "=== Check at $(date) ==="
    
    # 检查日志文件
    if [ -f user_psm_codegen.log ]; then
        # 显示文件大小
        SIZE=$(stat -c%s user_psm_codegen.log 2>/dev/null || stat -f%z user_psm_codegen.log 2>/dev/null)
        echo "Log file size: $SIZE bytes"
        
        # 显示计划结果
        echo -e "\n--- Planning Result ---"
        grep -A 20 "=== Planning Result ===" user_psm_codegen.log | tail -25
        
        # 显示最新进度
        echo -e "\n--- Latest Progress ---"
        tail -50 user_psm_codegen.log | grep -E "(Step completed|Task completed|Error|write_file -|Creating|Writing|Iteration)"
        
        # 检查是否完成
        if grep -q "Task completed successfully" user_psm_codegen.log; then
            echo -e "\n✅ Task completed successfully!"
            
            # 显示生成的文件
            echo -e "\n--- Generated Files ---"
            if [ -d user_management/generated ]; then
                find user_management/generated -type f -name "*.py" -o -name "*.txt" -o -name "*.md" -o -name ".env*" | sort
            fi
            
            # 显示文件统计
            echo -e "\n--- File Statistics ---"
            if [ -d user_management/generated ]; then
                echo "Python files: $(find user_management/generated -name "*.py" | wc -l)"
                echo "Total files: $(find user_management/generated -type f | wc -l)"
                echo "Total lines: $(find user_management/generated -type f -exec wc -l {} + | tail -1)"
            fi
            
            break
        fi
        
        # 检查错误
        ERROR_COUNT=$(grep -c "Error:" user_psm_codegen.log 2>/dev/null || echo 0)
        if [ "$ERROR_COUNT" -gt 0 ]; then
            echo -e "\n❌ Errors found: $ERROR_COUNT"
            echo "Latest errors:"
            grep -A 3 "Error:" user_psm_codegen.log | tail -12
        fi
        
        # 显示当前步骤
        echo -e "\n--- Current Step ---"
        tail -100 user_psm_codegen.log | grep -E "Iteration [0-9]+:" | tail -1
        
        # 显示已写入的文件
        echo -e "\n--- Files Written So Far ---"
        grep "write_file -" user_psm_codegen.log | awk -F'"' '{print $4}' | sort -u
        
    else
        echo "Log file not found yet..."
    fi
    
    echo -e "\nWaiting 60 seconds for next check...\n"
    sleep 60
done

echo -e "\n=== Monitoring completed at $(date) ==="