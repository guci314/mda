#!/bin/bash
# 测试增强功能的脚本

echo "PIM 编译器增强功能测试"
echo "====================="

# 检查环境变量
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "警告: 未设置 DEEPSEEK_API_KEY"
fi

# 创建测试目录
mkdir -p test_output

echo ""
echo "1. 编译带单元测试的 PIM 文件到 PSM"
echo "-----------------------------------"
python -m cli.main compile examples/user_management_with_unit_tests.md \
    -o test_output \
    --verbose

echo ""
echo "2. 生成代码和单元测试"
echo "-------------------"
python -m cli.main compile examples/user_management_with_unit_tests.md \
    -o test_output \
    --generate-code \
    --verbose

echo ""
echo "3. 生成代码但跳过 lint 检查"
echo "-------------------------"
python -m cli.main compile examples/user_management_with_unit_tests.md \
    -o test_output \
    --generate-code \
    --no-lint \
    --verbose

echo ""
echo "4. 生成代码但不运行测试"
echo "---------------------"
python -m cli.main compile examples/user_management_with_unit_tests.md \
    -o test_output \
    --generate-code \
    --no-run-tests \
    --verbose

echo ""
echo "测试完成！检查 test_output 目录查看结果。"