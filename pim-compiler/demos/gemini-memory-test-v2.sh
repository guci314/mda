#!/bin/bash
# gemini-memory-test-v2.sh - 测试 Gemini CLI 的记忆能力（改进版）

# 设置输出文件
OUTPUT_FILE="gemini_output.log"
> "$OUTPUT_FILE"  # 清空文件

# 创建命名管道
mkfifo gemini_pipe_in
mkfifo gemini_pipe_out

# 启动 Gemini CLI，同时捕获输出
(gemini -c < gemini_pipe_in 2>&1 | tee -a "$OUTPUT_FILE" > gemini_pipe_out) &
GEMINI_PID=$!

# 清理函数
cleanup() {
    echo -e "\n清理中..."
    kill $GEMINI_PID 2>/dev/null
    rm -f gemini_pipe_in gemini_pipe_out
}
trap cleanup EXIT

# 读取输出
read_response() {
    local timeout=${1:-5}
    local response=""
    local start_time=$(date +%s)
    
    while true; do
        if read -t 1 line < gemini_pipe_out; then
            echo "$line"
            response="${response}${line}\n"
            
            # 如果遇到提示符，停止读取
            if [[ "$line" == ">" ]]; then
                break
            fi
        fi
        
        # 超时检查
        local current_time=$(date +%s)
        if [ $((current_time - start_time)) -gt $timeout ]; then
            break
        fi
    done
}

echo "测试 Gemini CLI 记忆功能"
echo "========================"

# 等待 Gemini 启动
sleep 2

# 第一次交互：告诉电话号码
echo -e "\n[步骤1] 告诉 Gemini 电话号码..."
echo "发送: 我的电话号码是18674048895，请记住它。"
echo "我的电话号码是18674048895，请记住它。" > gemini_pipe_in

echo -e "\nGemini 响应:"
read_response

# 第二次交互：询问电话号码
echo -e "\n[步骤2] 询问之前的电话号码..."
echo "发送: 我刚才告诉你的电话号码是什么？"
echo "我刚才告诉你的电话号码是什么？" > gemini_pipe_in

echo -e "\nGemini 响应:"
read_response

echo -e "\n测试完成！"
echo "完整输出已保存到: $OUTPUT_FILE"
echo -e "\n查看输出文件:"
echo "================================"
cat "$OUTPUT_FILE"