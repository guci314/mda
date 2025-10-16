#!/bin/bash
# 检查是否有重要文件被.gitignore忽略

echo "=== 检查可能被错误忽略的重要文件 ==="
echo ""

cd "$(dirname "$0")"

# 1. 检查knowledge目录中被忽略的文件
echo "📚 检查knowledge目录..."
ignored_knowledge=$(find pim-compiler/react_is_all_you_need/knowledge -type f -name "*.md" -o -name "*.py" | while read file; do
    if git check-ignore -q "$file" 2>/dev/null; then
        echo "  ⚠️  $file"
    fi
done)

if [ -z "$ignored_knowledge" ]; then
    echo "  ✅ knowledge目录中没有被忽略的文件"
else
    echo "$ignored_knowledge"
fi

echo ""

# 2. 检查docs目录中被忽略的文件
echo "📄 检查docs目录..."
ignored_docs=$(find pim-compiler/react_is_all_you_need/docs -type f -name "*.md" 2>/dev/null | while read file; do
    if git check-ignore -q "$file" 2>/dev/null; then
        echo "  ⚠️  $file"
    fi
done)

if [ -z "$ignored_docs" ]; then
    echo "  ✅ docs目录中没有被忽略的文件"
else
    echo "$ignored_docs"
fi

echo ""

# 3. 列出所有未跟踪的文件（可能需要添加）
echo "📋 未跟踪的文件（可能需要提交）:"
untracked=$(git ls-files --others --exclude-standard | grep -E "\.(md|py)$" | head -20)

if [ -z "$untracked" ]; then
    echo "  ✅ 没有未跟踪的重要文件"
else
    echo "$untracked" | while read file; do
        echo "  📝 $file"
    done
fi

echo ""
echo "=== 检查完成 ==="
echo ""
echo "💡 如果发现重要文件被忽略，可以："
echo "   1. 修改.gitignore添加例外规则"
echo "   2. 使用 git add -f <file> 强制添加"
echo "   3. 提交并推送到GitHub"
