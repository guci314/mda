#!/bin/bash
# simple-gemini-chat.sh - 简单的 Gemini CLI 聊天脚本

# 创建管道
mkfifo /tmp/gemini_in /tmp/gemini_out 2>/dev/null

# 启动 Gemini CLI
(gemini -c < /tmp/gemini_in > /tmp/gemini_out 2>&1) &
GEMINI_PID=$!

# 清理函数
cleanup() {
    kill $GEMINI_PID 2>/dev/null
    rm -f /tmp/gemini_in /tmp/gemini_out
    echo "Bye!"
}
trap cleanup EXIT

# 读取输出的后台进程
(
    while true; do
        if read -r line < /tmp/gemini_out; then
            [[ "$line" != ">" ]] && echo "$line"
        fi
    done
) &

# 主循环
echo "Gemini CLI Chat (输入 'exit' 退出)"
echo "=================================="

while true; do
    read -p "> " input
    [[ "$input" == "exit" ]] && break
    echo "$input" > /tmp/gemini_in
    sleep 1  # 给 Gemini 时间响应
done