#!/bin/bash

# 激活虚拟环境
source ../react_agent_env/bin/activate

# 启动Jupyter Notebook
echo "启动Jupyter Notebook，使用React Agent虚拟环境..."
echo "内核名称: React Agent Environment"
echo "访问地址: http://localhost:8888"
echo "按 Ctrl+C 停止服务器"
echo ""

jupyter notebook --notebook-dir=. 