#!/bin/bash
# 监控验证程序的执行进度

LOG_FILE="hooked_validation_v2.log"
PID=1285021

echo "=========================================="
echo "监控异步记忆验证程序"
echo "PID: $PID"
echo "日志文件: $LOG_FILE"
echo "=========================================="

# 检查进程是否还在运行
if ps -p $PID > /dev/null; then
    echo "✅ 进程正在运行"
else
    echo "❌ 进程已结束"
fi

echo ""
echo "最新日志（最后30行）："
echo "------------------------------------------"
tail -30 $LOG_FILE

echo ""
echo "关键事件统计："
echo "------------------------------------------"
echo "工作Agent轮数: $(grep -c "🤔 思考第" $LOG_FILE)"
echo "工具调用次数: $(grep -c "🔧 调用工具" $LOG_FILE)"
echo "观察者快照: $(grep -c "📸.*快照" $LOG_FILE)"
echo "成功事件: $(grep -c "✅" $LOG_FILE)"
echo "错误事件: $(grep -c "❌" $LOG_FILE)"

echo ""
echo "生成的文件："
echo "------------------------------------------"
if [ -d "hooked_async_validation" ]; then
    find hooked_async_validation -type f -name "*.json" -o -name "*.py" | head -10
else
    echo "验证目录尚未创建"
fi