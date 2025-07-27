#!/bin/bash
# gemini-memory-test.sh - 测试 Gemini CLI 的记忆能力

# 创建命名管道
mkfifo gemini_pipe

# 启动 Gemini CLI 并重定向输入
gemini -c < gemini_pipe &
GEMINI_PID=$!

# 发送命令到 Gemini
send_to_gemini() {
    echo "$1" > gemini_pipe
}

# 清理函数
cleanup() {
    kill $GEMINI_PID 2>/dev/null
    rm -f gemini_pipe
}
trap cleanup EXIT

echo "测试 Gemini CLI 记忆功能"
echo "========================"

# 第一次交互：告诉电话号码
echo -e "\n[步骤1] 告诉 Gemini 电话号码..."
send_to_gemini "我的电话号码是18674048895，请记住它。"
sleep 3

# 第二次交互：询问电话号码
echo -e "\n[步骤2] 询问之前的电话号码..."
send_to_gemini "我刚才告诉你的电话号码是什么？"
sleep 3

echo -e "\n测试完成！"
echo "查看 Gemini 是否记住了电话号码。"

# 保持进程运行几秒以查看输出
sleep 5