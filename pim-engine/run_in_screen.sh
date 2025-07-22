#!/bin/bash
# 在 screen 会话中运行测试

SESSION_NAME="mda_tests"
TEST_NAME=$1
TEST_CMD=$2

if [ -z "$TEST_NAME" ] || [ -z "$TEST_CMD" ]; then
    echo "用法: $0 <测试名称> <测试命令>"
    echo "示例: $0 deepseek_test 'python -m pytest tests/converters/test_pim_to_psm_deepseek.py -v'"
    exit 1
fi

# 创建或附加到 screen 会话
screen -dmS "$SESSION_NAME-$TEST_NAME" bash -c "
    export DEEPSEEK_API_KEY=\$(grep DEEPSEEK_API_KEY .env | cut -d= -f2)
    export GEMINI_API_KEY=\$(grep GEMINI_API_KEY .env | cut -d= -f2)
    echo '开始运行测试: $TEST_NAME'
    echo '命令: $TEST_CMD'
    echo '========================='
    $TEST_CMD
    echo '========================='
    echo '测试完成，按任意键退出'
    read -n 1
"

echo "✓ 测试已在 screen 会话中启动: $SESSION_NAME-$TEST_NAME"
echo ""
echo "使用以下命令查看输出:"
echo "  screen -r $SESSION_NAME-$TEST_NAME"
echo ""
echo "列出所有 screen 会话:"
echo "  screen -ls"
echo ""
echo "分离会话: Ctrl+A, D"