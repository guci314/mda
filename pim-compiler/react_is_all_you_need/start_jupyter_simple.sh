#!/bin/bash

echo "=== Jupyter Notebook 启动脚本 ==="
echo ""

# 激活虚拟环境
echo "1. 激活虚拟环境..."
source ../react_agent_env/bin/activate

# 检查环境
echo "2. 检查环境..."
python -c "import sys; print('Python路径:', sys.executable)"
python -c "import ipykernel; print('ipykernel版本:', ipykernel.__version__)"

# 检查内核
echo "3. 检查可用内核..."
jupyter kernelspec list

# 清理可能的残留进程
echo "4. 清理残留进程..."
pkill -f jupyter 2>/dev/null || true
pkill -f ipykernel 2>/dev/null || true

# 等待一下
sleep 2

# 启动Jupyter，使用更简单的配置
echo "5. 启动Jupyter Notebook..."
echo "使用端口: 8888"
echo "访问地址: http://localhost:8888"
echo "按 Ctrl+C 停止服务器"
echo ""

# 使用简化的启动参数
jupyter notebook \
    --no-browser \
    --port=8888 \
    --ip=127.0.0.1 \
    --allow-root \
    --NotebookApp.token='' \
    --NotebookApp.password='' \
    --NotebookApp.open_browser=False 