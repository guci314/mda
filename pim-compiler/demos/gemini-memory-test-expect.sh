#!/usr/bin/expect -f
# gemini-memory-test-expect.sh - 使用 expect 测试 Gemini CLI 记忆

set timeout 10

# 启动 Gemini CLI
spawn gemini -c

# 等待提示符
expect ">"

# 第一次交互
puts "\n====== 步骤1: 告诉电话号码 ======"
send "我的电话号码是18674048895，请记住它。\r"
expect ">"

# 获取响应（跳过命令回显）
set response1 $expect_out(buffer)
puts "Gemini 响应: $response1"

# 第二次交互
puts "\n====== 步骤2: 询问电话号码 ======"
send "我刚才告诉你的电话号码是什么？\r"
expect ">"

# 获取响应
set response2 $expect_out(buffer)
puts "Gemini 响应: $response2"

# 检查是否包含电话号码
if {[string match "*18674048895*" $response2]} {
    puts "\n✅ 成功！Gemini 记住了电话号码。"
} else {
    puts "\n❌ 失败！Gemini 没有记住电话号码。"
}

# 退出
send "exit\r"
expect eof