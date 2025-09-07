#!/bin/bash
# Agent状态恢复工具

if [ $# -eq 0 ]; then
    echo "用法: $0 <快照目录> [目标目录]"
    echo "可用快照:"
    ls -d agent_snapshots/*/ 2>/dev/null | sed 's/^/  /'
    exit 1
fi

SNAPSHOT_DIR="$1"
TARGET_DIR="${2:-.}"

if [ ! -d "$SNAPSHOT_DIR" ]; then
    echo "错误: 快照目录不存在: $SNAPSHOT_DIR"
    exit 1
fi

echo "从快照恢复agent: $SNAPSHOT_DIR"
echo "目标目录: $TARGET_DIR"

# 恢复核心文件
cp "$SNAPSHOT_DIR/system_prompt.txt" "$TARGET_DIR/" 2>/dev/null || echo "无system_prompt.txt"
cp "$SNAPSHOT_DIR/task_process.md" "$TARGET_DIR/" 2>/dev/null || echo "无task_process.md"

# 恢复知识库
if [ -d "$SNAPSHOT_DIR/.notes" ]; then
    rm -rf "$TARGET_DIR/.notes" 2>/dev/null
    cp -r "$SNAPSHOT_DIR/.notes" "$TARGET_DIR/"
fi

# 恢复其他工作文件
find "$SNAPSHOT_DIR" -maxdepth 1 -name "*.py" -o -name "*.md" -o -name "*.json" | while read file; do
    if [ "$file" != "$SNAPSHOT_DIR/snapshot_manifest.json" ]; then
        cp "$file" "$TARGET_DIR/" 2>/dev/null
    fi
done

echo "agent恢复完成"
echo "恢复的文件:"
find "$TARGET_DIR" -name "system_prompt.txt" -o -name "task_process.md" -o -name ".notes" | sed 's/^/  /'