#!/bin/bash
# 修复 VSCode Jupyter 启动问题

echo "=== 启动 Jupyter (修复版) ==="

# 激活虚拟环境
echo "激活虚拟环境..."
source ../react_agent_env/bin/activate

# 保存原始代理设置
export ORIGINAL_ALL_PROXY=$all_proxy
export ORIGINAL_HTTP_PROXY=$http_proxy
export ORIGINAL_HTTPS_PROXY=$https_proxy

# 临时禁用 SOCKS 代理（导致 kernel 无法启动）
echo "临时禁用代理..."
unset all_proxy
unset ALL_PROXY

# 但保留 HTTP 代理用于 API 访问
echo "保留 HTTP 代理: $http_proxy"

# 启动 Jupyter Lab
echo ""
echo "启动 Jupyter Lab..."
echo "提示: 在 VSCode 中请选择 'React Agent Minimal' kernel"
echo ""

jupyter lab --port=8899 --no-browser