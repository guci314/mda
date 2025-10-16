#!/bin/bash
# 快速测试compact_prompt.md

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}🧪 Compact提示词快速测试${NC}"
echo ""

# 检查API密钥
if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo -e "${RED}❌ 错误：未找到DEEPSEEK_API_KEY环境变量${NC}"
    echo ""
    echo "请设置环境变量："
    echo "  export DEEPSEEK_API_KEY=your_key_here"
    echo ""
    echo "或者从.env文件加载："
    echo "  source ../../.env  # 如果.env在pim-compiler目录"
    exit 1
fi

echo -e "${GREEN}✅ API密钥已配置${NC}"
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 运行测试
echo -e "${YELLOW}⏳ 运行测试中...${NC}"
python3.12 test_compact_prompt.py

# 检查退出码
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✅ 测试完成！${NC}"

    # 显示报告位置
    if [ -f "compact_test_report.json" ]; then
        echo ""
        echo "📊 详细报告："
        echo "  - 位置: tests/compact_test_report.json"

        # 如果有jq，显示简要统计
        if command -v jq &> /dev/null; then
            echo ""
            echo "📈 快速统计："
            jq -r '
                "  - 平均压缩率: \(.avg_compression * 100 | round)%",
                "  - 平均评分: \(.avg_score * 100 | round)%",
                "  - 通过测试: \([.results[] | select(.evaluation_score >= 0.7)] | length)/\(.total_tests)"
            ' compact_test_report.json
        fi
    fi
else
    echo ""
    echo -e "${RED}❌ 测试失败${NC}"
    exit 1
fi
