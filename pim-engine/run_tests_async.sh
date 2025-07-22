#!/bin/bash
# 异步运行测试的脚本

# 设置输出目录
OUTPUT_DIR="test_results"
mkdir -p $OUTPUT_DIR

# 获取时间戳
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 运行测试函数
run_test() {
    local test_name=$1
    local test_cmd=$2
    local output_file="$OUTPUT_DIR/${test_name}_${TIMESTAMP}.log"
    
    echo "开始运行测试: $test_name"
    echo "输出文件: $output_file"
    
    # 后台运行测试
    (
        echo "=== 测试开始: $(date) ===" > $output_file
        echo "命令: $test_cmd" >> $output_file
        echo "===========================" >> $output_file
        
        # 加载环境变量
        export DEEPSEEK_API_KEY=$(grep DEEPSEEK_API_KEY /home/guci/aiProjects/mda/pim-engine/.env | cut -d= -f2)
        export GEMINI_API_KEY=$(grep GEMINI_API_KEY /home/guci/aiProjects/mda/pim-engine/.env | cut -d= -f2)
        
        # 运行测试
        eval $test_cmd >> $output_file 2>&1
        
        echo "===========================" >> $output_file
        echo "=== 测试结束: $(date) ===" >> $output_file
        echo "退出码: $?" >> $output_file
    ) &
    
    # 保存PID
    echo $! > "$OUTPUT_DIR/${test_name}.pid"
    echo "进程ID: $!"
}

# 检查测试状态
check_status() {
    echo "=== 测试状态 ==="
    for pid_file in $OUTPUT_DIR/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat $pid_file)
            test_name=$(basename $pid_file .pid)
            if ps -p $pid > /dev/null; then
                echo "[$test_name] 运行中 (PID: $pid)"
            else
                echo "[$test_name] 已完成"
                # 显示最后几行日志
                log_file="$OUTPUT_DIR/${test_name}_*.log"
                echo "  最后几行输出:"
                tail -n 5 $log_file 2>/dev/null | sed 's/^/    /'
            fi
        fi
    done
}

# 主菜单
case "$1" in
    "deepseek-pim")
        run_test "deepseek_pim" "python -m pytest tests/converters/test_pim_to_psm_deepseek.py -v"
        ;;
    "deepseek-code")
        run_test "deepseek_code" "python -m pytest tests/converters/test_psm_to_code_deepseek.py -v"
        ;;
    "gemini-langchain")
        run_test "gemini_langchain" "python -m pytest tests/converters/test_pim_to_psm_gemini_langchain.py -v"
        ;;
    "all")
        run_test "all_tests" "python -m pytest tests/converters/ -v"
        ;;
    "status")
        check_status
        ;;
    "clean")
        echo "清理测试结果..."
        rm -f $OUTPUT_DIR/*.pid
        rm -f $OUTPUT_DIR/*.log
        ;;
    *)
        echo "使用方法: $0 {deepseek-pim|deepseek-code|gemini-langchain|all|status|clean}"
        echo ""
        echo "命令说明:"
        echo "  deepseek-pim    - 运行 DeepSeek PIM 转换测试"
        echo "  deepseek-code   - 运行 DeepSeek 代码生成测试"
        echo "  gemini-langchain - 运行 Gemini LangChain 测试"
        echo "  all             - 运行所有测试"
        echo "  status          - 查看测试状态"
        echo "  clean           - 清理测试结果"
        exit 1
        ;;
esac