#!/bin/bash

echo "=== 清理 PIM Engine 过时文件 ==="
echo

# 1. 删除测试结果文件
echo "删除测试结果文件..."
rm -f ai_generation_result.json
rm -f ai_result.json
rm -f template_generation_result.json
rm -f template_result.json
rm -f generated_code.zip
rm -f pim-engine.log

# 2. 删除临时测试脚本
echo "删除临时测试脚本..."
rm -f test_ai_now.py
rm -f test_ai_detailed.py
rm -f test_simple_generation.py
rm -f test_ai_generation.js
rm -f test_ai_generation_final.sh
rm -f test_ai_local.sh
rm -f test_gemini_cli_now.sh
rm -f test_gemini_docker.sh
rm -f test_gemini_simple.sh
rm -f run_gemini_tests.sh
rm -f check_gemini_cli.sh
rm -f run_puppeteer_test.sh

# 3. 删除无用的符号链接
echo "删除无用的符号链接..."
rm -f models/models

# 4. 删除过时的文档
echo "删除过时的文档..."
rm -f gemini-cli-update.md
rm -f 测试AI生成代码.md
rm -f 使用AI生成代码指南.md

# 5. 删除重复的 Dockerfile
echo "删除重复的 Dockerfile..."
rm -f Dockerfile.llm.cn

# 6. 删除特定构建脚本（可选）
echo "删除特定构建脚本..."
rm -f build-cn.sh
rm -f build-with-proxy.sh

echo
echo "✅ 清理完成！"
echo

# 显示剩余文件
echo "=== 剩余的主要文件 ==="
ls -la | grep -E "(\.sh|\.py|\.md|\.yml|Dockerfile)" | grep -v cleanup.sh