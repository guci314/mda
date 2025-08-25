#!/bin/bash
# 监控任务触发的验证程序

LOG_FILE="task_triggered_validation.log"
WORK_DIR="task_triggered_validation"

echo "=========================================="
echo "监控任务触发的记忆观察系统"
echo "日志文件: $LOG_FILE"
echo "=========================================="

# 检查进程
if pgrep -f "validate_task_triggered_memory.py" > /dev/null; then
    echo "✅ 进程正在运行"
else
    echo "⏸️ 进程已结束"
fi

echo ""
echo "执行阶段："
echo "------------------------------------------"
echo "阶段1 (工作Agent): $(grep -c "阶段1：工作Agent" $LOG_FILE) 次"
echo "阶段2 (观察者分析): $(grep -c "阶段2：观察者Agent" $LOG_FILE) 次"
echo "阶段3 (海马体巩固): $(grep -c "阶段3：海马体Agent" $LOG_FILE) 次"

echo ""
echo "关键事件："
echo "------------------------------------------"
echo "工作Agent轮数: $(grep -c "🤔 思考第" $LOG_FILE)"
echo "消息钩子捕获: $(grep -c "📌 \[钩子\]" $LOG_FILE)"
echo "任务完成: $(grep -c "✅ 工作Agent任务完成" $LOG_FILE)"
echo "观察者活动: $(grep -c "观察者Agent开始分析" $LOG_FILE)"

echo ""
echo "观察者记忆系统："
echo "------------------------------------------"
if [ -d "$WORK_DIR/observer/.vscode_memory" ]; then
    echo "✅ .vscode_memory 存在"
    echo "  - episodes: $(ls $WORK_DIR/observer/.vscode_memory/episodes/*.json 2>/dev/null | wc -l) 个"
    echo "  - states: $(ls $WORK_DIR/observer/.vscode_memory/states/*.json 2>/dev/null | wc -l) 个"
else
    echo "❌ .vscode_memory 不存在"
fi

if [ -d "$WORK_DIR/observer/.message_views" ]; then
    echo "✅ .message_views 存在"
    echo "  - 文件数: $(ls $WORK_DIR/observer/.message_views/*.json 2>/dev/null | wc -l)"
else
    echo "❌ .message_views 不存在"
fi

echo ""
echo "最新日志（最后20行）："
echo "------------------------------------------"
tail -20 $LOG_FILE