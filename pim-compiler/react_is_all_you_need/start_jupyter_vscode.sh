#!/bin/bash
# VSCode Jupyter 启动脚本

echo "启动 Jupyter for VSCode..."

# 激活虚拟环境
source ../react_agent_env/bin/activate

# 临时禁用 SOCKS 代理
unset all_proxy

# 设置环境变量
export JUPYTER_PLATFORM_DIRS=1
export TRANSFORMERS_OFFLINE=1
export HF_DATASETS_OFFLINE=1

# 启动 Jupyter
jupyter lab --no-browser
