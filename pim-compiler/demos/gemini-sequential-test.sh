#!/bin/bash
# gemini-sequential-test.sh - 顺序执行两个独立的 Gemini 命令

echo "测试 Gemini CLI 记忆功能（顺序执行）"
echo "===================================="
echo

# 第一个命令
echo "[1] 告诉电话号码："
echo "我的电话号码是18674048895，请记住它。" | gemini -c
echo
echo "===================================="
echo

# 等待一下
sleep 2

# 第二个命令 - 注意：这会启动新的会话，所以可能记不住
echo "[2] 询问电话号码："
echo "我刚才告诉你的电话号码是什么？" | gemini -c
echo
echo "===================================="
echo

echo "注意：如果 Gemini 记不住，说明每次调用都是新会话。"
echo "需要在同一个会话中进行多轮对话。"