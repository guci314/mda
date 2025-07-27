#!/bin/bash
# 在虚拟环境中运行 ReactAgent 的便捷脚本

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查虚拟环境
if [ ! -d "react_agent_env" ]; then
    echo -e "${YELLOW}虚拟环境不存在，正在创建...${NC}"
    python -m venv react_agent_env
    
    # 激活虚拟环境并安装依赖
    source react_agent_env/bin/activate
    ./install_react_agent_deps.sh
else
    # 激活虚拟环境
    source react_agent_env/bin/activate
fi

# 检查是否在虚拟环境中
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo -e "${RED}错误：无法激活虚拟环境${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 虚拟环境已激活: $VIRTUAL_ENV${NC}"

# 设置环境变量
export DISABLE_TOKEN_PATCH=1

# 运行 ReactAgent
echo -e "${GREEN}启动 ReactAgent...${NC}"
python direct_react_agent_v3_fixed.py "$@"