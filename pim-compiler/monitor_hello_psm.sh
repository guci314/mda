#!/bin/bash

echo "=== Hello World PSM Generation Monitor ==="
echo "Started at: $(date)"
echo "Monitoring hello_psm_final.log"
echo "Press Ctrl+C to stop"
echo

while true; do
    echo "=== Check at $(date) ==="
    
    # 检查日志文件
    if [ -f hello_psm_final.log ]; then
        # 显示计划结果
        echo -e "\n--- Planning Result ---"
        grep -A 15 "=== Planning Result ===" hello_psm_final.log | tail -20
        
        # 显示最新进度
        echo -e "\n--- Latest Progress ---"
        tail -30 hello_psm_final.log | grep -E "(Step completed|Task completed|Error|write_file -|Creating|Writing)"
        
        # 检查是否完成
        if grep -q "Task completed successfully" hello_psm_final.log; then
            echo -e "\n✅ Task completed successfully!"
            
            # 显示生成的文件
            echo -e "\n--- Generated Files ---"
            for file in main.py requirements.txt README.md; do
                filepath="hello_world_project/generated/$file"
                if [ -f "$filepath" ]; then
                    echo -e "\n✅ $file ($(wc -l < "$filepath") lines)"
                else
                    echo -e "\n❌ $file - Not found"
                fi
            done
            
            # 显示 main.py 预览
            if [ -f "hello_world_project/generated/main.py" ]; then
                echo -e "\n--- main.py preview (first 20 lines) ---"
                head -20 hello_world_project/generated/main.py
            fi
            
            break
        fi
        
        # 检查错误
        if grep -q "Error:" hello_psm_final.log; then
            echo -e "\n❌ Errors found:"
            grep -A 5 "Error:" hello_psm_final.log | tail -15
        fi
        
        # 显示当前步骤
        echo -e "\n--- Current Step ---"
        tail -50 hello_psm_final.log | grep -E "Iteration [0-9]+:" | tail -1
    else
        echo "Log file not found yet..."
    fi
    
    echo -e "\nWaiting 60 seconds for next check...\n"
    sleep 60
done

echo -e "\n=== Monitoring completed at $(date) ==="