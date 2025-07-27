#!/bin/bash
# 在虚拟环境中使用React Agent编译用户管理PIM

cd /home/guci/aiProjects/mda/pim-compiler

# 激活虚拟环境
source venv_test/bin/activate

# 设置输出目录
OUTPUT_DIR="output/venv_compile/react_agent_user_management"
LOG_FILE="output/venv_compile/react_agent_compile.log"

# 创建输出目录
mkdir -p output/venv_compile

echo "=== Compiling User Management PIM with React Agent ==="
echo "Python: $(which python)"
echo "Output: $OUTPUT_DIR"
echo "Log: $LOG_FILE"

# 运行编译
python compile_pim.py \
    --pim examples/user_management.md \
    --generator react-agent \
    --platform fastapi \
    --output-dir $OUTPUT_DIR \
    --max-iterations 30 \
    > $LOG_FILE 2>&1 &

PID=$!
echo "Started compilation process (PID: $PID)"
echo "Monitor progress: tail -f $LOG_FILE"

# 等待几秒检查是否正常启动
sleep 5

if ps -p $PID > /dev/null; then
    echo "✅ Process is running..."
    echo "Recent log:"
    tail -n 20 $LOG_FILE
else
    echo "❌ Process exited early"
    echo "Error log:"
    tail -n 50 $LOG_FILE
fi