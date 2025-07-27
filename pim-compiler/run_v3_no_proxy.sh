#!/bin/bash
# 清理代理设置并运行 v3 fixed
unset http_proxy
unset https_proxy  
unset all_proxy
unset HTTP_PROXY
unset HTTPS_PROXY
unset ALL_PROXY

source venv_clean/bin/activate
python direct_react_agent_v3_fixed.py