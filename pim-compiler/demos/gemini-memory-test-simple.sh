#!/bin/bash
# gemini-memory-test-simple.sh - 最简单的测试方法

# 创建临时文件存储命令
cat > /tmp/gemini_commands.txt << EOF
我的电话号码是18674048895，请记住它。
我刚才告诉你的电话号码是什么？
exit
EOF

echo "测试 Gemini CLI 记忆功能"
echo "========================"
echo
echo "执行以下命令："
cat /tmp/gemini_commands.txt
echo
echo "========================"
echo "Gemini 输出："
echo

# 运行 Gemini CLI 并输入命令
gemini -c < /tmp/gemini_commands.txt

# 清理
rm -f /tmp/gemini_commands.txt

echo
echo "========================"
echo "测试完成！检查 Gemini 是否记住了电话号码 18674048895"